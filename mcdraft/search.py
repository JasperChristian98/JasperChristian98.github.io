"""Attach universal search without modifying the preserved build stages."""

PAGE_HTML = '''
<section class="page" id="page-search" aria-labelledby="search-title">
  <div class="page-heading"><h1 id="search-title" tabindex="-1">Search McDraft</h1><p>Find every page, section, player, fantasy team and club.</p></div>
  <form id="search-form" role="search"><label for="search-query">Search everything</label><div class="search-query-row"><input id="search-query" type="search" placeholder="Player, team, club or feature…" autocomplete="off"><button type="submit">Search</button></div></form>
  <div id="search-shortcuts"></div>
  <div id="search-filters" class="search-filters" aria-label="Filter search results"></div>
  <p id="search-count" role="status" aria-live="polite"></p>
  <div id="search-list"></div>
  <button id="search-more" type="button" hidden>Load more results</button>
</section>
'''

ASSETS = '''
<link rel="stylesheet" href="assets/search.css">
<script defer src="assets/search.js"></script>
'''


def integrate_template(template):
    anchor = '<section class="page" id="page-transfers">'
    if 'id="page-search"' in template:
        raise RuntimeError('Search is already integrated')
    for token in (anchor, '</body>'):
        if template.count(token) != 1:
            raise RuntimeError('Search insertion point changed: ' + token)
    return template.replace(anchor, PAGE_HTML.lstrip() + '\n' + anchor, 1).replace(
        '</body>', ASSETS + '\n</body>', 1)
