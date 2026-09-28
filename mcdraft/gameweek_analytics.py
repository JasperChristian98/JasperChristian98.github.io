"""Weekly manager-performance analytics added after the legacy page render."""


TAB = '''<button class="analytics-subtab" type="button" onclick="showAnalyticsSubtab('gameweek-lab', this)">Gameweek Lab <span>6</span></button>'''

PAGE = '''<div class="analytics-subpage" id="analytics-sub-gameweek-lab">
  <div class="card gw-lab-intro"><div><span>Weekly performance</span><h2>Gameweek Lab</h2>
    <p class="card-description">Actual weekly manager scores, separated into level, consistency, rank and momentum. Every view follows the shared Manager filter; league-average benchmarks and weekly ranks remain fixed for fair comparisons.</p></div><strong id="gw-lab-status" aria-live="polite"></strong></div>
  <div id="gw-lab-summary" class="analytics-insight-grid gw-lab-summary"></div>
  <div class="analytics-chart-grid gw-lab-grid">
    <section class="card analytics-chart-card gw-lab-card gw-lab-wide"><h2>Weekly score heatmap</h2><p class="card-description">The actual fantasy score recorded by each manager in every completed gameweek.</p><div id="gw-lab-score-heatmap" class="gw-lab-scroll"></div></section>
    <section class="card analytics-chart-card gw-lab-card gw-lab-wide"><h2>Weekly rank heatmap</h2><p class="card-description">Rank among all McDraft managers for that gameweek. Filtering hides rows without recalculating rank.</p><div id="gw-lab-rank-heatmap" class="gw-lab-scroll"></div></section>
    <section class="card analytics-chart-card gw-lab-card gw-lab-wide"><h2>Score distributions</h2><p class="card-description">Minimum, middle 50%, median and maximum, with every actual gameweek plotted as a dot.</p><div id="gw-lab-distribution" class="gw-lab-scroll"></div></section>
    <section class="card analytics-chart-card gw-lab-card"><h2>Scoring level vs consistency</h2><p class="card-description">Higher average scores move right; lower week-to-week volatility moves down.</p><div id="gw-lab-consistency"></div></section>
    <section class="card analytics-chart-card gw-lab-card"><h2>Boom and bust weeks</h2><p class="card-description">A boom is 10+ points above that week’s league average; a bust is 10+ below it.</p><div id="gw-lab-boom-bust"></div></section>
    <section class="card analytics-chart-card gw-lab-card gw-lab-wide"><h2>Weekly output table</h2><p class="card-description">Level, range, volatility and short-term momentum in one compact summary.</p><div id="gw-lab-table"></div></section>
  </div>
</div>'''

ASSETS = '''<link rel="stylesheet" href="assets/gameweek-analytics.css">
<script defer src="assets/gameweek-analytics.js"></script>
'''


def integrate_template(template: str) -> str:
    tab_anchor = '<button class="analytics-subtab active" type="button" onclick="showAnalyticsSubtab(\'insights\', this)">'
    page_anchor = '<div class="analytics-subpage active" id="analytics-sub-insights">'
    nav_anchor = "['McDraft Insights','analytics','analytics','insights'],"
    if ('id="analytics-sub-gameweek-lab"' in template or 'assets/gameweek-analytics.js' in template
            or any(template.count(anchor) != 1 for anchor in (tab_anchor, page_anchor, nav_anchor, '</body>'))):
        raise RuntimeError('Gameweek Lab insertion point changed or already integrated')
    return (template.replace(tab_anchor, TAB + '\n        ' + tab_anchor, 1)
            .replace(page_anchor, PAGE + '\n    ' + page_anchor, 1)
            .replace(nav_anchor, "['Gameweek Lab','analytics','analytics','gameweek-lab'],\n  " + nav_anchor, 1)
            .replace('</body>', ASSETS + '</body>', 1))
