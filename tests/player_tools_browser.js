window.addEventListener('DOMContentLoaded',()=>setTimeout(async()=>{
  const checks=[],check=(ok,label)=>checks.push((ok?'OK: ':'FAILED: ')+label),$=id=>document.getElementById(id);
  const wait=()=>new Promise(resolve=>setTimeout(resolve,100));
  try {
    enterManagerDashboard();
    const cmp=McDraftCompare,line=McDraftLineup;
    check(!!cmp&&!!line,'tools initialise');
    playerSearchData.slice(0,4).forEach(p=>cmp.add(p.id));
    check(cmp.ids().length===4,'four players selectable');
    check(!cmp.add(playerSearchData[0].id)&&cmp.ids().length===4,'duplicate rejected');
    check(!cmp.add(playerSearchData[4].id)&&cmp.ids().length===4,'fifth player rejected');
    $('mcd-compare-tray').querySelectorAll('button')[4].click();
    check($('mcd-comparison').open,'comparison opens as accessible dialog');
    check($('mcd-comparison').querySelectorAll('thead th').length===5,'four comparison columns');
    check($('mcd-comparison').textContent.includes('Next 3 GW projected points'),'forecast comparison labelled');
    cmp.remove(playerSearchData[0].id);check(cmp.ids().length===3,'remove updates selection');
    $('mcd-compare-find').value=playerSearchData[4].name;$('mcd-compare-find').dispatchEvent(new Event('input'));
    check($('mcd-comparison').querySelector('.mcd-compare-options button'),'player finder offers results');
    $('mcd-comparison').close();
    McDraftSearch.open(playerSearchData[4].name,'player');
    check($('search-list').querySelector('[data-compare-player]'),'search results offer comparison');
    $('search-list').querySelector('[data-compare-player]').click();check(cmp.ids().length===4,'search adds a player');
    function squad(d,m,f){let id=0;return ['GKP',...Array(d).fill('DEF'),...Array(m).fill('MID'),...Array(f).fill('FWD')].map(position=>({id:++id,position}));}
    check([[3,4,3],[3,5,2],[4,3,3],[4,4,2],[4,5,1],[5,2,3],[5,3,2],[5,4,1]].every(a=>line.valid(squad(...a))),'all eight legal formations accepted');
    check(!line.valid(squad(2,5,3))&&!line.valid(squad(5,5,0))&&!line.valid(squad(3,3,3)),'illegal formations and wrong XI size rejected');
    const state={starters:squad(4,4,2),bench:[{id:12,position:'GKP'},{id:13,position:'DEF'},{id:14,position:'MID'},{id:15,position:'FWD'}]};
    const before=JSON.stringify(state);
    check(!!line.swap(state,2,15),'cross-position swap can change 4-4-2 to 3-4-3');
    check(!!line.swap(state,1,12),'goalkeeper swap accepted');
    check(!line.swap(state,1,15),'goalkeeper for outfield swap rejected');
    check(!line.swap(state,2,2)&&!line.swap(state,999,15),'non-bench and missing players rejected');
    check(JSON.stringify(state)===before,'swap does not mutate original squad');
    const manager=$('war-room-manager').value,original=JSON.stringify(MANAGER_WAR_ROOM[manager]);
    showPage('war-room');await wait();
    check(!!$('mcd-lineup-out'),'War Room editor rendered');
    check(!$('mcd-lineup-swap').disabled,'valid swap offered');
    $('mcd-lineup-swap').click();
    check(!$('mcd-lineup-reset').disabled&&$('mcd-lineup-status').textContent.includes('starts;'),'swap updates draft');
    const heading=$('mcd-lineup-editor').parentElement.querySelector('h3').textContent;
    renderManagerWarRoom();check(!$('mcd-lineup-reset').disabled,'draft survives War Room rerender');
    check($('mcd-lineup-editor').parentElement.querySelector('h3').textContent===heading,'formation remains consistent');
    check(JSON.stringify(MANAGER_WAR_ROOM[manager])===original,'official baseline and probabilities unchanged');
    const other=[...$('war-room-manager').options].find(o=>o.value!==manager&&MANAGER_WAR_ROOM[o.value]?.you?.starters.length===11);
    if(other){$('war-room-manager').value=other.value;renderManagerWarRoom();check($('mcd-lineup-reset').disabled,'other team has its own unedited draft');$('war-room-manager').value=manager;renderManagerWarRoom();check(!$('mcd-lineup-reset').disabled,'switching back restores first team draft');}
    $('mcd-lineup-reset').click();check($('mcd-lineup-reset').disabled,'reset restores original XI');
    showWarRoomPlayer(MANAGER_WAR_ROOM[manager].you.starters[0].id,'you');
    check(!!$('war-room-player-detail').querySelector('[data-compare-player]'),'War Room detail offers comparison');
    check($('mcd-compare-tray').getBoundingClientRect().width<=document.documentElement.clientWidth,'tray fits mobile viewport');
  }catch(error){checks.push('FAILED: '+error.stack);}
  const report=document.createElement('pre');report.id='player-tools-report';report.textContent=JSON.stringify(checks);document.body.append(report);
},400));
