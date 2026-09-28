/* Browser-only comparisons and lineup drafts. Official squad data stays intact. */
(() => {
  'use strict';
  const $=id=>document.getElementById(id);
  const el=(tag,text,cls)=>{const n=document.createElement(tag);if(text!=null)n.textContent=text;if(cls)n.className=cls;return n;};
  const button=(text,action)=>{const b=el('button',text,'mcd-player-tool');b.type='button';b.addEventListener('click',action);return b;};
  const players=()=>typeof playerSearchData==='undefined'?[]:playerSearchData;
  const player=id=>players().find(p=>String(p.id)===String(id));
  const numeric=v=>v!==null&&v!==undefined&&v!==''&&Number.isFinite(Number(v));
  const format=v=>numeric(v)?Number(v).toLocaleString('en-GB',{maximumFractionDigits:1}):'—';
  let selected=[],tray,dialog,options,table,status,trayStatus;
  function add(id) {
    id=String(id);if(!player(id))return false;
    if(selected.includes(id)){announce('Already in your comparison.');return false;}
    if(selected.length>=4){announce('You can compare up to four players. Remove one to add another.');return false;}
    selected.push(id);renderCompare();announce(player(id).name+' added to comparison.');return true;
  }
  function announce(message){if(status)status.textContent=message;if(trayStatus)trayStatus.textContent=message;}
  function remove(id){selected=selected.filter(p=>p!==String(id));renderCompare();}
  function compareButton(id) {const b=button(selected.includes(String(id))?'Added to comparison':'Compare',()=>add(id));b.dataset.comparePlayer=String(id);return b;}
  function renderOptions() {
    options.replaceChildren();const q=$('mcd-compare-find').value.trim().toLowerCase();if(!q)return;
    players().filter(p=>[p.name,p.team,p.position].join(' ').toLowerCase().includes(q)).slice(0,12).forEach(p=>{
      const b=button(p.name+' · '+p.position+' · '+p.team,()=>add(p.id));b.disabled=selected.includes(String(p.id))||selected.length>=4;options.append(b);
    });
    if(!options.children.length)options.append(el('p','No matching players.'));
  }
  function renderCompare() {
    if(!tray)return;
    tray.replaceChildren(el('strong','Compare players · '+selected.length+'/4'));
    selected.forEach(id=>{const b=button(player(id).name+' ×',()=>remove(id));b.setAttribute('aria-label','Remove '+player(id).name+' from comparison');tray.append(b);});
    tray.append(button('Open comparison',()=>{renderCompare();if(!dialog.open)dialog.showModal();}));
    tray.append(button('Clear',()=>{selected=[];renderCompare();announce('Comparison cleared.');}));
    trayStatus=el('p');trayStatus.setAttribute('role','status');tray.append(trayStatus);tray.hidden=!selected.length;
    document.querySelectorAll('[data-compare-player]').forEach(b=>{b.textContent=selected.includes(b.dataset.comparePlayer)?'Added to comparison':'Compare';});
    table.replaceChildren();const chosen=selected.map(player).filter(Boolean);
    if(chosen.length<2)table.append(el('p','Choose two to four players to compare.'));
    if(chosen.length){
      const grid=el('table'),head=el('thead'),row=el('tr');row.append(el('th','Metric'));
      chosen.forEach(p=>{const th=el('th',p.name);th.scope='col';th.append(el('small',p.position+' · '+p.team),button('Remove',()=>remove(p.id)));row.append(th);});head.append(row);grid.append(head);
      const body=el('tbody');
      const metrics=[['Fantasy team',p=>p.fantasy_team||'Free Agent'],['Season points',p=>format(p.total_points)],['Minutes',p=>format(p.minutes)],
        ['Points per game',p=>format(p.points_per_game)],['Form',p=>format(p.form)],['Goals',p=>format(p.goals)],['Assists',p=>format(p.assists)],
        ['Clean sheets',p=>format(p.clean_sheets)],['Saves',p=>format(p.saves)],['Bonus points',p=>format(p.bonus)],
        ['Player rating / 100',p=>format(p.player_rating)],['Next 3 GW projected points',p=>format(p.next3_projected_points)],
        ['Availability',p=>({a:'Available',d:'Doubtful',i:'Injured',s:'Suspended',u:'Unavailable',n:'Unavailable'})[p.availability?.status]||'Unknown'],
        ['Availability news',p=>p.availability?.news||'No news captured'],['Upcoming fixtures',p=>(p.next_fixtures||[]).slice(0,3).map(f=>'GW'+f.gw+': '+(f.label||'—')).join(' · ')||'No fixtures captured']];
      metrics.forEach(([label,value])=>{const tr=el('tr'),th=el('th',label);th.scope='row';tr.append(th);chosen.forEach(p=>tr.append(el('td',value(p))));body.append(tr);});grid.append(body);table.append(grid);
    }
    renderOptions();
  }
  function counts(rows){const c={GKP:0,DEF:0,MID:0,FWD:0};rows.forEach(p=>{if(p.position in c)c[p.position]++;});return c;}
  function valid(rows) {
    if(rows.length!==11||new Set(rows.map(p=>String(p.id))).size!==11||rows.some(p=>p.id==null))return false;
    const c=counts(rows);return c.GKP===1&&c.DEF>=3&&c.DEF<=5&&c.MID>=2&&c.MID<=5&&c.FWD>=1&&c.FWD<=3&&Object.values(c).reduce((a,b)=>a+b,0)===11;
  }
  function swap(state,outId,inId) {
    const out=state.starters.findIndex(p=>String(p.id)===String(outId)),incoming=state.bench.findIndex(p=>String(p.id)===String(inId));
    if(out<0||incoming<0)return null;
    const starters=[...state.starters],bench=[...state.bench];[starters[out],bench[incoming]]=[bench[incoming],starters[out]];
    if(!valid(starters)||new Set([...starters,...bench].map(p=>String(p.id))).size!==starters.length+bench.length)return null;
    return {starters,bench};
  }
  const drafts=new Map();
  const total=rows=>rows.every(p=>numeric(p.projection))?rows.reduce((sum,p)=>sum+Number(p.projection),0):null;
  function attachLineup() {
    const manager=$('war-room-manager')?.value,data=typeof MANAGER_WAR_ROOM==='undefined'?null:MANAGER_WAR_ROOM[manager];
    const panel=$('war-room-content')?.querySelector('.war-room-team-panel');if(!panel||!data||data.warning)return;
    const original=data.you,roster=[...(original.starters||[]),...(original.bench||[])];
    const key=JSON.stringify([manager,data.gw,roster.map(p=>[p.id,p.position,p.projection])]);
    if(!drafts.has(key))drafts.set(key,{starters:[...(original.starters||[])],bench:[...(original.bench||[])]});
    let draft=drafts.get(key);
    const editor=el('div',null,'mcd-lineup-editor');editor.id='mcd-lineup-editor';
    editor.append(el('strong','Plan your starting XI'),el('p','Swap a starter with a bench player. This draft stays for this visit; make official changes in FPL.'));
    const summary=el('p',null,'mcd-lineup-summary'),controls=el('div',null,'mcd-lineup-controls');
    const outgoing=el('select'),incoming=el('select');outgoing.id='mcd-lineup-out';incoming.id='mcd-lineup-in';
    const outLabel=el('label','Move to bench'),inLabel=el('label','Bring into XI');outLabel.append(outgoing);inLabel.append(incoming);
    const message=el('p');message.id='mcd-lineup-status';message.setAttribute('role','status');
    const apply=button('Swap players',()=>{
      const next=swap(draft,outgoing.value,incoming.value);if(!next){message.textContent='That swap would create an invalid formation.';return;}
      const out=draft.starters.find(p=>String(p.id)===outgoing.value),into=draft.bench.find(p=>String(p.id)===incoming.value);
      draft=next;drafts.set(key,draft);draw();message.textContent=into.name+' starts; '+out.name+' moves to the bench.';
    });apply.id='mcd-lineup-swap';
    const reset=button('Reset to optimal XI',()=>{draft={starters:[...original.starters],bench:[...original.bench]};drafts.set(key,draft);draw();message.textContent='Restored the original optimal XI.';});reset.id='mcd-lineup-reset';
    controls.append(outLabel,inLabel,apply,reset);editor.append(summary,controls,el('p','Valid XI: 1 goalkeeper, 3–5 defenders, 2–5 midfielders, 1–3 forwards; 11 players in total.'),message);
    function incomingOptions(){
      incoming.replaceChildren();draft.bench.forEach(p=>{const option=new Option(p.name+' · '+p.position,String(p.id));option.disabled=!swap(draft,outgoing.value,p.id);if(option.disabled)option.text+=' — invalid formation';incoming.add(option);});
      const allowed=[...incoming.options].find(o=>!o.disabled);incoming.value=allowed?.value||'';apply.disabled=!allowed;
    }
    function draw(){
      const c=counts(draft.starters),formation=[c.DEF,c.MID,c.FWD].join('-'),projection=total(draft.starters),baseline=total(original.starters);
      const delta=projection===null||baseline===null?null:projection-baseline;
      summary.textContent=formation+' · '+format(projection)+' projected points'+(delta===null?'':' · '+(delta>=0?'+':'')+format(delta)+' vs optimal XI');
      outgoing.replaceChildren(...draft.starters.map(p=>new Option(p.name+' · '+p.position,String(p.id))));incomingOptions();
      const holder=el('div');holder.innerHTML=warRoomFormation(draft.starters,draft.bench,formation,'you',manager);
      const replacement=holder.firstElementChild;panel.replaceChildren(...replacement.childNodes);panel.prepend(editor);
      reset.disabled=draft.starters.every((p,i)=>String(p.id)===String(original.starters[i]?.id));
    }
    outgoing.addEventListener('change',incomingOptions);
    if(!valid(draft.starters)||roster.length!==15||new Set(roster.map(p=>String(p.id))).size!==15){editor.replaceChildren(el('p','Lineup editing needs a complete 15-player squad with a valid starting XI.'));panel.prepend(editor);return;}
    draw();
    const wrap=$('war-room-content');
    const forecast=wrap.querySelector('.war-room-matchup')?.parentElement;
    if(forecast)forecast.prepend(el('p','Original optimal-XI forecast. Probabilities and analysis below use the original lineup.','card-description'));
    const description=wrap.querySelector('.war-room-pitch-wrap')?.previousElementSibling;
    if(description?.classList.contains('card-description'))description.textContent='Your lineup draft and the opponent’s optimal projected XI. Click a player for details or comparison.';
  }
  function init(){
    const host=document.querySelector('.app-shell')||document.body;
    tray=el('aside',null,'mcd-compare-tray');tray.id='mcd-compare-tray';tray.setAttribute('aria-label','Player comparison tray');host.append(tray);
    dialog=el('dialog',null,'mcd-comparison');dialog.id='mcd-comparison';dialog.setAttribute('aria-labelledby','mcd-comparison-title');
    const header=el('header'),title=el('h2','Player comparison');title.id='mcd-comparison-title';header.append(title,button('Close',()=>dialog.close()));dialog.append(header);
    const label=el('label','Add a player');label.htmlFor='mcd-compare-find';const input=el('input');input.id='mcd-compare-find';input.type='search';input.placeholder='Search name, club or position';input.addEventListener('input',renderOptions);
    options=el('div',null,'mcd-compare-options');table=el('div',null,'mcd-compare-scroll');status=el('p');status.setAttribute('role','status');
    dialog.append(label,input,options,status,el('p','Season statistics and projections use the current dashboard snapshot. Projections are estimates.'),table);host.append(dialog);
    const launch=button('Compare players',()=>{renderCompare();dialog.showModal();});$('player-search')?.parentElement?.append(launch);
    if(typeof renderPlayerDirectoryCard==='function'){
      const original=window.renderPlayerDirectoryCard;
      window.renderPlayerDirectoryCard=function(p){return original(p).replace(/<\/div>\s*$/, '<button type="button" class="mcd-player-tool" data-compare-player="'+Number(p.id)+'">Compare</button></div>');};
      document.addEventListener('click',event=>{const b=event.target.closest('[data-compare-player]');if(b&&!b.dataset.boundCompare)add(b.dataset.comparePlayer);});
      const originalButton=compareButton;
      window.McDraftCompare.button=id=>{const b=originalButton(id);b.dataset.boundCompare='true';return b;};
      window.filterPlayers?.();
    }
    if(typeof renderManagerWarRoom==='function'){const original=window.renderManagerWarRoom;window.renderManagerWarRoom=function(){const result=original.apply(this,arguments);attachLineup();return result;};}
    if(typeof showWarRoomPlayer==='function'){const original=window.showWarRoomPlayer;window.showWarRoomPlayer=function(id,side){const result=original.apply(this,arguments);if(player(id))$('war-room-player-detail')?.append(window.McDraftCompare.button(id));return result;};}
    renderCompare();window.renderManagerWarRoom?.();
  }
  window.McDraftCompare={add,remove,button:compareButton,ids:()=>[...selected]};
  window.McDraftLineup={valid,swap};
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();
