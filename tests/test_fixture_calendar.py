"""Calendar integration and real-dashboard browser checks."""
import html
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import unittest
from mcdraft.fixture_calendar import integrate_template

ROOT = Path(__file__).resolve().parents[1]


class FixtureCalendarTests(unittest.TestCase):
    def test_integration_and_safe_schedule(self):
        source = '<section class="page active" id="page-overview"></section>' + "['League overview','overview','overview','standings'],</body>"
        output = integrate_template(source, {'1': [{'team1': '</script><script>alert(1)</script>'}]})
        self.assertEqual(output.count('id="page-calendar"'), 1)
        self.assertIn("['Fixture calendar','calendar']", output)
        self.assertNotIn('</script><script>alert', output)
        with self.assertRaises(RuntimeError):
            integrate_template(output)
        with self.assertRaises(RuntimeError):
            integrate_template('</body>')

    @unittest.skipUnless(os.environ.get('MCD_SEARCH_BROWSER'), 'Set MCD_SEARCH_BROWSER to Chrome/Edge')
    def test_calendar_in_browser(self):
        with tempfile.TemporaryDirectory(prefix='mcd-calendar-') as directory:
            folder = Path(directory)
            source = (ROOT/'index.html').read_text(encoding='utf-8').replace('<head>', '<head><base href="'+ROOT.as_uri()+'/">', 1)
            source = re.sub(r'<script[^>]+src="https?://[^>]+></script>', '', source)
            source = source.replace('</body>', '<script src="tests/fixture_calendar_browser.js"></script></body>')
            (folder/'test.html').write_text(source, encoding='utf-8')
            result = subprocess.run([os.environ['MCD_SEARCH_BROWSER'], '--headless', '--disable-gpu', '--no-first-run', '--allow-file-access-from-files', '--host-resolver-rules=MAP * ~NOTFOUND', '--virtual-time-budget=5000', '--window-size=500,800', '--user-data-dir='+str(folder/'profile'), '--dump-dom', (folder/'test.html').as_uri()], capture_output=True, timeout=55, creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
            report = re.search(r'<pre id="calendar-test-report">(.*?)</pre>', result.stdout.decode('utf-8', errors='replace'), re.S)
            self.assertIsNotNone(report, result.stderr.decode('utf-8', errors='replace')[-1500:])
            checks = json.loads(html.unescape(report.group(1)))
            self.assertFalse(any('FAILED' in c for c in checks), checks)
            self.assertGreaterEqual(len(checks), 10)
