"""Offline integration checks; backend permissions have a separate SQL suite."""
import ast
import hashlib
import html
import json
import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

from mcdraft.league_chat import integrate_template, PAGE_HTML, ASSETS
from mcdraft.pipeline import STAGES_DIR, REPO_DIR


class LeagueChatTests(unittest.TestCase):
    def template(self):
        tree=ast.parse((STAGES_DIR/'10_cup_and_template.py').read_text(encoding='utf-8'))
        return next(n.value.value for n in ast.walk(tree) if isinstance(n,ast.Assign)
                    and any(isinstance(t,ast.Name) and t.id=='html_template' for t in n.targets))

    def test_navigation_and_assets_survive_build(self):
        result=integrate_template(self.template())
        self.assertEqual(result.count('id="page-league-chat"'),1)
        self.assertEqual(result.count("['League chat','league-chat']"),1)
        self.assertIn('__JAVASCRIPT__',result)
        for path in re.findall(r'(?:src|href)="([^"]+)"',ASSETS):
            self.assertTrue((REPO_DIR/path).is_file(),path)

    def test_fail_closed_for_duplicate_or_missing_anchors(self):
        with self.assertRaises(RuntimeError):
            integrate_template(integrate_template(self.template()))
        with self.assertRaises(RuntimeError):
            integrate_template(self.template().replace("['Results & Team of the Week','gameweeks'],",''))

    def test_all_bound_ui_elements_exist(self):
        script=(REPO_DIR/'assets/league-chat.js').read_text(encoding='utf-8')
        ids=set(re.findall(r'id="([^"]+)"',PAGE_HTML))
        for name in re.findall(r"\bel\('([^']+)'\)",script):
            self.assertIn('chat-'+name,ids)

    def test_public_configuration_and_pinned_dependency(self):
        config=(REPO_DIR/'assets/chat-config.js').read_text()
        self.assertRegex(config,r"supabaseUrl: '(?:https://[^']+)?'")
        self.assertRegex(config,r"publishableKey: '(?:sb_publishable_[^']+)?'")
        self.assertNotIn('sb_secret_',config)
        client=REPO_DIR/'assets/vendor/supabase-2.117.2.js'
        self.assertEqual(hashlib.sha256(client.read_bytes()).hexdigest(),
                         '59d39487c3589843b410322d8a3d562ce022aba1e5ccb16898ef3fb2a0da2ecd')

    def test_team_aliases_match_membership_setup(self):
        config=(REPO_DIR/'assets/chat-config.js').read_text(encoding='utf-8')
        aliases=json.loads(re.search(r'teamLogins:\s*(\{.*?\})',config,re.S).group(1))
        self.assertEqual(len(set(aliases.values())),len(aliases))
        sql=(REPO_DIR/'supabase/setup_team_memberships.sql').read_text(encoding='utf-8')
        for team,alias in aliases.items():
            self.assertRegex(alias,r'^team-\d+@chat\.mcdraft\.invalid$')
            self.assertIn("('"+alias+"', '"+team.replace("'","''")+"')",sql)
        script=(REPO_DIR/'assets/league-chat.js').read_text(encoding='utf-8')
        self.assertIn('signInWithPassword',script)
        self.assertNotIn('signInWithOtp',script)
        self.assertNotIn('verifyOtp',script)

    @unittest.skipUnless(os.environ.get('MCD_CHAT_BROWSER'), 'Set MCD_CHAT_BROWSER to Chrome/Edge for browser tests')
    def test_browser_chat_lifecycle(self):
        with tempfile.TemporaryDirectory(prefix='mcdraft-chat-test-') as directory:
            folder=Path(directory)
            page=PAGE_HTML.replace('class="page"','class="page active"')
            source=('<html><head><meta name="viewport" content="width=device-width,initial-scale=1">'
                    '<base href="'+REPO_DIR.as_uri()+'/">'
                    '<link rel="stylesheet" href="assets/league-chat.css"></head><body>'+page+
                    '<script src="tests/chat_browser_fixture.js"></script>'
                    '<script src="assets/league-chat.js"></script>'
                    '<script src="assets/chat-sharing.js"></script></body></html>')
            (folder/'test.html').write_text(source,encoding='utf-8')
            args=[os.environ['MCD_CHAT_BROWSER'],'--headless','--disable-gpu','--no-first-run',
                  '--no-default-browser-check','--allow-file-access-from-files',
                  '--host-resolver-rules=MAP * ~NOTFOUND','--virtual-time-budget=12000',
                  '--window-size=500,900','--user-data-dir='+str(folder/'profile'),
                  '--dump-dom',(folder/'test.html').as_uri()]
            result=subprocess.run(args,capture_output=True,timeout=50,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
            output=result.stdout.decode('utf-8',errors='replace')
            report=re.search(r'<pre id="chat-test-report"[^>]*>(.*?)</pre>',output,re.S)
            self.assertIsNotNone(report,result.stderr.decode('utf-8',errors='replace')[-2000:])
            checks=json.loads(html.unescape(report.group(1)))
            self.assertFalse(any('FAILED:' in c for c in checks),checks)
            self.assertGreaterEqual(len(checks),15)


if __name__=='__main__':
    unittest.main()
