window.addEventListener('DOMContentLoaded',()=>setTimeout(async()=>{
  const checks=[],check=(ok,label)=>checks.push((ok?'OK: ':'FAILED: ')+label),wait=()=>new Promise(resolve=>setTimeout(resolve,100));
  try{
    const welcome=document.getElementById('mcd-welcome-team');
    if(welcome){welcome.value=MANAGER_ORDER[0];enterManagerDashboard();setAnalyticsManagerPreset('all');await wait();}
    const api=window.MCDChartAtlas;
    check(Boolean(api),'Chart Atlas API is available');
    check(Boolean(window.MCDraftPositionFilter),'shared Analytics position filter is available');
    check(document.querySelectorAll('#analytics-position-filter .analytics-position-button').length===5,'shared position controls appear beside the manager filter');
    if(!api)throw new Error('Chart Atlas did not initialise');
    check(api.count===100,'exactly 100 chart specifications exist');
    check(document.querySelectorAll('.chart-atlas').length===16,'atlas appears on all sixteen Analytics pages');
    check(document.querySelectorAll('.atlas-card').length===100,'exactly 100 chart cards are mounted');
    const expected={insights:4,matrices:4,ratings:4,player:12,relationships:4,'river-passport':4,club:10,'squad-strength':10,'squad-build':8,decisions:6,availability:4,fixtures:6,season:8,'league-stats':4,gameweek:6,visuals:6};
    Object.entries(expected).forEach(([target,count])=>check(document.querySelectorAll(`.chart-atlas[data-atlas-target="${target}"] .atlas-card`).length===count,`${target} receives ${count} charts`));
    Object.keys(expected).forEach(target=>api.renderTarget(target));
    const fullGameweekOutput=[...document.querySelectorAll('#gw-lab-score-heatmap .gw-heat-cell')].map(cell=>cell.textContent).join('|');
    check(document.querySelectorAll('.atlas-host svg,.atlas-host .atlas-bar-list,.atlas-host .atlas-stack-list').length===100,'all 100 chart hosts render visual output');
    check([...document.querySelectorAll('.atlas-card')].every(card=>card.classList.contains('card')&&card.classList.contains('analytics-chart-card')),'atlas cards use the standard Analytics card formatting');
    // Measure rendered fills: the presence of chart markup does not prove bars are visible.
    // Mount copies outside inactive tabs so every bar chart participates in layout.
    const barProbe=document.createElement('article');barProbe.className='card analytics-chart-card atlas-card';barProbe.style.width='600px';
    document.body.append(barProbe);
    const barLists=[...document.querySelectorAll('.atlas-host .atlas-bar-list')];
    let measuredBars=0;
    const barsVisible=barLists.every(list=>{
      barProbe.replaceChildren(list.cloneNode(true));
      return [...barProbe.querySelectorAll('.atlas-bar-fill')].every(fill=>{
        if(parseFloat(fill.style.width)<=0)return true;
        measuredBars++;
        const bounds=fill.getBoundingClientRect(),track=fill.parentElement.getBoundingClientRect();
        return bounds.width>0&&bounds.height>0&&bounds.width<=track.width&&bounds.height<=track.height;
      });
    });
    barProbe.remove();
    check(measuredBars>0&&barsVisible,'nonzero values produce visible bar fills within their tracks across atlas charts');
    const seriesLines=[...document.querySelectorAll('.atlas-series-line')];
    check(seriesLines.length>5,'weekly charts draw visible line series');
    check(seriesLines.every(line=>{const style=getComputedStyle(line);return style.stroke!=='none'&&style.stroke!=='transparent'&&parseFloat(style.strokeWidth)>=3;}),'line series have visible themed strokes');
    const playerSection=document.querySelector('.chart-atlas[data-atlas-target="player"]');
    const before=playerSection.querySelectorAll('[data-atlas-position]').length;
    api.setPosition('MID');await wait();api.renderTarget('player');
    const marks=[...playerSection.querySelectorAll('[data-atlas-position]')];
    check(before>10&&marks.length>0,'player charts contain filtered marks');
    check(marks.every(mark=>mark.dataset.atlasPosition==='MID'),'position filter restricts chart marks to midfielders');
    check(document.querySelector('[data-visual-position="MID"]')?.classList.contains('active'),'Visual Analytics uses the shared position state');
    const visibleLegacy=[...document.querySelectorAll('#analytics-sub-player [data-player-id]:not([hidden])')];
    const wrongLegacy=visibleLegacy.filter(row=>playerSearchData.find(player=>Number(player.id)===Number(row.dataset.playerId))?.position!=='MID');
    check(visibleLegacy.length>0&&!wrongLegacy.length,'legacy Player Analytics charts use the shared position filter'+(wrongLegacy.length?' · '+wrongLegacy.slice(0,3).map(row=>row.dataset.playerId+':'+row.className).join(', '):''));
    check(typeof ratingLabPool==='function'&&ratingLabPool().every(player=>player.position==='MID'),'Rating Lab uses the shared position filter');
    const relationship=typeof relationshipAssemble==='function'?relationshipAssemble():{nodes:[]};
    check(relationship.nodes.length>0&&relationship.nodes.every(node=>node.position==='MID'),'Player Relationships uses the shared position filter');
    const filteredGameweekOutput=[...document.querySelectorAll('#gw-lab-score-heatmap .gw-heat-cell')].map(cell=>cell.textContent).join('|');
    check(filteredGameweekOutput.length>0&&filteredGameweekOutput!==fullGameweekOutput,'Gameweek Lab recalculates output for selected positions');
    showAnalyticsSubtab('river-passport',null);renderTransferRiverPassport();
    const moverNames=[...document.querySelectorAll('#player-passport-detail .passport-mover-list b')].map(node=>node.textContent.trim());
    const wrongMovers=moverNames.filter(name=>!playerSearchData.some(player=>player.name===name&&player.position==='MID'));
    check(moverNames.length>0&&!wrongMovers.length,'Transfer River player lists use the shared position filter'+(wrongMovers.length?' · '+wrongMovers.slice(0,4).join(', '):''));
    api.setPosition('ALL');
    document.querySelector('[data-visual-position="MID"]')?.click();
    check(window.MCDraftPositionFilter.positions().size===1&&window.MCDraftPositionFilter.allows('MID'),'Visual Analytics shortcut changes the shared position state');
    check(document.querySelectorAll('#visual-area-position path').length===1,'Visual Analytics shortcut redraws its charts immediately');
    api.setPosition('ALL');
    if(typeof setAnalyticsManagerPreset==='function'&&typeof toggleAnalyticsManager==='function'){
      setAnalyticsManagerPreset('none');toggleAnalyticsManager(MANAGER_ORDER[0]);await wait();api.renderTarget('player');
      const ownerMarks=[...playerSection.querySelectorAll('[data-atlas-owner]')].filter(mark=>mark.dataset.atlasOwner);
      check(ownerMarks.length>0&&ownerMarks.every(mark=>mark.dataset.atlasOwner===MANAGER_ORDER[0]),'manager filter restricts player chart marks');
      setAnalyticsManagerPreset('all');
    }
    for(const position of ['GKP','DEF','MID','FWD']){
      api.setPosition('ALL');api.setPosition(position);
      const cards=[...document.querySelectorAll('#page-analytics .analytics-player-bar-card')];
      check(cards.length>0&&cards.every(card=>{
        const rows=[...card.querySelectorAll('.analytics-player-bar')];
        const eligible=rows.filter(row=>playerSearchData.find(player=>Number(player.id)===Number(row.dataset.playerId))?.position===position);
        const expected=eligible.slice(0,Number(card.dataset.playerLimit||20));
        const visible=rows.filter(row=>!row.hidden);
        return expected.length===visible.length&&expected.every((row,index)=>row===visible[index]);
      }),`${position} leaderboards filter before applying their row limit`);
      const atlasPlayers=[...document.querySelectorAll('.atlas-bar-row[data-atlas-player-id]')];
      check(atlasPlayers.length>0&&atlasPlayers.every(row=>row.dataset.atlasPosition===position),`${position} filters player bars across all atlas pages`);
    }
    api.setPosition('ALL');
    check(playerSection.querySelectorAll('[data-atlas-position]').length===before,'All restores the original atlas player marks');
    check([...document.querySelectorAll('.analytics-player-bar:not([hidden])')].every(row=>row.getAttribute('aria-hidden')!=='true'),'restored player bars are accessible');
    for(const activation of ['click','Enter',' ']){
      showPage('analytics');showAnalyticsSubtab('player',null);api.renderTarget('player');
      const row=playerSection.querySelector('.atlas-bar-row[data-atlas-player-id]');
      const id=row.dataset.atlasPlayerId;
      document.getElementById('player-position-filter').value='GKP';
      if(activation==='click')row.querySelector('.atlas-bar-fill').click();
      else row.dispatchEvent(new KeyboardEvent('keydown',{key:activation,bubbles:true,cancelable:true}));
      await wait();
      for(let attempt=0;attempt<20&&document.getElementById('player-details-'+id)?.style.display!=='block';attempt++)await wait();
      const details=document.getElementById('player-details-'+id);
      check(document.getElementById('page-players').classList.contains('active')&&details?.style.display==='block'&&details.getBoundingClientRect().height>0,`${JSON.stringify(activation)} opens the exact player's visible details`);
      check(document.getElementById('player-search-results').firstElementChild===document.activeElement,'player details receive keyboard focus');
    }
    showPage('analytics');showAnalyticsSubtab('club',null);api.renderTarget('club');
    const clubBar=document.querySelector('.chart-atlas[data-atlas-target="club"] .atlas-bar-row');
    clubBar.click();
    check(!clubBar.hasAttribute('data-atlas-player-id')&&document.getElementById('page-analytics').classList.contains('active'),'group bars keep chart inspection without opening a player');
  }catch(error){checks.push('FAILED: '+error.stack);}
  const report=document.createElement('pre');report.id='chart-atlas-report';report.textContent=JSON.stringify(checks);document.body.append(report);
},650));
