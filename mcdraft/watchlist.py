"""Persisted player watchlist, attached outside the preserved legacy stages."""

PAGE = '''<div class="player-subpage" id="player-sub-watchlist">
  <div class="card"><h2>Player watchlist</h2>
    <p class="card-description">Players you are keeping an eye on. Saved in this browser across refreshes; stats reflect the latest loaded dashboard.</p>
    <p id="watchlist-status" role="status"></p>
    <label for="watchlist-search">Find a watched player</label>
    <input id="watchlist-search" type="search" placeholder="Name, club, position or owner">
    <div id="watchlist-rows"></div>
  </div>
</div>
'''
ASSETS = '''<link rel="stylesheet" href="assets/watchlist.css">
<script defer src="assets/watchlist.js"></script>
'''


def integrate_template(template):
    anchor = '<div class="player-subpage" id="player-sub-directory">'
    tab = '<button type="button" class="analytics-subtab player-page-tab" onclick="showPlayerSubtab(\'directory\',this)">Player Directory</button>'
    if 'id="player-sub-watchlist"' in template or any(template.count(x) != 1 for x in (anchor, tab, '</body>')):
        raise RuntimeError('Watchlist insertion point changed or already integrated')
    return (template.replace(anchor, PAGE + anchor, 1)
            .replace(tab, tab + '\n<button type="button" class="analytics-subtab player-page-tab" onclick="showPlayerSubtab(\'watchlist\',this)">Watchlist</button>', 1)
            .replace('</body>', ASSETS + '</body>', 1))
