"""Small, tested Overview action digest built from existing planner/War Room models.

No new forecasts are computed here: the same projections, ownership snapshot and
legal-XI solver remain the source of truth. No transactions are submitted.
"""
from __future__ import annotations

import json


def make_decisions(planner: dict, war_room: dict, game_state: str = 'upcoming') -> dict:
    """Return action cards for every manager, excluding unsupported suggestions."""
    result = {}
    for manager, plan in planner.items():
        room = war_room.get(manager) or {}
        weeks = plan.get('weeks') or []
        if not weeks or room.get('warning'):
            result[manager] = {'gw': None, 'opponent': None, 'items': [],
                               'message': plan.get('warning') or room.get('warning') or 'No upcoming fixtures.'}
            continue
        week = weeks[0]
        gw = week.get('gw')
        cards = []
        flags = (room.get('you') or {}).get('flags') or []
        starting_ids = {p['id'] for p in week.get('starters', [])}
        for p in sorted(flags, key=lambda p: (p['id'] not in starting_ids, float(p.get('availability', 1) if p.get('availability') is not None else 1))):
            if p['id'] not in starting_ids:
                continue  # the XI is the immediate decision; bench risk stays in War Room
            avail = p.get('availability')
            pct = f"{round(float(avail)*100)}% modelled availability" if avail is not None else 'FPL availability flag'
            cards.append({'kind': 'availability', 'urgency': 0, 'title': f"Review {p['name']}'s availability",
                          'detail': f"Projected starter · {pct}. Check the latest team news and your bench before the deadline.",
                          'target': 'war-room', 'cta': 'Inspect in War Room'})
        # Compare near-term impact with five-week impact, using each existing
        # optimiser's own estimates. Do not add them together or imply certainty.
        near = (room.get('upgrades') or [])[:1]
        long = (plan.get('suggestions') or [])[:1]
        if near and float(near[0].get('gain') or 0) > .5:
            u = near[0]
            cards.append({'kind':'waiver', 'urgency':1, 'title':f"Consider {u['in_name']} for GW{gw}",
                          'detail': f"Replacing {u['out_name']} is projected to add {float(u['gain']):.1f} XI pts this week. Subject to waiver priority and unchanged ownership.",
                          'target':'war-room','cta':'Review one-week upgrade'})
        if long and float(long[0].get('gain') or 0) > 1:
            u = long[0]
            # Don't recommend the same swap twice; keep the long horizon only
            # when it points at something materially different.
            if not near or u.get('id') != near[0].get('in_id') or u.get('drop_id') != near[0].get('out_id'):
                cards.append({'kind':'planning','urgency':2,'title':f"Five-week opportunity: {u['name']}",
                              'detail':f"Swapping out {u['drop_name']} adds {float(u['gain']):.1f} projected XI pts across the next five GWs, before waiver restrictions.",
                              'target':'myteam','cta':'Explore five-GW planner'})
        by_pos = room.get('positional') or []
        weak = min(by_pos, key=lambda v: float(v.get('edge') or 0), default=None)
        if weak and float(weak.get('edge') or 0) < -1.0:
            cards.append({'kind':'matchup','urgency':3, 'title':f"Matchup concern: {weak['position']}",
                          'detail':f"Your opponent projects {abs(float(weak['edge'])):.1f} more XI points in this position. Inspect both sides before changing your XI.",
                          'target':'war-room','cta':'Compare the two XIs'})
        if len(weeks) > 1:
            worst = min(weeks, key=lambda w: float(w.get('xi') or 0))
            if worst.get('gw') != gw and float(week.get('xi') or 0) - float(worst.get('xi') or 0) >= 5:
                cards.append({'kind':'planning','urgency':4,'title':f"Plan ahead for GW{worst['gw']}",
                              'detail':f"Your best legal XI projects {float(worst['xi']):.1f} pts in that week versus {float(week['xi']):.1f} now. Check blanks, doubles and squad cover.",
                              'target':'myteam','cta':'Explore five-GW planner'})
        cards.sort(key=lambda item: item['urgency'])
        result[manager] = {'gw':gw, 'opponent':room.get('opponent') or week.get('opponent'),
                           'items':cards[:4], 'message': 'No urgent modelled issues. Review your XI closer to the deadline.' if not cards else None,
                           'as_of': 'Current dashboard build', 'live': game_state == 'live'}
    return result


DECISION_CENTRE_HTML = '''<div class="card decision-centre" id="decision-centre" aria-label="Decision Centre">
 <div class="decision-head"><div><span class="relationship-eyebrow">YOUR NEXT MOVE</span><h2>Decision Centre</h2>
 <p class="card-description">A short action list from your existing War Room and five-GW planner — not another set of forecasts.</p></div>
 <label>Manager<select id="decision-manager" onchange="renderDecisionCentre()"></select></label></div>
 <div id="decision-content" aria-live="polite"></div>
 <p class="decision-note">Read-only suggestions based on the last dashboard update. Verify availability, current ownership and waiver order before making a move.</p>
</div>'''

DECISION_CENTRE_CSS = '''
.decision-head{display:flex;align-items:start;justify-content:space-between;gap:12px;flex-wrap:wrap}
.decision-head label{font-size:12px;color:var(--muted);font-weight:700;display:grid;gap:5px}
.decision-head select{background:var(--bg-secondary);color:var(--text);border:1px solid var(--border);padding:8px;border-radius:9px;max-width:230px}
.decision-list{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px;margin-top:15px}
.decision-item{border:1px solid var(--border);border-radius:12px;background:var(--bg-secondary);padding:15px;display:flex;flex-direction:column;gap:8px}
.decision-item h3{font-size:15px;margin:0}.decision-item p{font-size:12px;color:var(--muted);margin:0;line-height:1.5;flex:1}
.decision-item button{border:1px solid var(--accent);background:transparent;color:var(--text);padding:9px;border-radius:9px;cursor:pointer;font-weight:700;text-align:left}
.decision-item button:hover,.decision-item button:focus-visible{background:rgba(52,211,153,.12)}
.decision-note{font-size:11px;color:var(--muted);margin:12px 0 0}.decision-meta{font-size:12px;color:var(--muted);margin-top:8px}
.decision-kind{font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.06em;color:var(--accent)}
'''

# This is appended to the legacy javascript string before HTML publishing.
DECISION_CENTRE_JS = r'''
const DECISION_CENTRE = __DECISION_CENTRE_DATA__;
function renderDecisionCentre(){
 const select=document.getElementById('decision-manager'),root=document.getElementById('decision-content');
 if(!select||!root)return;
 if(!select.dataset.ready){
   select.innerHTML=Object.keys(DECISION_CENTRE).map(m=>'<option value="'+escapePlayerHTML(m)+'">'+escapePlayerHTML(m)+'</option>').join('');
   const preferred=(typeof currentMyTeamManager==='function'&&currentMyTeamManager())||'Kamararama FC';
   if(Object.prototype.hasOwnProperty.call(DECISION_CENTRE,preferred))select.value=preferred;
   select.dataset.ready='1';
 }
 const data=DECISION_CENTRE[select.value]||{};
 const meta=data.gw?('GW'+data.gw+' · vs '+escapePlayerHTML(data.opponent||'TBC')):'Upcoming fixtures unavailable';
 const items=(data.items||[]).map(item=>
   '<article class="decision-item"><span class="decision-kind">'+escapePlayerHTML(item.kind)+'</span><h3>'+escapePlayerHTML(item.title)+'</h3><p>'+escapePlayerHTML(item.detail)+'</p><button type="button" data-target="'+escapePlayerHTML(item.target)+'" onclick="showPage(this.dataset.target)">'+escapePlayerHTML(item.cta)+' →</button></article>').join('');
 root.innerHTML='<div class="decision-meta">'+meta+(data.live?' · Live GW — reassess after the deadline':'')+'</div>'+
    (items?'<div class="decision-list">'+items+'</div>':'<p class="decision-meta">'+escapePlayerHTML(data.message||'No immediate actions.')+'</p>');
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',renderDecisionCentre);
else renderDecisionCentre();
'''


def javascript_with_data(payload: dict) -> str:
    # Ensure a player name cannot close a script tag or inject JS.
    safe = json.dumps(payload, ensure_ascii=True, separators=(',', ':')).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
    return DECISION_CENTRE_JS.replace('__DECISION_CENTRE_DATA__', safe)
