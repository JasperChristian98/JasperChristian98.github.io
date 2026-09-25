"""Offline regression checks for the sticky tabs and shared next-GW forecasts."""
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest
from mcdraft.pipeline import STAGES_DIR
from mcdraft.war_room_layout import move_war_room, WAR_ROOM_NAV_JS
from mcdraft.layout_and_odds import update_layout, shared_fixture_odds, JS, CSS
from mcdraft.manager_preference import integrate_client


class DashboardLayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source=(STAGES_DIR/'10_cup_and_template.py').read_text(encoding='utf-8')
        start=source.index('html_template = r"""')+len('html_template = r"""')
        cls.template=update_layout(move_war_room(source[start:source.index('"""',start)]))

    def test_my_team_radars_are_real_subtabs_and_stay_singletons(self):
        html=self.template
        for section in ('performance','vulnerability','squad','planner','war-room'):
            self.assertEqual(html.count('id="myteam-sub-'+section+'"'),1)
        self.assertEqual(html.count('id="myteam-radar"'),1)
        self.assertEqual(html.count('id="myteam-vulnerability"'),1)
        self.assertEqual(html.count('id="myteam-vulnerability-card"'),1)
        self.assertIn("'Vulnerability radar','myteam','myteam','vulnerability'",html)
        self.assertIn("'Performance radar','myteam','myteam','performance'",html)
        self.assertLess(html.index('class="analytics-subtabs myteam-tabs"'),html.index('id="myteam-sub-squad"'))
        self.assertNotIn('id="page-war-room"',html)

    def test_overview_rankings_predictions_and_trends_are_distinct(self):
        html=self.template
        for name in ('rankings','predictions','trends'):
            self.assertEqual(html.count('id="overview-insight-'+name+'"'),1)
            self.assertIn("'overview','overview-insight','"+name+"'",html)
        self.assertEqual(html.count('__POWER_RANKINGS_TABLE__'),1)  # Overview only
        self.assertEqual(html.count('__SEASON_PREDICTION_TABLE__'),1)
        self.assertEqual(html.count('id="chart-h2h"'),1)
        self.assertIn("'overview-insight':showOverviewInsightSubtab",html)
        self.assertIn("'overview-insight':'overview-insight-'",html)
        self.assertIn('.overview-insight-tab,.myteam-tab',html)

    def test_sticky_tabs_below_responsive_header(self):
        self.assertIn('position:sticky',CSS)
        self.assertIn('--mcd-sticky-top',CSS)
        self.assertIn('header.getBoundingClientRect().height',JS)
        self.assertIn('renderTrendChart',JS)

    def test_changed_template_anchors_fail_loudly(self):
        with self.assertRaises(RuntimeError):
            update_layout(move_war_room(self.template.replace('id="myteam-radar"','id="missing-radar"')))

    def test_combined_client_javascript_syntax(self):
        if not shutil.which('node'): self.skipTest('Node not installed')
        s=(STAGES_DIR/'09_client_assets.py').read_text(encoding='utf-8')
        original=s.split('javascript = r"""',1)[1].split('"""',1)[0]
        js=integrate_client(original)+'\n'+WAR_ROOM_NAV_JS+'\n'+JS
        js=re.sub(r'__[A-Z][A-Z0-9_]*__','null',js)
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'dashboard.js';path.write_text(js,encoding='utf-8')
            result=subprocess.run(['node','--check',str(path)],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)


class SharedOddsTests(unittest.TestCase):
    def test_reversed_fixture_is_identical_with_correct_orientation(self):
        calls=[]
        def model(a,b,simulations=10000,seed=17288):
            calls.append((a,b,simulations,seed))
            return {'team1_win':63.,'draw':4.,'team2_win':33.,'team1_mean':55.,'team2_mean':45.,
                    'team1_low':36,'team1_high':68,'team2_low':27,'team2_high':63,'confidence':{'label':'medium'}}
        lookup=shared_fixture_odds(model)
        first=lookup('Alpha','Zulu')
        backward=lookup('Zulu','Alpha')
        again=lookup('Alpha','Zulu')
        self.assertEqual(len(calls),1)
        self.assertEqual(backward['team1_win'],first['team2_win'])
        self.assertEqual(backward['team2_win'],first['team1_win'])
        self.assertEqual(backward['team1_mean'],first['team2_mean'])
        self.assertEqual(backward['team1_low'],first['team2_low'])
        self.assertEqual(again,first)
        backward['confidence']['label']='corrupted'
        self.assertEqual(lookup('Alpha','Zulu')['confidence']['label'],'medium')
        lookup('Alpha','Zulu',simulations=20000)
        self.assertEqual(len(calls),2)

    def test_empty_forecasts_stay_unavailable(self):
        model=shared_fixture_odds(lambda *args,**kwargs:None)
        self.assertIsNone(model('A','B'))
        self.assertIsNone(model('B','A'))


if __name__=='__main__':unittest.main()
