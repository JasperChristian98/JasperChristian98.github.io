window.addEventListener('load',()=>{
 const checks=[],check=(v,s)=>{if(!v)throw Error(s);checks.push(s);},$=id=>document.getElementById('calendar-'+id);
 try{
  document.getElementById('mcd-manager-welcome').hidden=true;document.body.classList.remove('mcd-welcome-open');document.querySelector('.app-shell')?.removeAttribute('inert');showPage('calendar');
  check(!$('month').textContent.includes('undefined'),'current month is populated');
  check(document.getElementById('mcd-welcome-date').textContent.length>10,'welcome date rendered');
  check(!document.getElementById('mcd-stat-date')&&!document.getElementById('mcd-player-context'),'daily card footers removed');
  const original=$('month').textContent;while(!$('prev').disabled)$('prev').click();check($('month').textContent.includes('August'),'August lower bound');
  check($('agenda').querySelectorAll('.calendar-event').length>0,'historical results displayed');
  $('kind').value='fantasy';$('kind').dispatchEvent(new Event('change'));
  check([...$('agenda').querySelectorAll('.calendar-event')].every(n=>n.classList.contains('fantasy')),'fantasy filter');
  const fixtures=[...$('agenda').querySelectorAll('.calendar-event')].map(n=>n.textContent);check(fixtures.length>0&&new Set(fixtures).size===fixtures.length,'fantasy results deduplicated across managers');
  $('team').selectedIndex=1;$('team').dispatchEvent(new Event('change'));const name=$('team').selectedOptions[0].textContent;
  check([...$('agenda').querySelectorAll('.calendar-event strong')].every(n=>n.textContent.includes(name)),'team filter');
  $('team').value='';$('status').value='upcoming';$('status').dispatchEvent(new Event('change'));check(!$('empty').hidden,'empty filter state');
  while(!$('next').disabled)$('next').click();check($('month').textContent.includes('May'),'May upper bound');
  check($('agenda').querySelectorAll('.calendar-event').length>0,'remaining fantasy fixtures reach May');
  $('status').value='all';$('kind').value='all';$('kind').dispatchEvent(new Event('change'));$('today').click();check($('month').textContent===original,'current month shortcut');
  const date=$('grid').querySelector('button');date.click();check(date.getAttribute('aria-pressed')==='false'&&$('grid').querySelector('[aria-pressed=true]'),'day selection updates');
  check($('grid').scrollWidth<=$('grid').clientWidth,'mobile calendar fits');
 }catch(e){checks.push('FAILED: '+e.stack);}
 const report=document.createElement('pre');report.id='calendar-test-report';report.textContent=JSON.stringify(checks);document.body.append(report);
});
