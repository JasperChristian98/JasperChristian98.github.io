"""Home calendar integration; preserved stages remain unchanged."""
import json

PAGE = '''<section class="page" id="page-calendar">
<div class="page-heading"><h1>Fixture calendar</h1><p>Premier League and fantasy football, August to May.</p></div>
<div class="card fixture-calendar">
<div class="calendar-controls"><button id="calendar-prev" aria-label="Previous month">&#8592;</button><h2 id="calendar-month" aria-live="polite"></h2><button id="calendar-next" aria-label="Next month">&#8594;</button><button id="calendar-today">Current month</button></div>
<div class="calendar-filters"><label>Season<select id="calendar-season"></select></label><label>Competition<select id="calendar-kind"><option value="all">All football</option><option value="pl">Premier League</option><option value="fantasy">Fantasy league</option></select></label><label>Team<select id="calendar-team"><option value="">All teams</option></select></label><label>Show<select id="calendar-status"><option value="all">Fixtures &amp; results</option><option value="upcoming">Upcoming</option><option value="finished">Results</option></select></label></div>
<p class="card-description">Times are UK time. Fantasy matchups appear on their gameweek's opening day and cover the whole gameweek.</p>
<div id="calendar-grid" class="calendar-grid" aria-label="Month calendar"></div>
<p id="calendar-empty" role="status" hidden>No matches match these filters this month.</p>
<div id="calendar-agenda" aria-live="polite"></div>
<details id="calendar-undated" hidden><summary>Dates to be confirmed</summary><div></div></details>
</div></section>'''


def integrate_template(template, schedule=None):
    anchor = '<section class="page active" id="page-overview">'
    nav = "['League overview','overview','overview','standings'],"
    if 'id="page-calendar"' in template or any(template.count(a) != 1 for a in (anchor, nav, '</body>')):
        raise RuntimeError('Calendar insertion point changed or already integrated')
    payload = json.dumps(schedule or {}, ensure_ascii=True).replace('<', '\\u003c')
    assets = ('<script id="calendar-schedule" type="application/json">' + payload + '</script>\n'
              '<link rel="stylesheet" href="assets/fixture-calendar.css">\n'
              '<script defer src="assets/fixture-calendar.js"></script>\n')
    return template.replace(anchor, PAGE + '\n' + anchor, 1).replace(nav, nav + "\n  ['Fixture calendar','calendar'],", 1).replace('</body>', assets + '</body>', 1)
