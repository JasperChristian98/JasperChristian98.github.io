"""One coherent mobile navigation layer on top of McDraft's existing routes.

Does not replace MCD_MENU, duplicate selectors, or change desktop routing. The
post-template CSS is deliberately last so old legacy media queries cannot win.
"""
from __future__ import annotations

CSS = r'''
/* McDraft mobile navigation v1: one scroll root, one sticky-tab system. */
@media (max-width:850px) {
 :root { --mcd-mobile-bottom-height:72px; --mcd-sticky-top:0px; }
 html { scroll-padding-top:58px; -webkit-text-size-adjust:100%; }
 body { overflow-x:clip; }
 .mcd-workspace, .mcd-workspace>.main {
   display:block; min-width:0; max-width:100%;
   overflow:visible!important; /* overflow-x:hidden breaks position:sticky on iOS */
 }
 .mcd-workspace>.main {
   padding:12px 12px calc(var(--mcd-mobile-bottom-height) + 23px + env(safe-area-inset-bottom))!important;
 }
 .mcd-workspace .page { min-width:0; max-width:100%; }
 .mcd-mobile-bottom {
   position:fixed; z-index:130; inset:auto 0 0;
   min-height:var(--mcd-mobile-bottom-height);
   display:grid; grid-template-columns:repeat(5,minmax(0,1fr));
   gap:2px; align-items:stretch;
   padding:5px max(5px,env(safe-area-inset-left)) calc(5px + env(safe-area-inset-bottom)) max(5px,env(safe-area-inset-right));
   background:var(--card); border-top:1px solid var(--border);
 }
 .mcd-mobile-bottom button {
   min-width:0; min-height:58px; padding:5px 2px;
   display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px;
   font:700 10px/1.3 inherit; font-family:inherit; border-radius:10px;
   white-space:nowrap;touch-action:manipulation;
 }
 .mcd-mobile-bottom button.is-current { color:var(--accent); background:var(--card-hover); }
 .mcd-mobile-current {
   display:flex; align-items:center; justify-content:space-between;
   gap:8px; min-width:0; margin:0 0 12px; padding:8px 10px;
 }
 .mcd-mobile-current span { min-width:0; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
 .mcd-mobile-current button { min-height:40px; flex-shrink:0; }
 /* All section strips look, stick and scroll the same way. No nested clipping. */
 #page-myteam>.myteam-tabs,
 #page-overview>.overview-tabs,
 #overview-sub-intelligence>.overview-insight-tabs,
 #page-analytics .analytics-subtabs,
 #page-players .player-page-tabs,
 #page-clubs .club-explorer-tabs,
 #page-transfers .transfer-subtabs,
 #page-season-summary .season-summary-tabs,
 #page-draft-centre .draft-centre-tabs {
   position:sticky!important;top:var(--mcd-sticky-top,0px)!important;
   z-index:85;display:flex;align-items:center;flex-wrap:nowrap;
   width:100%;max-width:100%;min-width:0;
   overflow-x:auto;overflow-y:hidden;overscroll-behavior-x:contain;
   -webkit-overflow-scrolling:touch;scrollbar-width:none;
   scroll-padding-inline:8px;gap:7px;padding:8px 4px 10px;
   box-sizing:border-box;background:var(--bg);border-bottom:1px solid var(--border);
   margin-top:0;margin-bottom:14px;
 }
 #page-myteam>.myteam-tabs::-webkit-scrollbar,
 #page-overview>.overview-tabs::-webkit-scrollbar,
 #overview-sub-intelligence>.overview-insight-tabs::-webkit-scrollbar,
 #page-analytics .analytics-subtabs::-webkit-scrollbar { display:none; }
 #page-myteam>.myteam-tabs>.myteam-tab,
 #page-overview>.overview-tabs>.overview-tab,
 #overview-sub-intelligence>.overview-insight-tabs>.overview-insight-tab,
 #page-analytics .analytics-subtab {
   flex:0 0 auto!important; min-height:40px; white-space:nowrap;
   font-size:12px; padding:9px 12px;touch-action:manipulation;
 }
 /* Second Overview row sticks exactly beneath the first, not behind it. */
 #overview-sub-intelligence>.overview-insight-tabs {
   top:calc(var(--mcd-sticky-top,0px) + var(--mcd-overview-tabs-height,0px))!important;
   z-index:84;
 }
 .mcd-mobile-sheet:not([hidden]) {z-index:180;}
 .mcd-mobile-sheet-panel {
   width:100%;max-width:650px;
   max-height:min(85dvh,780px);min-height:0;
   border-radius:20px 20px 0 0;
 }
 .mcd-mobile-sheet-content { overflow-y:auto;min-height:0;-webkit-overflow-scrolling:touch; }
 .mcd-mobile-sheet-links button {min-height:48px;touch-action:manipulation;}
 .page-heading {scroll-margin-top:64px;}
 [id^="myteam-sub-"],[id^="overview-insight-"],.card {scroll-margin-top:calc(var(--mcd-sticky-top,0px) + 65px);}
}
@media (max-width:370px) {
 .mcd-mobile-bottom button {font-size:9px;}
 .mcd-mobile-bottom .mcd-nav-icon {font-size:20px;}
 .mcd-mobile-current {font-size:11px;}
 .mcd-mobile-current button {font-size:11px;padding:7px;}
}
@media (min-width:851px) { .mcd-mobile-bottom,.mcd-mobile-current,.mcd-mobile-sheet {display:none!important;} }
@media (prefers-reduced-motion:reduce) {
 .mcd-mobile-bottom button,.mcd-mobile-sheet-panel {transition:none!important;}
}
'''

JS = r'''
/* Consolidate all mobile section navigation around the existing MCD_MENU. */
(function(){
 const mobileQuery=window.matchMedia('(max-width:850px)');
 const strips=[
  '#page-myteam>.myteam-tabs',
  '#page-overview>.overview-tabs',
  '#overview-sub-intelligence>.overview-insight-tabs',
  '#page-analytics .analytics-subtabs',
  '#page-players .player-page-tabs',
  '#page-clubs .club-explorer-tabs',
  '#page-transfers .transfer-subtabs',
  '#page-season-summary .season-summary-tabs',
  '#page-draft-centre .draft-centre-tabs'
 ];
 function visible(el){return !!el&&el.getClientRects().length>0;}
 function measure(){
   if(typeof mcdMeasureStickyTabs==='function')mcdMeasureStickyTabs();
   if(!mobileQuery.matches)return;
   document.documentElement.style.setProperty('--mcd-sticky-top','0px');
   const outer=document.querySelector('#page-overview.active>.overview-tabs');
   const height=visible(outer)?Math.ceil(outer.getBoundingClientRect().height):0;
   document.documentElement.style.setProperty('--mcd-overview-tabs-height',height+'px');
 }
 function centreActive(strip){
   if(!strip||!mobileQuery.matches||!visible(strip))return;
   const active=strip.querySelector('.active,[aria-selected="true"]');
   if(!active)return;
   const left=active.offsetLeft-strip.offsetLeft;
   const target=left-(strip.clientWidth-active.offsetWidth)/2;
   if(Math.abs(strip.scrollLeft-target)>5)strip.scrollTo({left:Math.max(0,target),behavior:'auto'});
 }
 function activeStrip(){return strips.map(s=>document.querySelector(s)).find(visible);}
 function syncLocation(){
   const path=typeof mcdActivePage==='function'?mcdActivePage():'overview';
   const group=typeof MCD_MENU!=='undefined'?MCD_MENU.find(g=>g.items.some(x=>x[1]===path)):null;
   const name=group?.title||'Home';
   const loc=document.getElementById('mcd-mobile-location');
   if(loc&&!loc.textContent.trim())loc.textContent=name;
   const here=document.getElementById('mcd-mobile-current');
   if(here)here.setAttribute('aria-label','Current section: '+name);
 }
 function initialise(){
   if(document.documentElement.dataset.mcdMobileNavReady==='1')return;
   document.documentElement.dataset.mcdMobileNavReady='1';
   // No second menu or duplicate event bindings: the legacy sidebar, bottom
   // bar and sheet all use MCD_MENU and mcdNavGoto already.
   const bottom=document.getElementById('mcd-mobile-bottom');
   if(bottom){bottom.setAttribute('aria-label','Main navigation');}
   document.querySelectorAll('[data-mcd-mobile]').forEach(btn=>{
     btn.setAttribute('aria-label',btn.textContent.trim()||'Browse');
     if(btn.dataset.mcdMobile==='more')btn.setAttribute('aria-haspopup','dialog');
   });
   const sheet=document.getElementById('mcd-mobile-sheet');
   if(sheet){
     sheet.setAttribute('aria-label','Browse McDraft sections');
     sheet.addEventListener('keydown',function(ev){
       if(ev.key!=='Tab'||sheet.hidden)return;
       const controls=Array.from(sheet.querySelectorAll('button:not([disabled])')).filter(visible);
       if(!controls.length)return;
       if(ev.shiftKey&&document.activeElement===controls[0]){ev.preventDefault();controls[controls.length-1].focus();}
       else if(!ev.shiftKey&&document.activeElement===controls[controls.length-1]){ev.preventDefault();controls[0].focus();}
     });
   }
   document.addEventListener('click',ev=>{
     const tab=ev.target.closest('.myteam-tab,.overview-tab,.overview-insight-tab,.analytics-subtab,.player-page-tab,.club-explorer-tab,.transfer-subtab,.season-summary-tab,.draft-centre-tab');
     if(!tab||!mobileQuery.matches)return;
     requestAnimationFrame(()=>{measure();centreActive(tab.parentElement);syncLocation();});
   });
   window.addEventListener('resize',measure,{passive:true});
   window.addEventListener('orientationchange',()=>{requestAnimationFrame(()=>{measure();strips.forEach(s=>centreActive(document.querySelector(s)));});},{passive:true});
   // Sync after route changes triggered from bottom nav or mobile sheet.
   document.addEventListener('click',ev=>{
     if(!ev.target.closest('[data-mcd-mobile],.mcd-mobile-sheet-links button,.mcd-nav-link'))return;
     requestAnimationFrame(()=>{measure();syncLocation();strips.forEach(s=>centreActive(document.querySelector(s)));});
   });
   measure();syncLocation();
   strips.forEach(s=>centreActive(document.querySelector(s)));
 }
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',initialise);
 else initialise();
})();
'''


def append_final_mobile_css(template: str) -> str:
    """Inject after legacy CSS, so the consolidated mobile rules actually win."""
    anchor = '</style>\n\n</head>'
    if template.count(anchor) != 1:
        raise RuntimeError('Final stylesheet insertion point changed')
    if 'McDraft mobile navigation v1' in template:
        raise RuntimeError('Mobile navigation already integrated')
    return template.replace(anchor, CSS + '\n' + anchor, 1)
