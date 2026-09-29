(() => {
  'use strict';

  const POSITIONS=['GKP','DEF','MID','FWD'];
  const POSITION_LABELS={GKP:'GK',DEF:'DEF',MID:'MID',FWD:'FWD'};
  const POSITION_COLOURS={GKP:'#fbbf24',DEF:'#38bdf8',MID:'#a78bfa',FWD:'#fb7185'};
  const PALETTE=['#38bdf8','#a78bfa','#34d399','#fbbf24','#fb7185','#22d3ee','#f97316','#60a5fa','#84cc16','#c084fc'];
  const activePositions=new Set(POSITIONS);
  const positionState=()=>window.MCDraftPositionFilter?window.MCDraftPositionFilter.positions():new Set(activePositions);
  const esc=value=>String(value??'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');
  const num=value=>Number.isFinite(Number(value))?Number(value):0;
  const average=values=>values.length?values.reduce((sum,value)=>sum+value,0)/values.length:0;
  const deviation=values=>values.length?Math.sqrt(average(values.map(value=>(value-average(values))**2))):0;
  const ownerOf=player=>(!player.fantasy_team||/^free agents?$/i.test(player.fantasy_team))?'Free agents':player.fantasy_team;
  const allPlayers=()=>typeof playerSearchData==='undefined'?[]:playerSearchData.filter(player=>player&&player.draft_active!==false);

  const pages={
    insights:'analytics-sub-insights',matrices:'analytics-sub-matrices',ratings:'analytics-sub-ratings',
    player:'analytics-sub-player',relationships:'analytics-sub-relationships','river-passport':'analytics-sub-river-passport',
    club:'analytics-sub-club','squad-strength':'analytics-sub-squad-strength',
    'squad-build':'analytics-sub-squad-build',decisions:'analytics-sub-decisions',fixtures:'analytics-sub-fixtures-h2h',
    availability:'analytics-sub-availability-impact',season:'analytics-sub-season','league-stats':'analytics-sub-league-stats',
    gameweek:'analytics-sub-gameweek-lab',visuals:'analytics-sub-visuals'
  };
  const pageNames={insights:'McDraft Insights',matrices:'Matrix Lab',ratings:'Rating Lab',player:'Player Analytics',relationships:'Player Relationships','river-passport':'Transfer River + Player Passport',club:'Club Analytics','squad-strength':'Squad Strength','squad-build':'Squad Construction',decisions:'Manager Decisions',availability:'Availability Impact',fixtures:'Fixtures & H2H',season:'Overall Season','league-stats':'League Stats',gameweek:'Gameweek Lab',visuals:'Visual Analytics'};
  const specs=[];
  const add=(target,items)=>items.forEach(item=>specs.push({target,...item}));
  const bar=(title,metric,description='Ranked comparison',extra={})=>({title,metric,description,type:'bar',...extra});
  const scatter=(title,x,y,description='Relationship and outliers',extra={})=>({title,x,y,description,type:'scatter',...extra});
  const hist=(title,metric,description='Distribution across the selected pool')=>({title,metric,description,type:'histogram'});
  const groupBar=(title,group,metric,reducer='sum',description='Filtered group comparison',extra={})=>({title,group,metric,reducer,description,type:'group-bar',...extra});
  const groupScatter=(title,group,x,y,xReducer='avg',yReducer='avg',description='Filtered group relationship')=>({title,group,x,y,xReducer,yReducer,description,type:'group-scatter'});
  const stack=(title,group,metric,reducer='sum',description='Position mix within each group')=>({title,group,metric,reducer,description,type:'stack'});
  const weekly=(title,group,description='Actual player output by gameweek',area=false)=>({title,group,description,type:'weekly',area});
  const weeklyStat=(title,stat,description='Manager gameweek profile for selected positions')=>({title,stat,description,type:'weekly-stat'});

  add('player',[
    bar('Points leaderboard','total_points'),bar('Player rating board','player_rating'),bar('Value index','player_value'),bar('Projected season ceiling','projected_season_points'),
    bar('Next three gameweeks','next3_projected_points'),bar('Form leaders','form'),bar('Goal scorers','goals'),bar('Assist makers','assists'),
    scatter('Rating vs points','player_rating','total_points'),scatter('Value vs next-three forecast','player_value','next3_projected_points'),scatter('Form vs total output','form','total_points'),scatter('Minutes vs points','minutes','total_points'),
    scatter('Club strength vs projection','club_strength','projected_remaining_points'),scatter('Fixture run vs value','fixture_run_score','player_value'),scatter('Goals vs assists','goals','assists'),scatter('Draft rank vs points','blended_draft_rank','total_points'),
    hist('Rating distribution','player_rating'),hist('Value distribution','player_value'),hist('Points distribution','total_points'),hist('Minutes-share distribution','minutes_share')
  ]);
  add('club',[
    groupBar('Club points inventory','team','total_points'),groupBar('Average club rating','team','player_rating','avg'),groupBar('Average club value','team','player_value','avg'),
    groupBar('Goals by club','team','goals'),groupBar('Assists by club','team','assists'),groupBar('Next-three club forecast','team','next3_projected_points'),
    groupScatter('Club rating vs points','team','player_rating','total_points','avg','sum'),groupScatter('Club goals vs assists','team','goals','assists','sum','sum'),
    groupScatter('Club strength vs projection','team','club_strength','projected_remaining_points','avg','sum'),groupScatter('Fixture run vs next-three output','team','fixture_run_score','next3_projected_points','avg','sum'),
    stack('Club points by position','team','total_points'),stack('Club player supply by position','team','__count','sum')
  ]);
  add('squad-strength',[
    groupBar('Average squad rating','owner','player_rating','avg'),groupBar('Squad points bank','owner','total_points'),groupBar('Average squad value','owner','player_value','avg'),
    groupBar('Squad season projection','owner','projected_remaining_points'),groupBar('Average squad form','owner','form','avg'),groupBar('Next-three squad forecast','owner','next3_projected_points'),
    groupScatter('Squad rating vs points','owner','player_rating','total_points','avg','sum'),groupScatter('Squad value vs projection','owner','player_value','projected_remaining_points','avg','sum'),
    groupScatter('Squad form vs next-three','owner','form','next3_projected_points','avg','sum'),groupScatter('Minutes security vs rating','owner','minutes_share','player_rating','avg','avg'),
    stack('Squad ratings by position','owner','player_rating','avg'),stack('Squad points by position','owner','total_points')
  ]);
  add('squad-build',[
    groupBar('Squad size','owner','__count'),groupBar('Club diversity','owner','team','distinct'),groupBar('Minutes accumulated','owner','minutes'),groupBar('Goals assembled','owner','goals'),
    stack('Roster allocation by position','owner','__count'),stack('Points construction by position','owner','total_points'),stack('Value construction by position','owner','player_value'),
    groupScatter('Squad size vs points','owner','__count','total_points','sum','sum'),groupScatter('Club diversity vs rating','owner','team','player_rating','distinct','avg'),groupScatter('Defensive returns vs clean sheets','owner','defensive_contributions','clean_sheets','sum','sum')
  ]);
  add('decisions',[
    groupBar('Transfer traffic','owner','transfers'),groupBar('Hot and cold balance','owner','hot_cold_score','avg'),groupBar('Rating movement','owner','rating_gw_delta'),groupBar('Estimated matches missed','owner','matches_missed_estimate'),
    groupScatter('Transfer demand vs value','owner','transfers','player_value','sum','avg'),groupScatter('Rating movement vs form','owner','rating_gw_delta','form','sum','avg'),
    groupScatter('Availability vs squad value','owner','availability_next','player_value','avg','avg'),groupScatter('Temperature vs forecast','owner','hot_cold_score','next3_projected_points','avg','sum')
  ]);
  add('fixtures',[
    groupBar('Manager fixture runway','owner','fixture_run_score','avg'),groupBar('Manager next-three total','owner','next3_projected_points'),groupBar('Club fixture runway','team','fixture_run_score','avg'),
    groupBar('Projected remaining output','owner','projected_remaining_points'),groupScatter('Fixture runway vs next three','owner','fixture_run_score','next3_projected_points','avg','sum'),
    groupScatter('Fixture runway vs projection','team','fixture_run_score','projected_remaining_points','avg','sum'),bar('Best individual fixture runs','fixture_run_score'),bar('Largest next-three hauls','next3_projected_points')
  ]);
  add('season',[
    weekly('Weekly output by position','position','Stacked actual points by position',true),weekly('Weekly output by manager','owner'),weekly('Weekly output by club','team'),
    groupBar('Season points by manager','owner','total_points'),groupBar('Points per game by manager','owner','points_per_game','avg'),groupBar('Season goals by manager','owner','goals'),groupBar('Season assists by manager','owner','assists'),
    hist('Season points spread','total_points'),hist('Current form spread','form'),hist('Bonus points spread','bonus')
  ]);
  add('gameweek',[
    weekly('Position scoring waves','position','Actual scoring by selected positions',true),weekly('Manager scoring waves','owner','Actual player output assigned to current squads',true),
    weekly('Club scoring waves','team'),weekly('Pool scoring pulse','total'),weeklyStat('Manager average gameweek','average'),weeklyStat('Manager volatility','volatility'),weeklyStat('Manager high score','high'),weeklyStat('Manager low score','low')
  ]);
  add('visuals',[
    {...bar('Defensive contribution leaders','defensive_contributions'),type:'lollipop'},{...bar('Save leaders','saves'),type:'lollipop'},
    {...bar('Bonus magnets','bonus'),type:'lollipop'},{...bar('Clean-sheet leaders','clean_sheets'),type:'lollipop'},
    groupBar('Rating by position','position','player_rating','avg'),groupBar('Value by position','position','player_value','avg'),groupBar('Points by position','position','total_points','sum'),groupBar('Projection by position','position','projected_remaining_points','sum')
  ]);
  add('ratings',[
    bar('Expanded player ratings','player_rating'),bar('Largest rating changes','rating_gw_delta'),hist('Rating model distribution','player_rating'),scatter('Rating vs model value','player_rating','player_value')
  ]);
  const move=(from,target,titles)=>specs.forEach(spec=>{if(spec.target===from&&titles.includes(spec.title))spec.target=target;});
  move('player','relationships',['Club strength vs projection','Fixture run vs value','Goals vs assists','Draft rank vs points']);
  move('player','matrices',['Rating distribution','Value distribution','Points distribution','Minutes-share distribution']);
  move('club','league-stats',['Club points by position','Club player supply by position']);
  move('season','league-stats',['Current form spread','Bonus points spread']);
  move('squad-strength','insights',['Squad ratings by position','Squad points by position']);
  move('gameweek','insights',['Manager high score','Manager low score']);
  move('squad-build','river-passport',['Club diversity vs rating','Defensive returns vs clean sheets']);
  move('fixtures','river-passport',['Best individual fixture runs','Largest next-three hauls']);
  move('decisions','availability',['Availability vs squad value','Temperature vs forecast']);
  move('visuals','availability',['Points by position','Projection by position']);

  function activeOwners(){
    const container=document.getElementById('analytics-manager-chips');
    if(!container||!container.querySelector('.chart-chip'))return null;
    return new Set([...container.querySelectorAll('.chart-chip.active')].map(chip=>chip.textContent.trim()));
  }
  function filteredPlayers(){
    const owners=activeOwners();
    const selected=positionState();return allPlayers().filter(player=>selected.has(player.position)&&(!owners||owners.has(ownerOf(player))));
  }
  function metric(player,key){
    if(key==='__count')return 1;
    return num(player[key]);
  }
  function groupKey(player,key){return key==='owner'?ownerOf(player):key==='position'?(POSITION_LABELS[player.position]||player.position):player[key];}
  function reduce(players,key,reducer='sum'){
    if(reducer==='distinct')return new Set(players.map(player=>String(player[key]??''))).size;
    const values=players.map(player=>metric(player,key)).filter(Number.isFinite);
    if(reducer==='avg')return average(values);
    if(reducer==='max')return Math.max(0,...values);
    return values.reduce((sum,value)=>sum+value,0);
  }
  function grouped(players,key){
    const groups=new Map();
    players.forEach(player=>{const label=groupKey(player,key)||'Unknown';if(!groups.has(label))groups.set(label,[]);groups.get(label).push(player);});
    return groups;
  }
  function colour(label,index=0){
    if(typeof MANAGER_COLORS!=='undefined'&&MANAGER_COLORS[label])return MANAGER_COLORS[label];
    const position=Object.entries(POSITION_LABELS).find(([,name])=>name===label)?.[0];
    if(position)return POSITION_COLOURS[position];
    let hash=0;for(const char of String(label))hash=((hash<<5)-hash)+char.charCodeAt(0);
    return PALETTE[Math.abs(hash||index)%PALETTE.length];
  }
  function format(value){const absolute=Math.abs(value);return absolute>=1000?(value/1000).toFixed(1)+'k':absolute>=100?Math.round(value).toString():value.toFixed(absolute<10?1:0);}
  function empty(host,message='No matching data for this filter.'){host.innerHTML=`<div class="atlas-empty">${esc(message)}</div>`;}

  function renderBars(host,rows){
    rows=rows.filter(row=>Number.isFinite(row.value)).sort((a,b)=>b.value-a.value).slice(0,15);
    if(!rows.length)return empty(host);
    const maximum=Math.max(1,...rows.map(row=>Math.abs(row.value)));
    host.innerHTML='<div class="analytics-bar-chart atlas-bar-list">'+rows.map((row,index)=>`<div class="analytics-bar-row atlas-bar-row" role="button" tabindex="0" data-chart-detail="${esc(row.label)} · ${format(row.value)}" ${row.playerId!=null?`data-atlas-player-id="${esc(row.playerId)}" aria-label="Open details for ${esc(row.label)}"`:""} data-atlas-position="${esc(row.position||'')}" data-atlas-owner="${esc(row.owner||'')}"><span class="analytics-bar-label atlas-bar-name" title="${esc(row.label)}">${esc(row.label)}</span><span class="analytics-bar-track atlas-bar-track"><i class="analytics-bar-fill atlas-bar-fill" style="width:${Math.abs(row.value)/maximum*100}%;background:${colour(row.label,index)}"></i></span><strong class="analytics-bar-value atlas-bar-value">${format(row.value)}</strong></div>`).join('')+'</div>';
  }
  function playerRows(players,spec){return players.map(player=>({playerId:player.id,label:player.name,value:metric(player,spec.metric),position:player.position,owner:ownerOf(player)}));}
  function groupRows(players,spec,key=spec.metric,reducer=spec.reducer){return [...grouped(players,spec.group)].map(([label,pool])=>({label,value:reduce(pool,key,reducer),pool}));}

  function renderScatter(host,rows,xLabel,yLabel){
    rows=rows.filter(row=>Number.isFinite(row.x)&&Number.isFinite(row.y));if(!rows.length)return empty(host);
    const width=720,height=290,left=48,right=20,top=18,bottom=40,plotW=width-left-right,plotH=height-top-bottom;
    const minX=Math.min(0,...rows.map(row=>row.x)),maxX=Math.max(1,...rows.map(row=>row.x)),minY=Math.min(0,...rows.map(row=>row.y)),maxY=Math.max(1,...rows.map(row=>row.y));
    const x=value=>left+(value-minX)/Math.max(1,maxX-minX)*plotW,y=value=>top+(1-(value-minY)/Math.max(1,maxY-minY))*plotH;
    const grid=[0,.25,.5,.75,1].map(f=>`<line class="trend-chart-gridline atlas-gridline" x1="${left+plotW*f}" x2="${left+plotW*f}" y1="${top}" y2="${top+plotH}"/><line class="trend-chart-gridline atlas-gridline" x1="${left}" x2="${left+plotW}" y1="${top+plotH*f}" y2="${top+plotH*f}"/><text class="trend-chart-axis-label atlas-axis" x="${left+plotW*f}" y="${height-22}" text-anchor="middle">${format(minX+(maxX-minX)*f)}</text><text class="trend-chart-axis-label atlas-axis" x="${left-7}" y="${top+plotH*(1-f)+3}" text-anchor="end">${format(minY+(maxY-minY)*f)}</text>`).join('');
    const dots=rows.map((row,index)=>`<circle class="atlas-dot" tabindex="0" data-chart-detail="${esc(row.label)} · ${format(row.x)} / ${format(row.y)}" data-atlas-position="${esc(row.position||'')}" data-atlas-owner="${esc(row.owner||'')}" cx="${x(row.x).toFixed(1)}" cy="${y(row.y).toFixed(1)}" r="${rows.length>40?4:6}" fill="${colour(row.position||row.label,index)}"><title>${esc(row.label)} · ${format(row.x)} / ${format(row.y)}</title></circle>`).join('');
    const labels=rows.length<=20?rows.map(row=>`<text class="atlas-axis" x="${x(row.x)+7}" y="${y(row.y)-5}">${esc(String(row.label).slice(0,15))}</text>`).join(''):'';
    host.innerHTML=`<div class="trend-chart-svg-wrap"><svg class="atlas-svg" viewBox="0 0 ${width} ${height}" role="img" aria-label="${esc(xLabel)} against ${esc(yLabel)}">${grid}${dots}${labels}<text class="analytics-svg-axis-title atlas-axis" x="${left+plotW/2}" y="${height-7}" text-anchor="middle">${esc(xLabel)} →</text><text class="analytics-svg-axis-title atlas-axis" transform="translate(12 ${top+plotH/2}) rotate(-90)" text-anchor="middle">${esc(yLabel)} →</text></svg></div>`;
  }
  function renderHistogram(host,players,spec){
    const values=players.map(player=>metric(player,spec.metric)).filter(Number.isFinite);if(!values.length)return empty(host);
    const bins=10,minimum=Math.min(...values),maximum=Math.max(...values),span=Math.max(1,maximum-minimum),counts=Array(bins).fill(0);
    values.forEach(value=>counts[Math.min(bins-1,Math.floor((value-minimum)/span*bins))]++);
    const width=720,height=290,left=42,right=18,top=18,bottom=40,plotW=width-left-right,plotH=height-top-bottom,maxCount=Math.max(1,...counts);
    const bars=counts.map((count,index)=>{const w=plotW/bins-5,h=count/maxCount*plotH;return `<rect x="${left+index*plotW/bins+2}" y="${top+plotH-h}" width="${w}" height="${h}" rx="3" fill="${PALETTE[index%PALETTE.length]}"><title>${format(minimum+index*span/bins)}–${format(minimum+(index+1)*span/bins)}: ${count} players</title></rect>`;}).join('');
    host.innerHTML=`<svg class="atlas-svg" viewBox="0 0 ${width} ${height}" role="img" aria-label="${esc(spec.title)}">${bars}<text class="atlas-axis" x="${left}" y="${height-10}">${format(minimum)}</text><text class="atlas-axis" x="${width-right}" y="${height-10}" text-anchor="end">${format(maximum)}</text><text class="atlas-axis" x="${left+plotW/2}" y="${height-8}" text-anchor="middle">${esc(spec.metric.replaceAll('_',' '))}</text></svg>`;
  }
  function renderLollipop(host,players,spec){
    const rows=playerRows(players,spec).sort((a,b)=>b.value-a.value).slice(0,12);if(!rows.length)return empty(host);
    const width=720,left=145,right=45,top=12,rowH=21,height=top+rows.length*rowH+16,max=Math.max(1,...rows.map(row=>Math.abs(row.value)));
    host.innerHTML=`<svg class="atlas-svg" viewBox="0 0 ${width} ${height}" role="img" aria-label="${esc(spec.title)}">${rows.map((row,index)=>{const yy=top+index*rowH+9,xx=left+Math.abs(row.value)/max*(width-left-right);return `<text class="atlas-axis" x="${left-7}" y="${yy+3}" text-anchor="end">${esc(row.label.slice(0,20))}</text><line class="atlas-lollipop-line" x1="${left}" x2="${xx}" y1="${yy}" y2="${yy}"/><circle class="atlas-lollipop-dot" data-atlas-position="${row.position}" data-atlas-owner="${esc(row.owner)}" cx="${xx}" cy="${yy}" r="5" fill="${colour(row.position,index)}"><title>${esc(row.label)} · ${format(row.value)}</title></circle>`;}).join('')}</svg>`;
  }
  function renderStack(host,players,spec){
    const rows=[...grouped(players,spec.group)].map(([label,pool])=>({label,values:Object.fromEntries(POSITIONS.map(position=>[position,reduce(pool.filter(player=>player.position===position),spec.metric,spec.reducer)]))}));
    rows.sort((a,b)=>Object.values(b.values).reduce((x,y)=>x+y,0)-Object.values(a.values).reduce((x,y)=>x+y,0));if(!rows.length)return empty(host);
    const selected=positionState();host.innerHTML='<div class="atlas-stack-list">'+rows.slice(0,15).map(row=>{const total=Math.max(.001,Object.values(row.values).reduce((sum,value)=>sum+Math.max(0,value),0));return `<div class="atlas-stack-row"><span class="atlas-stack-name" title="${esc(row.label)}">${esc(row.label)}</span><span class="atlas-stack-track">${POSITIONS.filter(position=>selected.has(position)).map(position=>`<i style="width:${Math.max(0,row.values[position])/total*100}%;background:${POSITION_COLOURS[position]}" title="${POSITION_LABELS[position]}: ${format(row.values[position])}"></i>`).join('')}</span></div>`;}).join('')+'</div><div class="atlas-legend">'+POSITIONS.filter(position=>selected.has(position)).map(position=>`<span><i style="background:${POSITION_COLOURS[position]}"></i>${POSITION_LABELS[position]}</span>`).join('')+'</div>';
  }
  function weeklyDataset(players,group){
    const weeks=[...new Set(players.flatMap(player=>(player.history||[]).map(row=>num(row.gw))))].filter(Boolean).sort((a,b)=>a-b),values=new Map();
    players.forEach(player=>(player.history||[]).forEach(row=>{const key=group==='total'?'All selected':group==='owner'?((row.owners||[])[0]||ownerOf(player)):groupKey(player,group);if(!values.has(key))values.set(key,new Map());values.get(key).set(num(row.gw),num(values.get(key).get(num(row.gw)))+num(row.points));}));
    let series=[...values].map(([label,map])=>({label,values:weeks.map(week=>num(map.get(week)))}));series.sort((a,b)=>b.values.reduce((x,y)=>x+y,0)-a.values.reduce((x,y)=>x+y,0));return {weeks,series:series.slice(0,10)};
  }
  function renderWeekly(host,players,spec){
    const {weeks,series}=weeklyDataset(players,spec.group);if(!weeks.length||!series.length)return empty(host,'No completed player gameweeks for this filter.');
    const width=720,height=300,left=42,right=15,top=18,bottom=43,plotW=width-left-right,plotH=height-top-bottom,max=Math.max(1,...series.flatMap(row=>row.values));
    const x=index=>left+(weeks.length===1?plotW/2:index*plotW/(weeks.length-1)),y=value=>top+(1-value/max)*plotH;
    const grid=[0,.25,.5,.75,1].map(f=>`<line class="trend-chart-gridline atlas-gridline" x1="${left}" x2="${width-right}" y1="${top+plotH*f}" y2="${top+plotH*f}"/><text class="trend-chart-axis-label atlas-axis" x="${left-7}" y="${top+plotH*f+3}" text-anchor="end">${format(max*(1-f))}</text>`).join('');
    const paths=series.map((row,index)=>{const points=row.values.map((value,i)=>`${x(i)},${y(value)}`),line=`M${points.join(' L')}`,seriesColour=colour(row.label,index);return `${spec.area?`<path class="atlas-series-area" d="${line} L${x(weeks.length-1)},${top+plotH} L${x(0)},${top+plotH} Z" style="fill:${seriesColour}"/>`:''}<path class="atlas-series-line" d="${line}" style="stroke:${seriesColour}"><title>${esc(row.label)}</title></path>${row.values.map((value,i)=>`<circle class="atlas-series-point" cx="${x(i)}" cy="${y(value)}" r="3.5" style="fill:${seriesColour}"><title>${esc(row.label)} · GW${weeks[i]}: ${format(value)}</title></circle>`).join('')}`;}).join('');
    const step=Math.max(1,Math.ceil(weeks.length/8)),labels=weeks.map((week,index)=>index%step===0||index===weeks.length-1?`<text class="atlas-axis" x="${x(index)}" y="${height-10}" text-anchor="middle">GW${week}</text>`:'').join('');
    host.innerHTML=`<div class="trend-chart-svg-wrap"><svg class="atlas-svg" viewBox="0 0 ${width} ${height}" role="img" aria-label="${esc(spec.title)}">${grid}${paths}${labels}</svg></div><div class="atlas-legend">${series.map((row,index)=>`<span><i style="background:${colour(row.label,index)}"></i>${esc(row.label)}</span>`).join('')}</div>`;
  }
  function renderWeeklyStat(host,players,spec){
    const {series}=weeklyDataset(players,'owner'),rows=series.map(row=>({label:row.label,value:spec.stat==='average'?average(row.values):spec.stat==='volatility'?deviation(row.values):spec.stat==='high'?Math.max(0,...row.values):Math.min(...row.values)}));renderBars(host,rows);
  }
  function renderSpec(spec,host){
    const players=filteredPlayers();
    if(spec.type==='bar')return renderBars(host,playerRows(players,spec));
    if(spec.type==='histogram')return renderHistogram(host,players,spec);
    if(spec.type==='lollipop')return renderLollipop(host,players,spec);
    if(spec.type==='group-bar')return renderBars(host,groupRows(players,spec));
    if(spec.type==='stack')return renderStack(host,players,spec);
    if(spec.type==='weekly')return renderWeekly(host,players,spec);
    if(spec.type==='weekly-stat')return renderWeeklyStat(host,players,spec);
    if(spec.type==='scatter')return renderScatter(host,players.map(player=>({label:player.name,x:metric(player,spec.x),y:metric(player,spec.y),position:player.position,owner:ownerOf(player)})),spec.x.replaceAll('_',' '),spec.y.replaceAll('_',' '));
    if(spec.type==='group-scatter')return renderScatter(host,[...grouped(players,spec.group)].map(([label,pool])=>({label,x:reduce(pool,spec.x,spec.xReducer),y:reduce(pool,spec.y,spec.yReducer)})),spec.x.replaceAll('_',' '),spec.y.replaceAll('_',' '));
  }
  function openPlayerDetails(playerId){
    const player=allPlayers().find(player=>String(player.id)===playerId);
    if(!player)return;
    window.showPage('players');
    window.showPlayerSubtab('directory',document.querySelector('.player-page-tab[onclick*="directory"]'));
    ['player-position-filter','player-club-filter','player-fantasy-filter'].forEach(id=>{const control=document.getElementById(id);if(control)control.value='';});
    document.getElementById('player-search').value=player.name;
    // Wait for the directory's scheduled render, then select by ID even for duplicate names.
    requestAnimationFrame(()=>{
    const results=document.getElementById('player-search-results');
    results.innerHTML=window.renderPlayerDirectoryCard(player);
    document.getElementById('player-directory-count').textContent='1 player';
    window.togglePlayerDetails(player.id);
    const card=results.firstElementChild;
    card.tabIndex=-1;card.focus({preventScroll:true});card.scrollIntoView({block:'start'});
    });
  }
  // Capture player activation before the generic chart inspector handles the row.
  document.addEventListener('click',event=>{
    const row=event.target.closest('.atlas-bar-row[data-atlas-player-id]');
    if(!row)return;
    event.preventDefault();event.stopPropagation();openPlayerDetails(row.dataset.atlasPlayerId);
  },true);
  document.addEventListener('keydown',event=>{
    if(event.key!=='Enter'&&event.key!==' ')return;
    const row=event.target.closest('.atlas-bar-row[data-atlas-player-id]');
    if(!row)return;
    event.preventDefault();event.stopPropagation();row.click();
  },true);
  function controls(){return `<div class="chart-atlas-position-filter" role="group" aria-label="Chart Atlas position filter"><span>Position</span><button class="atlas-position-button" data-atlas-position-filter="ALL" type="button">All</button>${POSITIONS.map(position=>`<button class="atlas-position-button" data-atlas-position-filter="${position}" type="button">${POSITION_LABELS[position]}</button>`).join('')}</div>`;}
  function build(){
    Object.entries(pages).forEach(([target,pageId])=>{
      const page=document.getElementById(pageId);if(!page||page.querySelector('.chart-atlas'))return;
      const targetSpecs=specs.filter(spec=>spec.target===target),section=document.createElement('section');section.className='chart-atlas';section.dataset.atlasTarget=target;
      section.innerHTML=`<div class="card chart-atlas-head"><div><span class="chart-atlas-kicker">Extended Chart Atlas</span><h2>${esc(pageNames[target])}: deeper cuts</h2><p class="card-description">Supplemental views respond to the dashboard manager filter and the position filter below.</p></div><strong class="chart-atlas-count">${targetSpecs.length} extra charts</strong>${controls()}</div><div class="analytics-chart-grid chart-atlas-grid">${targetSpecs.map(spec=>`<article class="card analytics-chart-card atlas-card"><h2>${esc(spec.title)}</h2><p class="card-description">${esc(spec.description)}</p><div class="atlas-host" data-atlas-index="${specs.indexOf(spec)}"><div class="atlas-section-loading">Open this page to draw the chart.</div></div></article>`).join('')}</div>`;
      page.append(section);
    });
    syncControls();renderActive();
  }
  function syncControls(){
    const selected=positionState(),all=selected.size===POSITIONS.length;
    document.querySelectorAll('[data-atlas-position-filter]').forEach(button=>{const position=button.dataset.atlasPositionFilter,isActive=position==='ALL'?all:selected.has(position);button.classList.toggle('active',isActive);button.setAttribute('aria-pressed',String(isActive));});
  }
  function setPosition(position){
    if(window.MCDraftPositionFilter){window.MCDraftPositionFilter.set(position);return;}
    if(position==='ALL')POSITIONS.forEach(item=>activePositions.add(item));
    else if(activePositions.size===POSITIONS.length){activePositions.clear();activePositions.add(position);}
    else if(activePositions.has(position)&&activePositions.size>1)activePositions.delete(position);else activePositions.add(position);
    syncControls();document.querySelectorAll('.chart-atlas[data-atlas-rendered="true"]').forEach(section=>renderTarget(section.dataset.atlasTarget));
  }
  function renderTarget(target){
    const section=document.querySelector(`.chart-atlas[data-atlas-target="${target}"]`);if(!section)return;
    section.querySelectorAll('.atlas-host').forEach(host=>renderSpec(specs[num(host.dataset.atlasIndex)],host));section.dataset.atlasRendered='true';
  }
  function renderActive(){const active=document.querySelector('.analytics-subpage.active .chart-atlas');if(active)renderTarget(active.dataset.atlasTarget);}
  function refreshFilteredCharts(){
    document.querySelectorAll('.chart-atlas[data-atlas-rendered="true"]').forEach(section=>renderTarget(section.dataset.atlasTarget));
    if(typeof window.renderVisualAnalytics==='function')window.renderVisualAnalytics();
    if(typeof window.renderGameweekLab==='function')window.renderGameweekLab();
  }
  function connectManagerFilter(){
    ['setAnalyticsManagerPreset','toggleAnalyticsManager','toggleAnalyticsFreeAgents'].forEach(name=>{
      const original=window[name];if(typeof original!=='function'||original.__atlasConnected)return;
      const connected=function(...args){const result=original.apply(this,args);refreshFilteredCharts();return result;};
      connected.__atlasConnected=true;window[name]=connected;
    });
  }
  function initialise(){
    if(specs.length!==100)throw new Error(`Chart Atlas expected 100 specs, received ${specs.length}`);build();connectManagerFilter();
    if(window.MCDraftPositionFilter)window.MCDraftPositionFilter.subscribe(()=>{syncControls();document.querySelectorAll('.chart-atlas[data-atlas-rendered="true"]').forEach(section=>renderTarget(section.dataset.atlasTarget));});
    const chips=document.getElementById('analytics-manager-chips');if(chips){let pending=false;new MutationObserver(()=>{if(pending)return;pending=true;requestAnimationFrame(()=>{pending=false;document.querySelectorAll('.chart-atlas[data-atlas-rendered="true"]').forEach(section=>renderTarget(section.dataset.atlasTarget));});}).observe(chips,{subtree:true,childList:true,attributes:true,attributeFilter:['class']});}
  }
  document.addEventListener('click',event=>{const position=event.target.closest('[data-atlas-position-filter]');if(position){setPosition(position.dataset.atlasPositionFilter);return;}if(event.target.closest('.analytics-subtab,.mcd-nav-link'))requestAnimationFrame(renderActive);});
  window.MCDChartAtlas={count:specs.length,specs,pages,renderTarget,setPosition,filteredPlayers};
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',initialise,{once:true});else initialise();
})();
