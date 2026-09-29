/* Facts come from the dashboard snapshot; no external requests or invented trivia. */
(() => {
  'use strict';
  const number = value => (typeof value==='number'||(typeof value==='string'&&value.trim()!=='')) && Number.isFinite(Number(value)) ? Number(value) : null;
  const fmt = value => new Intl.NumberFormat('en-GB',{maximumFractionDigits:1}).format(value);
  const plural = (n,word) => fmt(n)+' '+word+(n===1?'':'s');
  const positive = value => number(value)!==null && number(value)>0;
  function buildFacts({players=[],clubs={},teams={}}={}) {
    const facts=new Map();
    function add(type,entity,metric,sentence,context) {
      const id=JSON.stringify([type,String(entity),metric]);
      facts.set(id,{id,type,entity:String(entity),sentence,context});
    }
    players.forEach(p=>{
      if(p.id==null||!p.name)return;
      const context=[p.team,p.position,'Season totals in the current dashboard snapshot'].filter(Boolean).join(' · ');
      const addPlayer=(metric,sentence,scope=context)=>add('Player',p.id,metric,sentence,scope);
      [['total_points','fantasy point'],['goals','goal'],['assists','assist'],['bonus','bonus point'],['minutes','minute']].forEach(([key,label])=>{
        if(positive(p[key]))addPlayer(key,`${p.name} has ${plural(Number(p[key]),label)} this season.`);
      });
      if(['GKP','DEF'].includes(p.position)&&positive(p.clean_sheets))addPlayer('clean_sheets',`${p.name} has earned ${plural(Number(p.clean_sheets),'FPL clean sheet')} this season.`);
      if(p.position==='GKP'&&positive(p.saves))addPlayer('saves',`${p.name} has made ${plural(Number(p.saves),'save')} this season.`);
      if(number(p.goals)!==null&&number(p.assists)!==null&&Number(p.goals)+Number(p.assists)>=3)
        addPlayer('goal_involvements',`${p.name} has ${fmt(Number(p.goals)+Number(p.assists))} goal involvements this season: ${plural(Number(p.goals),'goal')} and ${plural(Number(p.assists),'assist')}.`);
      if(number(p.minutes)>=450&&positive(p.total_points))addPlayer('points_per_90',`${p.name} has scored ${fmt(Number(p.total_points)*90/Number(p.minutes))} fantasy points per 90 minutes this season.`,context+' · Minimum 450 minutes played');
      const history=Array.isArray(p.history)?p.history.filter(h=>number(h.gw)>0&&number(h.points)!==null):[];
      if(history.length){
        const best=history.reduce((a,b)=>Number(a.points)>=Number(b.points)?a:b);
        if(Number(best.points)>=8)addPlayer('best_haul',`${p.name}'s biggest recorded gameweek haul is ${plural(Number(best.points),'point')}, in GW${best.gw}.`,'Player history · '+plural(history.length,'recorded gameweek'));
        const hauls=history.filter(h=>Number(h.points)>=10).length;
        if(hauls>0)addPlayer('double_digits',`${p.name} has ${plural(hauls,'double-digit haul')} across ${plural(history.length,'recorded gameweek')}.`,'Player history · A double-digit haul is at least 10 fantasy points');
      }
      const owners=Array.isArray(p.owners)?new Set(p.owners.filter(o=>typeof o==='string'&&o&&o!=='Free Agent'&&o!=='Free agents')):new Set();
      if(owners.size>=2)addPlayer('owners',`${p.name} has been owned by ${fmt(owners.size)} different fantasy teams.`,'Ownership history recorded by the dashboard');
    });
    Object.values(clubs||{}).forEach(c=>{
      if(c.id==null||!c.name)return;
      const club=(metric,sentence,context='Club Explorer · Current dashboard snapshot')=>add('Club',c.id,metric,sentence,context);
      if(positive(c.pl_points))club('league_points',`${c.name} have ${plural(Number(c.pl_points),'Premier League point')} in the current table.`);
      if(positive(c.fpl_points))club('fantasy_points',`${c.name} have ${plural(Number(c.fpl_points),'combined FPL point')} in Club Explorer.`);
      const weeks=Array.isArray(c.gw_points)?c.gw_points.filter(w=>number(w.gw)>0&&number(w.points)!==null):[];
      if(weeks.length){
        const best=weeks.reduce((a,b)=>Number(a.points)>=Number(b.points)?a:b);
        if(positive(best.points))club('best_week',`${c.name}'s biggest recorded FPL gameweek total is ${plural(Number(best.points),'point')}, in GW${best.gw}.`,'Club Explorer · '+plural(weeks.length,'recorded gameweek'));
      }
      const ids=new Set((c.player_ids||[]).map(String));
      const owned=players.filter(p=>ids.has(String(p.id))&&p.fantasy_team&&p.fantasy_team!=='Free Agent'&&p.fantasy_team!=='Free agents');
      if(owned.length)club('owned_players',`${plural(owned.length,'player')} in ${c.name}'s current player pool ${owned.length===1?'is':'are'} owned by fantasy teams.`,'Club Explorer player pool · Current fantasy ownership');
      const managers=new Set(owned.map(p=>p.fantasy_team));
      if(managers.size>=2)club('owners',`${c.name}'s currently owned players are spread across ${plural(managers.size,'fantasy team')}.`,'Club Explorer player pool · Current fantasy ownership');
    });
    Object.entries(teams||{}).forEach(([name,t])=>{
      if(!name)return;
      const games=(Array.isArray(t.games)?t.games:[]).filter(g=>number(g.gw)>0&&number(g.points)!==null&&number(g.against)!==null&&['W','D','L'].includes(g.result)).sort((a,b)=>Number(a.gw)-Number(b.gw));
      if(!games.length)return;
      const context='Fantasy team · '+plural(games.length,'recorded completed fixture');
      const team=(metric,sentence)=>add('Fantasy team',name,metric,sentence,context);
      const wins=games.filter(g=>g.result==='W'), draws=games.filter(g=>g.result==='D');
      team('record',`${name} have a record of ${wins.length}W ${draws.length}D ${games.length-wins.length-draws.length}L across ${plural(games.length,'recorded completed fixture')}.`);
      const total=games.reduce((sum,g)=>sum+Number(g.points),0);
      team('average',`${name} average ${fmt(total/games.length)} fantasy points per recorded completed fixture.`);
      const best=games.reduce((a,b)=>Number(a.points)>=Number(b.points)?a:b);
      team('best_week',`${name}'s highest recorded completed-fixture score is ${plural(Number(best.points),'point')} in GW${best.gw}.`);
      if(wins.length){
        const big=wins.reduce((a,b)=>Number(a.points)-Number(a.against)>=Number(b.points)-Number(b.against)?a:b);
        team('biggest_win',`${name}'s biggest recorded winning margin is ${plural(Number(big.points)-Number(big.against),'point')}, against ${big.opponent} in GW${big.gw}.`);
        const close=wins.filter(g=>Number(g.points)-Number(g.against)<=5).length;
        if(close)team('close_wins',`${name} have won ${plural(close,'recorded fixture')} by five points or fewer.`);
      }
      let run=0,longest=0,previous=null;
      games.forEach(g=>{run=g.result==='W'?(previous!==null&&Number(g.gw)===previous+1?run+1:1):0;longest=Math.max(longest,run);previous=Number(g.gw);});
      if(longest>=2)team('win_streak',`${name}'s longest recorded winning streak is ${plural(longest,'consecutive gameweek')}.`);
      const roster=players.filter(p=>p.fantasy_team===name);
      const represented=new Set(roster.map(p=>p.team).filter(Boolean));
      if(represented.size>=2)add('Fantasy team',name,'club_variety',`${name}'s current squad contains players from ${plural(represented.size,'different club')}.`,'Fantasy team · Current squad snapshot');
    });
    return [...facts.values()].sort((a,b)=>a.id<b.id?-1:a.id>b.id?1:0);
  }
  function londonDay(date=new Date()) {
    const parts=new Intl.DateTimeFormat('en-GB',{timeZone:'Europe/London',year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(date);
    const get=type=>parts.find(p=>p.type===type).value;return `${get('year')}-${get('month')}-${get('day')}`;
  }
  function hash(value) {let h=2166136261;for(let i=0;i<value.length;i++){h^=value.charCodeAt(i);h=Math.imul(h,16777619);}return h>>>0;}
  function pick(facts,day=londonDay()) {
    if(!facts.length)return null;
    // Rotate categories, then pick a subject and one of its facts. Large player
    // pools and subjects with more fields do not crowd out clubs or teams.
    const categories=['Player','Fantasy team','Club'].filter(type=>facts.some(f=>f.type===type));
    const ordinal=Math.floor(Date.parse(day+'T00:00:00Z')/86400000);
    const type=categories[((ordinal%categories.length)+categories.length)%categories.length];
    const eligible=facts.filter(f=>f.type===type);
    const subjects=[...new Set(eligible.map(f=>f.entity))].sort();
    const subject=subjects[hash(day+':subject')%subjects.length];
    return eligible.filter(f=>f.entity===subject).sort((a,b)=>hash(day+':'+a.id)-hash(day+':'+b.id)||a.id.localeCompare(b.id))[0];
  }
  let facts=[],currentDay='',players=[];
  function pickPlayer(pool,allFacts,day=londonDay(),saved=null) {
    const priorities=['best_haul','goal_involvements','double_digits','goals','assists','clean_sheets','saves','total_points','bonus','points_per_90','minutes','owners'];
    const available=pool.filter(p=>p.id!=null&&p.name&&p.draft_active!==false&&allFacts.some(f=>f.type==='Player'&&f.entity===String(p.id)));
    if(!available.length)return null;
    const retained=saved?.day===day?available.find(p=>String(p.id)===String(saved.id)):null;
    const p=retained||[...available].sort((a,b)=>hash(day+':daily-player:'+a.id)-hash(day+':daily-player:'+b.id)||String(a.id).localeCompare(String(b.id)))[0];
    const candidates=allFacts.filter(f=>f.type==='Player'&&f.entity===String(p.id));
    const fact=(retained&&candidates.find(f=>f.id===saved.factId))||candidates.sort((a,b)=>{
      const rank=f=>{const i=priorities.indexOf(JSON.parse(f.id)[2]);return i<0?99:i;};
      return rank(a)-rank(b)||a.id.localeCompare(b.id);
    })[0];
    return {player:p,fact};
  }
  function renderPlayer(day,date){
    const card=document.getElementById('mcd-player-of-day');if(!card)return;
    const key='mcdraft-player-of-day-v1';let saved=null;
    try{saved=JSON.parse(localStorage.getItem(key)||'null');}catch{}
    const chosen=pickPlayer(players,facts,day,saved);card.hidden=!chosen;if(!chosen)return;
    const {player:p,fact}=chosen;
    try{localStorage.setItem(key,JSON.stringify({day,id:String(p.id),factId:fact.id}));}catch{}
    const set=(id,value)=>{document.getElementById(id).textContent=value;};
    set('mcd-player-name',p.name);
    set('mcd-player-position',({GKP:'Goalkeeper',DEF:'Defender',MID:'Midfielder',FWD:'Forward'})[p.position]||p.position||'Unknown');
    set('mcd-player-club',p.team||'Unknown club');
    set('mcd-player-owner',p.fantasy_team||'Free Agent');
    set('mcd-player-headline',fact.sentence);
  }
  function dailyFact(day) {
    // Retain today's identity across frequent dashboard rebuilds, but always
    // show its latest value. Never cache a sentence that could become stale.
    const key='mcdraft-stat-of-day-v1';
    try {
      const saved=JSON.parse(localStorage.getItem(key)||'null');
      if(saved?.day===day){const found=facts.find(f=>f.id===saved.id);if(found)return found;}
    } catch { /* Storage is optional. */ }
    const fact=pick(facts,day);
    if(fact)try{localStorage.setItem(key,JSON.stringify({day,id:fact.id}));}catch{ /* Storage is optional. */ }
    return fact;
  }
  function render(date=new Date()) {
    const card=document.getElementById('mcd-stat-of-day');if(!card)return;
    document.getElementById('mcd-welcome-date').textContent=new Intl.DateTimeFormat('en-GB',{timeZone:'Europe/London',weekday:'long',day:'numeric',month:'long',year:'numeric'}).format(date);
    currentDay=londonDay(date);const fact=dailyFact(currentDay);
    renderPlayer(currentDay,date);
    card.hidden=!fact;if(!fact)return;
    document.getElementById('mcd-stat-category').textContent=fact.type;
    document.getElementById('mcd-stat-fact').textContent=fact.sentence;
  }
  function init() {
    players=typeof playerSearchData==='undefined'?[]:playerSearchData;
    facts=buildFacts({players,
      clubs:typeof CLUB_EXPLORER_DATA==='undefined'?{}:CLUB_EXPLORER_DATA,
      teams:typeof MCD_MATCHUP_STATS==='undefined'?{}:MCD_MATCHUP_STATS});render();
    const refresh=()=>{if(londonDay()!==currentDay)render();};
    document.addEventListener('visibilitychange',()=>{if(!document.hidden)refresh();});
    setInterval(refresh,60000);
  }
  window.McDraftDailyStat={buildFacts,pick,pickPlayer,londonDay,render};
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();
