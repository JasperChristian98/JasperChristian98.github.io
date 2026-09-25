"""Manager-style comparison page with comparable spider graphs."""
from __future__ import annotations

import html
import json
from typing import Callable, Dict, Iterable, List, Optional

AXES = [
    ("activity", "Activity"),
    ("trade_game", "Trade game"),
    ("efficiency", "XI efficiency"),
    ("bench_control", "Bench control"),
    ("stability", "Stability"),
    ("form", "Recent form"),
]


def _normalise(values: Dict[str, float], *, inverse: bool = False) -> Dict[str, int]:
    if not values:
        return {}
    cleaned = {k: float(v or 0.0) for k, v in values.items()}
    lo = min(cleaned.values())
    hi = max(cleaned.values())
    if hi == lo:
        return {k: 50 for k in cleaned}
    out = {}
    for key, value in cleaned.items():
        if inverse:
            score = (hi - value) / (hi - lo)
        else:
            score = (value - lo) / (hi - lo)
        out[key] = int(round(score * 100))
    return out


def _blurb(top: List[str], low: List[str]) -> str:
    if not top and not low:
        return "Style indicators are still too limited to draw a clear picture."
    if top and low:
        return (f"Leans most heavily on {top[0]} and {top[1]}, while {low[0]} and {low[1]} "
                f"show up less strongly in the current profile.")
    if top:
        return f"Most clearly defined by {top[0]} and {top[1]}."
    return f"Least associated with {low[0]} and {low[1]} at the moment."


def build_manager_styles(
    managers: Iterable[str],
    manager_style_profile: Callable[[str], Dict],
    positions: Optional[Dict[str, int]] = None,
) -> Dict:
    managers = list(managers)
    positions = positions or {}
    raw = {}
    for manager in managers:
        profile = manager_style_profile(manager)
        raw[manager] = {
            "tags": profile.get("tags", []),
            "activity_per_gw": float(profile.get("activity_per_gw", 0.0) or 0.0),
            "trades": float(profile.get("trades", 0.0) or 0.0),
            "efficiency": float(profile.get("efficiency", 0.0) or 0.0),
            "bench_per_gw": float(profile.get("bench_per_gw", 0.0) or 0.0),
            "volatility": float(profile.get("volatility", 0.0) or 0.0),
            "recent_avg": float(profile.get("recent_avg", 0.0) or 0.0),
            "pickups": float(profile.get("pickups", 0.0) or 0.0),
        }

    activity = _normalise({m: row["activity_per_gw"] for m, row in raw.items()})
    trade_game = _normalise({m: row["trades"] + (0.35 * row["pickups"]) for m, row in raw.items()})
    efficiency = {
        m: max(0, min(100, int(round(row["efficiency"]))))
        for m, row in raw.items()
    }
    bench_control = _normalise({m: row["bench_per_gw"] for m, row in raw.items()}, inverse=True)
    stability = _normalise({m: row["volatility"] for m, row in raw.items()}, inverse=True)
    form = _normalise({m: row["recent_avg"] for m, row in raw.items()})

    cards = []
    for manager in managers:
        scores = {
            "activity": activity.get(manager, 50),
            "trade_game": trade_game.get(manager, 50),
            "efficiency": efficiency.get(manager, 50),
            "bench_control": bench_control.get(manager, 50),
            "stability": stability.get(manager, 50),
            "form": form.get(manager, 50),
        }
        ordered = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
        weakest = sorted(scores.items(), key=lambda item: (item[1], item[0]))
        top_labels = [dict(AXES)[key].lower() for key, _ in ordered[:2]]
        low_labels = [dict(AXES)[key].lower() for key, _ in weakest[:2]]
        cards.append({
            "manager": manager,
            "position": positions.get(manager),
            "scores": [scores[key] for key, _ in AXES],
            "score_map": scores,
            "tags": list(raw[manager]["tags"]),
            "headline": _blurb(top_labels, low_labels),
            "activity_per_gw": round(raw[manager]["activity_per_gw"], 2),
            "trades": int(raw[manager]["trades"]),
            "efficiency": round(raw[manager]["efficiency"], 1),
            "bench_per_gw": round(raw[manager]["bench_per_gw"], 1),
            "volatility": round(raw[manager]["volatility"], 1),
            "recent_avg": round(raw[manager]["recent_avg"], 1),
        })
    cards.sort(key=lambda row: ((row["position"] is None), row["position"], row["manager"].lower()))
    return {
        "axes": [{"key": key, "label": label} for key, label in AXES],
        "managers": cards,
    }


PAGE_HTML = """
<section class="page" id="page-manager-styles">
    <div class="page-heading"><h1>Manager Styles</h1><p>Every manager on the same six-axis spider graph, so you can compare habits, squad management and current form at a glance.</p></div>
    <div class="card">
        <h2>League style map</h2>
        <p class="card-description">Each radar uses the same axes and the same 0–100 scale across the league. Higher is not always "better": activity and trade game describe behaviour, while bench control and stability reward cleaner week-to-week management.</p>
        <div class="style-legend" id="manager-styles-legend"></div>
    </div>
    <div class="manager-styles-grid" id="manager-styles-grid"></div>
</section>
"""

CSS = r"""
.manager-styles-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,340px),1fr));gap:16px;margin-top:16px}
.manager-style-card{border:1px solid var(--border,#405069);border-radius:16px;background:var(--card-bg,#132236);padding:16px;display:flex;flex-direction:column;gap:14px;box-shadow:0 10px 25px rgba(0,0,0,.12)}
.manager-style-head{display:flex;justify-content:space-between;align-items:flex-start;gap:12px}
.manager-style-head h3{margin:0;font-size:1.16rem}
.manager-style-rank{display:inline-flex;align-items:center;justify-content:center;min-width:36px;height:36px;border-radius:999px;background:rgba(57,184,200,.18);border:1px solid rgba(57,184,200,.35);font-weight:700}
.manager-style-rank small{font-size:.65rem;margin-left:2px;opacity:.8}
.style-tag-list{display:flex;flex-wrap:wrap;gap:8px}.style-tag{display:inline-flex;align-items:center;gap:6px;padding:7px 10px;border-radius:999px;border:1px solid rgba(57,184,200,.28);background:rgba(57,184,200,.11);font-size:.78rem;font-weight:600}
.style-tag[title]{cursor:help}
.style-note{margin:0;color:var(--muted,#9eb0c7);line-height:1.55;font-size:.93rem}
.style-legend{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin-top:14px}.style-legend div{border:1px solid rgba(128,128,128,.18);border-radius:12px;padding:11px 12px;background:rgba(128,128,128,.05)}.style-legend strong{display:block;margin-bottom:3px;font-size:.9rem}
.manager-style-stats{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px}.manager-style-stats span{display:flex;flex-direction:column;gap:4px;border:1px solid rgba(128,128,128,.2);border-radius:12px;padding:10px}.manager-style-stats b{font-size:1.15rem}
.manager-style-radar{width:min(100%,340px);height:auto;overflow:visible;margin:0 auto;display:block}.manager-style-ring{fill:none;stroke:currentColor;stroke-opacity:.14}.manager-style-axis{stroke:currentColor;stroke-opacity:.18}.manager-style-label{fill:currentColor;font-size:11px;font-weight:600}.manager-style-area{fill:#39b8c8;fill-opacity:.24;stroke:#39b8c8;stroke-width:2.2}.manager-style-dot{fill:#39b8c8;stroke:var(--card-bg,#132236);stroke-width:1.3}
body[data-theme="light"] .manager-style-card{background:#fff}
@media(max-width:680px){.manager-style-stats{grid-template-columns:repeat(2,minmax(0,1fr))}}
"""


def javascript_with_data(data: Dict) -> str:
    payload = json.dumps(data, separators=(",", ":"), ensure_ascii=False)
    js = r"""
const MANAGER_STYLES_DATA=__PAYLOAD__;
function managerStyleOrdinal(n){
 if(!n&&n!==0)return '';const value=Number(n)||0;const mod100=value%100;
 if(mod100>=11&&mod100<=13)return 'th';
 return ({1:'st',2:'nd',3:'rd'})[value%10]||'th';
}
function managerStyleRadarSVG(values,labels,caption){
 const n=values.length,cx=170,cy=145,r=108;function point(i,t){const a=(i*2*Math.PI/n)-Math.PI/2;return [cx+Math.cos(a)*r*t,cy+Math.sin(a)*r*t];}
 let svg='<svg class="manager-style-radar" viewBox="0 0 340 305" role="img" aria-label="'+escapePlayerHTML(caption)+'">';
 [0.25,0.5,0.75,1].forEach(level=>{svg+='<polygon class="manager-style-ring" points="'+labels.map((_,i)=>point(i,level).map(v=>v.toFixed(1)).join(',')).join(' ')+'"/>';});
 labels.forEach((label,i)=>{const end=point(i,1);const text=point(i,1.17);svg+='<line class="manager-style-axis" x1="'+cx+'" y1="'+cy+'" x2="'+end[0].toFixed(1)+'" y2="'+end[1].toFixed(1)+'"/>';svg+='<text class="manager-style-label" x="'+text[0].toFixed(1)+'" y="'+(text[1]+4).toFixed(1)+'" text-anchor="middle">'+escapePlayerHTML(label)+'</text>';});
 const coords=values.map((v,i)=>point(i,Math.max(0,Math.min(100,Number(v)||0))/100));
 svg+='<polygon class="manager-style-area" points="'+coords.map(pt=>pt.map(v=>v.toFixed(1)).join(',')).join(' ')+'"/>';
 coords.forEach((pt,i)=>{svg+='<circle class="manager-style-dot" cx="'+pt[0].toFixed(1)+'" cy="'+pt[1].toFixed(1)+'" r="3.5"><title>'+escapePlayerHTML(labels[i])+': '+Math.round(values[i])+'/100</title></circle>';});
 return svg+'</svg>';
}
function renderManagerStyles(){
 const grid=document.getElementById('manager-styles-grid');if(!grid||!MANAGER_STYLES_DATA)return;
 const axes=MANAGER_STYLES_DATA.axes||[];const labels=axes.map(a=>a.label);
 const descriptions={activity:'How active a manager is in the market overall.',trade_game:'How much they lean into trades and transactions.',efficiency:'How much of the squad\'s available score reaches the XI.',bench_control:'How little value gets stranded on the bench.',stability:'How steady the weekly scores have been.',form:'How hot the team\'s recent scoring run is.'};
 const legend=document.getElementById('manager-styles-legend');
 if(legend&&!legend.dataset.ready){
   legend.innerHTML=axes.map(axis=>'<div><strong>'+escapePlayerHTML(axis.label)+'</strong><span>'+escapePlayerHTML(descriptions[axis.key]||'')+'</span></div>').join('');
   legend.dataset.ready='1';
 }
 grid.innerHTML=(MANAGER_STYLES_DATA.managers||[]).map(item=>{
   const tags=(item.tags||[]).map(tag=>'<span class="style-tag" title="'+escapePlayerHTML(tag.description||'')+'">'+escapePlayerHTML(tag.name||'')+'</span>').join('');
   const pos=item.position?'<span class="manager-style-rank">'+item.position+'<small>'+managerStyleOrdinal(item.position)+'</small></span>':'';
   return '<article class="manager-style-card">'
     +'<div class="manager-style-head"><div><h3>'+escapePlayerHTML(item.manager)+'</h3><p class="style-note">'+escapePlayerHTML(item.headline||'')+'</p></div>'+pos+'</div>'
     +managerStyleRadarSVG(item.scores||[],labels,(item.manager||'Manager')+' style radar')
     +'<div class="style-tag-list">'+(tags||'<span class="style-note">No standout tags yet.</span>')+'</div>'
     +'<div class="manager-style-stats">'
        +'<span><small>Activity / GW</small><b>'+escapePlayerHTML(String(item.activity_per_gw))+'</b></span>'
        +'<span><small>Trades</small><b>'+escapePlayerHTML(String(item.trades))+'</b></span>'
        +'<span><small>XI efficiency</small><b>'+escapePlayerHTML(String(item.efficiency))+'%</b></span>'
        +'<span><small>Bench pts / GW</small><b>'+escapePlayerHTML(String(item.bench_per_gw))+'</b></span>'
        +'<span><small>Volatility</small><b>'+escapePlayerHTML(String(item.volatility))+'</b></span>'
        +'<span><small>Recent avg</small><b>'+escapePlayerHTML(String(item.recent_avg))+'</b></span>'
      +'</div>'
     +'</article>';
 }).join('');
}
document.addEventListener('DOMContentLoaded',renderManagerStyles);
"""
    return js.replace('__PAYLOAD__', payload)


__all__ = [
    "AXES",
    "CSS",
    "PAGE_HTML",
    "build_manager_styles",
    "javascript_with_data",
]
