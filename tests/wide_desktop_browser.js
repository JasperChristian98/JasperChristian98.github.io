window.addEventListener('DOMContentLoaded',()=>setTimeout(async()=>{
  const checks=[],check=(ok,label)=>checks.push((ok?'OK: ':'FAILED: ')+label);
  const wait=()=>new Promise(resolve=>setTimeout(resolve,80));
  try{
    enterManagerDashboard();
    const wide=innerWidth>=1800,workspace=document.getElementById('mcd-workspace'),header=document.querySelector('.header-top');
    if(wide){
      check(workspace.getBoundingClientRect().width>1770,'large desktop workspace expands');
      check(workspace.getBoundingClientRect().width<=2321,'workspace capped on larger monitors');
      check(header.getBoundingClientRect().width>1500,'header expands with desktop content');
    }else check(workspace.getBoundingClientRect().width<=1771,'smaller viewports retain existing workspace limit');
    for(const page of ['overview','players','myteam','analytics','manager-styles']){
      showPage(page);await wait();
      const active=document.getElementById('page-'+page);
      check(active.getBoundingClientRect().right<=innerWidth+1,page+' fits viewport');
      check(document.documentElement.scrollWidth<=innerWidth+1,page+' has no document-wide horizontal scroll');
    }
    showPage('myteam');showMyTeamSubtab('war-room',document.querySelector('.myteam-tab[data-myteam-section="war-room"]'));await wait();
    const panels=[...document.querySelectorAll('.war-room-team-panel')];
    if(wide)check(panels.length===2&&Math.abs(panels[0].getBoundingClientRect().top-panels[1].getBoundingClientRect().top)<2,'War Room pitches sit side by side');
    if(wide){workspace.style.transition='none';workspace.classList.add('mcd-compact');await wait();const sidebarWidth=document.querySelector('.mcd-sidebar').getBoundingClientRect().width;check(sidebarWidth<=73,'collapsed sidebar remains compact ('+sidebarWidth+'px)');workspace.classList.remove('mcd-compact');}
    check(document.querySelector('.global-search-input').getBoundingClientRect().width>80,'search remains usable');
  }catch(e){checks.push('FAILED: '+e.stack);}
  const report=document.createElement('pre');report.id='wide-desktop-report';report.textContent=JSON.stringify(checks);document.body.append(report);
},350));
