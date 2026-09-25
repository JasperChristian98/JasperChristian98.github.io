"""Offline integration tests for the full-screen manager welcome experience."""
import unittest
from pathlib import Path
from mcdraft.manager_preference import (
    MANAGER_WELCOME_HTML, MANAGER_HEADER_HTML, MANAGER_PICKER_CSS,
    MANAGER_PICKER_JS, integrate_client,
)
from mcdraft.decision_centre import javascript_with_data
from mcdraft.pipeline import STAGES_DIR


class ManagerPreferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        stage=(STAGES_DIR/'09_client_assets.py').read_text(encoding='utf-8')
        cls.original=stage.split('javascript = r"""',1)[1].split('"""',1)[0]

    def test_welcome_is_first_and_requires_confirmation(self):
        self.assertIn('<span class="mcd-welcome-league">__LEAGUE_NAME__',MANAGER_WELCOME_HTML)
        self.assertIn('id="mcd-welcome-team"',MANAGER_WELCOME_HTML)
        self.assertIn('onsubmit="event.preventDefault(); enterManagerDashboard()"',MANAGER_WELCOME_HTML)
        self.assertIn('id="mcd-welcome-continue" type="submit" disabled',MANAGER_WELCOME_HTML)
        self.assertIn('role="dialog" aria-modal="true"',MANAGER_WELCOME_HTML)
        self.assertIn('openManagerWelcome();',MANAGER_PICKER_JS)
        self.assertIn('modal.hidden=true;',MANAGER_PICKER_JS)
        self.assertIn('app.inert=true;',MANAGER_PICKER_JS)

    def test_global_header_picker_and_matching_theme(self):
        pipeline=(Path(__file__).parents[1]/'mcdraft/pipeline.py').read_text(encoding='utf-8')
        self.assertNotIn('MANAGER_PICKER_HTML',pipeline)
        self.assertNotIn('mcd-change-manager',MANAGER_PICKER_CSS)
        self.assertNotIn('mcd-preferred-manager-label',MANAGER_PICKER_JS)
        for token in ('var(--bg)','var(--card)','var(--border)','var(--text)','var(--accent)'):
            self.assertIn(token,MANAGER_PICKER_CSS)
        self.assertIn('change your team anytime beside the search bar',MANAGER_WELCOME_HTML)
        self.assertIn('id="mcd-header-team"',MANAGER_HEADER_HTML)
        self.assertIn("syncManagerSelection(this.value,'header')",MANAGER_HEADER_HTML)
        self.assertIn('.mcd-header-manager',MANAGER_PICKER_CSS)
        self.assertIn('MANAGER_HEADER_HTML',pipeline)
        self.assertIn('@media(max-width:620px)',MANAGER_PICKER_CSS)

    def test_syncs_existing_features(self):
        script=integrate_client(self.original)
        self.assertIn('safeInit("welcome screen", initialiseManagerPreference)',script)
        for selector in ('my-team-select','war-room-manager','decision-manager'):
            self.assertIn(selector,script)
        self.assertIn('renderDecisionCentre()',script)
        self.assertIn('localStorage.setItem(MCD_MANAGER_PREFERENCE_KEY,manager)',script)
        self.assertIn("document.getElementById('mcd-header-team')",script)

    def test_html_integration(self):
        from mcdraft.pipeline import run
        source=Path(run.__code__.co_filename).read_text(encoding='utf-8')
        self.assertIn('MANAGER_WELCOME_HTML',source)
        self.assertIn("body_anchor = '<body>'",source)
        self.assertIn('header_search',source)

    def test_fail_closed_on_changed_anchors(self):
        with self.assertRaises(RuntimeError):
            integrate_client('function initialiseDashboard() {}')

    def test_full_javascript_syntax(self):
        import shutil,subprocess,tempfile,re
        if not shutil.which('node'): self.skipTest('Node.js unavailable')
        script=integrate_client(self.original)+'\n'+javascript_with_data({})
        script=re.sub(r'__[A-Z][A-Z0-9_]*__','null',script)
        with tempfile.TemporaryDirectory() as folder:
            file=Path(folder)/'dashboard.js'
            file.write_text(script,encoding='utf-8')
            result=subprocess.run(['node','--check',str(file)],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)

if __name__=='__main__': unittest.main()
