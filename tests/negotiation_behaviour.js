// Appended to the client script by test_trade_negotiation.py; also runnable in V8.
function assert(condition,message){if(!condition)throw new Error(message);}
assert(mcdNegClassify({value:90},{value:100},1,-.5).label==='Ambitious','Viewer receives upgrade');
assert(mcdNegClassify({value:100},{value:90},-.5,1).label==='Safe','Partner receives appealing offer');
assert(mcdNegClassify({value:100},{value:90},-.5,-.1)===null,'A partner fit loss is not Safe');
assert(mcdNegClassify({value:100},{value:100},0,0).label==='Even','Equal values are Even');
assert(mcdNegClassify({value:100},{value:60},0,1)===null,'Do not recommend severe overpayment');
const manager=Object.keys(TRADE_SIMULATOR_DATA)[0];
const offers=mcdNegDiscover(manager,'');
assert(offers.length>0,'Find offers');
for(const size of [1,2,3])assert(offers.slice(0,16).some(d=>d.give.length===size),'Show each package size early');
for(const deal of offers){
 assert(deal.give.length===deal.receive.length,'Equal numbers');
 assert(deal.give.map(p=>p.position).sort().join()===deal.receive.map(p=>p.position).sort().join(),'Position quotas');
 assert(new Set([...deal.give,...deal.receive].map(p=>p.id)).size===deal.give.length*2,'Distinct players');
 assert(deal.give.every(p=>TRADE_SIMULATOR_DATA[manager].includes(p)),'Viewer ownership');
 assert(deal.receive.every(p=>TRADE_SIMULATOR_DATA[deal.partner].includes(p)),'Partner ownership');
 const give=mcdNegTotal(deal.give,'value'),receive=mcdNegTotal(deal.receive,'value');
 if(deal.category==='Ambitious')assert(receive>give&&deal.fitA>0,'Ambition always benefits viewer');
 if(deal.category==='Safe')assert(give>receive&&deal.fitB>=0,'Safe gives partner value and fit');
}
for(const size of ['2','3']){
 const filtered=mcdNegDiscover(manager,'','',size);
 assert(filtered.length>0&&filtered.every(d=>d.give.length===Number(size)),'Size filter');
}
const safe=mcdNegDiscover(manager,'','Safe');
assert(safe.every(d=>d.category==='Safe'),'Category filter');
const partner=Object.keys(TRADE_SIMULATOR_DATA)[1];
assert(mcdNegDiscover(manager,partner).every(d=>d.partner===partner),'Partner filter');
assert(mcdNegDiscover(manager,manager).length===0,'No self trades');
assert(mcdNegDiscover('missing','').length===0,'Missing roster');
const packageDeal=offers.find(d=>d.give.length===3);
const card=mcdNegCard(packageDeal,0);
assert([...packageDeal.give,...packageDeal.receive].every(p=>card.includes(escapePlayerHTML(p.name))),'Display whole package');
