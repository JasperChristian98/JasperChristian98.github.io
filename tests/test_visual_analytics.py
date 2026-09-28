import html
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import unittest

from mcdraft.visual_analytics import integrate_template, refresh_existing_template


ROOT = Path(__file__).resolve().parents[1]


class VisualAnalyticsTests(unittest.TestCase):
    def test_integration_adds_page_tab_and_assets_once(self):
        source = '''<body><div class="analytics-subtabs" role="tablist" aria-label="Analytics sections">
<button class="analytics-subtab active" type="button" onclick="showAnalyticsSubtab('insights', this)">McDraft Insights</button></div>
<div class="analytics-subpage active" id="analytics-sub-insights"></div>
<script>const MCD_MENU=[{items:[['McDraft Insights','analytics','analytics','insights'],]}];</script></body>'''
        result = integrate_template(source)
        self.assertIn('analytics-sub-visuals', result)
        self.assertIn("showAnalyticsSubtab('visuals', this)", result)
        self.assertIn("['Visual Analytics','analytics','analytics','visuals']", result)
        refreshed = refresh_existing_template(result)
        self.assertIn('Visual Analytics <span>11</span>', refreshed)
        self.assertEqual(refreshed.count('id="analytics-sub-visuals"'), 1)
        self.assertIn('assets/visual-analytics.js', result)
        with self.assertRaises(RuntimeError):
            integrate_template(result)

    def test_pipeline_integrates_after_the_analytics_placeholder_is_published(self):
        pipeline = (ROOT / 'mcdraft' / 'pipeline.py').read_text(encoding='utf-8')
        self.assertNotIn("state['html_template'] = integrate_visual_analytics", pipeline)
        integration = pipeline.index('rendered_html = integrate_visual_analytics(rendered_html)')
        published_output_check = pipeline.index('if not output.is_file()')
        self.assertGreater(integration, published_output_check)

    @unittest.skipUnless(os.environ.get('MCD_SEARCH_BROWSER'), 'Set MCD_SEARCH_BROWSER to Chrome/Edge')
    def test_charts_render_with_real_dashboard_data(self):
        with tempfile.TemporaryDirectory(prefix='mcd-visuals-') as directory:
            folder = Path(directory)
            source = (ROOT / 'index.html').read_text(encoding='utf-8')
            source = source.replace('<head>', '<head><base href="' + ROOT.as_uri() + '/">', 1)
            source = re.sub(r'<script[^>]+src="https?://[^>]+></script>', '', source)
            source = source.replace('</body>', '<script src="tests/visual_analytics_browser.js"></script></body>')
            page = folder / 'test.html'
            page.write_text(source, encoding='utf-8')
            result = subprocess.run([
                os.environ['MCD_SEARCH_BROWSER'], '--headless', '--disable-gpu', '--no-first-run',
                '--no-default-browser-check', '--allow-file-access-from-files',
                '--host-resolver-rules=MAP * ~NOTFOUND', '--virtual-time-budget=7000',
                '--window-size=1920,1080', '--user-data-dir=' + str(folder / 'profile'),
                '--dump-dom', page.as_uri()
            ], capture_output=True, timeout=50,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            document = result.stdout.decode('utf-8', errors='replace')
            report = re.search(r'<pre id="visual-analytics-report"[^>]*>(.*?)</pre>', document, re.S)
            self.assertIsNotNone(report, result.stderr.decode('utf-8', errors='replace')[-1200:])
            checks = json.loads(html.unescape(report.group(1)))
            self.assertFalse(any(check.startswith('FAILED:') for check in checks), checks)


if __name__ == '__main__':
    unittest.main()
