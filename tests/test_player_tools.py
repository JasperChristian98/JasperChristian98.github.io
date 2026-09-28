import html
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import unittest

from mcdraft.player_tools import integrate_template
from mcdraft.club_badges import integrate_template as integrate_badges

ROOT = Path(__file__).resolve().parents[1]


class PlayerToolsTests(unittest.TestCase):
    def test_build_integration(self):
        result = integrate_template('<body></body>')
        self.assertEqual(result.count('assets/player-tools.js'), 1)
        with self.assertRaises(RuntimeError):
            integrate_template(result)

    @unittest.skipUnless(os.environ.get('MCD_SEARCH_BROWSER'), 'Set MCD_SEARCH_BROWSER to Chrome/Edge')
    def test_browser_comparison_and_lineup(self):
        with tempfile.TemporaryDirectory(prefix='mcd-player-tools-') as directory:
            folder = Path(directory)
            source = (ROOT / 'index.html').read_text(encoding='utf-8')
            if 'assets/player-tools.js' not in source:
                source = integrate_template(source)
            if 'assets/club-badges.js' not in source:
                source = integrate_badges(source)
            source = source.replace('<head>', '<head><base href="' + ROOT.as_uri() + '/">', 1)
            source = re.sub(r'<script[^>]+src="https?://[^>]+></script>', '', source)
            source = source.replace('</body>', '<script src="tests/player_tools_browser.js"></script></body>')
            (folder / 'test.html').write_text(source, encoding='utf-8')
            result = subprocess.run([os.environ['MCD_SEARCH_BROWSER'], '--headless', '--disable-gpu',
                '--no-first-run', '--no-default-browser-check', '--allow-file-access-from-files',
                '--host-resolver-rules=MAP * ~NOTFOUND', '--virtual-time-budget=8000',
                '--window-size=500,900', '--user-data-dir=' + str(folder / 'profile'),
                '--dump-dom', (folder / 'test.html').as_uri()], capture_output=True, timeout=55,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            report = re.search(r'<pre id="player-tools-report"[^>]*>(.*?)</pre>', result.stdout.decode('utf-8', errors='replace'), re.S)
            self.assertIsNotNone(report, result.stderr.decode('utf-8', errors='replace')[-2000:])
            checks = json.loads(html.unescape(report.group(1)))
            self.assertFalse(any('FAILED:' in c for c in checks), checks)
            self.assertGreaterEqual(len(checks), 18, checks)


if __name__ == '__main__':
    unittest.main()
