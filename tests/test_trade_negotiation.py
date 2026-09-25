"""Trade Negotiation Room integration and regression checks."""
import ast
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from mcdraft.trade_negotiation import integrate_template, JS, CSS, ROOM_HTML
from mcdraft.pipeline import PACKAGE_DIR, STAGES_DIR
from mcdraft.war_room_layout import move_war_room
from mcdraft.layout_and_odds import update_layout


class TradeNegotiationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source=(STAGES_DIR/'10_cup_and_template.py').read_text(encoding='utf-8')
        tree=ast.parse(source)
        template=next(n.value.value for n in ast.walk(tree)
            if isinstance(n,ast.Assign)
            and any(isinstance(t,ast.Name) and t.id=='html_template' for t in n.targets)
            and isinstance(n.value,ast.Constant) and isinstance(n.value.value,str))
        cls.template=update_layout(move_war_room(template))

    def test_moves_trade_archive_to_separate_tab_without_losing_data(self):
        html=integrate_template(self.template)
        self.assertEqual(html.count('id="transfer-subpanel-trades"'),1)
        self.assertEqual(html.count('id="transfer-subpanel-history"'),1)
        self.assertEqual(html.count('__HISTORICAL_TRADES__'),1)
        self.assertEqual(html.count('__TRADES_TABLE__'),1)
        self.assertEqual(html.count('__TRADE_SIMULATOR__'),1)
        room=html[html.index('id="transfer-subpanel-trades"'):html.index('id="transfer-subpanel-history"')]
        history=html[html.index('id="transfer-subpanel-history"'):html.index('id="page-draft-centre"')]
        self.assertIn('mcd-negotiation-room',room)
        self.assertNotIn('__HISTORICAL_TRADES__',room)
        self.assertIn('__HISTORICAL_TRADES__',history)
        self.assertIn('__TRADES_TABLE__',history)
        self.assertIn("['Trade History','transfers','transfers','history']",html)
        room=html[html.index('id="transfer-subpanel-trades"'):html.index('id="transfer-subpanel-lab"')]
        lab=html[html.index('id="transfer-subpanel-lab"'):html.index('id="transfer-subpanel-history"')]
        self.assertNotIn('__TRADE_SIMULATOR__',room)
        self.assertIn('__TRADE_SIMULATOR__',lab)
        self.assertIn("['Trade Lab','transfers','transfers','lab']",html)

    def test_invalid_html_anchor_fails_loudly(self):
        with self.assertRaises(RuntimeError):
            integrate_template(self.template.replace('__TRADE_SIMULATOR__','__TRADE_LAB_CHANGED__'))
        with self.assertRaises(RuntimeError):
            integrate_template(self.template.replace('__HISTORICAL_TRADES__','__TRADE_ARCHIVE_CHANGED__'))

    def test_original_trade_lab_is_reused_for_analysis(self):
        self.assertIn('const mcdOriginalEvaluateTradeSimulator=evaluateTradeSimulator',JS)
        self.assertIn("const TRADE_SIMULATOR_DATA",(STAGES_DIR/'09_client_assets.py').read_text())
        self.assertIn('renderTradeSimulator()',JS)
        self.assertIn('samePositionSignature',JS)
        self.assertIn('mcdNegOriginalSyncManagerSelection',JS)
        self.assertIn('Safe',ROOM_HTML)
        self.assertIn('Ambitious',ROOM_HTML)

    @unittest.skipUnless(shutil.which('node'),'Node not installed')
    def test_package_generation_and_viewer_labels(self):
        import json
        rosters={name:[dict(id=side*100+i,name=f'{name} {i}',position=pos,
                           value=40+i*2+side,projection=4+i*.05,form=4,importance=5)
                       for i,pos in enumerate(['GKP']*2+['DEF']*5+['MID']*5+['FWD']*3)]
                 for side,name in enumerate(['A','B'])}
        script=('const TRADE_SIMULATOR_DATA='+json.dumps(rosters)+';'
                'const document={addEventListener(){}};'
                'function evaluateTradeSimulator(){} function draftScoutTrade(){}'
                'function escapePlayerHTML(s){return String(s);}' + JS
                + (Path(__file__).parent/'negotiation_behaviour.js').read_text())
        result=subprocess.run(['node','-e',script],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)

    @unittest.skipUnless(shutil.which('node'),'Node not installed')
    def test_trade_negotiation_javascript_syntax(self):
        with tempfile.NamedTemporaryFile(suffix='.js',mode='w',delete=False) as f:
            f.write(JS)
            path=f.name
        try:
            result=subprocess.run(['node','--check',path],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
        finally:
            Path(path).unlink(missing_ok=True)


if __name__=='__main__':unittest.main()
