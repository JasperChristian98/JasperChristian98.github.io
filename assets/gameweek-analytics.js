(() => {
  'use strict';
  const esc=value=>String(value??'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');
  const average=values=>values.length?values.reduce((sum,value)=>sum+value,0)/values.length:0;
  const round=value=>Number(value||0).toFixed(1);
  const colour=(manager,index)=>typeof MANAGER_COLORS!=='undefined'&&MANAGER_COLORS[manager]?MANAGER_COLORS[manager]:['#38bdf8','#f472b6','#4ade80','#facc15','#a78bfa','#fb923c'][index%6];

  function source(){
    const original=typeof TREND_DATA==='undefined'||!TREND_DATA.scores?{}:TREND_DATA.scores;
    if(!window.MCDraftPositionFilter||window.MCDraftPositionFilter.isAll()||typeof playerSearchData==='undefined')return original;
    const allowed=window.MCDraftPositionFilter.positions(),totals=new Map();
    playerSearchData.filter(player=>allowed.has(player.position)).forEach(player=>(player.history||[]).forEach(row=>{
      const manager=(row.owners||[])[0];if(!manager)return;const key=manager+'|'+Number(row.gw);totals.set(key,(totals.get(key)||0)+(Number(row.points)||0));
    }));
    const managers=typeof MANAGER_ORDER==='undefined'?Object.keys(original):MANAGER_ORDER;
    return Object.fromEntries(managers.map(manager=>[manager,[...totals].filter(([key])=>key.startsWith(manager+'|')).map(([key,value])=>[Number(key.slice(manager.length+1)),value]).sort((a,b)=>a[0]-b[0])]));
  }
  function selectedManagers(){
    const data=source(),container=document.getElementById('analytics-manager-chips');
    if(!container||!container.querySelector('.chart-chip'))return (typeof MANAGER_ORDER==='undefined'?Object.keys(data):MANAGER_ORDER).filter(manager=>data[manager]?.length);
    const active=new Set([...container.querySelectorAll('.chart-chip.active')].map(chip=>chip.textContent.trim()));
    return (typeof MANAGER_ORDER==='undefined'?Object.keys(data):MANAGER_ORDER).filter(manager=>active.has(manager)&&data[manager]?.length);
  }
  function weeks(){return [...new Set(Object.values(source()).flatMap(rows=>rows.map(row=>Number(row[0]))))].sort((a,b)=>a-b);}
  function values(manager){return (source()[manager]||[]).map(row=>Number(row[1])||0);}
  function valueAt(manager,gw){const row=(source()[manager]||[]).find(item=>Number(item[0])===Number(gw));return row?Number(row[1])||0:null;}
  function quantile(items,q){if(!items.length)return 0;const sorted=[...items].sort((a,b)=>a-b),position=(sorted.length-1)*q,base=Math.floor(position),rest=position-base;return sorted[base]+(sorted[base+1]===undefined?0:rest*(sorted[base+1]-sorted[base]));}
  function deviation(items){if(items.length<2)return 0;const mean=average(items);return Math.sqrt(average(items.map(value=>(value-mean)**2)));}
  function empty(host,message='Choose at least one manager to populate this view.'){host.innerHTML='<div class="visual-empty">'+esc(message)+'</div>';}
  function leagueAverage(gw){const scores=Object.keys(source()).map(manager=>valueAt(manager,gw)).filter(value=>value!==null);return average(scores);}

  function scoreColour(value,minimum,maximum){const ratio=maximum>minimum?(value-minimum)/(maximum-minimum):.5;return `hsl(${215-ratio*85} 68% ${24+ratio*34}%)`;}
  function rankColour(rank,total){const ratio=total>1?(rank-1)/(total-1):0;return `hsl(${145-ratio*140} 62% ${36+ratio*8}%)`;}
  function renderHeatmaps(managers,gws){
    const allScores=Object.values(source()).flatMap(rows=>rows.map(row=>Number(row[1])||0)),minimum=Math.min(...allScores,0),maximum=Math.max(...allScores,1);
    const scoreHost=document.getElementById('gw-lab-score-heatmap'),rankHost=document.getElementById('gw-lab-rank-heatmap');
    if(!managers.length){empty(scoreHost);empty(rankHost);return;}
    const header='<div></div>'+gws.map(gw=>`<div class="gw-heat-head">GW${gw}</div>`).join('');
    let score=header,rank=header;
    managers.forEach(manager=>{
      score+=`<div class="gw-heat-manager" title="${esc(manager)}">${esc(manager)}</div>`;
      rank+=`<div class="gw-heat-manager" title="${esc(manager)}">${esc(manager)}</div>`;
      gws.forEach(gw=>{
        const value=valueAt(manager,gw);
        const weekly=Object.keys(source()).map(name=>({name,value:valueAt(name,gw)})).filter(row=>row.value!==null).sort((a,b)=>b.value-a.value);
        const position=weekly.findIndex(row=>row.name===manager)+1;
        score+=value===null?'<div class="gw-heat-cell" style="background:#334155">—</div>':`<div class="gw-heat-cell" style="background:${scoreColour(value,minimum,maximum)}" title="${esc(manager)} · GW${gw}: ${round(value)}">${Math.round(value)}</div>`;
        rank+=position<1?'<div class="gw-heat-cell" style="background:#334155">—</div>':`<div class="gw-heat-cell" style="background:${rankColour(position,weekly.length)}" title="${esc(manager)} · GW${gw}: rank ${position}">#${position}</div>`;
      });
    });
    const style=`grid-template-columns:190px repeat(${gws.length},42px)`;
    scoreHost.innerHTML=`<div class="gw-heatmap" style="${style}">${score}</div>`;
    rankHost.innerHTML=`<div class="gw-heatmap" style="${style}">${rank}</div>`;
  }

  function renderDistribution(managers){
    const host=document.getElementById('gw-lab-distribution');if(!managers.length)return empty(host);
    const all=managers.flatMap(values),minimum=Math.min(...all,0),maximum=Math.max(...all,1),span=Math.max(1,maximum-minimum);
    const width=930,left=190,right=24,top=25,rowHeight=48,bottom=36,height=top+managers.length*rowHeight+bottom,plotW=width-left-right;
    const x=value=>left+(value-minimum)/span*plotW;
    const ticks=[0,.25,.5,.75,1].map(fraction=>{const value=minimum+span*fraction,xx=x(value);return `<line class="gw-lab-gridline" x1="${xx}" x2="${xx}" y1="${top-12}" y2="${height-bottom+5}"/><text class="gw-lab-axis" x="${xx}" y="${height-10}" text-anchor="middle">${Math.round(value)}</text>`;}).join('');
    const rows=managers.map((manager,index)=>{
      const data=values(manager),low=Math.min(...data),q1=quantile(data,.25),median=quantile(data,.5),q3=quantile(data,.75),high=Math.max(...data),mean=average(data),yy=top+index*rowHeight+rowHeight/2,c=colour(manager,index);
      const dots=(source()[manager]||[]).map(row=>`<circle class="gw-score-dot" cx="${x(Number(row[1])||0)}" cy="${yy}" r="4" fill="${c}"><title>${esc(manager)} · GW${row[0]}: ${round(row[1])}</title></circle>`).join('');
      return `<text class="gw-lab-axis" x="${left-10}" y="${yy+4}" text-anchor="end">${esc(manager)}</text><line class="gw-box-line" x1="${x(low)}" x2="${x(high)}" y1="${yy}" y2="${yy}"/><rect class="gw-box-iqr" x="${x(q1)}" y="${yy-10}" width="${Math.max(2,x(q3)-x(q1))}" height="20" rx="5"/><line class="gw-box-median" x1="${x(median)}" x2="${x(median)}" y1="${yy-10}" y2="${yy+10}"/>${dots}<circle class="gw-box-average" cx="${x(mean)}" cy="${yy}" r="5"><title>Average ${round(mean)}</title></circle>`;
    }).join('');
    host.innerHTML=`<svg class="gw-lab-svg" viewBox="0 0 ${width} ${height}" role="img" aria-label="Manager score distributions">${ticks}${rows}</svg>`;
  }

  function renderConsistency(managers){
    const host=document.getElementById('gw-lab-consistency');if(!managers.length)return empty(host);
    const rows=managers.map((manager,index)=>({manager,index,avg:average(values(manager)),sd:deviation(values(manager))}));
    const width=720,height=360,left=48,right=20,top=24,bottom=43,plotW=width-left-right,plotH=height-top-bottom;
    const minX=Math.min(...rows.map(row=>row.avg))-2,maxX=Math.max(...rows.map(row=>row.avg))+2,maxY=Math.max(1,...rows.map(row=>row.sd))+1;
    const x=value=>left+(value-minX)/Math.max(1,maxX-minX)*plotW,y=value=>top+(1-value/maxY)*plotH;
    const grid=[0,.25,.5,.75,1].map(fraction=>`<line class="gw-lab-gridline" x1="${left+plotW*fraction}" x2="${left+plotW*fraction}" y1="${top}" y2="${top+plotH}"/><line class="gw-lab-gridline" x1="${left}" x2="${left+plotW}" y1="${top+plotH*fraction}" y2="${top+plotH*fraction}"/>`).join('');
    const points=rows.map(row=>`<g tabindex="0"><circle class="gw-scatter-dot" cx="${x(row.avg)}" cy="${y(row.sd)}" r="7" fill="${colour(row.manager,row.index)}"><title>${esc(row.manager)} · avg ${round(row.avg)} · volatility ${round(row.sd)}</title></circle><text class="gw-scatter-label" x="${x(row.avg)+10}" y="${y(row.sd)+3}">${esc(row.manager.length>17?row.manager.slice(0,16)+'…':row.manager)}</text></g>`).join('');
    host.innerHTML=`<svg class="gw-lab-svg" viewBox="0 0 ${width} ${height}" role="img" aria-label="Average score against volatility">${grid}${points}<text class="gw-lab-axis" x="${left+plotW/2}" y="${height-7}" text-anchor="middle">Average weekly score →</text><text class="gw-lab-axis" transform="translate(12 ${top+plotH/2}) rotate(-90)" text-anchor="middle">Volatility (lower is steadier) →</text></svg>`;
  }

  function renderBoomBust(managers,gws){
    const host=document.getElementById('gw-lab-boom-bust');if(!managers.length)return empty(host);
    host.innerHTML='<div class="gw-boom-list">'+managers.map(manager=>{
      let boom=0,bust=0,steady=0;
      gws.forEach(gw=>{const value=valueAt(manager,gw);if(value===null)return;const delta=value-leagueAverage(gw);if(delta>=10)boom++;else if(delta<=-10)bust++;else steady++;});
      const total=Math.max(1,boom+bust+steady);
      return `<div class="gw-boom-row"><div class="gw-boom-name" title="${esc(manager)}">${esc(manager)}</div><div class="gw-boom-track"><i class="gw-boom" style="width:${boom/total*100}%"></i><i class="gw-steady" style="width:${steady/total*100}%"></i><i class="gw-bust" style="width:${bust/total*100}%"></i></div><div class="gw-boom-counts">${boom} boom · ${bust} bust</div></div>`;
    }).join('')+'</div>';
  }

  function sparkline(data){
    if(!data.length)return '—';const width=120,height=28,pad=2,min=Math.min(0,...data),max=Math.max(1,...data),span=Math.max(1,max-min);
    const points=data.map((value,index)=>`${pad+(data.length===1?(width-2*pad)/2:index*(width-2*pad)/(data.length-1))},${pad+(max-value)*(height-2*pad)/span}`),last=points.at(-1).split(',');
    return `<svg class="gw-mini-spark" viewBox="0 0 ${width} ${height}" role="img" aria-label="Scores ${data.join(', ')}"><polyline points="${points.join(' ')}"/><circle cx="${last[0]}" cy="${last[1]}" r="2.5"/></svg>`;
  }
  function metrics(manager){const data=values(manager),avg=average(data),last3=average(data.slice(-3));return {manager,data,avg,median:quantile(data,.5),high:Math.max(...data),low:Math.min(...data),sd:deviation(data),last3,delta:last3-avg};}
  function renderTable(managers){
    const host=document.getElementById('gw-lab-table');if(!managers.length)return empty(host);
    const rows=managers.map(metrics).sort((a,b)=>b.avg-a.avg);
    host.innerHTML='<div class="gw-lab-table-wrap"><table class="gw-lab-table"><thead><tr><th>#</th><th>Manager</th><th>Average</th><th>Median</th><th>High</th><th>Low</th><th>Volatility</th><th>Last 3</th><th>Momentum</th><th>Weekly scores</th></tr></thead><tbody>'+rows.map((row,index)=>`<tr><td>${index+1}</td><td><strong>${esc(row.manager)}</strong></td><td>${round(row.avg)}</td><td>${round(row.median)}</td><td>${round(row.high)}</td><td>${round(row.low)}</td><td>${round(row.sd)}</td><td>${round(row.last3)}</td><td class="${row.delta>=0?'gw-momentum-up':'gw-momentum-down'}">${row.delta>=0?'+':''}${round(row.delta)}</td><td>${sparkline(row.data)}</td></tr>`).join('')+'</tbody></table></div>';
  }

  function renderSummary(managers){
    const host=document.getElementById('gw-lab-summary');if(!managers.length){host.innerHTML='';return;}
    const rows=managers.map(metrics),best=[...rows].sort((a,b)=>b.avg-a.avg)[0],steady=[...rows].sort((a,b)=>a.sd-b.sd)[0],ceiling=[...rows].sort((a,b)=>b.high-a.high)[0],momentum=[...rows].sort((a,b)=>b.delta-a.delta)[0];
    const cards=[['Scoring leader',`${best.manager} average ${round(best.avg)} points per completed GW.`],['Steadiest floor',`${steady.manager} have the lowest weekly volatility at ${round(steady.sd)}.`],['Highest ceiling',`${ceiling.manager} own the top single-week score: ${round(ceiling.high)}.`],['Momentum',`${momentum.manager} are ${momentum.delta>=0?'+':''}${round(momentum.delta)} points above their season pace across the last three.`]];
    host.innerHTML=cards.map(([label,text])=>`<div class="analytics-insight"><span>${esc(label)}</span><strong>${esc(text)}</strong></div>`).join('');
  }

  function renderGameweekLab(){
    if(!document.getElementById('analytics-sub-gameweek-lab'))return;
    const managers=selectedManagers(),gws=weeks();
    renderSummary(managers);renderHeatmaps(managers,gws);renderDistribution(managers);renderConsistency(managers);renderBoomBust(managers,gws);renderTable(managers);
    const status=document.getElementById('gw-lab-status');if(status)status.textContent=`${managers.length} managers · ${gws.length} gameweeks`;
  }
  function initialise(){
    const chips=document.getElementById('analytics-manager-chips');if(chips){let pending=false;new MutationObserver(()=>{if(pending)return;pending=true;requestAnimationFrame(()=>{pending=false;renderGameweekLab();});}).observe(chips,{childList:true,subtree:true,attributes:true,attributeFilter:['class']});}
    if(window.MCDraftPositionFilter)window.MCDraftPositionFilter.subscribe(()=>renderGameweekLab());
    renderGameweekLab();
  }
  window.renderGameweekLab=renderGameweekLab;
  document.addEventListener('click',event=>{if(event.target.closest('.analytics-subtab[onclick*="gameweek-lab"]'))requestAnimationFrame(renderGameweekLab);});
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',initialise,{once:true});else initialise();
})();
