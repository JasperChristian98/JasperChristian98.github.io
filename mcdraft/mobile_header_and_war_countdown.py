"""Compact two-control mobile header and fixture-backed War Room countdown.

Presentation-only integration; never changes existing prediction calculations.
"""
from __future__ import annotations

from datetime import datetime, timezone
import json
from typing import Iterable, Mapping

CSS = r'''
/* Keep global search and the team picker on the SAME row on small screens. */
@media (max-width:850px) {
  .header .header-top {display:flex; flex-wrap:wrap; column-gap:8px; row-gap:9px; align-items:center;}
  .header .global-search-wrap {
    order:10; flex:1 1 0; width:auto; min-width:0; max-width:none;
    margin:0; box-sizing:border-box;
  }
  .header .mcd-header-manager {
    order:11; flex:0 0 42%; width:42%; min-width:0; max-width:160px;
    margin:0; gap:0; box-sizing:border-box;
  }
  .header .mcd-header-manager span {display:none;}
  .header .global-search-input,
  .header .mcd-header-manager select {
    width:100%; min-width:0; height:38px; min-height:38px;
    box-sizing:border-box; border-radius:9px; font-size:12px;
  }
  .header .global-search-input {padding:8px 9px; text-overflow:ellipsis;}
  .header .mcd-header-manager select {padding:7px 22px 7px 7px; text-overflow:ellipsis;}
  .header .global-search-results {min-width:min(285px,calc(100vw - 24px));}
}
@media (max-width:380px) {
  .header .mcd-header-manager {flex-basis:43%; width:43%;}
  .header .global-search-input,
  .header .mcd-header-manager select {font-size:11px;}
}
/* Prominent but compact countdown above the War Room's matchup content. */
#myteam-sub-war-room .wr-countdown {
  display:flex; align-items:center; gap:16px; justify-content:space-between;
  border:1px solid var(--border); background:var(--card);
  border-radius:14px; padding:15px 18px; margin:0 0 16px;
}
#myteam-sub-war-room .wr-countdown-eyebrow {color:var(--accent);font-size:11px;font-weight:800;letter-spacing:.07em;}
#myteam-sub-war-room .wr-countdown h3 {color:var(--text);font-size:18px;margin:4px 0;}
#myteam-sub-war-room .wr-countdown-detail {color:var(--muted);font-size:12px;line-height:1.4;}
#myteam-sub-war-room .wr-countdown-time {font-variant-numeric:tabular-nums;font-size:clamp(20px,4vw,31px);font-weight:850;color:var(--text);white-space:nowrap;}
@media(max-width:540px){
  #myteam-sub-war-room .wr-countdown {gap:8px;flex-wrap:wrap;padding:13px;}
  #myteam-sub-war-room .wr-countdown h3{font-size:16px;}
  #myteam-sub-war-room .wr-countdown-time {font-size:23px;}
}
'''

WAR_ROOM_COUNTDOWN_HTML = '''<div id="wr-next-gw-countdown" class="wr-countdown" role="status" aria-live="off">
  <div><span class="wr-countdown-eyebrow">NEXT GAMEWEEK</span>
  <h3 id="wr-countdown-title">Checking kickoff…</h3>
  <div id="wr-countdown-detail" class="wr-countdown-detail"></div></div>
  <div id="wr-countdown-time" class="wr-countdown-time" aria-label="Time until kickoff">—</div>
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
    """Find the earliest future kickoff of the next *unstarted* gameweek.

    If the current GW is live, skip its remaining fixtures and target GW+1.
    A double gameweek uses its earliest scheduled match. Missing TBD times are
    ignored and never replaced by a fabricated deadline-time estimate.
    """
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
        return {'gw': target, 'kickoff': None}
    # Prefer the next gameweek with a confirmed future fixture, not the
    # physically earliest date of an unrelated later fixture.
    gw = min(g for g, _ in future)
    kickoff = min(t for g, t in future if g == gw)
    return {'gw': gw, 'kickoff': kickoff.isoformat().replace('+00:00', 'Z')}


def countdown_javascript(data: dict) -> str:
    payload = json.dumps(data, ensure_ascii=False).replace('<', '\\u003c')
    return r'''
const MCD_WAR_ROOM_KICKOFF = __DATA__;
function updateWarRoomCountdown(){
 const root=document.getElementById('wr-next-gw-countdown');if(!root)return;
 const title=document.getElementById('wr-countdown-title');
 const detail=document.getElementById('wr-countdown-detail');
 const remaining=document.getElementById('wr-countdown-time');
 const info=MCD_WAR_ROOM_KICKOFF;
 if(!info||!info.kickoff){
   title.textContent='GW'+(info?.gw||'?')+' · Date to be confirmed';
   detail.textContent='Kickoff time is not available in the fixture feed yet.';
   remaining.textContent='TBC';return;
 }
 const kickoff=new Date(info.kickoff),ms=kickoff.getTime()-Date.now();
 if(!Number.isFinite(kickoff.getTime())){title.textContent='Kickoff date unavailable';remaining.textContent='TBC';return;}
 title.textContent='GW'+info.gw+' kicks off';
 detail.textContent=kickoff.toLocaleString(undefined,{weekday:'short',day:'numeric',month:'short',hour:'2-digit',minute:'2-digit',timeZoneName:'short'});
 if(ms<=0){remaining.textContent='Kickoff underway';return;}
 const days=Math.floor(ms/86400000),hours=Math.floor(ms%86400000/3600000),mins=Math.floor(ms%3600000/60000);
 remaining.textContent=days+'d '+hours+'h '+mins+'m';
 remaining.setAttribute('aria-label',days+' days '+hours+' hours '+mins+' minutes until GW'+info.gw);
}
document.addEventListener('DOMContentLoaded',()=>{
 updateWarRoomCountdown();
 // The page can stay open through kickoff; updates once per minute.
 window.setInterval(updateWarRoomCountdown,60000);
});
'''.replace('__DATA__', payload)


def insert_war_room_countdown(template: str) -> str:
    """Inject into relocated My Team War Room (not the old standalone page)."""
    marker = '<div class="myteam-subpage" id="myteam-sub-war-room">'
    if template.count(marker) != 1:
        raise RuntimeError('My Team War Room countdown insertion point changed')
    if 'id="wr-next-gw-countdown"' in template:
        raise RuntimeError('War Room countdown already inserted')
    return template.replace(marker, marker + '\n' + WAR_ROOM_COUNTDOWN_HTML, 1)
