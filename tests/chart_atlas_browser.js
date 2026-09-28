window.addEventListener('DOMContentLoaded',()=>setTimeout(async()=>{
  const checks=[],check=(ok,label)=>checks.push((ok?'OK: ':'FAILED: ')+label),wait=()=>new Promise(resolve=>setTimeout(resolve,100));
  try{
    const api=window.MCDChartAtlas;
    check(Boolean(api),'Chart Atlas API is available');
    check(api.count===100,'exactly 100 chart specifications exist');
    check(document.querySelectorAll('.chart-atlas').length===16,'atlas appears on all sixteen Analytics pages');
    check(document.querySelectorAll('.atlas-card').length===100,'exactly 100 chart cards are mounted');
    const expected={insights:4,matrices:4,ratings:4,player:12,relationships:4,'river-passport':4,club:10,'squad-strength':10,'squad-build':8,decisions:6,availability:4,fixtures:6,season:8,'league-stats':4,gameweek:6,visuals:6};
    Object.entries(expected).forEach(([target,count])=>check(document.querySelectorAll(`.chart-atlas[data-atlas-target="${target}"] .atlas-card`).length===count,`${target} receives ${count} charts`));
    Object.keys(expected).forEach(target=>api.renderTarget(target));
    check(document.querySelectorAll('.atlas-host svg,.atlas-host .atlas-bar-list,.atlas-host .atlas-stack-list').length===100,'all 100 chart hosts render visual output');
    const playerSection=document.querySelector('.chart-atlas[data-atlas-target="player"]');
    const before=playerSection.querySelectorAll('[data-atlas-position]').length;
    api.setPosition('MID');await wait();api.renderTarget('player');
    const marks=[...playerSection.querySelectorAll('[data-atlas-position]')];
    check(before>10&&marks.length>0,'player charts contain filtered marks');
    check(marks.every(mark=>mark.dataset.atlasPosition==='MID'),'position filter restricts chart marks to midfielders');
    api.setPosition('ALL');
    if(typeof setAnalyticsManagerPreset==='function'&&typeof toggleAnalyticsManager==='function'){
      setAnalyticsManagerPreset('none');toggleAnalyticsManager(MANAGER_ORDER[0]);await wait();api.renderTarget('player');
      const ownerMarks=[...playerSection.querySelectorAll('[data-atlas-owner]')].filter(mark=>mark.dataset.atlasOwner);
      check(ownerMarks.length>0&&ownerMarks.every(mark=>mark.dataset.atlasOwner===MANAGER_ORDER[0]),'manager filter restricts player chart marks');
      setAnalyticsManagerPreset('all');
    }
  }catch(error){checks.push('FAILED: '+error.stack);}
  const report=document.createElement('pre');report.id='chart-atlas-report';report.textContent=JSON.stringify(checks);document.body.append(report);
},650));
