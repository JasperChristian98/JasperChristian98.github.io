(() => {
  'use strict';

  const palette = ['#38bdf8','#a78bfa','#34d399','#fbbf24','#fb7185','#22d3ee','#c084fc','#84cc16','#f97316','#60a5fa'];
  const positionColours = {GKP:'#fbbf24', DEF:'#38bdf8', MID:'#a78bfa', FWD:'#fb7185'};
  const positionLabels = {GKP:'Goalkeepers', DEF:'Defenders', MID:'Midfielders', FWD:'Forwards'};
  const esc = value => String(value ?? '').replace(/&/g,'&amp;').replace(/</g,'&lt;')
    .replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');
  const num = value => Number.isFinite(Number(value)) ? Number(value) : 0;
  const allPlayers = () => typeof playerSearchData === 'undefined' ? [] : playerSearchData.filter(player => player && player.draft_active !== false);
  const ownerOf = player => (!player.fantasy_team || /^free agents?$/i.test(player.fantasy_team)) ? 'Free agents' : player.fantasy_team;

  function activeOwners() {
    const container = document.getElementById('analytics-manager-chips');
    if (!container || !container.querySelector('.chart-chip')) return null;
    const chips = [...container.querySelectorAll('.chart-chip.active')];
    return new Set(chips.map(chip => chip.textContent.trim()));
  }

  function filteredPlayers() {
    const owners = activeOwners();
    return owners ? allPlayers().filter(player => owners.has(ownerOf(player))) : allPlayers();
  }

  function empty(host, message='No matching data for the current filter.') {
    host.innerHTML = '<div class="visual-empty">' + esc(message) + '</div>';
  }

  function gameweeks(players=allPlayers()) {
    return [...new Set(players.flatMap(player => (player.history || []).map(row => Number(row.gw))))]
      .filter(Number.isFinite).sort((a,b) => a-b);
  }

  function aggregateByGameweek(players, classifier) {
    const weeks = gameweeks(players);
    const keys = [];
    const values = {};
    players.forEach(player => (player.history || []).forEach(row => {
      const key = classifier(player, row);
      if (!key) return;
      if (!values[key]) { values[key] = Object.fromEntries(weeks.map(gw => [gw, 0])); keys.push(key); }
      values[key][Number(row.gw)] = num(values[key][Number(row.gw)]) + num(row.points);
    }));
    return {weeks, series:keys.map(key => ({key, values:weeks.map(gw => num(values[key][gw]))}))};
  }

  function renderArea(hostId, dataset, colours, labels) {
    const host = document.getElementById(hostId);
    if (!host) return;
    const {weeks, series} = dataset;
    if (!weeks.length || !series.length) return empty(host, 'No completed gameweeks yet.');
    const width=760, height=285, left=42, right=12, top=15, bottom=34;
    const plotW=width-left-right, plotH=height-top-bottom;
    const totals=weeks.map((_,index) => series.reduce((sum,row) => sum + Math.max(0,row.values[index]),0));
    const maximum=Math.max(1,...totals);
    const x=index => left + (weeks.length===1 ? plotW/2 : index*plotW/(weeks.length-1));
    const y=value => top + plotH - (value/maximum)*plotH;
    let cumulative=weeks.map(() => 0), paths='';
    series.forEach((row,index) => {
      const lower=[...cumulative];
      const upper=row.values.map((value,i) => cumulative[i] += Math.max(0,value));
      const points=upper.map((value,i) => `${x(i).toFixed(1)},${y(value).toFixed(1)}`)
        .concat(lower.map((value,i) => `${x(i).toFixed(1)},${y(value).toFixed(1)}`).reverse());
      paths += `<path d="M${points.join(' L')} Z" fill="${colours[index]}" fill-opacity=".78"><title>${esc(labels[index])}</title></path>`;
    });
    const yGrid=[0,.25,.5,.75,1].map(fraction => {
      const value=maximum*fraction, yy=y(value);
      return `<line class="visual-grid-line" x1="${left}" x2="${width-right}" y1="${yy}" y2="${yy}"/><text class="visual-axis-label" x="${left-7}" y="${yy+3}" text-anchor="end">${Math.round(value)}</text>`;
    }).join('');
    const step=Math.max(1,Math.ceil(weeks.length/8));
    const xLabels=weeks.map((gw,index) => (index%step===0 || index===weeks.length-1)
      ? `<text class="visual-axis-label" x="${x(index)}" y="${height-10}" text-anchor="middle">GW${gw}</text>` : '').join('');
    host.innerHTML=`<svg class="visual-svg" viewBox="0 0 ${width} ${height}" role="img" aria-label="Stacked area chart">${yGrid}${paths}${xLabels}</svg>`+
      `<div class="visual-legend">${series.map((row,index) => `<span><i style="background:${colours[index]}"></i>${esc(labels[index])}</span>`).join('')}</div>`;
  }

  function splitTreemap(items, x, y, width, height, output) {
    if (!items.length) return;
    if (items.length===1) { output.push({...items[0],x,y,width,height}); return; }
    const total=items.reduce((sum,item) => sum+item.value,0);
    let running=0, cut=1, best=Infinity;
    for (let index=1; index<items.length; index++) {
      running += items[index-1].value;
      const distance=Math.abs(total/2-running);
      if (distance<best) { best=distance; cut=index; }
    }
    const first=items.slice(0,cut), second=items.slice(cut);
    const firstTotal=first.reduce((sum,item) => sum+item.value,0), ratio=total ? firstTotal/total : .5;
    if (width>=height) {
      splitTreemap(first,x,y,width*ratio,height,output);
      splitTreemap(second,x+width*ratio,y,width*(1-ratio),height,output);
    } else {
      splitTreemap(first,x,y,width,height*ratio,output);
      splitTreemap(second,x,y+height*ratio,width,height*(1-ratio),output);
    }
  }

  function colourFor(label, index) {
    if (typeof MANAGER_COLORS !== 'undefined' && MANAGER_COLORS[label]) return MANAGER_COLORS[label];
    let hash=0; for (const character of label) hash=((hash<<5)-hash)+character.charCodeAt(0);
    return palette[Math.abs(hash || index)%palette.length];
  }

  function renderTreemap(hostId, items, unit) {
    const host=document.getElementById(hostId); if(!host)return;
    items=items.filter(item => item.value>0).sort((a,b) => b.value-a.value);
    if(!items.length)return empty(host);
    const cells=[]; splitTreemap(items,0,0,100,100,cells);
    host.innerHTML=cells.map((cell,index) => {
      const showValue=cell.width>10 && cell.height>13;
      return `<div class="visual-tree-cell" tabindex="0" aria-label="${esc(cell.label)}: ${cell.value.toFixed(1)} ${esc(unit)}" title="${esc(cell.label)} · ${cell.value.toFixed(1)} ${esc(unit)}" style="left:${cell.x}%;top:${cell.y}%;width:${cell.width}%;height:${cell.height}%;background:${colourFor(cell.label,index)}"><strong>${esc(cell.label)}</strong>${showValue?`<small>${cell.value.toFixed(1)} ${esc(unit)}</small>`:''}</div>`;
    }).join('');
  }

  function swarmOffset(index) {
    if (!index) return 0;
    const level=Math.ceil(index/2);
    return (index%2 ? -1 : 1)*level*7;
  }

  function renderBeeswarm(hostId, rows, groups, metric, axisLabel, domain) {
    const host=document.getElementById(hostId);if(!host)return;
    rows=rows.filter(row => Number.isFinite(num(row[metric])));
    if(!rows.length)return empty(host);
    const width=760,left=78,right=18,top=28,rowHeight=62,bottom=38,height=top+groups.length*rowHeight+bottom;
    const minimum=domain?.[0] ?? Math.min(...rows.map(row=>num(row[metric])));
    const maximum=domain?.[1] ?? Math.max(...rows.map(row=>num(row[metric])));
    const span=Math.max(1,maximum-minimum), plotW=width-left-right;
    const x=value => left+Math.max(0,Math.min(1,(value-minimum)/span))*plotW;
    const bins=new Map(), points=[];
    rows.sort((a,b)=>num(a[metric])-num(b[metric])).forEach(row => {
      const groupIndex=groups.indexOf(row.group);if(groupIndex<0)return;
      const xx=x(num(row[metric])), key=groupIndex+':'+Math.round(xx/10), rank=bins.get(key)||0;
      bins.set(key,rank+1);
      const yy=top+groupIndex*rowHeight+rowHeight/2+swarmOffset(rank);
      const colour=positionColours[row.position]||colourFor(row.group,groupIndex);
      points.push(`<circle class="visual-bee" tabindex="0" cx="${xx.toFixed(1)}" cy="${yy.toFixed(1)}" r="4.5" fill="${colour}" aria-label="${esc(row.name)}: ${num(row[metric]).toFixed(1)}"><title>${esc(row.name)} · ${esc(row.position)} · ${num(row[metric]).toFixed(1)}</title></circle>`);
    });
    const ticks=[0,.25,.5,.75,1].map(fraction => {
      const value=minimum+span*fraction,xx=x(value);
      return `<line class="visual-grid-line" x1="${xx}" x2="${xx}" y1="${top-8}" y2="${height-bottom+4}"/><text class="visual-axis-label" x="${xx}" y="${height-13}" text-anchor="middle">${value.toFixed(maximum<=10?1:0)}</text>`;
    }).join('');
    const groupLabels=groups.map((group,index) => `<text class="visual-axis-label" x="${left-9}" y="${top+index*rowHeight+rowHeight/2+4}" text-anchor="end">${esc(group)}</text>`).join('');
    host.innerHTML=`<svg class="visual-svg" viewBox="0 0 ${width} ${height}" role="img" aria-label="${esc(axisLabel)} beeswarm chart">${ticks}${groupLabels}${points.join('')}<text class="visual-axis-label" x="${left+plotW/2}" y="${height-1}" text-anchor="middle">${esc(axisLabel)}</text></svg>`;
  }

  function heatColour(value, maximum) {
    const ratio=maximum>0 ? Math.max(0,Math.min(1,value/maximum)) : 0;
    const light=18+ratio*40;
    return `hsl(${205-ratio*55} 72% ${light}%)`;
  }

  function renderHeatmap(hostId, rows, columns, getter, formatter=value=>value.toFixed(0)) {
    const host=document.getElementById(hostId);if(!host)return;
    if(!rows.length || !columns.length)return empty(host);
    const values=rows.flatMap(row => columns.map(column => num(getter(row,column))));
    const maximum=Math.max(1,...values);
    let content='<div></div>'+columns.map(column=>`<div class="visual-heatmap-head">${esc(column.label)}</div>`).join('');
    rows.forEach(row => {
      content+=`<div class="visual-heatmap-label" title="${esc(row.label)}">${esc(row.label)}</div>`;
      columns.forEach(column => {
        const value=num(getter(row,column));
        content+=`<div class="visual-heatmap-cell" style="background:${heatColour(value,maximum)}" title="${esc(row.label)} · ${esc(column.label)}: ${formatter(value)}">${formatter(value)}</div>`;
      });
    });
    host.innerHTML=`<div class="visual-heatmap" style="grid-template-columns:145px repeat(${columns.length},30px)">${content}</div>`;
  }

  function sparkline(player) {
    const values=(player.history||[]).map(row=>num(row.points));
    if(!values.length)return '<span class="muted">—</span>';
    const width=92,height=27,pad=2,minimum=Math.min(0,...values),maximum=Math.max(1,...values),span=Math.max(1,maximum-minimum);
    const points=values.map((value,index) => `${pad+(values.length===1?(width-2*pad)/2:index*(width-2*pad)/(values.length-1))},${pad+(maximum-value)*(height-2*pad)/span}`);
    const last=points[points.length-1].split(',');
    return `<svg class="visual-spark" viewBox="0 0 ${width} ${height}" role="img" aria-label="Recent points: ${values.join(', ')}"><polyline points="${points.join(' ')}"/><circle cx="${last[0]}" cy="${last[1]}" r="2.5"/></svg>`;
  }

  function inlineMetric(value) {
    const safe=Math.max(0,Math.min(100,num(value)));
    return `<div class="visual-inline-metric"><div class="visual-inline-track"><div class="visual-inline-fill" style="width:${safe}%"></div></div><strong>${safe.toFixed(0)}</strong></div>`;
  }

  function renderTable() {
    const host=document.getElementById('visual-table-players');if(!host)return;
    const rows=filteredPlayers().filter(player => num(player.minutes)>0 && Number.isFinite(Number(player.player_rating)))
      .sort((a,b)=>num(b.player_rating)-num(a.player_rating)||num(b.player_value)-num(a.player_value)).slice(0,30);
    if(!rows.length)return empty(host);
    host.innerHTML='<div class="visual-table-wrap"><table class="visual-model-table"><thead><tr><th>#</th><th>Player</th><th>Owner</th><th>Rating</th><th>Value</th><th>Season pts</th><th>Next 3</th><th>Recent GWs</th></tr></thead><tbody>'+
      rows.map((player,index)=>`<tr><td>${index+1}</td><td><strong>${esc(player.name)}</strong><span class="visual-player-meta">${esc(player.position)} · ${esc(player.team)}</span></td><td>${esc(ownerOf(player))}</td><td>${inlineMetric(player.player_rating)}</td><td>${inlineMetric(player.player_value)}</td><td>${num(player.total_points).toFixed(0)}</td><td>${num(player.next3_projected_points).toFixed(1)}</td><td>${sparkline(player)}</td></tr>`).join('')+
      '</tbody></table></div>';
  }

  function renderVisualAnalytics() {
    if(!document.getElementById('analytics-sub-visuals'))return;
    const players=allPlayers(), selected=filteredPlayers();
    const byPosition=aggregateByGameweek(players,(player)=>player.position);
    const orderedPositions=['GKP','DEF','MID','FWD'].filter(position=>byPosition.series.some(row=>row.key===position));
    byPosition.series=orderedPositions.map(position=>byPosition.series.find(row=>row.key===position));
    renderArea('visual-area-position',byPosition,orderedPositions.map(position=>positionColours[position]),orderedPositions.map(position=>positionLabels[position]));
    const byOwnership=aggregateByGameweek(players,(_player,row)=>(row.owners||[]).length?'Owned':'Free agent');
    const ownerOrder=['Owned','Free agent'].filter(key=>byOwnership.series.some(row=>row.key===key));
    byOwnership.series=ownerOrder.map(key=>byOwnership.series.find(row=>row.key===key));
    renderArea('visual-area-ownership',byOwnership,['#38bdf8','#64748b'],ownerOrder);

    const clubTotals=new Map();players.forEach(player=>clubTotals.set(player.team,(clubTotals.get(player.team)||0)+Math.max(0,num(player.total_points))));
    renderTreemap('visual-treemap-clubs',[...clubTotals].map(([label,value])=>({label,value})),'pts');
    const ownerTotals=new Map();selected.filter(player=>ownerOf(player)!=='Free agents').forEach(player=>ownerTotals.set(ownerOf(player),(ownerTotals.get(ownerOf(player))||0)+Math.max(0,num(player.player_value))));
    renderTreemap('visual-treemap-owners',[...ownerTotals].map(([label,value])=>({label,value})),'value');

    const rated=players.filter(player=>num(player.minutes)>0 && Number.isFinite(Number(player.player_rating)));
    renderBeeswarm('visual-beeswarm-rating',rated.map(player=>({...player,group:player.position})),['GKP','DEF','MID','FWD'],'player_rating','Player rating /100',[40,100]);
    const valued=selected.filter(player=>Number.isFinite(Number(player.player_value))).map(player=>({...player,group:ownerOf(player)==='Free agents'?'Free agents':'Owned'}));
    renderBeeswarm('visual-beeswarm-value',valued,['Owned','Free agents'],'player_value','Player value /100',[0,100]);

    const weeks=gameweeks(players), clubRows=[...new Set(players.map(player=>player.team))].map(label=>({label}));
    const clubWeek=new Map();players.forEach(player=>(player.history||[]).forEach(row=>clubWeek.set(player.team+'|'+row.gw,(clubWeek.get(player.team+'|'+row.gw)||0)+num(row.points))));
    clubRows.sort((a,b)=>weeks.reduce((sum,gw)=>sum+num(clubWeek.get(b.label+'|'+gw)),0)-weeks.reduce((sum,gw)=>sum+num(clubWeek.get(a.label+'|'+gw)),0));
    renderHeatmap('visual-heatmap-clubs',clubRows,weeks.map(gw=>({key:gw,label:'GW'+gw})),(row,column)=>clubWeek.get(row.label+'|'+column.key)||0);

    const positions=['GKP','DEF','MID','FWD'];
    const chosenOwners=[...new Set(selected.map(ownerOf).filter(owner=>owner!=='Free agents'))];
    const squadRows=chosenOwners.map(label=>({label}));
    renderHeatmap('visual-heatmap-squads',squadRows,positions.map(position=>({key:position,label:position})),(row,column)=>{
      const pool=selected.filter(player=>ownerOf(player)===row.label && player.position===column.key && Number.isFinite(Number(player.player_rating)));
      return pool.length ? pool.reduce((sum,player)=>sum+num(player.player_rating),0)/pool.length : 0;
    },value=>value?value.toFixed(0):'—');
    renderTable();
    const status=document.getElementById('visual-analytics-status');
    if(status)status.textContent=`${selected.length} filtered players · ${weeks.length} completed GWs`;
  }

  window.renderVisualAnalytics=renderVisualAnalytics;
  document.addEventListener('click',event=>{
    if(event.target.closest('#analytics-manager-chips, .analytics-subtab[onclick*="visuals"]')) requestAnimationFrame(renderVisualAnalytics);
  });
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',renderVisualAnalytics,{once:true});
  else renderVisualAnalytics();
})();
