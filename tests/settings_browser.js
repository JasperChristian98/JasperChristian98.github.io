window.addEventListener('DOMContentLoaded',()=>setTimeout(()=>{
  const checks=[],check=(ok,label)=>checks.push((ok?'OK: ':'FAILED: ')+label),$=id=>document.getElementById(id);
  const change=(id,value)=>{$(id).value=value;$(id).dispatchEvent(new Event('change',{bubbles:true}));};
  try{
    if(new URLSearchParams(location.search).get('phase')==='reload'){check($('mcd-manager-welcome').hidden,'saved team skips welcome');check($('page-calendar').classList.contains('active'),'saved landing page opens');}
    const welcome=$('mcd-welcome-team');welcome.value=MANAGER_ORDER[0];enterManagerDashboard();
    const nav=document.querySelector('[data-mcd-page="settings"]');
    check(Boolean(nav),'Settings is in the dashboard navigation');nav.click();
    check($('page-settings').classList.contains('active'),'Settings opens through navigation');
    const phase=new URLSearchParams(location.search).get('phase');
    if(phase==='save'){
      change('settings-theme','light');change('settings-motion','reduced');change('settings-font','editorial');
      check(getComputedStyle(document.body).fontFamily.includes('Georgia'),'font applies immediately');
      check(JSON.parse(localStorage.getItem('mcdraft-settings-v1')).font==='editorial','font is stored');
      check(document.body.dataset.theme==='light','theme applies immediately');
      check(document.documentElement.dataset.motion==='reduced','motion preference applies immediately');
      check(JSON.parse(localStorage.getItem('mcdraft-settings-v1')).theme==='light','preferences are stored');
      const probe=document.createElement('i');probe.className='atlas-bar-fill';document.body.append(probe);
      check(getComputedStyle(probe).animationName==='none','reduced motion disables chart animations');probe.remove();
      const stat=document.createElement('span');stat.textContent='6.37';$('page-settings').append(stat);showPage('settings');
      change('settings-numbers','rounded');check(stat.textContent==='6.4','rounded numeric display');change('settings-numbers','detailed');check(stat.textContent==='6.37','detailed display restores source precision');
      const fontBefore=parseFloat(getComputedStyle(stat).fontSize);
      change('settings-size','large');check(parseFloat(getComputedStyle(stat).fontSize)>fontBefore,'text size increases');stat.remove();check(document.documentElement.dataset.density!==undefined,'extra settings initialized');
      change('settings-chartView','tables');
      check(document.querySelectorAll('.preference-table-wrap table').length>0,'chart tables contain rendered data');
      const chart=document.querySelector('.has-preference-table');check(getComputedStyle(chart.querySelector('.preference-table-wrap')).display==='block','table preference shows alternative');
      change('settings-chartLabels','hide');check(document.documentElement.dataset.chartLabels==='hide','value labels preference applies');
      change('settings-clutter','minimal');check(document.documentElement.dataset.clutter==='minimal','minimal clutter applies');
      change('settings-horizon','1');check($('wi-horizon').value==='1'&&$('sim-horizon').value==='1','next-gameweek horizon supported in both tools');
      $('wi-horizon').value='5';change('settings-accent','blue');check($('wi-horizon').value==='5','unrelated preferences preserve manual horizon');
      change('settings-horizon','3');check($('wi-horizon').value==='3','changing default reapplies horizon');
      const sample=document.createElement('span');sample.className='player-directory-name';sample.textContent=playerSearchData[0].name;$('page-settings').append(sample);
      const oldName=playerSearchData[0].full_name;playerSearchData[0].full_name='Test Full Player Name';
      change('settings-playerNames','full');check(sample.textContent==='Test Full Player Name','full name presentation uses captured name');
      change('settings-playerNames','short');check(sample.textContent===playerSearchData[0].name,'short name restored without changing source');sample.remove();playerSearchData[0].full_name=oldName;
      change('settings-density','compact');check(document.documentElement.dataset.density==='compact','density applies');
      change('settings-accent','purple');check(document.body.style.getPropertyValue('--accent')!=='','accent applies');
      change('settings-calendarKind','fantasy');change('settings-weekStart','sunday');
      check(document.getElementById('calendar-kind').value==='fantasy'&&document.querySelector('.calendar-weekday').textContent==='Sun','calendar defaults apply');
      change('settings-scores','hide');showPage('calendar');
      const reveal=document.querySelector('#page-calendar .settings-score-reveal');check(!!reveal,'calendar scores have reveal control');if(reveal){reveal.click();check(reveal.parentElement.dataset.scoreRevealed==='true','score can be revealed');}
      showPage('settings');change('settings-landing','calendar');change('settings-skip','yes');
      const first=document.querySelector('#settings-home-list input');first.checked=false;first.dispatchEvent(new Event('change'));check(document.querySelector('#overview-sub-standings .settings-home-hidden'),'home section hidden');
      const down=document.querySelector('#settings-home-list button[aria-label^="Move down"]');down.click();check(JSON.parse(localStorage.getItem('mcdraft-display-settings-v1')).homeOrder.length>0,'home order saved');
      document.dispatchEvent(new CustomEvent('mcdraft:chat-unread',{detail:{count:3,incoming:false}}));check(!document.getElementById('settings-chat-badge').hidden,'chat badge shown');
      change('settings-badges','no');check(document.getElementById('settings-chat-badge').hidden,'chat badge can be disabled');
      const mute=document.getElementById('settings-muteUntil');mute.value='2099-01-01T12:00';mute.dispatchEvent(new Event('change'));change('settings-badges','yes');check(document.getElementById('settings-chat-badge').hidden,'mute suppresses badge');
      check(document.getElementById('header-settings')&&document.getElementById('header-calendar').textContent.trim()==='','header shortcuts are icons');
      check(getComputedStyle(document.querySelector('.theme-toggle-label')).display==='none','theme label hidden');
      localStorage.setItem('mcdraft-player-watchlist-v1','[]');
    }else{
      check($('settings-chartView').value==='tables'&&$('settings-clutter').value==='minimal'&&$('wi-horizon').value==='3','analysis preferences survive restart');
      check(document.getElementById('settings-density').value==='compact'&&document.getElementById('settings-landing').value==='calendar','extra preferences survive restart');
      check($('settings-theme').value==='light'&&document.body.dataset.theme==='light','appearance survives a fresh browser launch');
      check($('settings-motion').value==='reduced'&&document.documentElement.dataset.motion==='reduced','motion survives a fresh browser launch');
      check($('settings-font').value==='editorial'&&getComputedStyle(document.body).fontFamily.includes('Georgia'),'font survives browser restart');
      $('theme-toggle').click();
      check($('settings-theme').value==='dark','header theme toggle updates Settings');
      const manager=localStorage.getItem('mcdraft-preferred-manager-v1');
      $('settings-reset').click();
      check(document.documentElement.dataset.chartView==='charts'&&document.documentElement.dataset.clutter==='full','analysis preferences reset');
      check(document.documentElement.dataset.density==='standard'&&!document.querySelector('#overview-sub-standings .settings-home-hidden'),'reset restores layout and home');
      check($('settings-theme').value==='system'&&$('settings-motion').value==='system','reset restores device preferences');
      check($('settings-font').value==='rounded'&&getComputedStyle(document.body).fontFamily.includes('Trebuchet'),'reset restores default font');
      check(document.body.dataset.theme===(matchMedia('(prefers-color-scheme: light)').matches?'light':'dark'),'device theme is resolved');
      check(localStorage.getItem('mcdraft-player-watchlist-v1')==='[]'&&localStorage.getItem('mcdraft-preferred-manager-v1')===manager,'reset preserves watchlist and team');
      localStorage.setItem('mcdraft-settings-v1',JSON.stringify({theme:'light',motion:'reduced'}));
      window.dispatchEvent(new StorageEvent('storage',{key:'mcdraft-settings-v1'}));
      check($('settings-theme').value==='light'&&document.documentElement.dataset.motion==='reduced','preferences synchronize from another tab');
      check($('settings-font').value==='rounded','old saved preferences default to rounded font');
      localStorage.setItem('mcdraft-settings-v1',JSON.stringify({font:'invalid'}));window.dispatchEvent(new StorageEvent('storage',{key:'mcdraft-settings-v1'}));
      check($('settings-font').value==='rounded','invalid font falls back safely');
      const original=Storage.prototype.setItem;
      Storage.prototype.setItem=function(){throw new DOMException('Blocked','SecurityError');};
      try{
        change('settings-theme','dark');change('settings-font','mono');
        check(getComputedStyle(document.body).fontFamily.includes('monospace'),'font works without storage');
        check(document.body.dataset.theme==='dark'&&$('settings-status').textContent.includes('visit only'),'blocked storage keeps controls usable and explains persistence');
      }finally{Storage.prototype.setItem=original;}
    }
    check($('page-settings').scrollWidth<=$('page-settings').clientWidth,'settings has no horizontal overflow');
    const gear=$('header-settings').getBoundingClientRect();check(gear.width>0&&gear.left>=0&&gear.right<=innerWidth,'settings shortcut fits header');
    $('header-calendar').click();check($('page-calendar').classList.contains('active'),'calendar shortcut works');$('header-settings').click();check($('page-settings').classList.contains('active'),'settings shortcut works');
    showPage('overview');check(!$('page-settings').classList.contains('active'),'Settings closes when navigating away');
  }catch(error){checks.push('FAILED: '+error.stack);}
  const report=document.createElement('pre');report.id='settings-report';report.textContent=JSON.stringify(checks);document.body.append(report);
},700));
