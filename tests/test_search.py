"""Build integration plus optional real-dashboard browser search checks."""
import ast
import html
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import unittest

from mcdraft.search import integrate_template, ASSETS
from mcdraft.league_chat import integrate_template as integrate_chat

ROOT = Path(__file__).resolve().parents[1]


class SearchTests(unittest.TestCase):
    def test_build_integration(self):
        tree = ast.parse((ROOT / 'mcdraft/stages/10_cup_and_template.py').read_text(encoding='utf-8'))
        template = next(n.value.value for n in ast.walk(tree) if isinstance(n, ast.Assign)
                        and any(isinstance(t, ast.Name) and t.id == 'html_template' for t in n.targets))
        result = integrate_template(template)
        self.assertEqual(result.count('id="page-search"'), 1)
        self.assertIn('__JAVASCRIPT__', result)
        for asset in re.findall(r'(?:src|href)="([^"]+)"', ASSETS):
            self.assertTrue((ROOT / asset).is_file())
        with self.assertRaises(RuntimeError):
            integrate_template(result)
        with self.assertRaises(RuntimeError):
            integrate_template('')

    @unittest.skipUnless(os.environ.get('MCD_SEARCH_BROWSER'), 'Set MCD_SEARCH_BROWSER to Chrome/Edge')
    def test_real_dashboard_in_browser(self):
        with tempfile.TemporaryDirectory(prefix='mcd-search-') as directory:
            folder = Path(directory)
            source = (ROOT / 'index.html').read_text(encoding='utf-8')
            if 'id="page-league-chat"' not in source:
                source = integrate_chat(source)
            source = source.replace('<head>', '<head><base href="' + ROOT.as_uri() + '/">', 1)
            # The local index/data and search need no third-party scripts or services.
            source = re.sub(r'<script[^>]+src="https?://[^>]+></script>', '', source)
            source = source.replace('</body>', '<script src="tests/search_browser.js"></script></body>')
            (folder / 'test.html').write_text(source, encoding='utf-8')
            args = [os.environ['MCD_SEARCH_BROWSER'], '--headless', '--disable-gpu', '--no-first-run',
                    '--no-default-browser-check', '--allow-file-access-from-files',
                    '--host-resolver-rules=MAP * ~NOTFOUND', '--virtual-time-budget=15000',
                    '--window-size=500,900', '--user-data-dir=' + str(folder / 'profile'),
                    '--dump-dom', (folder / 'test.html').as_uri()]
            result = subprocess.run(args, capture_output=True, timeout=55,
                                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            output = result.stdout.decode('utf-8', errors='replace')
            report = re.search(r'<pre id="search-test-report"[^>]*>(.*?)</pre>', output, re.S)
            self.assertIsNotNone(report, result.stderr.decode('utf-8', errors='replace')[-2000:])
            checks = json.loads(html.unescape(report.group(1)))
            self.assertFalse(any('FAILED:' in c for c in checks), checks)
            self.assertGreaterEqual(len(checks), 18, checks)


if __name__ == '__main__':
    unittest.main()
