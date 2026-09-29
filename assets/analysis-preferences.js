/* Presentation only: player identities and model inputs are never changed. */
(() => {
 'use strict';
 const make=(tag,text)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=String(text);return n;};
 let prefs={},lastHorizon=null;
 const initialHorizons=new Map(),names=new WeakMap();
 function table(host,columns,rows){
  if(!rows.length)return;
  host.classList.add('has-preference-table');
  host.querySelector(':scope > .preference-table-wrap')?.remove();
  const wrap=make('div');wrap.className='preference-table-wrap';const t=make('table'),caption=make('caption',host.closest('.card')?.querySelector('h2,h3')?.textContent||'Chart data');
  const head=make('thead'),hr=make('tr');for(const column of columns){const th=make('th',column);th.scope='col';hr.append(th);}head.append(hr);
  const body=make('tbody');for(const row of rows){const tr=make('tr');for(const value of row)tr.append(make('td',typeof value==='number'?Number(value.toFixed(2)):value??'—'));body.append(tr);}
  t.append(caption,head,body);wrap.append(t);host.append(wrap);
 }
 function decorate(root){
  const players=typeof playerSearchData==='undefined'?[]:playerSearchData;
  const unique=new Map();for(const p of players){if(unique.has(p.name))unique.set(p.name,null);else unique.set(p.name,p);}
  for(const n of root.querySelectorAll('.player-directory-name,.visual-player-name,.atlas-bar-name,.player-name,.preference-table-wrap td')){
   if(n.children.length||n.closest('#page-league-chat'))continue;
   let original=names.get(n);if(!original||n.textContent!==original.rendered){const p=unique.get(n.textContent.trim());if(!p)continue;original={short:p.name,full:p.full_name||p.name,rendered:n.textContent};}
   const next=prefs.playerNames==='full'?original.full:original.short;if(n.textContent!==next)n.textContent=next;original.rendered=next;names.set(n,original);
  }
 }
 function apply(next){
  const redraw=!prefs.chartView||prefs.chartView!==next.chartView;
  prefs=next;
  if(redraw){document.querySelectorAll('.chart-atlas[data-atlas-rendered="true"]').forEach(section=>window.MCDChartAtlas?.renderTarget(section.dataset.atlasTarget));window.renderVisualAnalytics?.();}
  for(const [key,value]of [['chartView',next.chartView||'charts'],['chartLabels',next.chartLabels||'show'],['clutter',next.clutter||'full']])document.documentElement.dataset[key]=value;
  const horizon=next.horizon||'existing';
  if(horizon!==lastHorizon){
   for(const id of ['wi-horizon','sim-horizon']){const el=document.getElementById(id);if(!el)continue;if(!initialHorizons.has(id))initialHorizons.set(id,el.value);
    if(id==='sim-horizon'&&!el.querySelector('option[value="1"]'))el.insertBefore(new Option('Next gameweek','1'),el.firstChild);
    const desired=horizon==='existing'?initialHorizons.get(id):horizon;
    if([...el.options].some(o=>o.value===desired)&&el.value!==desired){el.value=desired;el.dispatchEvent(new Event('change',{bubbles:true}));}
   }lastHorizon=horizon;
  }
  decorate(document.querySelector('.page.active')||document.body);
 }
 document.addEventListener('mcdraft:preferences',e=>apply(e.detail));
 window.McDraftAnalysisPreferences={table,decorate};
})();
