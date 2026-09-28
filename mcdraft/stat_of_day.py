"""Add a daily fact to the bottom of the welcome/team selector."""
import re

CARD_HTML = '''
    <div class="mcd-daily-cards">
    <aside id="mcd-stat-of-day" class="mcd-stat-of-day" aria-labelledby="mcd-stat-title" hidden>
      <div class="mcd-stat-heading"><h2 id="mcd-stat-title">Stat of the day</h2><span id="mcd-stat-category"></span></div>
      <p id="mcd-stat-fact"></p>
      <p id="mcd-stat-context"></p>
      <small id="mcd-stat-date"></small>
    </aside>
    <aside id="mcd-player-of-day" class="mcd-stat-of-day" aria-labelledby="mcd-player-title" hidden>
      <div class="mcd-stat-heading"><h2 id="mcd-player-title">Player of the day</h2></div>
      <h3 id="mcd-player-name"></h3>
      <dl class="mcd-player-daily-details">
        <div><dt>Position</dt><dd id="mcd-player-position"></dd></div>
        <div><dt>Club</dt><dd id="mcd-player-club" data-club-name></dd></div>
        <div><dt>Fantasy team</dt><dd id="mcd-player-owner"></dd></div>
      </dl>
      <p id="mcd-player-headline"></p>
      <p id="mcd-player-context"></p>
      <small id="mcd-player-date"></small>
    </aside>
    </div>'''

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
