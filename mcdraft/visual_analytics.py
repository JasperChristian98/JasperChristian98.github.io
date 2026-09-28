"""Additional browser-rendered visual analytics, kept outside legacy stages."""


TAB = '''<button class="analytics-subtab" type="button" onclick="showAnalyticsSubtab('visuals', this)">Visual Analytics <span>11</span></button>'''

PAGE = '''<div class="analytics-subpage" id="analytics-sub-visuals">
  <div class="card visual-analytics-intro">
    <div><span class="visual-kicker">Chart gallery</span><h2>Visual Analytics</h2>
      <p class="card-description">Eleven alternative views of scoring, ownership, player quality and squad shape. Every chart follows the shared Manager filter and the position filter below.</p></div>
    <span id="visual-analytics-status" class="muted" aria-live="polite"></span>
    <div class="visual-position-filter" role="group" aria-label="Filter Visual Analytics by position">
      <span>Positions</span><button type="button" data-visual-position="ALL">All</button><button type="button" data-visual-position="GKP">GK</button><button type="button" data-visual-position="DEF">DEF</button><button type="button" data-visual-position="MID">MID</button><button type="button" data-visual-position="FWD">FWD</button>
    </div>
  </div>
  <div class="analytics-chart-grid visual-analytics-grid">
    <section class="card analytics-chart-card visual-chart-card"><h2>Scoring mix by position</h2><p class="card-description">Stacked gameweek points from every active player, split by fantasy position.</p><div id="visual-area-position" class="visual-chart-host"></div></section>
    <section class="card analytics-chart-card visual-chart-card"><h2>Owned vs free-agent output</h2><p class="card-description">Where gameweek points lived at the time they were scored.</p><div id="visual-area-ownership" class="visual-chart-host"></div></section>
    <section class="card analytics-chart-card visual-chart-card visual-wide"><h2>Scoring mix by manager per gameweek</h2><p class="card-description">Actual player points stacked by their fantasy manager in each completed gameweek.</p><div id="visual-area-managers" class="visual-chart-host"></div></section>
    <section class="card analytics-chart-card visual-chart-card"><h2>Premier League club output</h2><p class="card-description">Weighted convex cells sized by current season fantasy points.</p><div id="visual-treemap-clubs" class="visual-chart-host visual-treemap"></div></section>
    <section class="card analytics-chart-card visual-chart-card"><h2>Fantasy squad value</h2><p class="card-description">Selected squads sized by the combined model value of their current players.</p><div id="visual-treemap-owners" class="visual-chart-host visual-treemap"></div></section>
    <section class="card analytics-chart-card visual-chart-card"><h2>Player rating distribution</h2><p class="card-description">A positional beeswarm of active players with recorded minutes.</p><div id="visual-beeswarm-rating" class="visual-chart-host"></div></section>
    <section class="card analytics-chart-card visual-chart-card"><h2>Player value by ownership</h2><p class="card-description">Owned and available players spread across the McDraft value model.</p><div id="visual-beeswarm-value" class="visual-chart-host"></div></section>
    <section class="card analytics-chart-card visual-chart-card visual-wide"><h2>Club output heatmap</h2><p class="card-description">Fantasy points by Premier League club and completed gameweek.</p><div id="visual-heatmap-clubs" class="visual-chart-host visual-heatmap-scroll"></div></section>
    <section class="card analytics-chart-card visual-chart-card visual-wide"><h2>Actual player output by gameweek</h2><p class="card-description">The top 30 filtered players by season output, with the points they actually returned in every completed gameweek.</p><div id="visual-heatmap-players" class="visual-chart-host visual-heatmap-scroll"></div></section>
    <section class="card analytics-chart-card visual-chart-card"><h2>Squad rating heatmap</h2><p class="card-description">Average current player rating by selected manager and position.</p><div id="visual-heatmap-squads" class="visual-chart-host visual-heatmap-scroll"></div></section>
    <section class="card analytics-chart-card visual-chart-card visual-wide"><h2>Player model table chart</h2><p class="card-description">The leading current ratings with embedded value bars and recent-gameweek sparklines.</p><div id="visual-table-players" class="visual-chart-host"></div></section>
  </div>
</div>'''

ASSETS = '''<link rel="stylesheet" href="assets/analytics-position-filter.css">
<script defer src="assets/analytics-position-filter.js"></script>
<link rel="stylesheet" href="assets/visual-analytics.css">
<script defer src="assets/visual-analytics.js"></script>
'''


def integrate_template(template: str) -> str:
    tab_anchor = '<button class="analytics-subtab active" type="button" onclick="showAnalyticsSubtab(\'insights\', this)">'
    page_anchor = '<div class="analytics-subpage active" id="analytics-sub-insights">'
    nav_anchor = "['McDraft Insights','analytics','analytics','insights'],"
    if ('id="analytics-sub-visuals"' in template or 'assets/visual-analytics.js' in template
            or any(template.count(anchor) != 1 for anchor in (tab_anchor, page_anchor, nav_anchor, '</body>'))):
        raise RuntimeError('Visual Analytics insertion point changed or already integrated')
    return (template.replace(tab_anchor, TAB + '\n        ' + tab_anchor, 1)
            .replace(page_anchor, PAGE + '\n    ' + page_anchor, 1)
            .replace(nav_anchor, "['Visual Analytics','analytics','analytics','visuals'],\n  " + nav_anchor, 1)
            .replace('</body>', ASSETS + '</body>', 1))


def refresh_existing_template(template: str) -> str:
    """Refresh the generated page without requiring a complete data rebuild."""
    page_start = '<div class="analytics-subpage" id="analytics-sub-visuals">'
    page_end = '<div class="analytics-subpage active" id="analytics-sub-insights">'
    tab_marker = "showAnalyticsSubtab('visuals', this)"
    nav_anchor = "['McDraft Insights','analytics','analytics','insights'],"
    if any(template.count(marker) != 1 for marker in (page_start, page_end, tab_marker, nav_anchor)):
        raise RuntimeError('Existing Visual Analytics markup cannot be refreshed safely')
    start = template.index(page_start)
    end = template.index(page_end, start)
    marker = template.index(tab_marker)
    tab_start = template.rfind('<button', 0, marker)
    tab_end = template.index('</button>', marker) + len('</button>')
    template = template[:tab_start] + TAB + template[tab_end:]
    start = template.index(page_start)
    end = template.index(page_end, start)
    template = template[:start] + PAGE + '\n    ' + template[end:]
    nav_entry = "['Visual Analytics','analytics','analytics','visuals'],"
    if nav_entry not in template:
        template = template.replace(nav_anchor, nav_entry + '\n  ' + nav_anchor, 1)
    return template
