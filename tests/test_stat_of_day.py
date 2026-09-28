"""Daily fact integration and browser behaviour with real and synthetic data."""
import html
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import unittest

from mcdraft.manager_preference import MANAGER_WELCOME_HTML
from mcdraft.stat_of_day import integrate_template, ASSETS

ROOT = Path(__file__).resolve().parents[1]


class StatOfDayTests(unittest.TestCase):
    def test_welcome_card_and_assets(self):
        result = integrate_template('<body>' + MANAGER_WELCOME_HTML + '</body>')
        self.assertEqual(result.count('id="mcd-stat-of-day"'), 1)
        self.assertLess(result.index('class="mcd-welcome-foot"'), result.index('id="mcd-stat-of-day"'))
        self.assertLess(result.index('id="mcd-stat-of-day"'), result.index('</section>'))
        for asset in re.findall(r'(?:src|href)="([^"]+)"', ASSETS):
            self.assertTrue((ROOT / asset).is_file())
        with self.assertRaises(RuntimeError):
            integrate_template(result)
        with self.assertRaises(RuntimeError):
            integrate_template('<body></body>')

    @unittest.skipUnless(os.environ.get('MCD_SEARCH_BROWSER'), 'Set MCD_SEARCH_BROWSER to Chrome/Edge')
    def test_daily_facts_in_browser(self):
        with tempfile.TemporaryDirectory(prefix='mcd-daily-stat-') as directory:
            folder = Path(directory)
            source = (ROOT / 'index.html').read_text(encoding='utf-8')
            source = source.replace('<head>', '<head><base href="' + ROOT.as_uri() + '/">', 1)
            source = re.sub(r'<script[^>]+src="https?://[^>]+></script>', '', source)
            source = source.replace('</body>', '<script src="tests/stat_of_day_browser.js"></script></body>')
            (folder / 'test.html').write_text(source, encoding='utf-8')
            args = [os.environ['MCD_SEARCH_BROWSER'], '--headless', '--disable-gpu', '--no-first-run',
                    '--no-default-browser-check', '--allow-file-access-from-files',
                    '--host-resolver-rules=MAP * ~NOTFOUND', '--virtual-time-budget=5000',
                    '--window-size=375,600', '--user-data-dir=' + str(folder / 'profile'),
                    '--dump-dom', (folder / 'test.html').as_uri()]
            result = subprocess.run(args, capture_output=True, timeout=55,
                                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            output = result.stdout.decode('utf-8', errors='replace')
            report = re.search(r'<pre id="daily-stat-test-report"[^>]*>(.*?)</pre>', output, re.S)
            self.assertIsNotNone(report, result.stderr.decode('utf-8', errors='replace')[-2000:])
            checks = json.loads(html.unescape(report.group(1)))
            self.assertFalse(any('FAILED:' in c for c in checks), checks)
            self.assertGreaterEqual(len(checks), 17, checks)
            print('\n' + checks[-1])


if __name__ == '__main__':
    unittest.main()
