/* Save identities locally; display fresh metrics from each dashboard build. */
(() => {
  'use strict';
  const key='mcdraft-player-watchlist-v1',$=id=>document.getElementById(id);
  const pool=()=>typeof playerSearchData==='undefined'?[]:playerSearchData;
  const player=id=>pool().find(p=>String(p.id)===String(id));
  const el=(tag,text,cls)=>{const n=document.createElement(tag);if(text!=null)n.textContent=text;if(cls)n.className=cls;return n;};
  let warning='';
  function load(){try{const rows=JSON.parse(localStorage.getItem(key)||'[]');return new Map((Array.isArray(rows)?rows:[]).filter(r=>r&&/^\d+$/.test(String(r.id))&&typeof r.name==='string').map(r=>[String(r.id),{id:String(r.id),name:r.name}]));}catch{return new Map();}}
  let saved=load();
  function persist(){try{localStorage.setItem(key,JSON.stringify([...saved.values()]));warning='';}catch{warning='Browser storage is unavailable. Changes will only last for this visit.';}}
  function refreshButtons(){document.querySelectorAll('[data-watch-player]').forEach(b=>{
    const watched=saved.has(b.dataset.watchPlayer);b.textContent=watched?'Watching ✓':'Watch player';b.setAttribute('aria-pressed',String(watched));
    b.setAttribute('aria-label',(watched?'Remove from watchlist: ':'Add to watchlist: ')+(player(b.dataset.watchPlayer)?.name||saved.get(b.dataset.watchPlayer)?.name||'player'));
    b.title=warning|| (watched?'Saved in your browser. Click to remove.':'Save this player in your browser.');
  });}
  function toggle(id){id=String(id);const p=player(id);if(saved.has(id))saved.delete(id);else if(p)saved.set(id,{id,name:p.name});else return false;persist();render();refreshButtons();return saved.has(id);}
  function button(id){const b=el('button',saved.has(String(id))?'Watching ✓':'Watch player','mcd-watch-button');b.type='button';b.dataset.watchPlayer=String(id);b.setAttribute('aria-pressed',String(saved.has(String(id))));return b;}
  const fmt=value=>value!==null&&value!==undefined&&value!==''&&Number.isFinite(Number(value))?Number(value).toLocaleString('en-GB',{maximumFractionDigits:1}):'—';
  function render(){
    const root=$('watchlist-rows');if(!root)return;
    root.replaceChildren();const q=($('watchlist-search')?.value||'').trim().toLowerCase();
    $('watchlist-status').textContent=warning||saved.size+' player'+(saved.size===1?'':'s')+' saved in this browser.';
    const rows=[...saved.values()].map(s=>({saved:s,p:player(s.id)})).filter(({saved:s,p})=>!q||[p?.name||s.name,p?.team,p?.position,p?.fantasy_team].join(' ').toLowerCase().includes(q)).sort((a,b)=>(a.p?.name||a.saved.name).localeCompare(b.p?.name||b.saved.name));
    if(!rows.length){root.append(el('p',saved.size?'No watched players match your search.':'Your watchlist is empty. Use “Watch player” in search results, the Player Directory or War Room details.'));return;}
    rows.forEach(({saved:s,p})=>{
      const card=el('article',null,'watchlist-player');card.append(el('h3',p?.name||s.name));
      if(p){
        card.append(el('p',[p.position,p.team,p.fantasy_team||'Free Agent'].filter(Boolean).join(' · ')));
        const metrics=el('div',null,'watchlist-metrics');[['Season points',p.total_points],['Form',p.form],['Rating / 100',p.player_rating],['Next 3 GW projection',p.next3_projected_points]].forEach(([label,value])=>metrics.append(el('span',label+': '+fmt(value))));card.append(metrics);
        const status=({a:'Available',d:'Doubtful',i:'Injured',s:'Suspended',u:'Unavailable',n:'Unavailable'})[p.availability?.status]||'Availability unknown';
        card.append(el('p',status+(p.availability?.news?' · '+p.availability.news:'')));
        card.append(el('p','Fixtures: '+((p.next_fixtures||[]).slice(0,3).map(f=>'GW'+f.gw+': '+(f.label||'—')).join(' · ')||'No fixtures captured')));
        if(window.McDraftCompare)card.append(window.McDraftCompare.button(p.id));
        const open=el('button','Open player','mcd-watch-button');open.type='button';open.addEventListener('click',()=>{
          if(window.McDraftSearch){location.hash='mcd-result='+encodeURIComponent('player:'+p.id);}
          else{showPage('players');showPlayerSubtab('directory',document.querySelector('.player-page-tab[onclick*="directory"]'));$('player-search').value=p.name;filterPlayers();}
        });card.append(open);
      }else card.append(el('p','This player is no longer in the current dataset. You can remove the saved entry.'));
      const remove=el('button','Remove','mcd-watch-button');remove.type='button';remove.setAttribute('aria-label','Remove '+(p?.name||s.name)+' from watchlist');remove.addEventListener('click',()=>{toggle(s.id);$('watchlist-search')?.focus();});card.append(remove);root.append(card);
    });
  }
  function init(){
    document.addEventListener('click',event=>{const b=event.target.closest('[data-watch-player]');if(b)toggle(b.dataset.watchPlayer);});
    $('watchlist-search')?.addEventListener('input',render);
    if(typeof window.renderPlayerDirectoryCard==='function'){
      const original=window.renderPlayerDirectoryCard;
      window.renderPlayerDirectoryCard=function(p){return original(p).replace(/<\/div>\s*$/,button(p.id).outerHTML+'</div>');};
      window.filterPlayers?.();
    }
    if(typeof window.showWarRoomPlayer==='function'){
      const original=window.showWarRoomPlayer;
      window.showWarRoomPlayer=function(id,side){const result=original.apply(this,arguments);if(player(id))$('war-room-player-detail')?.append(button(id));return result;};
    }
    window.addEventListener('storage',event=>{if(event.key===key||event.key===null){saved=load();warning='';render();refreshButtons();}});
    render();refreshButtons();
  }
  window.McDraftWatchlist={button,toggle,ids:()=>[...saved.keys()]};
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();
