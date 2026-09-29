(() => {
  'use strict';
  const $=id=>document.getElementById('calendar-'+id);
  if(!$('grid'))return;
  const day=date=>new Intl.DateTimeFormat('en-CA',{timeZone:'Europe/London',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date(date));
  const valid=date=>date&&!Number.isNaN(Date.parse(date));
  const season=date=>Number(date.slice(0,4))-(Number(date.slice(5,7))<8?1:0);
  const pl=typeof PL_FIXTURE_BROWSER==='undefined'?{}:PL_FIXTURE_BROWSER;
  const stats=typeof MCD_MATCHUP_STATS==='undefined'?{}:MCD_MATCHUP_STATS;
  const schedule=JSON.parse(document.getElementById('calendar-schedule').textContent);
  const events=[],starts={},seen=new Set();
  for(const [gw,rows] of Object.entries(pl)){
    const dates=rows.map(r=>r.kickoff).filter(valid).sort();starts[gw]=dates[0]||null;
    for(const r of rows)events.push({kind:'pl',gw,home:r.home,away:r.away,date:valid(r.kickoff)?day(r.kickoff):null,kickoff:r.kickoff,finished:!!r.finished,score:r.finished?r.score:null});
  }
  function fantasy(gw,home,away,finished,score){
    const key=JSON.stringify([String(gw),...[home,away].sort()]);if(seen.has(key))return;seen.add(key);
    events.push({kind:'fantasy',gw,home,away,finished,score,date:starts[gw]?day(starts[gw]):null});
  }
  for(const [manager,data] of Object.entries(stats))for(const g of data.games||[])fantasy(g.gw,manager,g.opponent,true,g.points+' – '+g.against);
  for(const [gw,rows] of Object.entries(schedule))for(const r of rows)fantasy(gw,r.team1,r.team2,!!r.finished,null);
  // Older published dashboards contain the next fixtures in their planner cards.
  document.querySelectorAll('.fixture-planner-card').forEach(card=>{
    const gw=card.querySelector('.fixture-planner-gw')?.textContent.match(/\d+/)?.[0];
    const teams=[...card.querySelectorAll('.fixture-planner-match strong')].map(n=>n.textContent);
    if(gw&&teams.length===2)fantasy(gw,...teams,false,null);
  });
  const today=day(new Date()),current=season(today);
  const seasons=[...new Set([current,...events.filter(e=>e.date).map(e=>season(e.date))])].sort((a,b)=>b-a);
  seasons.forEach(y=>$('season').add(new Option(y+'/'+String(y+1).slice(-2),String(y))));
  let year=current,month=7,selectedDay=null;
  const node=(tag,text,cls)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n;};
  function reset(){const m=Number(today.slice(5,7))-1;year=current;month=m===5||m===6?16:m<7?m+12:m;$('season').value=String(year);selectedDay=null;render();}
  function teams(){const old=$('team').value,kind=$('kind').value;$('team').replaceChildren(new Option('All teams',''));
    for(const k of ['pl','fantasy']){if(kind!=='all'&&kind!==k)continue;const group=node('optgroup');group.label=k==='pl'?'Premier League':'Fantasy league';[...new Set(events.filter(e=>e.kind===k).flatMap(e=>[e.home,e.away]))].sort().forEach(t=>group.append(new Option(t,k+':'+t)));$('team').append(group);}
    if([...$('team').options].some(o=>o.value===old))$('team').value=old;
  }
  function matches(e){return ($('kind').value==='all'||e.kind===$('kind').value)&&(!$('team').value||[e.kind+':'+e.home,e.kind+':'+e.away].includes($('team').value))&&($('status').value==='all'||e.finished===($('status').value==='finished'));}
  function eventRow(e){const row=node('article',undefined,'calendar-event '+e.kind);row.append(node('small',(e.kind==='pl'?'Premier League':'Fantasy')+' · GW'+e.gw+' · '+(e.finished?'Full time':e.kind==='fantasy'?'Gameweek matchup':valid(e.kickoff)?new Intl.DateTimeFormat('en-GB',{timeZone:'Europe/London',hour:'2-digit',minute:'2-digit'}).format(new Date(e.kickoff)):'Time TBC')));row.append(node('strong',e.home+' '+(e.finished?(e.score||'Result unavailable'):'vs')+' '+e.away));return row;}
  function render(){
    const first=new Date(Date.UTC(year,month,1)),prefix=first.toISOString().slice(0,7),count=new Date(Date.UTC(year,month+1,0)).getUTCDate();
    $('month').textContent=new Intl.DateTimeFormat('en-GB',{month:'long',year:'numeric',timeZone:'UTC'}).format(first);$('prev').disabled=month===7;$('next').disabled=month===16;
    const rows=events.filter(e=>e.date?.startsWith(prefix)&&matches(e)).sort((a,b)=>(a.date+(a.kickoff||'')).localeCompare(b.date+(b.kickoff||'')));
    $('grid').replaceChildren(...['Mon','Tue','Wed','Thu','Fri','Sat','Sun'].map(d=>node('span',d,'calendar-weekday')));
    for(let i=0;i<(first.getUTCDay()+6)%7;i++)$('grid').append(node('span'));
    for(let d=1;d<=count;d++){const date=prefix+'-'+String(d).padStart(2,'0'),list=rows.filter(e=>e.date===date),b=node('button',undefined,'calendar-day');b.type='button';b.append(node('b',String(d)));b.setAttribute('aria-label',date+', '+list.length+' matches');b.setAttribute('aria-pressed',String(selectedDay===date));if(date===today)b.setAttribute('aria-current','date');for(const kind of ['pl','fantasy']){const n=list.filter(e=>e.kind===kind).length;if(n)b.append(node('small',n+' '+(kind==='pl'?'PL':'Fantasy'),kind));}b.onclick=()=>{selectedDay=selectedDay===date?null:date;render();};$('grid').append(b);}
    $('agenda').replaceChildren();$('empty').hidden=rows.length>0;
    if(selectedDay){const clear=node('button','Show whole month');clear.onclick=()=>{selectedDay=null;render();};$('agenda').append(clear);}
    const shown=rows.filter(e=>!selectedDay||e.date===selectedDay);let last='';
    for(const e of shown){if(last!==e.date){$('agenda').append(node('h3',new Intl.DateTimeFormat('en-GB',{weekday:'long',day:'numeric',month:'long',timeZone:'UTC'}).format(new Date(e.date+'T12:00:00Z'))));last=e.date;}$('agenda').append(eventRow(e));}
    if(selectedDay&&!shown.length)$('agenda').append(node('p','No matches on this day match your filters.'));
    const undated=events.filter(e=>!e.date&&matches(e));$('undated').hidden=!undated.length;$('undated').querySelector('div').replaceChildren(...undated.map(eventRow));
  }
  $('prev').onclick=()=>{if(month>7)month--;selectedDay=null;render();};$('next').onclick=()=>{if(month<16)month++;selectedDay=null;render();};$('today').onclick=reset;
  $('season').onchange=()=>{year=Number($('season').value);selectedDay=null;render();};
  for(const id of ['kind','team','status'])$(id).onchange=()=>{if(id==='kind')teams();selectedDay=null;render();};
  teams();reset();
})();
