"""Extend the existing Trade Lab with mutual-deal discovery and separate trade history.

The existing Trade Lab remains the authoritative manual deal builder. Suggestions
reuse its current ownership, valuation and projection payload; they never claim
that a manager will accept a proposed trade.
"""
from __future__ import annotations

ROOM_HTML = '''
<div class="card mcd-negotiation-room" id="mcd-negotiation-room">
  <div class="mcd-neg-header">
    <div><div class="eyebrow">THE NEGOTIATION ROOM</div><h2>Find a deal that works for both sides</h2>
      <p class="card-description">Uses today's owned players and the same player values as Trade Lab. Explore same-position trades, then load any offer into the existing simulator for a closer look.</p></div>
  </div>
  <div class="mcd-neg-controls">
    <label>My team<select id="mcd-neg-manager" onchange="renderNegotiationRoom()" aria-label="Your team for trade discovery"></select></label>
    <label>Potential trade partner<select id="mcd-neg-partner" onchange="renderNegotiationRoom()" aria-label="Potential trade partner"><option value="">All other managers</option></select></label>
    <label>Deal type<select id="mcd-neg-filter" onchange="renderNegotiationRoom()"><option value="">All proposals</option><option value="Safe">Safe</option><option value="Even">Even</option><option value="Ambitious">Ambitious</option></select></label>
  </div>
  <div class="mcd-neg-key">
    <div><strong>Safe</strong><span>Close model value and lower disruption to both squads.</span></div>
    <div><strong>Even</strong><span>Very close overall value, with a plausible gain in positional fit for each manager.</span></div>
    <div><strong>Ambitious</strong><span>One manager has to accept a meaningful valuation gap for a possible squad-fit gain.</span></div>
  </div>
  <p class="card-description">Labels describe modelled negotiation difficulty, not guaranteed acceptance, official league legality or medical clearance. All recommendations are hypothetical.</p>
  <div id="mcd-neg-results" aria-live="polite"><div class="notice">Choose your team to discover trades.</div></div>
</div>
'''

CSS = r'''
.mcd-negotiation-room{margin-bottom:16px}.mcd-neg-header{display:flex;justify-content:space-between;gap:15px;align-items:start}
.mcd-neg-controls{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:15px 0}
.mcd-neg-controls label{display:flex;flex-direction:column;gap:5px;font-size:12px;color:var(--muted);font-weight:800}
.mcd-neg-controls select{width:100%;min-width:0;border-radius:9px;border:1px solid var(--border);background:var(--bg-secondary);color:var(--text);padding:10px;font:inherit;font-size:13px}
.mcd-neg-key{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin:12px 0}
.mcd-neg-key>div{border-radius:12px;border:1px solid var(--border);background:var(--bg-secondary);padding:11px}
.mcd-neg-key strong{display:block;margin-bottom:4px;color:var(--text)}.mcd-neg-key span{font-size:12px;color:var(--muted);line-height:1.45}
.mcd-neg-offer{border:1px solid var(--border);border-radius:13px;background:var(--bg-secondary);padding:15px;margin-top:13px;min-width:0}
.mcd-neg-offer-header{display:flex;align-items:start;justify-content:space-between;gap:10px;flex-wrap:wrap}
.mcd-neg-badge{font-size:11px;font-weight:900;border-radius:999px;padding:5px 10px;border:1px solid var(--border)}
.mcd-neg-badge.safe{color:#68e9b3;background:rgba(22,163,116,.11);border-color:rgba(22,163,116,.4)}
.mcd-neg-badge.even{color:#61c6f4;background:rgba(56,189,248,.12);border-color:rgba(56,189,248,.4)}
.mcd-neg-badge.ambitious{color:#f4c77e;background:rgba(245,158,11,.11);border-color:rgba(245,158,11,.4)}
.mcd-neg-exchange{display:grid;grid-template-columns:minmax(0,1fr) auto minmax(0,1fr);gap:12px;margin:14px 0;align-items:center}
.mcd-neg-exchange>div{min-width:0;border:1px solid var(--border);border-radius:10px;padding:11px;background:var(--card)}
.mcd-neg-exchange strong,.mcd-neg-exchange small{display:block}.mcd-neg-exchange small{color:var(--muted);margin-top:4px}
.mcd-neg-metrics{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px}.mcd-neg-metrics span{display:flex;flex-direction:column;border:1px solid var(--border);border-radius:9px;padding:9px;font-size:12px}.mcd-neg-metrics b{font-size:17px;margin-top:3px}
.mcd-neg-notes{color:var(--muted);font-size:13px;line-height:1.5;margin:10px 0}.mcd-neg-action{padding:9px 13px;border:1px solid var(--accent);color:var(--text);background:var(--card);border-radius:9px;cursor:pointer;font:inherit;font-weight:750;margin-top:8px}
.mcd-neg-action:focus-visible{outline:2px solid var(--accent);outline-offset:3px}.mcd-neg-more{display:flex;justify-content:center;margin:16px 0}
.mcd-neg-audit{margin-top:12px;padding:13px;border-top:1px solid var(--border)}.mcd-neg-audit h4{margin:0 0 10px}.mcd-neg-check{display:flex;gap:8px;align-items:start;margin:7px 0;font-size:13px}.mcd-neg-check span:first-child{font-weight:900}
body[data-theme="light"] .mcd-neg-badge.safe{color:#076849}body[data-theme="light"] .mcd-neg-badge.even{color:#0c6388}body[data-theme="light"] .mcd-neg-badge.ambitious{color:#89520b}
@media(max-width:720px){.mcd-neg-controls,.mcd-neg-key{grid-template-columns:1fr}.mcd-neg-exchange{grid-template-columns:minmax(0,1fr);gap:8px}.mcd-neg-exchange>span{text-align:center}.mcd-neg-metrics{grid-template-columns:repeat(2,minmax(0,1fr))}}
'''

JS = r'''
/* McDraft Negotiation Room: no independent market data or hidden model. */
let mcdNegOffers=[];
function mcdNegNum(x){return Number(x)||0;}
function mcdNegByPos(players){const by={GKP:[],DEF:[],MID:[],FWD:[]};(players||[]).forEach(p=>{if(by[p.position])by[p.position].push(p)});return by;}
function mcdNegPositionMean(players,pos){const items=(players||[]).filter(p=>p.position===pos);return items.length?items.reduce((s,p)=>s+mcdNegNum(p.value),0)/items.length:0;}
function mcdNegFit(manager, outgoing, incoming){
 const roster=TRADE_SIMULATOR_DATA[manager]||[];
 // Baseline is the team's other options in the same role, not the entire pool.
 const other=roster.filter(p=>p.position===outgoing.position && p.id!==outgoing.id);
 const baseline=other.length?other.reduce((s,p)=>s+mcdNegNum(p.projection),0)/other.length:0;
 const newPotential=mcdNegNum(incoming.projection)-mcdNegNum(outgoing.projection);
 const formDifference=mcdNegNum(incoming.form)-mcdNegNum(outgoing.form);
 const importanceCost=Math.max(0,mcdNegNum(outgoing.importance)-mcdNegNum(incoming.importance))*0.035;
 const positionDepth=other.length<2?0.2:0;
 return newPotential*1.45+formDifference*.22+((mcdNegNum(incoming.projection)-baseline)*.13)-importanceCost-positionDepth;
}
function mcdNegClassify(a,b,fitA,fitB){
 const va=mcdNegNum(a.value),vb=mcdNegNum(b.value),avg=Math.max(1,(va+vb)/2);
 const fair=Math.max(0,Math.min(100,100-Math.abs(va-vb)/avg*100));
 // An offer must have some rationale for BOTH sides. A one-sided swap is not
 // labelled as mutual even when headline values are close.
 const mutual=fitA>=-.6&&fitB>=-.6;
 if(!mutual&&fair<69)return null;
 if(fair>=94&&fitA>=-.2&&fitB>=-.2)return {label:'Even',fair:fair};
 const disruption=(mcdNegNum(a.importance)+mcdNegNum(b.importance))/2;
 if(fair>=83&&disruption<=18&&mutual)return {label:'Safe',fair:fair};
 if(fair>=78&&mutual)return {label:'Even',fair:fair};
 if(fair>=57 && (fitA>0.6||fitB>0.6) && Math.min(fitA,fitB)>-1.1)return {label:'Ambitious',fair:fair};
 return null;
}
function mcdNegDiscover(manager,partner){
 const managers=partner?[partner]:Object.keys(TRADE_SIMULATOR_DATA||{}).filter(name=>name!==manager);
 const mine=mcdNegByPos(TRADE_SIMULATOR_DATA[manager]||[]);let out=[];
 for(const other of managers){if(other===manager)continue;const theirs=mcdNegByPos(TRADE_SIMULATOR_DATA[other]||[]);
  for(const pos of ['GKP','DEF','MID','FWD']){
   for(const a of (mine[pos]||[]))for(const b of (theirs[pos]||[])){
    const fitA=mcdNegFit(manager,a,b),fitB=mcdNegFit(other,b,a);
    const category=mcdNegClassify(a,b,fitA,fitB);if(!category)continue;
    const quality=Math.max(0,Math.min(100,category.fair*.67+Math.max(-10,Math.min(10,fitA+fitB))*2.2+((fitA>=0&&fitB>=0)?12:0)));
    out.push({manager,partner:other,give:[a],receive:[b],category:category.label,fair:category.fair,quality,fitA,fitB});
   }
  }
 }
 out.sort((a,b)=>b.quality-a.quality||b.fair-a.fair||a.partner.localeCompare(b.partner));
 // Limit duplicate variations for the same counterparty/position. Their
 // distinct offers remain visible in the manual simulator if desired.
 const seen=new Map(),selected=[];
 for(const deal of out){const key=deal.partner+'|'+deal.give[0].position;const used=seen.get(key)||0;
  if(used>=3)continue;seen.set(key,used+1);selected.push(deal);if(selected.length>=100)break;
 }
 return selected;
}
function mcdNegExplain(deal){
 const gap=Math.abs(mcdNegNum(deal.give[0].value)-mcdNegNum(deal.receive[0].value)).toFixed(1);
 const gainA=(mcdNegNum(deal.receive[0].projection)-mcdNegNum(deal.give[0].projection)).toFixed(1);
 const gainB=(mcdNegNum(deal.give[0].projection)-mcdNegNum(deal.receive[0].projection)).toFixed(1);
 return 'Model value gap: '+gap+'. Next-GW projection change: '+deal.manager+' '+(Number(gainA)>=0?'+':'')+gainA+' pts; '+deal.partner+' '+(Number(gainB)>=0?'+':'')+gainB+' pts. One side may prefer current form or squad balance over raw projection.';
}
function mcdNegCard(deal,index){
 const e=escapePlayerHTML;const a=deal.give[0],b=deal.receive[0];
 return '<article class="mcd-neg-offer">'
  +'<div class="mcd-neg-offer-header"><div><strong>'+e(deal.manager)+' ↔ '+e(deal.partner)+'</strong><div class="mcd-neg-notes">'+e(a.position)+' · one-for-one</div></div><span class="mcd-neg-badge '+deal.category.toLowerCase()+'">'+deal.category+'</span></div>'
  +'<div class="mcd-neg-exchange"><div><strong>'+e(a.name)+'</strong><small>'+e(deal.manager)+' gives · '+Number(a.value).toFixed(1)+' value</small></div><span>⇄</span><div><strong>'+e(b.name)+'</strong><small>'+e(deal.partner)+' gives · '+Number(b.value).toFixed(1)+' value</small></div></div>'
  +'<div class="mcd-neg-metrics"><span>Deal fit<b>'+deal.quality.toFixed(0)+'/100</b></span><span>Value fairness<b>'+deal.fair.toFixed(0)+'/100</b></span><span>Next-GW projections<b>'+Number(a.projection).toFixed(1)+' ↔ '+Number(b.projection).toFixed(1)+'</b></span></div>'
  +'<p class="mcd-neg-notes">'+e(mcdNegExplain(deal))+'</p>'
  +'<button class="mcd-neg-action" type="button" onclick="mcdNegLoadDeal('+index+')">Load in Trade Lab →</button></article>';
}
function mcdNegPopulate(){
 const own=document.getElementById('mcd-neg-manager'),opponent=document.getElementById('mcd-neg-partner');if(!own||!opponent)return;
 const names=Object.keys(TRADE_SIMULATOR_DATA||{});if(!own.options.length){names.forEach(name=>own.add(new Option(name,name)));}
 const selected=opponent.value;opponent.replaceChildren(new Option('All other managers',''));
 names.filter(name=>name!==own.value).forEach(name=>opponent.add(new Option(name,name)));
 if(names.includes(selected)&&selected!==own.value)opponent.value=selected;
}
function renderNegotiationRoom(){
 const own=document.getElementById('mcd-neg-manager'),partner=document.getElementById('mcd-neg-partner'),filter=document.getElementById('mcd-neg-filter'),results=document.getElementById('mcd-neg-results');
 if(!own||!partner||!filter||!results)return;
 mcdNegPopulate();const manager=own.value;
 if(!manager||!TRADE_SIMULATOR_DATA[manager]){results.innerHTML='<div class="notice">Select your team to see suitable deals.</div>';return;}
 mcdNegOffers=mcdNegDiscover(manager,partner.value).filter(d=>!filter.value||d.category===filter.value);
 const shown=mcdNegOffers.slice(0,16);
 results.innerHTML=shown.length?'<p class="card-description">'+mcdNegOffers.length+' model-compatible offer(s) found. Showing '+shown.length+'; proposals are not guaranteed to be accepted.</p>'+shown.map(mcdNegCard).join(''):
   '<div class="notice">No deals match these filters right now. Try another manager or switch to all proposal types.</div>';
 if(mcdNegOffers.length>16)results.innerHTML+='<div class="mcd-neg-more"><button type="button" class="mcd-neg-action" onclick="mcdNegShowMore()">Show more offers</button></div>';
}
function mcdNegShowMore(){const results=document.getElementById('mcd-neg-results');if(!results)return;results.innerHTML='<p class="card-description">'+mcdNegOffers.length+' proposals.</p>'+mcdNegOffers.map(mcdNegCard).join('');}
function mcdNegLoadDeal(index){
 const deal=mcdNegOffers[index];if(!deal)return;
 const a=document.getElementById('trade-sim-manager-a'),b=document.getElementById('trade-sim-manager-b');if(!a||!b)return;
 a.value=deal.manager;b.value=deal.partner;renderTradeSimulator();
 for(const [side,players] of [['a',deal.give],['b',deal.receive]])for(const p of players){
  const check=document.querySelector('.trade-sim-check[data-side="'+side+'"][data-id="'+Number(p.id)+'"]');if(check)check.checked=true;
 }
 evaluateTradeSimulator();
 document.querySelector('.trade-simulator')?.scrollIntoView({behavior:'smooth',block:'start'});
}
function mcdNegAuditTrade(){
 const result=document.getElementById('trade-sim-result'),a=document.getElementById('trade-sim-manager-a'),b=document.getElementById('trade-sim-manager-b');
 if(!result||!a||!b)return;if(result.querySelector('.mcd-neg-audit'))return;
 const outgoing=selectedTradePlayers('a',a.value),incoming=selectedTradePlayers('b',b.value);
 if(!outgoing.length&&!incoming.length)return;
 const checks=[];const validManagers=a.value&&b.value&&a.value!==b.value;
 checks.push([validManagers,'Two different managers selected.']);
 checks.push([outgoing.length>0&&outgoing.length===incoming.length,'Equal numbers of players on both sides.']);
 checks.push([samePositionSignature(tradePositionSignature(outgoing),tradePositionSignature(incoming)),'Position quotas match on both sides.']);
 const ownA=outgoing.every(p=>(TRADE_SIMULATOR_DATA[a.value]||[]).some(x=>x.id===p.id));
 const ownB=incoming.every(p=>(TRADE_SIMULATOR_DATA[b.value]||[]).some(x=>x.id===p.id));
 checks.push([ownA&&ownB,'Every selected player appears on the expected current roster.']);
 const ids=[...outgoing,...incoming].map(p=>p.id);
 checks.push([new Set(ids).size===ids.length,'No player is included twice.']);
 let html='<section class="mcd-neg-audit"><h4>Trade validity & negotiation</h4>';
 html+=checks.map(c=>'<div class="mcd-neg-check"><span>'+ (c[0]?'✓':'✕')+'</span><span>'+escapePlayerHTML(c[1])+'</span></div>').join('');
 if(checks.every(c=>c[0])&&outgoing.length===1&&incoming.length===1){
  const pa=outgoing[0],pb=incoming[0];const fA=mcdNegFit(a.value,pa,pb),fB=mcdNegFit(b.value,pb,pa),label=mcdNegClassify(pa,pb,fA,fB);
  const va=mcdNegNum(pa.value),vb=mcdNegNum(pb.value),fair=Math.max(0,100-Math.abs(va-vb)/Math.max(1,(va+vb)/2)*100);
  const tag=label?label.label:'One-sided';
  html+='<p class="mcd-neg-notes"><strong>Negotiation profile: '+escapePlayerHTML(tag)+'</strong> · Value fairness '+fair.toFixed(0)+'/100. '+escapePlayerHTML(mcdNegExplain({give:[pa],receive:[pb],manager:a.value,partner:b.value}))+'</p>';
 }
 else if(checks.every(c=>c[0]))html+='<p class="mcd-neg-notes">Structurally compatible package. Bundle-level negotiation difficulty is not rated by the one-for-one discovery model.</p>';
 html+='<p class="card-description">Draft roster and position checks only. The dashboard cannot certify live league trade windows, pending transactions, other managers\' consent or official processing.</p></section>';
 result.insertAdjacentHTML('beforeend',html);
}
// Preserve all original Trade Lab narration, then append deterministic checks.
const mcdOriginalEvaluateTradeSimulator=evaluateTradeSimulator;
evaluateTradeSimulator=function(){mcdOriginalEvaluateTradeSimulator();mcdNegAuditTrade();};
document.addEventListener('DOMContentLoaded',()=>{
 const select=document.getElementById('mcd-neg-manager');if(!select)return;
 mcdNegPopulate();const header=document.getElementById('mcd-header-team');
 if(header&&TRADE_SIMULATOR_DATA[header.value])select.value=header.value;
 else if(typeof mcdPreferredManager!=='undefined'&&TRADE_SIMULATOR_DATA[mcdPreferredManager])select.value=mcdPreferredManager;
 renderNegotiationRoom();
 header?.addEventListener('change',()=>{if(TRADE_SIMULATOR_DATA[header.value]){select.value=header.value;document.getElementById('mcd-neg-partner').value='';renderNegotiationRoom();}});
});
// The welcome screen updates the global selector programmatically, so a
// change event alone would miss the visitor's first choice.
if(typeof syncManagerSelection==='function'){
 const mcdNegOriginalSyncManagerSelection=syncManagerSelection;
 syncManagerSelection=function(manager,source){
  mcdNegOriginalSyncManagerSelection(manager,source);
  const selector=document.getElementById('mcd-neg-manager');
  if(selector&&TRADE_SIMULATOR_DATA[manager]){selector.value=manager;renderNegotiationRoom();}
 };
}

'''


def integrate_template(template: str) -> str:
    """Rehouse completed trades and place discovery above the manual simulator."""
    old_tabs = '''<button class="transfer-subtab" type="button" onclick="showTransferSubtab('trades', this)">Trades</button>'''
    if template.count(old_tabs) != 1:
        raise RuntimeError('Transfer tab insertion point changed')
    template = template.replace(old_tabs, old_tabs + '''<button class="transfer-subtab" type="button" onclick="showTransferSubtab('history', this)">Trade History</button>''', 1)
    trade_card = '''<div class="card">__TRADE_SIMULATOR__</div>'''
    if template.count(trade_card) != 1:
        raise RuntimeError('Trade Lab insertion point changed')
    template = template.replace(trade_card, ROOM_HTML + '\n              ' + trade_card, 1)
    recent = '''<div class="card"><h2>Recent League Trades · GW__LATEST_TRANSFER_GW__</h2>'''
    start = template.find(recent)
    if start == -1:
        raise RuntimeError('Historic trades insertion point changed')
    end = template.find('''\n            </div>\n        </section>''', start)
    if end == -1:
        raise RuntimeError('Historic trades end anchor changed')
    history = template[start:end]
    if '__HISTORICAL_TRADES__' not in history or '__TRADES_TABLE__' not in history:
        raise RuntimeError('Trade archive contents unexpectedly changed')
    template = template[:start] + template[end:]
    anchor = '''<div class="transfer-subpanel" id="transfer-subpanel-trades">'''
    if template.count(anchor) != 1:
        raise RuntimeError('Trade pane insertion point changed')
    # Previous trade pane remains purely prospective; history gets its own subtab.
    end_anchor = '''\n        </section>'''
    trade_start = template.index(anchor)
    trade_end = template.index(end_anchor, trade_start)
    insertion = '''\n            <div class="transfer-subpanel" id="transfer-subpanel-history">\n              ''' + history + '''\n            </div>'''
    template = template[:trade_end] + insertion + template[trade_end:]
    nav = "['Trades & Trade Lab','transfers','transfers','trades'],"
    if template.count(nav) != 1:
        raise RuntimeError('Transfer sidebar insertion point changed')
    template = template.replace(nav, "['Trade Negotiation Room','transfers','transfers','trades'],\n  ['Trade History','transfers','transfers','history'],", 1)
    return template

__all__ = ['ROOM_HTML', 'CSS', 'JS', 'integrate_template']
