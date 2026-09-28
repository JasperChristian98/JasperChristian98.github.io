import html
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import unittest

from mcdraft.subtab_order import integrate_template


ROOT = Path(__file__).resolve().parents[1]


class SubtabOrderTests(unittest.TestCase):
    def test_asset_is_added_once(self):
        result = integrate_template('<html><body></body></html>')
        self.assertEqual(result.count('assets/subtab-order.js'), 1)
        with self.assertRaises(RuntimeError):
            integrate_template(result)

    def test_asset_covers_sidebar_quick_links(self):
        script = (ROOT / 'assets' / 'subtab-order.js').read_text(encoding='utf-8')
        self.assertIn('#mcd-sidebar-sections .mcd-nav-children', script)
        self.assertIn('sortMcDraftQuickLinks', script)

    @unittest.skipUnless(os.environ.get('MCD_SEARCH_BROWSER'), 'Set MCD_SEARCH_BROWSER to Chrome/Edge')
    def test_all_subtab_bars_are_alphabetical(self):
        with tempfile.TemporaryDirectory(prefix='mcd-subtabs-') as directory:
            folder = Path(directory)
            source = (ROOT / 'index.html').read_text(encoding='utf-8')
            source = source.replace('<head>', '<head><base href="' + ROOT.as_uri() + '/">', 1)
            source = re.sub(r'<script[^>]+src="https?://[^>]+></script>', '', source)
            source = source.replace('</body>', '<script src="tests/subtab_order_browser.js"></script></body>')
            page = folder / 'test.html'
            page.write_text(source, encoding='utf-8')
            result = subprocess.run([
                os.environ['MCD_SEARCH_BROWSER'], '--headless', '--disable-gpu', '--no-first-run',
                '--no-default-browser-check', '--allow-file-access-from-files',
                '--host-resolver-rules=MAP * ~NOTFOUND', '--virtual-time-budget=5000',
                '--window-size=1440,1000', '--user-data-dir=' + str(folder / 'profile'),
                '--dump-dom', page.as_uri()
            ], capture_output=True, timeout=45,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            document = result.stdout.decode('utf-8', errors='replace')
            report = re.search(r'<pre id="subtab-order-report"[^>]*>(.*?)</pre>', document, re.S)
            self.assertIsNotNone(report, result.stderr.decode('utf-8', errors='replace')[-1200:])
            checks = json.loads(html.unescape(report.group(1)))
            self.assertFalse(any(check.startswith('FAILED:') for check in checks), checks)


if __name__ == '__main__':
    unittest.main()
