window.addEventListener('DOMContentLoaded',()=>setTimeout(()=>{
  const checks=[],check=(ok,label)=>checks.push((ok?'OK: ':'FAILED: ')+label);
  try{
    enterManagerDashboard();
    showPage('analytics');
    const tab=document.querySelector('.analytics-subtab[onclick*="visuals"]');
    showAnalyticsSubtab('visuals',tab);
    renderVisualAnalytics();
    check(Boolean(tab),'Visual Analytics tab exists');
    check(document.getElementById('analytics-sub-visuals')?.classList.contains('active'),'Visual Analytics page opens');
    check(document.querySelectorAll('#visual-area-position path').length>=4,'position stacked area renders');
    check(document.querySelectorAll('#visual-area-ownership path').length>=2,'ownership stacked area renders');
    check(document.querySelectorAll('#visual-treemap-clubs .visual-tree-cell').length>=10,'club convex treemap renders');
    check(document.querySelectorAll('#visual-treemap-owners .visual-tree-cell').length>=2,'owner convex treemap renders');
    check(document.querySelectorAll('#visual-beeswarm-rating .visual-bee').length>=20,'rating beeswarm renders');
    check(document.querySelectorAll('#visual-beeswarm-value .visual-bee').length>=20,'value beeswarm renders');
    check(document.querySelectorAll('#visual-heatmap-clubs .visual-heatmap-cell').length>=20,'club heatmap renders');
    check(document.querySelectorAll('#visual-heatmap-squads .visual-heatmap-cell').length>=4,'squad heatmap renders');
    check(document.querySelectorAll('#visual-table-players tbody tr').length>=10,'table chart renders');
    check(Boolean(document.getElementById('visual-analytics-status')?.textContent),'chart status describes data');
    setAnalyticsManagerPreset('none');renderVisualAnalytics();
    check(Boolean(document.querySelector('#visual-treemap-owners .visual-empty')),'owner charts follow manager filter');
    setAnalyticsManagerPreset('all');renderVisualAnalytics();
  }catch(error){checks.push('FAILED: '+error.stack);}
  const report=document.createElement('pre');report.id='visual-analytics-report';report.textContent=JSON.stringify(checks);document.body.append(report);
},450));
