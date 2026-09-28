/* Runs against the generated dashboard, including its actual navigation/data. */
window.addEventListener('DOMContentLoaded',()=>setTimeout(async()=>{
  const checks=[];
  const check=(condition,name)=>{checks.push((condition?'OK: ':'FAILED: ')+name);};
  const $=id=>document.getElementById(id);
  const wait=()=>new Promise(resolve=>setTimeout(resolve,100));
  try {
    const search=window.McDraftSearch;
    check(!!search,'search initialises');if(!search)throw Error('Search did not initialise');
    const audit=search.audit();check(audit.missing.length===0,'all registered destinations resolve: '+audit.missing.join(','));
    check(search.search('').filter(r=>r.type==='player').length===playerSearchData.length,'every player indexed');
    check(search.search('').filter(r=>r.type==='club').length===Object.keys(CLUB_EXPLORER_DATA).length,'every club indexed');
    check(MANAGER_ORDER.every(m=>search.search(m).some(r=>r.type==='team'&&r.label===m)),'every fantasy team indexed');
    check(search.search('league chat').some(r=>r.page==='league-chat'),'new pages indexed');
    check(search.normalise('Ødegaard')==='odegaard','accent and special letter matching');
    check(search.normalise('Man Utd')===search.normalise('Manchester United'),'club aliases');
    check(search.search('Arsenal DEF').some(r=>r.type==='player'&&r.player.team==='Arsenal'&&r.player.position==='DEF'),'multiple words across player fields');
    const player=playerSearchData.find(p=>p.name==='Haaland')||playerSearchData.find(p=>p.name.length>5);
    check(search.search(player.name)[0].label===player.name,'exact name ranks first');
    const typo=player.name.slice(0,-1)+'x';check(search.search(typo).some(r=>r.id==='player:'+player.id),'typo tolerance');
    $('global-search').value='planner';$('global-search').dispatchEvent(new KeyboardEvent('keydown',{key:'Enter',bubbles:true}));
    check($('page-search').classList.contains('active')&&location.hash.startsWith('#mcd-search='),'Enter opens results with URL');
    check($('search-list').querySelector('a'),'results contain destination links');
    search.open('','player');check($('search-list').children.length===30&&!$('search-more').hidden,'results are paginated, not truncated');
    $('search-more').click();check($('search-list').children.length===60,'load more reveals further results');
    search.open(player.name,'player');$('search-list').querySelector('.search-favourite').click();
    search.open('','favourites');check($('search-list').textContent.includes(player.name),'favourite is searchable');
    check(JSON.parse(localStorage.getItem('mcd-search-favourites')).includes('player:'+player.id),'favourite persists');
    check(JSON.parse(localStorage.getItem('mcd-search-recent')).includes(player.name),'recent query persists');
    ['player-position-filter','player-club-filter','player-fantasy-filter'].forEach(id=>{if($(id)?.options.length>1)$(id).selectedIndex=1;});
    search.open(player.name,'player');$('search-list').querySelector('h2 a').click();await wait();
    check($('page-players').classList.contains('active')&&$('player-sub-directory').classList.contains('active'),'player opens correct tab');
    check($('player-search-results').textContent.includes(player.name),'player visible despite previous filters');
    const team=search.search('').find(r=>r.type==='team');search.open(team.label,'team');$('search-list').querySelector('h2 a').click();await wait();
    check($('my-team-select').selectedOptions[0].text===team.label&&$('myteam-sub-squad').classList.contains('active'),'fantasy team selects matching roster');
    const club=search.search('').find(r=>r.type==='club');search.open(club.label,'club');$('search-list').querySelector('h2 a').click();await wait();
    check($('club-explorer-select').value===club.value&&$('club-sub-overview').classList.contains('active'),'club opens matching overview');
    search.open('','all');
    const nested=search.search('').find(r=>r.type==='section'&&r.routes?.length===2&&r.page==='overview');
    check(!!nested,'nested destination indexed');
    if(nested){const a=document.createElement('a');a.href='#mcd-result='+encodeURIComponent(nested.id);location.hash=a.hash;await wait();check(nested.routes.every(r=>$(r.target).classList.contains('active')),'nested tabs open through shared destination URL');}
    search.open('planner','section');const saved=location.hash;
    $('search-list').querySelector('h2 a')?.click();await wait();history.back();await wait();
    check(location.hash===saved&&$('page-search').classList.contains('active')&&$('search-query').value==='planner','Back restores query and results');
    location.hash='#mcd-search=q=Arsenal&type=player';await wait();
    check($('search-query').value==='Arsenal'&&$('search-filters').querySelector('[aria-pressed="true"]').textContent.startsWith('Players'),'shared search restores query and category');
    search.open('<img src=x onerror=alert(1)>');check(!$('page-search').querySelector('img'),'query is rendered as text');
    search.open('','all');
    check($('page-search').scrollWidth<=document.documentElement.clientWidth,'search fits mobile width');
    const privateHeading=document.createElement('h3');privateHeading.textContent='PRIVATE_CHAT_SENTINEL';$('chat-messages').append(privateHeading);search.rebuild();
    check(!search.search('PRIVATE_CHAT_SENTINEL').length,'private chat text excluded');privateHeading.remove();
    const ids=search.search('').map(r=>r.id);search.rebuild();check(JSON.stringify(ids)===JSON.stringify(search.search('').map(r=>r.id)),'destination IDs remain stable');
    checks.push('Coverage: '+JSON.stringify(audit));
  } catch(error) {checks.push('FAILED: '+error.stack);}
  const report=document.createElement('pre');report.id='search-test-report';report.textContent=JSON.stringify(checks);document.body.append(report);
},500));
