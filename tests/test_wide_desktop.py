import html
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import unittest
from mcdraft.wide_desktop import integrate_template

ROOT=Path(__file__).resolve().parents[1]


class WideDesktopTests(unittest.TestCase):
    def test_integration(self):
        result=integrate_template('<head></head><body></body>')
        self.assertEqual(result.count('assets/wide-desktop.css'),1)
        with self.assertRaises(RuntimeError):
            integrate_template(result)

    @unittest.skipUnless(os.environ.get('MCD_SEARCH_BROWSER'),'Set MCD_SEARCH_BROWSER to Chrome/Edge')
    def test_viewport_layouts(self):
        for width,height in [(2560,1440),(1920,1080),(1707,960),(390,844)]:
            with self.subTest(viewport=(width,height)),tempfile.TemporaryDirectory(prefix='mcd-wide-') as directory:
                folder=Path(directory)
                source=(ROOT/'index.html').read_text(encoding='utf-8')
                source=source.replace('<head>','<head><base href="'+ROOT.as_uri()+'/">',1)
                source=re.sub(r'<script[^>]+src="https?://[^>]+></script>','',source)
                source=source.replace('</body>','<script src="tests/wide_desktop_browser.js"></script></body>')
                (folder/'test.html').write_text(source,encoding='utf-8')
                result=subprocess.run([os.environ['MCD_SEARCH_BROWSER'],'--headless','--disable-gpu','--no-first-run',
                    '--no-default-browser-check','--allow-file-access-from-files','--host-resolver-rules=MAP * ~NOTFOUND',
                    '--force-device-scale-factor=1','--virtual-time-budget=8000',f'--window-size={width},{height}',
                    '--user-data-dir='+str(folder/'profile'),'--dump-dom',(folder/'test.html').as_uri()],
                    capture_output=True,timeout=55,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
                report=re.search(r'<pre id="wide-desktop-report"[^>]*>(.*?)</pre>',result.stdout.decode('utf-8',errors='replace'),re.S)
                self.assertIsNotNone(report,result.stderr.decode('utf-8',errors='replace')[-1200:])
                checks=json.loads(html.unescape(report.group(1)))
                self.assertFalse(any('FAILED:' in c for c in checks),checks)
