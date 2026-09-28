"""Additional browser-rendered visual analytics, kept outside legacy stages."""


TAB = '''<button class="analytics-subtab" type="button" onclick="showAnalyticsSubtab('visuals', this)">Visual Analytics <span>9</span></button>'''

PAGE = '''<div class="analytics-subpage" id="analytics-sub-visuals">
  <div class="card visual-analytics-intro">
    <div><span class="visual-kicker">Chart gallery</span><h2>Visual Analytics</h2>
      <p class="card-description">Nine alternative views of scoring, ownership, player quality and squad shape. League-wide charts use the whole player pool; owner-labelled charts follow the shared Manager filter above.</p></div>
    <span id="visual-analytics-status" class="muted" aria-live="polite"></span>
  </div>
  <div class="analytics-chart-grid visual-analytics-grid">
    <section class="card analytics-chart-card visual-chart-card"><h2>Scoring mix by position</h2><p class="card-description">Stacked gameweek points from every active player, split by fantasy position.</p><div id="visual-area-position" class="visual-chart-host"></div></section>
    <section class="card analytics-chart-card visual-chart-card"><h2>Owned vs free-agent output</h2><p class="card-description">Where gameweek points lived at the time they were scored.</p><div id="visual-area-ownership" class="visual-chart-host"></div></section>
    <section class="card analytics-chart-card visual-chart-card"><h2>Premier League club output</h2><p class="card-description">Weighted convex cells sized by current season fantasy points.</p><div id="visual-treemap-clubs" class="visual-chart-host visual-treemap"></div></section>
    <section class="card analytics-chart-card visual-chart-card"><h2>Fantasy squad value</h2><p class="card-description">Selected squads sized by the combined model value of their current players.</p><div id="visual-treemap-owners" class="visual-chart-host visual-treemap"></div></section>
    <section class="card analytics-chart-card visual-chart-card"><h2>Player rating distribution</h2><p class="card-description">A positional beeswarm of active players with recorded minutes.</p><div id="visual-beeswarm-rating" class="visual-chart-host"></div></section>
    <section class="card analytics-chart-card visual-chart-card"><h2>Player value by ownership</h2><p class="card-description">Owned and available players spread across the McDraft value model.</p><div id="visual-beeswarm-value" class="visual-chart-host"></div></section>
    <section class="card analytics-chart-card visual-chart-card visual-wide"><h2>Club output heatmap</h2><p class="card-description">Fantasy points by Premier League club and completed gameweek.</p><div id="visual-heatmap-clubs" class="visual-chart-host visual-heatmap-scroll"></div></section>
    <section class="card analytics-chart-card visual-chart-card"><h2>Squad rating heatmap</h2><p class="card-description">Average current player rating by selected manager and position.</p><div id="visual-heatmap-squads" class="visual-chart-host visual-heatmap-scroll"></div></section>
    <section class="card analytics-chart-card visual-chart-card visual-wide"><h2>Player model table chart</h2><p class="card-description">The leading current ratings with embedded value bars and recent-gameweek sparklines.</p><div id="visual-table-players" class="visual-chart-host"></div></section>
  </div>
</div>'''

ASSETS = '''<link rel="stylesheet" href="assets/visual-analytics.css">
<script defer src="assets/visual-analytics.js"></script>
'''


def integrate_template(template: str) -> str:
    tab_anchor = '<button class="analytics-subtab active" type="button" onclick="showAnalyticsSubtab(\'insights\', this)">'
    page_anchor = '<div class="analytics-subpage active" id="analytics-sub-insights">'
    if ('id="analytics-sub-visuals"' in template or 'assets/visual-analytics.js' in template
            or any(template.count(anchor) != 1 for anchor in (tab_anchor, page_anchor, '</body>'))):
        raise RuntimeError('Visual Analytics insertion point changed or already integrated')
    return (template.replace(tab_anchor, TAB + '\n        ' + tab_anchor, 1)
            .replace(page_anchor, PAGE + '\n    ' + page_anchor, 1)
            .replace('</body>', ASSETS + '</body>', 1))
