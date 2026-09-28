window.addEventListener('DOMContentLoaded',()=>setTimeout(async()=>{
  const checks=[],check=(ok,label)=>checks.push((ok?'OK: ':'FAILED: ')+label),wait=()=>new Promise(resolve=>setTimeout(resolve,160));
  try{
    enterManagerDashboard();
    const sidebar=[...document.querySelectorAll('.mcd-nav-link')].find(link=>link.textContent.trim()==='Gameweek Lab');
    sidebar?.click();renderGameweekLab();
    check(Boolean(sidebar),'Gameweek Lab appears in sidebar');
    check(document.getElementById('analytics-sub-gameweek-lab')?.classList.contains('active'),'sidebar opens Gameweek Lab');
    check(document.querySelectorAll('#gw-lab-score-heatmap .gw-heat-cell').length>=20,'score heatmap renders actual output');
    check(document.querySelectorAll('#gw-lab-rank-heatmap .gw-heat-cell').length>=20,'rank heatmap renders');
    check(document.querySelectorAll('#gw-lab-distribution .gw-box-iqr').length>=2,'score distributions render');
    check(document.querySelectorAll('#gw-lab-consistency .gw-scatter-dot').length>=2,'consistency scatter renders');
    check(document.querySelectorAll('#gw-lab-boom-bust .gw-boom-row').length>=2,'boom and bust view renders');
    check(document.querySelectorAll('#gw-lab-table tbody tr').length>=2,'weekly output table renders');
    check(document.querySelectorAll('#gw-lab-summary .analytics-insight').length===4,'weekly summary renders');
    const allRows=document.querySelectorAll('#gw-lab-table tbody tr').length;
    setAnalyticsManagerPreset('none');toggleAnalyticsManager(MANAGER_ORDER[0]);await wait();
    check(document.querySelectorAll('#gw-lab-table tbody tr').length===1&&allRows>1,'manager filter updates Gameweek Lab');
    setAnalyticsManagerPreset('none');await wait();
    check(Boolean(document.querySelector('#gw-lab-score-heatmap .visual-empty')),'empty manager filter clears Gameweek Lab');
    setAnalyticsManagerPreset('all');await wait();
  }catch(error){checks.push('FAILED: '+error.stack);}
  const report=document.createElement('pre');report.id='gameweek-analytics-report';report.textContent=JSON.stringify(checks);document.body.append(report);
},450));
