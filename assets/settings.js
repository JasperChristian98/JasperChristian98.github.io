(() => {
  'use strict';
  const key='mcdraft-settings-v1',themeKey='mcdraft-theme';
  const defaults={theme:'system',motion:'system'};
  const colourScheme=matchMedia('(prefers-color-scheme: light)');
  const $=id=>document.getElementById(id);
  let storageAvailable=true;
  function load(){
    try{
      const saved=JSON.parse(localStorage.getItem(key)||'null');
      const legacy=localStorage.getItem(themeKey);
      return {
        theme:['system','dark','light'].includes(saved?.theme)?saved.theme:['dark','light'].includes(legacy)?legacy:defaults.theme,
        motion:saved?.motion==='reduced'?'reduced':defaults.motion
      };
    }catch{return {...defaults};}
  }
  let preferences=load();
  const originalTheme=window.setDashboardTheme;
  function sync(){
    $('settings-theme').value=preferences.theme;
    $('settings-motion').value=preferences.motion;
  }
  function apply(){
    const theme=preferences.theme==='system'?(colourScheme.matches?'light':'dark'):preferences.theme;
    originalTheme(theme,false);
    document.documentElement.dataset.motion=preferences.motion;
    sync();
  }
  function save(){
    try{
      localStorage.setItem(key,JSON.stringify(preferences));
      storageAvailable=true;
    }catch{storageAvailable=false;}
    $('settings-status').textContent=storageAvailable?'Preferences saved in this browser.':'Browser storage is unavailable. Changes apply for this visit only.';
  }
  // Keep the existing header theme button and Settings in agreement.
  window.setDashboardTheme=function(theme,persist=true){
    if(!persist)return apply();
    preferences.theme=theme==='light'?'light':'dark';apply();save();
  };
  function init(){
    apply();
    const reducedMotion=matchMedia('(prefers-reduced-motion: reduce)');
    const reduceScroll=options=>options&&typeof options==='object'&&(preferences.motion==='reduced'||reducedMotion.matches)?{...options,behavior:'instant'}:options;
    const scrollWindow=window.scrollTo;
    window.scrollTo=function(...args){args[0]=reduceScroll(args[0]);return scrollWindow.apply(this,args);};
    const scrollElement=Element.prototype.scrollIntoView;
    Element.prototype.scrollIntoView=function(options){return scrollElement.call(this,reduceScroll(options));};
    $('settings-theme').addEventListener('change',event=>{preferences.theme=event.target.value;apply();save();});
    $('settings-motion').addEventListener('change',event=>{preferences.motion=event.target.value;apply();save();});
    $('settings-reset').addEventListener('click',()=>{preferences={...defaults};apply();save();});
    colourScheme.addEventListener('change',()=>{if(preferences.theme==='system')apply();});
    window.addEventListener('storage',event=>{if(event.key===key||event.key===null){preferences=load();apply();$('settings-status').textContent='Preferences updated.';}});
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();
