"""Discover position-compatible trade packages from the viewing manager's side.

The existing Trade Lab remains the authoritative manual deal builder. Suggestions
reuse its current ownership, valuation and projection payload; they never claim
that a manager will accept a proposed trade.
"""
from __future__ import annotations

ROOM_HTML = '''
<div class="card mcd-negotiation-room" id="mcd-negotiation-room">
  <div class="mcd-neg-header">
    <div><div class="eyebrow">THE NEGOTIATION ROOM</div><h2>Find a deal that works for both sides</h2>
      <p class="card-description">Explore one-, two- and three-player swaps using current rosters and Trade Lab values. Every package preserves both squads' position quotas.</p></div>
  </div>
  <div class="mcd-neg-controls">
    <label>My team<select id="mcd-neg-manager" onchange="renderNegotiationRoom()" aria-label="Your team for trade discovery"></select></label>
    <label>Potential trade partner<select id="mcd-neg-partner" onchange="renderNegotiationRoom()" aria-label="Potential trade partner"><option value="">All other managers</option></select></label>
    <label>Deal type<select id="mcd-neg-filter" onchange="renderNegotiationRoom()"><option value="">All proposals</option><option value="Safe">Safe</option><option value="Even">Even</option><option value="Ambitious">Ambitious</option></select></label>
    <label>Package size<select id="mcd-neg-size" onchange="renderNegotiationRoom()"><option value="">All sizes</option><option value="2">2 for 2</option><option value="3">3 for 3</option><option value="1">1 for 1</option></select></label>
  </div>
  <div class="mcd-neg-key">
    <div><strong>Safe</strong><span>Likely to appeal to the other manager: they gain model value and do not lose projected squad fit.</span></div>
    <div><strong>Even</strong><span>Very close overall value, with a plausible gain in positional fit for each manager.</span></div>
    <div><strong>Ambitious</strong><span>You ask for more value than you give. An upgrade for your team that may need a counteroffer to persuade the other manager.</span></div>
  </div>
  <p class="card-description">Labels are from My team's perspective. Safe means a stronger modelled case for acceptance, not a measured probability or a guarantee.</p>
  <div id="mcd-neg-results" aria-live="polite"><div class="notice">Choose your team to discover trades.</div></div>
</div>
'''

CSS = r'''
.mcd-negotiation-room{margin-bottom:16px}.mcd-neg-header{display:flex;justify-content:space-between;gap:15px;align-items:start}
.mcd-neg-controls{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin:15px 0}
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
function mcdNegClassify(a,b,fitA,fitB){
 const va=mcdNegNum(a.value),vb=mcdNegNum(b.value),avg=Math.max(1,(va+vb)/2);
 const fair=Math.max(0,Math.min(100,100-Math.abs(va-vb)/avg*100));
 // a is always what the viewer GIVES; b is what the viewer RECEIVES.
 const edge=(vb-va)/avg;
 if(fair<65)return null;
 if(edge<=-.04&&fitB>=0&&fitA>=-.6)return {label:'Safe',fair};
 if(Math.abs(edge)<.04&&fitA>=-.6&&fitB>=-.6)return {label:'Even',fair};
 if(edge>=.04&&fitA>0&&fitB>=-1.5)return {label:'Ambitious',fair};
 return null;
}
function mcdNegTotal(players,field){return players.reduce((s,p)=>s+mcdNegNum(p[field]),0);}
function mcdNegBundleFit(manager,outgoing,incoming){
 const ids=new Set(outgoing.map(p=>p.id)),roster=(TRADE_SIMULATOR_DATA[manager]||[]).filter(p=>!ids.has(p.id));
 let fit=0;
 for(const pos of ['GKP','DEF','MID','FWD']){
  const give=outgoing.filter(p=>p.position===pos),receive=incoming.filter(p=>p.position===pos);if(!give.length)continue;
  const other=roster.filter(p=>p.position===pos),baseline=other.length?mcdNegTotal(other,'projection')/other.length:0;
  fit+=(mcdNegTotal(receive,'projection')-mcdNegTotal(give,'projection'))*1.45
     +(mcdNegTotal(receive,'form')-mcdNegTotal(give,'form'))*.22
     +(mcdNegTotal(receive,'projection')-baseline*give.length)*.13
     -Math.max(0,mcdNegTotal(give,'importance')-mcdNegTotal(receive,'importance'))*.035
     -(other.length<2?.2:0);
 }
 return fit/outgoing.length;
}
function mcdNegBundles(players,size){
 const groups=new Map();
 function visit(start,picks){
  if(picks.length===size){const key=picks.map(p=>p.position).sort().join('|');if(!groups.has(key))groups.set(key,[]);groups.get(key).push({players:picks,value:mcdNegTotal(picks,'value')});return;}
  for(let i=start;i<=players.length-(size-picks.length);i++)visit(i+1,[...picks,players[i]]);
 }
 visit(0,[]);return groups;
}
const mcdNegCache=new Map();
function mcdNegDiscover(manager,partner,categoryFilter='',sizeFilter=''){
 const cacheKey=JSON.stringify([manager,partner,categoryFilter,sizeFilter]);if(mcdNegCache.has(cacheKey))return mcdNegCache.get(cacheKey);
 const managers=partner?[partner]:Object.keys(TRADE_SIMULATOR_DATA||{}).filter(name=>name!==manager),buckets={1:[],2:[],3:[]};
 for(const size of [2,3,1]){
  if(sizeFilter&&size!==Number(sizeFilter))continue;
  const mine=mcdNegBundles(TRADE_SIMULATOR_DATA[manager]||[],size);
  for(const other of managers){if(other===manager)continue;
   const theirs=mcdNegBundles(TRADE_SIMULATOR_DATA[other]||[],size),candidates=[];
   for(const [signature,gives] of mine){const receives=theirs.get(signature)||[];
    for(const a of gives)for(const b of receives){
     if(Math.abs(a.value-b.value)/Math.max(1,(a.value+b.value)/2)>.35)continue;
     const fitA=mcdNegBundleFit(manager,a.players,b.players),fitB=mcdNegBundleFit(other,b.players,a.players);
     const category=mcdNegClassify(a,b,fitA,fitB);if(!category||(categoryFilter&&category.label!==categoryFilter))continue;
     const quality=Math.max(0,Math.min(100,category.fair*.67+Math.max(-10,Math.min(10,fitA+fitB))*2.2+((fitA>=0&&fitB>=0)?12:0)));
     candidates.push({manager,partner:other,give:a.players,receive:b.players,category:category.label,fair:category.fair,quality,fitA,fitB});
    }
   }
   candidates.sort((a,b)=>b.quality-a.quality||b.fair-a.fair);
   // Retain distinct packages per category, so the filters cannot be crowded out.
   const counts=new Map(),usage=new Map();
   for(const deal of candidates){const count=counts.get(deal.category)||0;if(count>=8)continue;
    const key=deal.category+'|'+deal.give.map(p=>p.id).sort().join(',');if((usage.get(key)||0)>=2)continue;
    counts.set(deal.category,count+1);usage.set(key,(usage.get(key)||0)+1);buckets[size].push(deal);
   }
  }
  buckets[size].sort((a,b)=>b.quality-a.quality||a.partner.localeCompare(b.partner));
 }
 // Round-robin sizes makes 2-for-2 and 3-for-3 visible on the first screen.
 const selected=[];for(let i=0;selected.length<144;i++){let added=false;for(const size of [2,3,1])if(selected.length<144&&buckets[size][i]){selected.push(buckets[size][i]);added=true;}if(!added)break;}
 mcdNegCache.set(cacheKey,selected);return selected;
}
function mcdNegExplain(deal){
 const value=mcdNegTotal(deal.receive,'value')-mcdNegTotal(deal.give,'value'),projection=mcdNegTotal(deal.receive,'projection')-mcdNegTotal(deal.give,'projection');
 const signed=v=>(v>=0?'+':'')+v.toFixed(1);
 const reason=deal.category==='Safe'?'The other manager gains value with non-negative modelled fit, making this a stronger acceptance candidate.':deal.category==='Ambitious'?'You receive the value upgrade; the other manager may want a sweeter offer.':'Similar package values give both managers a balanced starting point.';
 return reason+' Your value change: '+signed(value)+'. Next-GW projection change: '+deal.manager+' '+signed(projection)+' pts; '+deal.partner+' '+signed(-projection)+' pts.';
}
function mcdNegCard(deal,index){
 const e=escapePlayerHTML,players=list=>list.map(p=>'<strong>'+e(p.name)+'</strong><small>'+e(p.position)+' · '+mcdNegNum(p.value).toFixed(1)+' value · '+mcdNegNum(p.projection).toFixed(1)+' projected</small>').join('');
 return '<article class="mcd-neg-offer">'
  +'<div class="mcd-neg-offer-header"><div><strong>'+e(deal.manager)+' ↔ '+e(deal.partner)+'</strong><div class="mcd-neg-notes">'+deal.give.length+' for '+deal.receive.length+'</div></div><span class="mcd-neg-badge '+deal.category.toLowerCase()+'">'+deal.category+'</span></div>'
  +'<div class="mcd-neg-exchange"><div><small>You give</small>'+players(deal.give)+'</div><span>⇄</span><div><small>You receive from '+e(deal.partner)+'</small>'+players(deal.receive)+'</div></div>'
  +'<div class="mcd-neg-metrics"><span>Your outgoing value<b>'+mcdNegTotal(deal.give,'value').toFixed(1)+'</b></span><span>Your incoming value<b>'+mcdNegTotal(deal.receive,'value').toFixed(1)+'</b></span><span>Value fairness<b>'+deal.fair.toFixed(0)+'/100</b></span></div>'
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
 mcdNegOffers=mcdNegDiscover(manager,partner.value,filter.value,document.getElementById('mcd-neg-size')?.value||'');
 const shown=mcdNegOffers.slice(0,16);
 results.innerHTML=shown.length?'<p class="card-description">'+mcdNegOffers.length+' model-compatible offer(s) found. Showing '+shown.length+'; proposals are not guaranteed to be accepted.</p>'+shown.map(mcdNegCard).join(''):
   '<div class="notice">No deals match these filters right now. Try another manager or switch to all proposal types.</div>';
 if(mcdNegOffers.length>16)results.innerHTML+='<div class="mcd-neg-more"><button type="button" class="mcd-neg-action" onclick="mcdNegShowMore()">Show more offers</button></div>';
}
function mcdNegShowMore(){const results=document.getElementById('mcd-neg-results');if(!results)return;results.innerHTML='<p class="card-description">'+mcdNegOffers.length+' proposals.</p>'+mcdNegOffers.map(mcdNegCard).join('');}
function mcdNegLoadDeal(index){
 const deal=mcdNegOffers[index];if(!deal)return;
 const a=document.getElementById('trade-sim-manager-a'),b=document.getElementById('trade-sim-manager-b');if(!a||!b)return;
 mcdOpenTradeLab();
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
 if(checks.every(c=>c[0])){
  const va=mcdNegTotal(outgoing,'value'),vb=mcdNegTotal(incoming,'value');
  const fA=mcdNegBundleFit(a.value,outgoing,incoming),fB=mcdNegBundleFit(b.value,incoming,outgoing),label=mcdNegClassify({value:va},{value:vb},fA,fB);
  const fair=Math.max(0,100-Math.abs(va-vb)/Math.max(1,(va+vb)/2)*100),tag=label?label.label:'Outside suggested range';
  html+='<p class="mcd-neg-notes"><strong>Negotiation profile for '+escapePlayerHTML(a.value)+': '+escapePlayerHTML(tag)+'</strong> · Value fairness '+fair.toFixed(0)+'/100. '+(label?escapePlayerHTML(mcdNegExplain({give:outgoing,receive:incoming,manager:a.value,partner:b.value,category:tag})):'The model does not find a strong enough case to recommend this package.')+'</p>';
 }
 html+='<p class="card-description">Draft roster and position checks only. The dashboard cannot certify live league trade windows, pending transactions, other managers\' consent or official processing.</p></section>';
 result.insertAdjacentHTML('beforeend',html);
}
// Preserve all original Trade Lab narration, then append deterministic checks.
const mcdOriginalEvaluateTradeSimulator=evaluateTradeSimulator;
evaluateTradeSimulator=function(){mcdOriginalEvaluateTradeSimulator();mcdNegAuditTrade();};
function mcdOpenTradeLab(){
 showPage('transfers');
 showTransferSubtab('lab',document.querySelector('#page-transfers .transfer-subtab[onclick*="lab"]'));
 if(typeof mcdNavSync==='function')mcdNavSync();
}
const mcdOriginalDraftScoutTrade=draftScoutTrade;
draftScoutTrade=function(playerId){mcdOriginalDraftScoutTrade(playerId);
 const p=playerSearchData.find(r=>Number(r.id)===Number(playerId)),mine=currentMyTeamManager();
 if(p&&mine&&p.fantasy_team&&p.fantasy_team!=='Free Agent'&&p.fantasy_team!==mine){mcdOpenTradeLab();document.querySelector('.trade-simulator')?.scrollIntoView({behavior:'smooth',block:'start'});}
};
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
    """Give discovery, the manual simulator and completed trades their own tabs."""
    old_tabs = '''<button class="transfer-subtab" type="button" onclick="showTransferSubtab('trades', this)">Trades</button>'''
    if template.count(old_tabs) != 1:
        raise RuntimeError('Transfer tab insertion point changed')
    template = template.replace(old_tabs, old_tabs.replace('>Trades<', '>Negotiation Room<') + '''<button class="transfer-subtab" type="button" onclick="showTransferSubtab('lab', this)">Trade Lab</button><button class="transfer-subtab" type="button" onclick="showTransferSubtab('history', this)">Trade History</button>''', 1)
    trade_card = '''<div class="card">__TRADE_SIMULATOR__</div>'''
    if template.count(trade_card) != 1:
        raise RuntimeError('Trade Lab insertion point changed')
    template = template.replace(trade_card, ROOM_HTML, 1)
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
    insertion = '''\n            <div class="transfer-subpanel" id="transfer-subpanel-lab">''' + trade_card + '''</div>\n            <div class="transfer-subpanel" id="transfer-subpanel-history">\n              ''' + history + '''\n            </div>'''
    template = template[:trade_end] + insertion + template[trade_end:]
    nav = "['Trades & Trade Lab','transfers','transfers','trades'],"
    if template.count(nav) != 1:
        raise RuntimeError('Transfer sidebar insertion point changed')
    template = template.replace(nav, "['Trade Negotiation Room','transfers','transfers','trades'],\n  ['Trade Lab','transfers','transfers','lab'],\n  ['Trade History','transfers','transfers','history'],", 1)
    return template

__all__ = ['ROOM_HTML', 'CSS', 'JS', 'integrate_template']
