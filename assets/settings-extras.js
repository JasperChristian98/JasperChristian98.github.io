(() => {
 'use strict';
 const key='mcdraft-display-settings-v1', $=id=>document.getElementById(id);
 const defaults={size:'standard',density:'standard',landing:'overview',skip:'no',accent:'default',scores:'show',calendarKind:'all',calendarTeam:'',weekStart:'monday',badges:'yes',sound:'no',muteUntil:'',numbers:'detailed',homeOrder:[],homeHidden:[]};
 const choices={size:['small','standard','large'],density:['compact','standard','spacious'],skip:['no','yes'],accent:['default','blue','purple','green','orange','pink'],scores:['show','hide'],calendarKind:['all','pl','fantasy'],weekStart:['monday','sunday'],badges:['yes','no'],sound:['no','yes'],numbers:['rounded','detailed']};
 function load(){try{const s=JSON.parse(localStorage.getItem(key)||'{}'),p={...defaults};for(const [k,options]of Object.entries(choices))if(options.includes(s[k]))p[k]=s[k];for(const k of ['landing','calendarTeam','muteUntil'])if(typeof s[k]==='string')p[k]=s[k];for(const k of ['homeOrder','homeHidden'])if(Array.isArray(s[k]))p[k]=s[k].filter(v=>typeof v==='string');return p;}catch{return {...defaults};}}
 let prefs=load(),unread=0,audio=null,started=false;
 const make=(tag,text)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;return n;};
 function save(){try{localStorage.setItem(key,JSON.stringify(prefs));$('settings-status').textContent='Preferences saved in this browser.';}catch{$('settings-status').textContent='Browser storage is unavailable. Changes apply for this visit only.';}}
 function select(name,label,help,options){const row=make('div');row.className='mcd-setting-row';const info=make('div'),l=make('label',label),p=make('p',help),input=make('select');l.htmlFor=input.id='settings-'+name;p.id=input.id+'-help';input.setAttribute('aria-describedby',p.id);for(const [value,text]of options)input.add(new Option(text,value));info.append(l,p);row.append(info,input);$('settings-extras').append(row);input.onchange=()=>{prefs[name]=input.value;apply();save();};return input;}
 function sync(){for(const name of Object.keys(defaults)){const input=$('settings-'+name);if(input)input.value=prefs[name];}}
 const palettes={blue:['#168de2','#0871bd'],purple:['#b090ff','#7544c2'],green:['#44cc9b','#147c56'],orange:['#ffa45a','#a34c08'],pink:['#f68abb','#b02c6b']};
 function accent(){const colours=palettes[prefs.accent];if(colours)document.body.style.setProperty('--accent',colours[document.body.dataset.theme==='light'?1:0]);else document.body.style.removeProperty('--accent');}
 let blocks=[];
 function home(){const host=$('overview-sub-standings');if(!host)return;const order=[...new Set([...prefs.homeOrder,...blocks.map(b=>b.key)])];for(const id of order){const block=blocks.find(b=>b.key===id);if(block){host.append(block.node);block.node.classList.toggle('settings-home-hidden',prefs.homeHidden.includes(id));}}}
 function homeControls(){const box=$('settings-home-list');if(!box)return;box.replaceChildren();const ordered=[...blocks].sort((a,b)=>{const order=[...prefs.homeOrder,...blocks.map(b=>b.key)];return order.indexOf(a.key)-order.indexOf(b.key);});ordered.forEach((block,i)=>{const row=make('div'),label=make('label'),input=make('input');input.type='checkbox';input.checked=!prefs.homeHidden.includes(block.key);label.append(input,document.createTextNode(' '+block.title));input.onchange=()=>{prefs.homeHidden=prefs.homeHidden.filter(k=>k!==block.key);if(!input.checked)prefs.homeHidden.push(block.key);home();save();};row.append(label);for(const [text,offset]of [['Move up',-1],['Move down',1]]){const b=make('button',offset<0?'↑':'↓');b.type='button';b.setAttribute('aria-label',text+' '+block.title);b.disabled=i+offset<0||i+offset>=ordered.length;b.onclick=()=>{const ids=ordered.map(x=>x.key);[ids[i],ids[i+offset]]=[ids[i+offset],ids[i]];prefs.homeOrder=ids;home();homeControls();save();};row.append(b);}box.append(row);});}
 const fontBase=new WeakMap(),numeric=new WeakMap();
 const scoreSelector='.fixture-score,.h2h-record-score,#pl-fixture-browser .future-fixture-vs,.calendar-score';
 function decorate(root){
  if(!root)return;
  for(const n of root.querySelectorAll(scoreSelector)){if(!/\d/.test(n.textContent)||n.querySelector('.settings-score-reveal'))continue;const content=make('span');while(n.firstChild)content.append(n.firstChild);content.className='settings-score-value';const b=make('button','Reveal score');b.type='button';b.className='settings-score-reveal';b.onclick=()=>{n.dataset.scoreRevealed='true';};n.classList.add('settings-score');n.append(content,b);}
  const factor={small:.92,standard:1,large:1.15}[prefs.size];
  const elements=[...root.querySelectorAll('*')];
  for(const n of elements)if(!fontBase.has(n)&&!n.closest('svg,script,style,pre,code')&&[...n.childNodes].some(t=>t.nodeType===3&&t.textContent.trim()))fontBase.set(n,{size:parseFloat(getComputedStyle(n).fontSize),inline:n.style.fontSize});
  for(const n of elements){
   if(n.closest('svg,script,style,pre,code')||!n.childNodes.length)continue;
   if([...n.childNodes].some(t=>t.nodeType===3&&t.textContent.trim())){if(!fontBase.has(n))fontBase.set(n,{size:parseFloat(getComputedStyle(n).fontSize),inline:n.style.fontSize});const base=fontBase.get(n);if(base.size){const value=factor===1?base.inline:(base.size*factor).toFixed(2)+'px';if(n.style.fontSize!==value)n.style.fontSize=value;}}
   if(n.children.length||n.matches('option,button,input,textarea')||n.closest('.settings-score,time,[datetime]'))continue;
   const text=n.textContent.trim();if(!numeric.has(n)&&! /^-?\d+\.\d+%?$/.test(text))continue;
   let original=numeric.get(n);if(!original||original.rendered!==n.textContent)original={source:n.textContent,rendered:n.textContent};
   const suffix=text.endsWith('%')?'%':'',v=parseFloat(original.source),digits=prefs.numbers==='rounded'?1:2;
   const formatted=v.toLocaleString('en-GB',{maximumFractionDigits:digits,useGrouping:false})+suffix;
   const out=prefs.numbers==='detailed'?original.source:formatted;if(n.textContent!==out)n.textContent=out;original.rendered=out;numeric.set(n,original);
  }
 }
 function visible(){decorate(document.querySelector('.page.active'));decorate(document.querySelector('.header'));const welcome=$('mcd-manager-welcome');if(welcome&&!welcome.hidden)decorate(welcome);}
 function muted(){return Date.parse(prefs.muteUntil)>Date.now();}
 function badge(){const b=$('settings-chat-badge');if(b){b.hidden=!unread||prefs.badges!=='yes'||muted();b.textContent=String(unread);b.setAttribute('aria-label',unread+' unread chat messages');}}
 function apply(){sync();accent();document.documentElement.dataset.density=prefs.density;document.documentElement.dataset.scores=prefs.scores;home();badge();visible();document.dispatchEvent(new CustomEvent('mcdraft:preferences',{detail:{...prefs}}));}
 function land(){if(document.getElementById('page-'+prefs.landing)){showPage(prefs.landing);window.mcdNavSync?.();}}
 function init(){
  if(!$('settings-extras')||started)return;started=true;
  select('size','Text size','Adjust dashboard text without changing your browser zoom.',[['small','Small'],['standard','Standard'],['large','Large']]);
  select('density','Layout density','Change spacing in cards and tables.',[['compact','Compact'],['standard','Standard'],['spacious','Spacious']]);
  const pages=[...document.querySelectorAll('section.page[id]')].map(p=>[p.id.replace('page-',''),p.querySelector('h1,h2')?.textContent||p.id.replace('page-','')]);
  if(!pages.some(p=>p[0]===prefs.landing))prefs.landing='overview';
  select('landing','Default landing page','Open this page after choosing your team or skipping welcome.',pages);
  select('skip','Skip welcome screen','Use your saved team on future visits. A first-time visitor still chooses a team.',[['no','Show welcome'],['yes','Skip with saved team']]);
  select('accent','Accent colour','Choose a highlight colour; light and dark themes use matching shades.',[['default','Dashboard default'],['blue','Blue'],['purple','Purple'],['green','Green'],['orange','Orange'],['pink','Pink']]);
  select('scores','Score visibility','Hide fixture scorelines until selected. Tables, charts and commentary remain visible.',[['show','Show scores'],['hide','Click to reveal scores']]);
  select('calendarKind','Calendar competition','Default competition when opening the calendar on a new visit.',[['all','All football'],['pl','Premier League'],['fantasy','Fantasy league']]);
  const teamOptions=[['','All teams']];for(const option of document.querySelectorAll('#calendar-team option'))if(option.value)teamOptions.push([option.value,option.textContent]);
  select('calendarTeam','Calendar team','Choose a default team. A team selection takes priority over the competition filter.',teamOptions);
  select('weekStart','Calendar week starts','Choose the first column in the month view.',[['monday','Monday'],['sunday','Sunday']]);
  select('badges','Chat unread badge','Show an unread counter beside the header shortcuts while this dashboard is open.',[['yes','Show'],['no','Hide']]);
  select('sound','Chat sound','Play a short sound for incoming messages when you are not reading the latest messages. Requires a click in this tab.',[['no','Off'],['yes','On']]);
  const muteRow=make('div');muteRow.className='mcd-setting-row';const label=make('label','Mute chat notifications until'),mute=make('input');mute.type='datetime-local';mute.id=label.htmlFor='settings-muteUntil';muteRow.append(label,mute);$('settings-extras').append(muteRow);mute.onchange=()=>{prefs.muteUntil=mute.value;badge();save();};
  select('numbers','Number formatting','Rounded uses up to one decimal in numeric stat cells. Detailed preserves available precision; calculations never change.',[['rounded','Rounded'],['detailed','Detailed']]);
  const host=$('overview-sub-standings');blocks=host?[...host.children].filter(n=>!n.matches('script,style')).map((n,i)=>({node:n,key:n.id||'home-'+i,title:n.querySelector('h2,h3')?.textContent.trim()||'Home section '+(i+1)})):[];
  const heading=make('h2','Home cards'),help=make('p','Show, hide and reorder the sections in Home → League overview.'),list=make('div');list.id='settings-home-list';$('settings-extras').append(heading,help,list);homeControls();
  const b=make('button');b.id='settings-chat-badge';b.className='header-calendar';b.type='button';b.hidden=true;b.onclick=()=>{showPage('league-chat');window.mcdNavSync?.();};document.querySelector('.theme-control')?.append(b);
  const enter=window.enterManagerDashboard;window.enterManagerDashboard=function(...args){const result=enter.apply(this,args);if($('mcd-manager-welcome')?.hidden)land();return result;};
  const show=window.showPage;window.showPage=function(...args){const result=show.apply(this,args);visible();return result;};
  apply();
  if(prefs.skip==='yes'&&typeof preferredManagerName==='function'&&preferredManagerName()){const select=$('mcd-welcome-team');select.value=preferredManagerName();window.enterManagerDashboard();}
  $('settings-reset').addEventListener('click',()=>{prefs={...defaults};apply();homeControls();save();});
  window.addEventListener('storage',e=>{if(e.key===key||e.key===null){prefs=load();apply();homeControls();}});
  document.addEventListener('mcdraft:appearance',accent);
  document.addEventListener('mcdraft:chat-unread',e=>{unread=e.detail.count;badge();if(e.detail.incoming&&prefs.sound==='yes'&&!muted()&&audio?.state==='running'){const osc=audio.createOscillator(),gain=audio.createGain();osc.connect(gain);gain.connect(audio.destination);osc.frequency.value=660;gain.gain.setValueAtTime(.05,audio.currentTime);gain.gain.exponentialRampToValueAtTime(.001,audio.currentTime+.15);osc.start();osc.stop(audio.currentTime+.16);}});
  document.addEventListener('click',()=>{if(prefs.sound==='yes')try{audio ||=new (window.AudioContext||window.webkitAudioContext)();audio.resume().catch(()=>{});}catch{};});
  setInterval(badge,30000);
  // Observe rerendered cards, not our own attribute changes. Disconnect while decorating.
  let pending=false;const observer=new MutationObserver(()=>{if(pending)return;pending=true;requestAnimationFrame(()=>{pending=false;observer.disconnect();visible();observe();});});
  const observe=()=>observer.observe(document.querySelector('.app-shell'),{childList:true,subtree:true,characterData:true});observe();
 }
 window.McDraftPreferences={get:()=>({...prefs})};
 if(document.readyState==='complete')init();else window.addEventListener('load',init,{once:true});
})();
