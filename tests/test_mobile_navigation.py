"""Regression checks for consolidated mobile navigation and sticky subtabs."""
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from mcdraft.mobile_navigation import CSS, JS, append_final_mobile_css
from mcdraft.layout_and_odds import update_layout
from mcdraft.war_room_layout import move_war_room
from mcdraft.pipeline import STAGES_DIR


class MobileNavigationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        raw = (STAGES_DIR / '10_cup_and_template.py').read_text(encoding='utf-8')
        start = raw.index('html_template = r"""') + len('html_template = r"""')
        cls.template = update_layout(move_war_room(raw[start:raw.index('"""',start)]))

    def test_css_injected_after_legacy_not_before(self):
        transformed = append_final_mobile_css(self.template)
        self.assertEqual(transformed.count('McDraft mobile navigation v1'), 1)
        self.assertLess(transformed.index('__CSS__'), transformed.index('McDraft mobile navigation v1'))
        with self.assertRaises(RuntimeError):
            append_final_mobile_css(transformed)
        with self.assertRaises(RuntimeError):
            append_final_mobile_css('<style>changed</style>')

    def test_one_menu_five_destinations(self):
        transformed = append_final_mobile_css(self.template)
        self.assertEqual(transformed.count('id="mcd-mobile-bottom"'), 1)
        self.assertEqual(transformed.count('id="mcd-mobile-sheet"'), 1)
        self.assertEqual(transformed.count('id="mcd-mobile-current"'), 1)
        for page in ('home','myteam','league','market','more'):
            self.assertIn('data-mcd-mobile="'+page+'"', transformed)
        self.assertIn('MCD_MENU', transformed)
        self.assertNotIn('const MCD_MENU', JS)

    def test_shared_sticky_offsets_and_safe_areas(self):
        for marker in ('#page-myteam>.myteam-tabs', '#page-overview>.overview-tabs',
                       '#overview-sub-intelligence>.overview-insight-tabs'):
            self.assertIn(marker, CSS)
        self.assertIn('overflow:visible!important', CSS)
        self.assertIn('env(safe-area-inset-bottom)', CSS)
        self.assertIn('--mcd-overview-tabs-height', CSS)
        self.assertIn('prefers-reduced-motion', CSS)
        self.assertIn('mcdMeasureStickyTabs()', JS)
        self.assertIn('centreActive', JS)
        self.assertIn("ev.key!=='Tab'", JS)

    def test_client_script_syntax(self):
        if not shutil.which('node'):
            self.skipTest('node not installed')
        with tempfile.TemporaryDirectory() as temp:
            filename = Path(temp) / 'mobile-navigation.js'
            filename.write_text(JS,encoding='utf-8')
            result = subprocess.run(['node','--check',str(filename)],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)

    def test_pipeline_integrates_nav_after_existing_features(self):
        import inspect
        from mcdraft.pipeline import run
        src = inspect.getsource(run)
        self.assertIn("state['javascript'] += '\\n' + MOBILE_NAV_JS",src)
        self.assertIn("append_final_mobile_css(state['html_template'])",src)
        self.assertLess(src.index('insert_header_countdown('),src.index('append_final_mobile_css('))


if __name__=='__main__': unittest.main()
