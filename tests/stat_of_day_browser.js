window.addEventListener('DOMContentLoaded',()=>setTimeout(()=>{
  const checks=[],check=(ok,label)=>checks.push((ok?'OK: ':'FAILED: ')+label);
  try {
    const api=window.McDraftDailyStat;
    check(!!api,'daily stat initialises');
    const facts=api.buildFacts({players:playerSearchData,clubs:CLUB_EXPLORER_DATA,teams:MCD_MATCHUP_STATS});
    check(facts.length>=300,'hundreds of facts from existing data');
    check(new Set(facts.map(f=>f.id)).size===facts.length,'facts have unique stable identities');
    check(!facts.some(f=>/NaN|undefined|null/.test(f.sentence)),'no missing values shown as facts');
    const day='2026-09-28',chosen=api.pick(facts,day);
    check(chosen.id===api.pick([...facts].reverse(),day).id,'same day and data give same pick regardless of input order');
    const days=['2026-09-28','2026-09-29','2026-09-30'].map(d=>api.pick(facts,d));
    check(new Set(days.map(f=>f.type)).size===3,'all three categories feature within three days');
    check(new Set(days.map(f=>f.id)).size===3,'daily pick changes');
    check(api.pick([],day)===null,'empty data has no fabricated fact');
    check(api.londonDay(new Date('2026-07-01T23:30:00Z'))==='2026-07-02','UK summer-time midnight');
    check(api.londonDay(new Date('2026-12-01T23:30:00Z'))==='2026-12-01','UK winter-time midnight');
    const fixture=api.buildFacts({players:[{id:1,name:'Example',position:'MID',team:'Club',fantasy_team:'Alpha',goals:2,assists:3,minutes:450,total_points:30,history:[{gw:1,points:12},{gw:2,points:4}]},
      {id:2,name:'Missing',goals:null,assists:'',minutes:false,total_points:'NaN'}],
      clubs:{one:{id:1,name:'Club',pl_points:9,fpl_points:100,player_ids:[1],gw_points:[{gw:1,points:30},{gw:2,points:70}]}},
      teams:{Alpha:{games:[{gw:1,points:50,against:40,result:'W',opponent:'Beta'},{gw:3,points:60,against:58,result:'W',opponent:'Gamma'}]}}});
    const has=(type,metric,value)=>fixture.some(f=>f.type===type&&JSON.parse(f.id)[2]===metric&&f.sentence.includes(value));
    check(has('Player','goal_involvements','5 goal involvements'),'goal contributions calculated from actual goals and assists');
    check(has('Player','points_per_90','6 fantasy points per 90'),'points per 90 calculation');
    check(!fixture.some(f=>f.entity==='2'),'missing, empty and invalid numbers excluded');
    check(has('Club','best_week','70 points, in GW2'),'club high score from recorded weekly points');
    check(has('Fantasy team','average','55 fantasy points'),'team average uses recorded completed games');
    check(has('Fantasy team','biggest_win','10 points'),'winning margin is correct');
    check(!fixture.some(f=>JSON.parse(f.id)[2]==='win_streak'),'missing gameweeks do not create a winning streak');
    const card=document.getElementById('mcd-stat-of-day'),welcome=document.getElementById('mcd-manager-welcome');
    check(!card.hidden&&!!document.getElementById('mcd-stat-fact').textContent,'daily card is populated');
    check(card.parentElement.classList.contains('mcd-daily-cards')&&card.parentElement===card.closest('.mcd-welcome-card').lastElementChild,'daily cards sit at the bottom of welcome selection');
    api.render(new Date('2026-09-28T12:00:00Z'));check(document.getElementById('mcd-stat-fact').textContent===chosen.sentence,'render uses correct daily fact');
    api.render(new Date('2026-09-29T12:00:00Z'));check(document.getElementById('mcd-stat-fact').textContent===api.pick(facts,'2026-09-29').sentence,'render advances at next date');
    const savedFact=facts.find(f=>f.id!==chosen.id);
    localStorage.setItem('mcdraft-stat-of-day-v1',JSON.stringify({day,id:savedFact.id,sentence:'STALE VALUE'}));
    api.render(new Date(day+'T12:00:00Z'));
    check(document.getElementById('mcd-stat-fact').textContent===savedFact.sentence,'daily identity survives refresh while sentence uses current data');
    localStorage.setItem('mcdraft-stat-of-day-v1','invalid JSON');api.render(new Date(day+'T12:00:00Z'));
    check(document.getElementById('mcd-stat-fact').textContent===chosen.sentence,'corrupt storage falls back to daily selection');
    welcome.scrollTop=0;
    check(card.closest('.mcd-welcome-card').getBoundingClientRect().top>=0,'welcome heading remains reachable on short screens');
    welcome.scrollTop=welcome.scrollHeight;
    check(card.getBoundingClientRect().bottom<=welcome.getBoundingClientRect().bottom+1,'bottom of stat can be reached by scrolling');
    check(welcome.scrollWidth<=welcome.clientWidth,'welcome has no horizontal overflow');
    check(!document.getElementById('mcd-welcome-continue').disabled,'team selection remains usable');
    const dailyPlayer=document.getElementById('mcd-player-of-day');
    check(!dailyPlayer.hidden&&dailyPlayer.parentElement===card.parentElement,'player card appears alongside stat card');
    const chosenPlayer=api.pickPlayer(playerSearchData,facts,day);
    check(chosenPlayer.player.id===api.pickPlayer([...playerSearchData].reverse(),facts,day).player.id,'player pick is stable across data ordering');
    const storage=JSON.parse(localStorage.getItem('mcdraft-player-of-day-v1'));
    const retained=api.pickPlayer(playerSearchData,facts,storage.day,storage);
    check(document.getElementById('mcd-player-name').textContent===retained.player.name,'saved player identity renders');
    check(document.getElementById('mcd-player-club').textContent===retained.player.team&&document.getElementById('mcd-player-owner').textContent===(retained.player.fantasy_team||'Free Agent'),'club and fantasy team come from current data');
    check(document.getElementById('mcd-player-headline').textContent===retained.fact.sentence,'headline uses a real fact for chosen player');
    check(api.pickPlayer([],facts,day)===null,'no invented player for empty dataset');
    const stale=api.pickPlayer(playerSearchData,facts,day,{day,id:'missing',factId:'missing'});
    check(!!stale&&stale.player.id===chosenPlayer.player.id,'missing saved player gets a valid replacement');
    check(dailyPlayer.getBoundingClientRect().top>=card.getBoundingClientRect().bottom,'daily cards stack on mobile');
    check(dailyPlayer.getBoundingClientRect().bottom<=welcome.getBoundingClientRect().bottom+1,'player card bottom is reachable on mobile');
    checks.push('Fact pool: '+facts.length+' ('+['Player','Fantasy team','Club'].map(type=>type+': '+facts.filter(f=>f.type===type).length).join(', ')+')');
  }catch(error){checks.push('FAILED: '+error.stack);}
  const report=document.createElement('pre');report.id='daily-stat-test-report';report.textContent=JSON.stringify(checks);document.body.append(report);
},300));
