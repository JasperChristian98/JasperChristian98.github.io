"""Offline regression coverage for My Team War Room and single header manager picker."""
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from mcdraft.war_room_layout import move_war_room, WAR_ROOM_NAV_JS
from mcdraft.manager_preference import MANAGER_PICKER_CSS, integrate_client
from mcdraft.decision_centre import javascript_with_data
from mcdraft.pipeline import STAGES_DIR


class WarRoomLayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = (STAGES_DIR / '10_cup_and_template.py').read_text(encoding='utf-8')
        start = source.index('html_template = r"""') + len('html_template = r"""')
        cls.original = source[start:source.index('"""', start)]
        cls.updated = move_war_room(cls.original)

    def test_war_room_exists_only_inside_my_team(self):
        self.assertNotIn('id="page-war-room"', self.updated)
        self.assertEqual(self.updated.count('id="myteam-sub-war-room"'), 1)
        self.assertEqual(self.updated.count('__MANAGER_WAR_ROOM_HTML__'), 1)
        self.assertEqual(self.updated.count('data-myteam-section="war-room"'), 1)
        self.assertIn("showMyTeamSubtab('war-room',this)", self.updated)
        self.assertIn("['Manager War Room','myteam','myteam','war-room']", self.updated)
        self.assertNotIn("['Manager War Room','war-room']", self.updated)

    def test_existing_links_redirect_and_render(self):
        self.assertIn("if (pageName === 'war-room')", WAR_ROOM_NAV_JS)
        self.assertIn("mcdOriginalShowPage('myteam')", WAR_ROOM_NAV_JS)
        self.assertIn("showMyTeamSubtab('war-room',tab)", WAR_ROOM_NAV_JS)
        self.assertIn("requestAnimationFrame(renderManagerWarRoom)", WAR_ROOM_NAV_JS)
        self.assertIn('#myteam-sub-war-room .war-room-manager-select{display:none!important}', MANAGER_PICKER_CSS)
        self.assertIn('#decision-centre .decision-head > label:has(#decision-manager)', MANAGER_PICKER_CSS)

    def test_changed_anchors_fail_loudly(self):
        with self.assertRaises(RuntimeError):
            move_war_room(self.original.replace('id="page-war-room"', 'id="unknown"'))

    def test_combined_js_syntax(self):
        if not shutil.which('node'):
            self.skipTest('Node.js unavailable')
        stage = (STAGES_DIR / '09_client_assets.py').read_text(encoding='utf-8')
        script = stage.split('javascript = r"""',1)[1].split('"""',1)[0]
        script = integrate_client(script) + '\n' + javascript_with_data({}) + '\n' + WAR_ROOM_NAV_JS
        script = re.sub(r'__[A-Z][A-Z0-9_]*__','null',script)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'combined.js'
            path.write_text(script,encoding='utf-8')
            result = subprocess.run(['node','--check',str(path)],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)


if __name__ == '__main__':
    unittest.main()
