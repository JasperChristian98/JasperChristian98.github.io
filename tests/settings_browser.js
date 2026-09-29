window.addEventListener('DOMContentLoaded',()=>setTimeout(()=>{
  const checks=[],check=(ok,label)=>checks.push((ok?'OK: ':'FAILED: ')+label),$=id=>document.getElementById(id);
  const change=(id,value)=>{$(id).value=value;$(id).dispatchEvent(new Event('change',{bubbles:true}));};
  try{
    const welcome=$('mcd-welcome-team');welcome.value=MANAGER_ORDER[0];enterManagerDashboard();
    const nav=document.querySelector('[data-mcd-page="settings"]');
    check(Boolean(nav),'Settings is in the dashboard navigation');nav.click();
    check($('page-settings').classList.contains('active'),'Settings opens through navigation');
    const phase=new URLSearchParams(location.search).get('phase');
    if(phase==='save'){
      change('settings-theme','light');change('settings-motion','reduced');
      check(document.body.dataset.theme==='light','theme applies immediately');
      check(document.documentElement.dataset.motion==='reduced','motion preference applies immediately');
      check(JSON.parse(localStorage.getItem('mcdraft-settings-v1')).theme==='light','preferences are stored');
      const probe=document.createElement('i');probe.className='atlas-bar-fill';document.body.append(probe);
      check(getComputedStyle(probe).animationName==='none','reduced motion disables chart animations');probe.remove();
      localStorage.setItem('mcdraft-player-watchlist-v1','[]');
    }else{
      check($('settings-theme').value==='light'&&document.body.dataset.theme==='light','appearance survives a fresh browser launch');
      check($('settings-motion').value==='reduced'&&document.documentElement.dataset.motion==='reduced','motion survives a fresh browser launch');
      $('theme-toggle').click();
      check($('settings-theme').value==='dark','header theme toggle updates Settings');
      const manager=localStorage.getItem('mcdraft-preferred-manager-v1');
      $('settings-reset').click();
      check($('settings-theme').value==='system'&&$('settings-motion').value==='system','reset restores device preferences');
      check(document.body.dataset.theme===(matchMedia('(prefers-color-scheme: light)').matches?'light':'dark'),'device theme is resolved');
      check(localStorage.getItem('mcdraft-player-watchlist-v1')==='[]'&&localStorage.getItem('mcdraft-preferred-manager-v1')===manager,'reset preserves watchlist and team');
      localStorage.setItem('mcdraft-settings-v1',JSON.stringify({theme:'light',motion:'reduced'}));
      window.dispatchEvent(new StorageEvent('storage',{key:'mcdraft-settings-v1'}));
      check($('settings-theme').value==='light'&&document.documentElement.dataset.motion==='reduced','preferences synchronize from another tab');
      const original=Storage.prototype.setItem;
      Storage.prototype.setItem=function(){throw new DOMException('Blocked','SecurityError');};
      try{
        change('settings-theme','dark');
        check(document.body.dataset.theme==='dark'&&$('settings-status').textContent.includes('visit only'),'blocked storage keeps controls usable and explains persistence');
      }finally{Storage.prototype.setItem=original;}
    }
    showPage('overview');check(!$('page-settings').classList.contains('active'),'Settings closes when navigating away');
  }catch(error){checks.push('FAILED: '+error.stack);}
  const report=document.createElement('pre');report.id='settings-report';report.textContent=JSON.stringify(checks);document.body.append(report);
},700));
