"""Add a daily fact to the bottom of the welcome/team selector."""
import re

CARD_HTML = '''
    <aside id="mcd-stat-of-day" class="mcd-stat-of-day" aria-labelledby="mcd-stat-title" hidden>
      <div class="mcd-stat-heading"><h2 id="mcd-stat-title">Stat of the day</h2><span id="mcd-stat-category"></span></div>
      <p id="mcd-stat-fact"></p>
      <p id="mcd-stat-context"></p>
      <small id="mcd-stat-date"></small>
    </aside>'''

ASSETS = '''
<link rel="stylesheet" href="assets/stat-of-day.css">
<script defer src="assets/stat-of-day.js"></script>
'''


def integrate_template(template):
    if 'id="mcd-stat-of-day"' in template:
        raise RuntimeError('Stat of the day is already integrated')
    anchor = re.compile(r'<div class="mcd-welcome-foot">[^<]*</div>')
    if len(anchor.findall(template)) != 1 or template.count('</body>') != 1:
        raise RuntimeError('Stat of the day welcome insertion point changed')
    return anchor.sub(lambda match: match[0] + CARD_HTML, template, count=1).replace(
        '</body>', ASSETS + '\n</body>', 1)
