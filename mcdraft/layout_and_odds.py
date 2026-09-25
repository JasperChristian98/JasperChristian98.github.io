"""Presentation-only dashboard layout refactor and shared next-GW odds cache.

No changes to the losslessly extracted legacy stages. All changes fail loudly if
an upstream HTML anchor changes, instead of silently rendering duplicate cards.
"""
from __future__ import annotations
from copy import deepcopy
import re

CSS = r'''
/* Sticky section navigation: do not trap it inside a clipped scrolling box. */
.mcd-workspace > .main { overflow-x:clip; }
#page-myteam>.myteam-tabs,
#page-overview>.overview-tabs,
#overview-sub-intelligence>.overview-insight-tabs {
 position:sticky;
 top:var(--mcd-sticky-top,0px);
 z-index:81;
 display:flex;
 flex-wrap:nowrap;
 align-items:center;
 max-width:100%;
 min-width:0;
 gap:8px;
 overflow-x:auto;
 overflow-y:hidden;
 overscroll-behavior-x:contain;
 -webkit-overflow-scrolling:touch;
 scrollbar-width:thin;
 background:var(--bg);
 padding:10px 2px 11px;
 margin:0 0 16px;
 border-bottom:1px solid var(--border);
 box-sizing:border-box;
}
#page-myteam>.myteam-tabs>.myteam-tab,
#page-overview>.overview-tabs>.overview-tab,
#overview-sub-intelligence>.overview-insight-tabs>.overview-insight-tab {
 flex:0 0 auto;
 white-space:nowrap;
 min-height:42px;
}
#overview-sub-intelligence>.overview-insight-tabs {
 top:calc(var(--mcd-sticky-top,0px) + var(--mcd-overview-tabs-height,0px));
 z-index:80;
}
.overview-insight-panel{display:none}
.overview-insight-panel.active{display:block}
/* The Overview tab bar is the structural parent of all content below it. */
#page-overview>.overview-tabs { margin-top:0; }
#overview-sub-standings>.decision-centre { margin:0 0 18px; }
@media(max-width:850px){
 /* Mobile header is in normal flow, so it must not leave an empty sticky gap. */
 :root{--mcd-sticky-top:0px}
 .mcd-workspace>.main {overflow-x:clip!important}
 #page-myteam>.myteam-tabs,
 #page-overview>.overview-tabs,
 #overview-sub-intelligence>.overview-insight-tabs {
   padding:8px 1px 10px;
   gap:7px;
   scroll-padding-inline:8px;
 }
 #page-myteam>.myteam-tabs>.myteam-tab,
 #page-overview>.overview-tabs>.overview-tab,
 #overview-sub-intelligence>.overview-insight-tabs>.overview-insight-tab {
   padding:10px 12px;
   font-size:12px;
 }
}
@media(max-width:410px){
 #page-overview>.overview-tabs>.overview-tab { font-size:11px;padding-inline:10px; }
}
'''

JS = r'''
/* Header is not sticky on mobile, so use zero offset there; on desktop only
   reserve space for a header that is genuinely fixed or sticky and visible. */
function mcdMeasureStickyTabs(){
 const header=document.querySelector('.header');
 const mobile=window.matchMedia('(max-width:850px)').matches;
 let top=0;
 if(header&&!mobile){
   const style=window.getComputedStyle(header);
   const rect=header.getBoundingClientRect();
   if((style.position==='fixed'||style.position==='sticky')&&rect.bottom>0&&rect.top<=1){
     top=Math.ceil(rect.height);
   }
 }
 document.documentElement.style.setProperty('--mcd-sticky-top',top+'px');
 const tabs=document.querySelector('#page-overview>.overview-tabs');
 const overviewActive=!!document.querySelector('#page-overview.active');
 const tabHeight=(tabs&&overviewActive)?Math.ceil(tabs.getBoundingClientRect().height):0;
 document.documentElement.style.setProperty('--mcd-overview-tabs-height',tabHeight+'px');
}
window.addEventListener('resize',mcdMeasureStickyTabs,{passive:true});
window.addEventListener('orientationchange',mcdMeasureStickyTabs,{passive:true});
document.addEventListener('DOMContentLoaded',()=>{
 mcdMeasureStickyTabs();
 const header=document.querySelector('.header');
 const overview=document.querySelector('#page-overview>.overview-tabs');
 if(typeof ResizeObserver!=='undefined'){
   const observer=new ResizeObserver(mcdMeasureStickyTabs);
   if(header)observer.observe(header);
   if(overview)observer.observe(overview);
 }
});
function showOverviewInsightSubtab(name,button){
 const top=document.querySelector('.overview-tab[onclick*="intelligence"]');
 showPage('overview');
 showOverviewSubtab('intelligence',top||null);
 document.querySelectorAll('.overview-insight-panel').forEach(el=>el.classList.toggle('active',el.id==='overview-insight-'+name));
 document.querySelectorAll('.overview-insight-tab').forEach(el=>{
   const selected=el===button||(!button&&(el.getAttribute('data-insight')===name));
   el.classList.toggle('active',selected);el.setAttribute('aria-selected',String(selected));
 });
 if(name==='trends')requestAnimationFrame(()=>{
   if(typeof trendState!=='undefined'&&typeof renderTrendChart==='function')
     ['h2h','rank','cumulative','scores'].forEach(key=>{if(trendState[key])renderTrendChart(key)});
 });
 mcdMeasureStickyTabs();
 if(typeof mcdNavSync==='function')requestAnimationFrame(()=>mcdNavSync('overview'));
}
'''



def _extract_once(text: str, begin: str, end: str) -> tuple[str, int, int]:
    a = text.find(begin)
    if a < 0 or text.count(begin) != 1:
        raise RuntimeError(f'Expected one layout start anchor {begin!r}')
    b = text.find(end, a + len(begin))
    if b < 0:
        raise RuntimeError(f'Expected layout end anchor {end!r}')
    return text[a:b], a, b


def update_layout(template: str) -> str:
    """Turn existing radar cards into My Team tabs and split Overview insights."""
    # Move My Team selector AFTER the sticky subtab bar, leaving summary visible
    # on the squad subtab only. Retain all existing element IDs and renderers.
    radar_begin = '            <div class="card"><h2>Squad Performance Radar</h2>'
    radar_end = '            <div class="analytics-subtabs myteam-tabs"'
    radars, a, b = _extract_once(template, radar_begin, radar_end)
    performance, sep, vuln = radars.partition('            <div class="card" id="myteam-vulnerability-card">')
    if not sep or performance.count('id="myteam-radar"') != 1 or vuln.count('id="myteam-vulnerability"') != 1:
        raise RuntimeError('Both original My Team radars must exist')
    vulnerability = sep + vuln
    template = template[:a] + template[b:]

    tabs_start = '            <div class="analytics-subtabs myteam-tabs"'
    tabs_end = '            <div class="myteam-subpage active" id="myteam-sub-squad">'
    bar, a, b = _extract_once(template, tabs_start, tabs_end)
    original_last = '<button type="button" class="analytics-subtab myteam-tab" onclick="showMyTeamSubtab(\'stats\',this)">Stats</button>'
    if bar.count(original_last) != 1:
        raise RuntimeError('My Team Stats tab anchor changed')
    additional = ('\n                <button type="button" class="analytics-subtab myteam-tab" '
                  'onclick="showMyTeamSubtab(\'performance\',this)">Performance Radar</button>'
                  '\n                <button type="button" class="analytics-subtab myteam-tab" '
                  'onclick="showMyTeamSubtab(\'vulnerability\',this)">Vulnerability Radar</button>')
    bar = bar.replace(original_last, original_last + additional, 1)
    template = template[:a] + bar + template[b:]
    squad = '<div class="myteam-subpage active" id="myteam-sub-squad">'
    if template.count(squad) != 1:
        raise RuntimeError('My Team squad page anchor changed')
    new_panels = ('<div class="myteam-subpage" id="myteam-sub-performance">' + performance + '</div>\n'
                  '            <div class="myteam-subpage" id="myteam-sub-vulnerability">' + vulnerability + '</div>\n            ')
    template = template.replace(squad, new_panels + squad, 1)

    # Put My Team tabs directly beneath the page heading, not below a long
    # summary card. The summary is part of the Squad subpage.
    myteam_start = '<section class="page" id="page-myteam">'
    myteam_end = '        <!-- ==================================================\n             GAMEWEEKS'
    section, a, b = _extract_once(template, myteam_start, myteam_end)
    top_bar, bar_a, bar_b = _extract_once(section, tabs_start, '            <div class="myteam-subpage" id="myteam-sub-performance">')
    # Extract original summary card between heading and tabs.
    head_and_card = section[:bar_a]
    match = re.search(r'(<div class="page-heading">.*?</div>)(\s*)(<div class="card">.*?</div>\s*</div>)\s*$', head_and_card, re.S)
    if not match:
        raise RuntimeError('My Team summary/header structure changed')
    heading = match.group(1)
    summary = match.group(3)
    # Make summary first content within Squad, but do not duplicate it.
    rest = section[bar_b:]
    squad_open = '<div class="myteam-subpage active" id="myteam-sub-squad">'
    if rest.count(squad_open) != 1:
        raise RuntimeError('Expected one My Team Squad subpage')
    rest = rest.replace(squad_open, squad_open + '\n' + summary, 1)
    section = section[:match.start(1)] + heading + '\n' + top_bar + rest
    template = template[:a] + section + template[b:]

    # Split existing Overview analytics into Rankings, Predictions and Trends
    # without regenerating any of the original chart/table markup.
    insights_start = '            <div class="overview-subpage" id="overview-sub-intelligence">'
    insights_end = '        __LIVE_CENTRE_PAGE__'
    section, a, b = _extract_once(template, insights_start, insights_end)
    # Preserve closing Overview section and original trend chart HTML.
    prefix = insights_start + '\n'
    if not section.startswith(prefix):
        raise RuntimeError('Overview insight opening changed')
    ranking_start = '<div class="dashboard-grid"><div class="card"><h2>Power Rankings</h2>'
    prediction_start = '<div class="card"><h2>Rest-of-Season Prediction</h2>'
    pedigree_start = '<div class="card"><h2>Squad Pedigree</h2>'
    trend_start = '<div class="dashboard-grid">'
    rank, ra, rb = _extract_once(section, ranking_start, prediction_start)
    prediction_to_trend, pa, pb = _extract_once(section, prediction_start, trend_start)
    if section.count(trend_start) != 2:  # rankings itself starts with grid
        raise RuntimeError('Unexpected Overview trends grid anchors')
    pedigree_at = prediction_to_trend.find(pedigree_start)
    if pedigree_at < 0 or prediction_to_trend.count(pedigree_start) != 1:
        raise RuntimeError('Overview pedigree card moved')
    predictions = prediction_to_trend[:pedigree_at]
    rankings = rank + '\n' + prediction_to_trend[pedigree_at:]
    # Trend grid is followed by its closing div, intelligence closing div and section.
    trend_region = section[pb:]
    tail = '            </div>\n        </section>'
    if tail not in trend_region:
        raise RuntimeError('Overview section closing anchor moved')
    tail_pos = trend_region.rfind(tail)
    # One extra grid-closing div precedes this tail; preserve it in trends.
    trends = trend_region[:tail_pos]
    rebuilt = '''            <div class="overview-subpage" id="overview-sub-intelligence">
                <div class="analytics-subtabs overview-insight-tabs" role="tablist" aria-label="Predictions and rankings">
                    <button type="button" class="analytics-subtab overview-insight-tab active" data-insight="rankings" onclick="showOverviewInsightSubtab('rankings',this)" aria-selected="true">Power Rankings</button>
                    <button type="button" class="analytics-subtab overview-insight-tab" data-insight="predictions" onclick="showOverviewInsightSubtab('predictions',this)" aria-selected="false">Predictions</button>
                    <button type="button" class="analytics-subtab overview-insight-tab" data-insight="trends" onclick="showOverviewInsightSubtab('trends',this)" aria-selected="false">League Trends</button>
                </div>
                <div class="overview-insight-panel active" id="overview-insight-rankings">\n''' + rankings + '''\n                </div>
                <div class="overview-insight-panel" id="overview-insight-predictions">\n''' + predictions + '''\n                </div>
                <div class="overview-insight-panel" id="overview-insight-trends">\n''' + trends + '''\n                </div>
''' + trend_region[tail_pos:]
    template = template[:a] + rebuilt + template[b:]

    # Sidebar entries use the existing global navigation dispatcher and its
    # explicit subtab kind, rather than relying on scroll-only anchors.
    old = "['Predictions & power rankings','overview','overview','intelligence'],"
    if template.count(old) != 1:
        raise RuntimeError('Overview sidebar link changed')
    template = template.replace(old,
        "['Power rankings','overview','overview-insight','rankings'],\n"
        "  ['Season predictions','overview','overview-insight','predictions'],\n"
        "  ['League trends','overview','overview-insight','trends'],", 1)
    old_vuln = "['Vulnerability radar','myteam','myteam','squad','myteam-vulnerability-card'],"
    if template.count(old_vuln) != 1:
        raise RuntimeError('My Team sidebar vulnerability item changed')
    template = template.replace(old_vuln,
        "['Performance radar','myteam','myteam','performance'],\n"
        "  ['Vulnerability radar','myteam','myteam','vulnerability'],", 1)
    selector = "analytics:'#page-analytics .analytics-subtab'"
    handler = "analytics:showAnalyticsSubtab"
    if template.count(selector) != 1 or template.count(handler) != 1:
        raise RuntimeError('Sidebar navigation dispatch changed')
    template = template.replace(selector, selector + ",'overview-insight':'.overview-insight-tab'", 1)
    template = template.replace(handler, handler + ",'overview-insight':showOverviewInsightSubtab", 1)
    lookup = "analytics:'analytics-sub-'"
    if template.count(lookup) != 1:
        raise RuntimeError('Active sidebar subtab lookup changed')
    template = template.replace(lookup, lookup + ",'overview-insight':'overview-insight-'", 1)
    click_selector = '.overview-tab,.myteam-tab'
    if template.count(click_selector) != 1:
        raise RuntimeError('Sidebar active-state click selector changed')
    template = template.replace(click_selector, '.overview-tab,.overview-insight-tab,.myteam-tab', 1)
    return template


def shared_fixture_odds(original):
    """Identical probabilities regardless of page or reversed manager order."""
    cache = {}
    swapped = [('team1_win','team2_win'),('team1_mean','team2_mean'),
               ('team1_low','team2_low'),('team1_high','team2_high')]
    def get(team1, team2, simulations=10000, seed=17288):
        pair = tuple(sorted((team1,team2)))
        key=(pair,simulations,seed)
        if key not in cache:
            cache[key]=original(pair[0],pair[1],simulations=simulations,seed=seed)
        result=deepcopy(cache[key])
        if result is not None and (team1,team2) != pair:
            for left,right in swapped:
                result[left],result[right]=result[right],result[left]
        return result
    get.cache=cache
    return get
