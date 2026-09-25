/* Shares are editable text snapshots. Opening a preview never sends a message. */
(() => {
  const el=id=>document.getElementById('chat-'+id);
  if(!el('share-tools'))return;
  const num=value=>Number.isFinite(Number(value))?Number(value).toFixed(1):'unavailable';
  const players=()=>typeof playerSearchData==='undefined'?[]:playerSearchData;
  const stamp=()=> 'Shared from the current McDraft dashboard · '+new Date().toLocaleDateString();
  function tradeText(deal){
    const list=items=>items.map(p=>p.name+' ('+p.position+')').join(', ');
    return ['TRANSFER PROPOSAL · '+deal.give.length+' for '+deal.receive.length,
      deal.manager+' gives: '+list(deal.give),deal.partner+' gives: '+list(deal.receive),
      (deal.category?deal.category+' from '+deal.manager+"’s perspective. ":'')+'Hypothetical offer, not an accepted trade.',stamp()].join('\n');
  }
  function playerText(p){
    return [(p.fantasy_team==='Free Agent'?'FREE AGENT':'PLAYER WATCH')+' · '+p.name,
      [p.position,p.team,p.fantasy_team||'Ownership unavailable'].filter(Boolean).join(' · '),
      'Season points: '+(p.total_points??p.points??'unavailable')+' · Form: '+num(p.form),
      'Model value: '+num(p.player_value),stamp()].join('\n');
  }
  function results(gw){
    const data=typeof MCD_MATCHUP_STATS==='undefined'?{}:MCD_MATCHUP_STATS,seen=new Set(),items=[];
    for(const [manager,team] of Object.entries(data))for(const g of team.games||[]){
      if(gw!==undefined && Number(g.gw)!==Number(gw))continue;
      const key=JSON.stringify([g.gw,...[manager,g.opponent].sort()]);if(seen.has(key))continue;seen.add(key);
      items.push({label:'GW'+g.gw+' · '+manager+' '+g.points+'–'+g.against+' '+g.opponent,
        text:['MATCH RESULT · GW'+g.gw,manager+' '+g.points+'–'+g.against+' '+g.opponent,'Completed league fixture.',stamp()].join('\n'),gw:g.gw});
    }
    // Older generated pages expose completed scores in their results cards.
    if(!items.length)document.querySelectorAll('.results-slide.completed-gw[id^="results-gw-"]').forEach(slide=>{
      const week=Number(slide.id.replace('results-gw-',''));if(gw!==undefined&&week!==Number(gw))return;
      slide.querySelectorAll('.fixture').forEach(fixture=>{
        const names=Array.from(fixture.querySelectorAll('.fixture-manager'),e=>e.textContent.trim());
        const scores=Array.from(fixture.querySelectorAll('.fixture-score'),e=>e.textContent.trim());
        if(names.length!==2||scores.length!==2)return;
        const score=names[0]+' '+scores[0]+'\u2013'+scores[1]+' '+names[1];
        items.push({label:'GW'+week+' \u00b7 '+score,text:['MATCH RESULT \u00b7 GW'+week,score,'Completed league fixture.',stamp()].join('\n'),gw:week});
      });
    });
    return items.sort((a,b)=>b.gw-a.gw||a.label.localeCompare(b.label));
  }
  let items=[];
  function populate(gw){
    const kind=el('share-kind').value;
    if(kind==='result')items=results(gw);
    else if(kind==='trade'){
      const manager=typeof currentMyTeamManager==='function'?currentMyTeamManager():null;
      const deals=manager&&typeof mcdNegDiscover==='function'?mcdNegDiscover(manager,''):[];
      items=deals.map(d=>({label:d.give.map(p=>p.name).join(' + ')+' ↔ '+d.receive.map(p=>p.name).join(' + ')+' · '+d.partner,text:tradeText(d)}));
    }else items=players().filter(p=>kind==='player'||p.fantasy_team==='Free Agent')
      .sort((a,b)=>String(a.name).localeCompare(String(b.name))).map(p=>({label:p.name+' · '+p.position+' · '+p.team,text:playerText(p)}));
    el('share-item').replaceChildren(...items.map((item,i)=>new Option(item.label,String(i))));
    el('share-pick').disabled=!items.length;
    if(!items.length)el('share-item').add(new Option('No matching items in the captured data',''));
  }
  el('share-kind').addEventListener('change',()=>populate());
  el('share-tools').addEventListener('toggle',()=>{if(el('share-tools').open)populate();});
  el('share-pick').addEventListener('click',()=>{const item=items[Number(el('share-item').value)];if(item)window.mcdChatDraftShare(item.text);});
  window.mcdChatShareTrade=index=>{
    const deal=typeof mcdNegOffers==='undefined'?null:mcdNegOffers[index];if(deal)window.mcdChatDraftShare(tradeText(deal));
  };
  function button(label,action){const b=document.createElement('button');b.type='button';b.className='mcd-chat-share-button';b.textContent=label;b.addEventListener('click',action);return b;}
  // Decorate existing renderers without editing the preserved legacy stages.
  if(typeof window.renderPlayerDirectoryCard==='function'){
    const original=window.renderPlayerDirectoryCard;
    window.renderPlayerDirectoryCard=function(player){return original(player).replace(/<\/div>\s*$/, '<button type="button" class="mcd-chat-share-button" data-chat-player="'+Number(player.id)+'">Share player in chat</button></div>');};
    document.addEventListener('click',event=>{
      const target=event.target.closest('[data-chat-player]');if(!target)return;
      const p=players().find(p=>Number(p.id)===Number(target.dataset.chatPlayer));if(p)window.mcdChatDraftShare(playerText(p));
    });
    if(typeof filterPlayers==='function')filterPlayers();
  }
  document.querySelectorAll('[id^="results-gw-"]').forEach(slide=>{
    const match=slide.id.match(/^results-gw-(\d+)$/);if(!match)return;
    const matches=results(Number(match[1]));if(!matches.length)return;
    // Per-fixture buttons avoid sharing an entire gameweek as one long message.
    const controls=document.createElement('div');
    for(const item of matches)controls.appendChild(button('Share: '+item.label,()=>window.mcdChatDraftShare(item.text)));
    slide.appendChild(controls);
  });
  const lab=document.querySelector('.trade-simulator');
  if(lab)lab.appendChild(button('Share this trade in chat',()=>{
    const a=document.getElementById('trade-sim-manager-a')?.value,b=document.getElementById('trade-sim-manager-b')?.value;
    if(!a||!b||a===b)return;
    const give=selectedTradePlayers('a',a),receive=selectedTradePlayers('b',b);
    if(!give.length||!receive.length)return;
    window.mcdChatDraftShare(tradeText({manager:a,partner:b,give,receive}));
  }));
})();
