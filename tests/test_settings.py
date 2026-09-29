import html
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import unittest

from mcdraft.settings import NAV, integrate_template

ROOT = Path(__file__).resolve().parents[1]


class SettingsTests(unittest.TestCase):
    def test_build_integration(self):
        source = '<body>' + NAV + '<section class="page" id="page-analytics"></section></body>'
        result = integrate_template(source)
        self.assertEqual(result.count('id="page-settings"'), 1)
        self.assertIn('assets/settings.js', result)
        self.assertIn(NAV + "\n  ['Settings','settings'],", result)
        with self.assertRaises(RuntimeError):
            integrate_template(result)

    @unittest.skipUnless(os.environ.get('MCD_SEARCH_BROWSER'), 'Set MCD_SEARCH_BROWSER to Chrome/Edge')
    def test_preferences_persist_and_remain_usable_without_storage(self):
        with tempfile.TemporaryDirectory(prefix='mcd-settings-') as directory:
            folder = Path(directory)
            source = (ROOT / 'index.html').read_text(encoding='utf-8')
            source = source.replace('<head>', '<head><base href="' + ROOT.as_uri() + '/">', 1)
            source = re.sub(r'<script[^>]+src="https?://[^>]+></script>', '', source)
            source = source.replace('</body>', '<script src="tests/settings_browser.js"></script></body>')
            page = folder / 'test.html'
            page.write_text(source, encoding='utf-8')
            for phase in ('save', 'reload'):
                result = subprocess.run([
                    os.environ['MCD_SEARCH_BROWSER'], '--headless', '--disable-gpu', '--no-first-run',
                    '--no-default-browser-check', '--allow-file-access-from-files',
                    '--host-resolver-rules=MAP * ~NOTFOUND', '--virtual-time-budget=10000',
                    '--window-size='+os.environ.get('MCD_SETTINGS_SIZE','1280,900'), '--user-data-dir=' + str(folder / 'profile'),
                    '--dump-dom', page.as_uri() + '?phase=' + phase,
                ], capture_output=True, timeout=60,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
                document = result.stdout.decode('utf-8', errors='replace')
                report = re.search(r'<pre id="settings-report"[^>]*>(.*?)</pre>', document, re.S)
                self.assertIsNotNone(report, result.stderr.decode('utf-8', errors='replace')[-1200:])
                checks = json.loads(html.unescape(report.group(1)))
                self.assertFalse(any(check.startswith('FAILED:') for check in checks), checks)
