(() => {
  'use strict';
  const positions=['GKP','DEF','MID','FWD'],labels={GKP:'GK',DEF:'DEF',MID:'MID',FWD:'FWD'};
  const selected=new Set(positions),listeners=new Set();
  const allPlayers=()=>typeof playerSearchData==='undefined'?[]:playerSearchData;
  const playerById=id=>allPlayers().find(player=>Number(player.id)===Number(id));
  const allows=position=>selected.has(position);
  const isAll=()=>selected.size===positions.length;
  function buttons(){return `<span>Positions</span><button type="button" class="analytics-position-button" data-analytics-position="ALL">All</button>${positions.map(position=>`<button type="button" class="analytics-position-button" data-analytics-position="${position}">${labels[position]}</button>`).join('')}`;}
  function mount(){
    const managerCard=document.querySelector('.analytics-manager-filter-card');
    if(managerCard&&!document.getElementById('analytics-position-filter')){
      const controls=document.createElement('div');controls.id='analytics-position-filter';controls.className='analytics-position-filter';controls.setAttribute('role','group');controls.setAttribute('aria-label','Filter all position-aware Analytics charts');controls.innerHTML=buttons();
      const average=managerCard.querySelector('.analytics-average-toggle');managerCard.insertBefore(controls,average||null);
      const description=managerCard.querySelector('.analytics-manager-filter-head .card-description');
      if(description)description.textContent='Manager and position selections apply across every compatible Analytics chart. Charts containing only manager, fixture or league-level totals remain unchanged.';
    }
    sync();applyLegacyCharts();
  }
  function sync(){
    document.querySelectorAll('[data-analytics-position],[data-visual-position],[data-atlas-position-filter]').forEach(button=>{
      const position=button.dataset.analyticsPosition||button.dataset.visualPosition||button.dataset.atlasPositionFilter;
      const active=position==='ALL'?isAll():selected.has(position);button.classList.toggle('active',active);button.setAttribute('aria-pressed',String(active));
    });
  }
  function set(position){
    if(position==='ALL')positions.forEach(item=>selected.add(item));
    else if(isAll()){selected.clear();selected.add(position);}
    else if(selected.has(position)&&selected.size>1)selected.delete(position);else selected.add(position);
    sync();listeners.forEach(listener=>listener(new Set(selected)));applyLegacyCharts();
    document.dispatchEvent(new CustomEvent('mcdraft:positionchange',{detail:{positions:[...selected]}}));
  }
  function markLegacyPlayers(){
    document.querySelectorAll('#page-analytics [data-player-id]').forEach(element=>{const player=playerById(element.dataset.playerId);if(player?.position)element.dataset.analyticsPlayerPosition=player.position;});
  }
  function applyLegacyCharts(){
    markLegacyPlayers();
    const matches=element=>{
      const owner=element.dataset.playerOwner;
      const ownerAllowed=typeof analyticsManagerState==='undefined'||analyticsManagerState.visible.has(owner)||(owner==='Free agents'&&analyticsManagerState.includeFreeAgents);
      return ownerAllowed&&allows(element.dataset.analyticsPlayerPosition);
    };
    const setVisible=(element,visible)=>{
      element.hidden=!visible;element.toggleAttribute('hidden',!visible);element.setAttribute('aria-hidden',String(!visible));
      element.style.removeProperty('display');element.removeAttribute('data-position-hidden');
    };
    const showEmpty=(card,count)=>{
      const empty=card.querySelector('.analytics-player-chart-empty');
      if(empty){empty.hidden=count>0;empty.textContent='No players in this chart match the selected teams and positions.';}
    };
    // Select from the full roster before capping and scaling a leaderboard.
    // Own visibility here so older generated pages cannot leave eligible rows hidden.
    document.querySelectorAll('#page-analytics .analytics-player-bar-card').forEach(card=>{
      const rows=[...card.querySelectorAll('.analytics-player-bar')];
      const visible=rows.filter(matches).slice(0,Math.max(1,Number(card.dataset.playerLimit)||20));
      const scale=Math.max(1,...visible.map(row=>Math.abs(Number(row.dataset.playerValue)||0)));
      rows.forEach(row=>setVisible(row,visible.includes(row)));
      visible.forEach(row=>{
        const fill=row.querySelector('.analytics-bar-fill');
        if(fill)fill.style.width=Math.max(2,Math.abs(Number(row.dataset.playerValue)||0)/scale*100).toFixed(1)+'%';
      });
      showEmpty(card,visible.length);
    });
    document.querySelectorAll('#page-analytics .analytics-player-scatter').forEach(card=>{
      let count=0;
      card.querySelectorAll('.analytics-player-dot').forEach(dot=>{const visible=matches(dot);setVisible(dot,visible);if(visible)count++;});
      showEmpty(card,count);
    });
    document.querySelectorAll('.analytics-player-position-card [data-player-position].analytics-bar-row').forEach(row=>row.hidden=!allows(row.dataset.playerPosition));
    const count=document.getElementById('analytics-player-count');if(count){const ids=new Set([...document.querySelectorAll('#analytics-sub-player .analytics-player-dot:not([hidden]),#analytics-sub-player .analytics-player-bar:not([hidden])')].map(row=>row.dataset.playerId));count.textContent=`${ids.size} players in charts · ${isAll()?'all positions':[...selected].map(position=>labels[position]).join(', ')}`;}
  }
  function connectLegacyRenderers(){
    if(typeof window.applyPlayerAnalyticsFilter==='function'&&!window.applyPlayerAnalyticsFilter.__positionConnected){
      const original=window.applyPlayerAnalyticsFilter;
      const connected=function(...args){
        const result=original.apply(this,args);applyLegacyCharts();return result;
      };
      connected.__positionConnected=true;window.applyPlayerAnalyticsFilter=connected;
    }
    if(typeof window.ratingLabPool==='function'){
      const original=window.ratingLabPool;window.ratingLabPool=function(){return original().filter(player=>allows(player.position));};
    }
    if(typeof window.relationshipAssemble==='function'){
      const original=window.relationshipAssemble;window.relationshipAssemble=function(){const result=original();const ids=new Set(result.nodes.filter(node=>allows(node.position)).map(node=>node.id));return {...result,nodes:result.nodes.filter(node=>ids.has(node.id)),edges:result.edges.filter(edge=>ids.has(edge.a)&&ids.has(edge.b)),message:ids.size?result.message:'No players match the shared position filter.'};};
    }
    if(typeof window.renderTransferRiverPassport==='function'&&typeof TRANSFER_RIVER_PASSPORT!=='undefined'){
      const original=window.renderTransferRiverPassport;window.renderTransferRiverPassport=function(...args){
        const data=TRANSFER_RIVER_PASSPORT,allowedPlayers=(data.players||[]).filter(player=>allows(player.position)),names=new Set(allowedPlayers.map(player=>player.name));
        const saved={players:data.players,edges:data.river_edges,movers:data.top_movers},allowedIds=new Set(allowedPlayers.map(player=>Number(player.id)));
        data.players=allowedPlayers;data.river_edges=(saved.edges||[]).map(edge=>{const playerNames=(edge.player_names||[]).filter(name=>names.has(name));return {...edge,player_names:playerNames,moves:playerNames.length};}).filter(edge=>edge.moves>0);data.top_movers=(saved.movers||[]).filter(row=>allowedIds.has(Number(row.id)));
        if(typeof passportState!=='undefined'&&passportState.focusPlayer!==null&&!allowedIds.has(Number(passportState.focusPlayer)))passportState.focusPlayer=null;
        try{return original.apply(this,args);}finally{data.players=saved.players;data.river_edges=saved.edges;data.top_movers=saved.movers;}
      };
    }
  }
  function refreshLegacy(){
    if(typeof window.applyPlayerAnalyticsFilter==='function')window.applyPlayerAnalyticsFilter();else applyLegacyCharts();
    if(typeof window.ratingLabRender==='function')window.ratingLabRender();
    if(typeof window.renderPlayerRelationshipGraph==='function')window.renderPlayerRelationshipGraph();
    if(typeof window.renderTransferRiverPassport==='function')window.renderTransferRiverPassport();
  }
  const api={positions:()=>new Set(selected),allows,isAll,set,subscribe(listener){listeners.add(listener);return()=>listeners.delete(listener);},refresh:refreshLegacy};
  window.MCDraftPositionFilter=api;
  document.addEventListener('click',event=>{const button=event.target.closest('[data-analytics-position]');if(button)set(button.dataset.analyticsPosition);});
  function initialise(){mount();connectLegacyRenderers();api.subscribe(refreshLegacy);refreshLegacy();}
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',initialise,{once:true});else initialise();
})();
