"""Mobile search/team header and fixture-backed kickoff countdown in the header.

The existing module filename is preserved so users only replace two Python files.
No countdown is inserted while the gameweek is live.
"""
from __future__ import annotations

from datetime import datetime, timezone
import json
from typing import Iterable, Mapping

CSS = r'''
/* The legacy mobile header uses flex-direction:column. Override that with an
   explicit grid; the two controls therefore cannot wrap onto separate rows. */
@media (max-width:850px) {
 .header .header-top {
   display:grid!important;
   grid-template-columns:minmax(0,1fr) minmax(0,1fr);
   grid-template-areas:"logo logo" "theme theme" "meta meta" "search manager";
   column-gap:8px;
   row-gap:9px;
   align-items:center!important;
   justify-items:stretch;
   flex-direction:row!important;
   flex-wrap:nowrap!important;
   width:100%;
   min-width:0;
   box-sizing:border-box;
 }
 .header .logo {grid-area:logo;min-width:0;}
 .header .theme-control {grid-area:theme;justify-self:center;min-width:0;margin:0;}
 .header .header-meta {grid-area:meta;min-width:0;margin:0;width:100%;text-align:left;}
 .header .global-search-wrap {
   grid-area:search;position:relative;width:100%;max-width:none;min-width:0;
   margin:0!important;flex:none!important;order:unset!important;
 }
 .header .mcd-header-manager {
   grid-area:manager;display:block;width:100%;max-width:none;min-width:0;
   margin:0!important;flex:none!important;order:unset!important;
 }
 .header .mcd-header-manager span {display:none;}
 .header .global-search-input,
 .header .mcd-header-manager select {
   display:block;width:100%;max-width:100%;min-width:0;height:39px;min-height:39px;
   box-sizing:border-box;border-radius:9px;font-size:12px;line-height:1.3;
 }
 .header .global-search-input {padding:8px 9px;text-overflow:ellipsis;}
 .header .mcd-header-manager select {padding:8px 23px 8px 8px;text-overflow:ellipsis;}
 .header .global-search-results {min-width:min(285px,calc(100vw - 24px));}
}
@media (max-width:380px) {
 .header .header-top {column-gap:6px;}
 .header .global-search-input,
 .header .mcd-header-manager select {font-size:11px;}
}
/* Shared header metadata on desktop and mobile. */
.header .header-meta {display:flex;align-items:center;justify-content:flex-end;gap:14px;flex-wrap:wrap;}
.header .mcd-updated-info {min-width:0;line-height:1.45;}
.header .mcd-kickoff-countdown {
 display:flex;flex-direction:column;gap:2px;align-items:flex-start;
 border-left:1px solid var(--border);padding-left:13px;white-space:nowrap;
 font-variant-numeric:tabular-nums;
}
.header .mcd-kickoff-countdown-label {font-size:10px;font-weight:800;letter-spacing:.045em;color:var(--accent);}
.header .mcd-kickoff-countdown-value {font-size:13px;font-weight:800;color:var(--text);}
.header .mcd-kickoff-countdown[hidden] {display:none!important;}
@media(max-width:850px){
 .header .header-meta {justify-content:flex-start;gap:9px;}
 .header .mcd-kickoff-countdown {padding-left:10px;}
 .header .mcd-kickoff-countdown-value {font-size:12px;}
}
'''

HEADER_COUNTDOWN_HTML = '''<div id="mcd-kickoff-countdown" class="mcd-kickoff-countdown" role="timer" aria-live="off">
    <span id="mcd-kickoff-countdown-label" class="mcd-kickoff-countdown-label">NEXT KICKOFF</span>
    <span id="mcd-kickoff-countdown-value" class="mcd-kickoff-countdown-value">Checking…</span>
</div>'''


def _parse_utc(raw):
    if not raw:
        return None
    try:
        when = datetime.fromisoformat(str(raw).replace('Z', '+00:00'))
        if when.tzinfo is None:
            return None
        return when.astimezone(timezone.utc)
    except (ValueError, TypeError, OverflowError):
        return None


def next_gameweek_kickoff(fixtures: Iterable[Mapping], *, current_gw: int,
                          live: bool, now: datetime | None = None) -> dict:
    """Choose the earliest known future match of the next not-yet-live GW."""
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError('now must be timezone aware')
    target = max(1, int(current_gw or 1)) + int(bool(live))
    future = []
    for fx in fixtures or []:
        try:
            gw = int(fx.get('event'))
        except (TypeError, ValueError):
            continue
        if gw < target:
            continue
        when = _parse_utc(fx.get('kickoff_time'))
        if when and when > now:
            future.append((gw, when))
    if not future:
        return {'gw': target, 'kickoff': None, 'live': bool(live)}
    gw = min(g for g, _ in future)
    kickoff = min(t for g, t in future if g == gw)
    return {'gw': gw, 'kickoff': kickoff.isoformat().replace('+00:00', 'Z'), 'live': bool(live)}


def countdown_javascript(data: dict) -> str:
    payload = json.dumps(data, ensure_ascii=False).replace('<', '\\u003c')
    return r'''
const MCD_HEADER_KICKOFF = __DATA__;
function updateHeaderKickoffCountdown(){
 const root=document.getElementById('mcd-kickoff-countdown');
 if(!root)return;
 const label=document.getElementById('mcd-kickoff-countdown-label');
 const remaining=document.getElementById('mcd-kickoff-countdown-value');
 const info=MCD_HEADER_KICKOFF;
 if(!info||info.live){root.hidden=true;return;}
 if(!info.kickoff){label.textContent='GW'+(info.gw||'?')+' KICKOFF';remaining.textContent='Date TBC';return;}
 const kickoff=new Date(info.kickoff),ms=kickoff.getTime()-Date.now();
 if(!Number.isFinite(kickoff.getTime())){remaining.textContent='Date TBC';return;}
 // If someone keeps the page open past kickoff, remove the countdown rather than
 // display a misleading negative time while waiting for the next GitHub build.
 if(ms<=0){root.hidden=true;return;}
 label.textContent='GW'+info.gw+' KICKOFF';
 const days=Math.floor(ms/86400000),hours=Math.floor(ms%86400000/3600000),mins=Math.floor(ms%3600000/60000);
 remaining.textContent=days+'d '+hours+'h '+mins+'m';
 remaining.title=kickoff.toLocaleString(undefined,{weekday:'short',day:'numeric',month:'short',hour:'2-digit',minute:'2-digit',timeZoneName:'short'});
 remaining.setAttribute('aria-label',days+' days '+hours+' hours '+mins+' minutes until GW'+info.gw);
}
document.addEventListener('DOMContentLoaded',()=>{
 updateHeaderKickoffCountdown();
 window.setInterval(updateHeaderKickoffCountdown,60000);
});
'''.replace('__DATA__', payload)


def insert_header_countdown(template: str, *, live: bool = False) -> str:
    """Keep last updated next to kickoff countdown; never show it during live GWs."""
    if 'id="mcd-kickoff-countdown"' in template:
        raise RuntimeError('Header kickoff countdown already inserted')
    if 'id="wr-next-gw-countdown"' in template:
        raise RuntimeError('Obsolete War Room countdown still present')
    anchor = '''            <div class="header-meta">

                Last updated:
                __LAST_UPDATED__

                <br>

                __FINISHED_COUNT__
                completed gameweeks

            </div>'''
    if template.count(anchor) != 1:
        raise RuntimeError('Header metadata insertion point changed')
    insert = '''            <div class="header-meta">
                <div class="mcd-updated-info">
                    Last updated: __LAST_UPDATED__<br>
                    __FINISHED_COUNT__ completed gameweeks
                </div>
                ''' + ('' if live else HEADER_COUNTDOWN_HTML) + '''
            </div>'''
    return template.replace(anchor, insert, 1)
