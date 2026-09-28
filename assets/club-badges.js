/* Badge resource IDs are not FPL/Draft team IDs. Preserve original text for search. */
(() => {
  'use strict';
  const clubs=[
    [3,'Arsenal','ARS'],[7,'Aston Villa','Villa','AVL'],[91,'Bournemouth','AFC Bournemouth','BOU'],
    [94,'Brentford','BRE'],[36,'Brighton','Brighton & Hove Albion','Brighton and Hove Albion','BHA'],
    [8,'Chelsea','CHE'],[9,'Coventry','Coventry City','COV'],[31,'Crystal Palace','Palace','CRY'],
    [11,'Everton','EVE'],[54,'Fulham','FUL'],[88,'Hull','Hull City','HUL'],[40,'Ipswich','Ipswich Town','IPS'],
    [2,'Leeds','Leeds United','LEE'],[14,'Liverpool','LIV'],[43,'Manchester City','Man City','MCI'],
    [1,'Manchester United','Man Utd','Man United','MUN'],[4,'Newcastle United','Newcastle','NEW'],
    [17,'Nottingham Forest',"Nott'm Forest",'Nottm Forest','Nott Forest','NFO'],
    [56,'Sunderland','SUN'],[6,'Tottenham','Tottenham Hotspur','Spurs','TOT']
  ];
  const normalise=value=>String(value||'').trim().toLowerCase().replace(/[’‘]/g,"'").replace(/\s+/g,' ');
  const aliases=new Map();clubs.forEach(([id,...names])=>names.forEach(name=>aliases.set(normalise(name),id)));
  const idFor=name=>aliases.get(normalise(name))||null;
  const url=id=>'https://resources.premierleague.com/premierleague25/badges-alt/'+id+'.svg';
  const scopes='td,th,.player-directory-card,.war-room-player-card,#club-explorer-summary,.search-result,.global-search-result,.mcd-comparison,.club-explorer-panel h2,.club-explorer-panel h3,[data-club-name]';
  const excluded='script,style,textarea,input,select,option,svg,canvas,pre,code,.mcd-club-label,#page-league-chat,[contenteditable="true"]';
  function label(name,id){
    const span=document.createElement('span');span.className='mcd-club-label';
    const img=document.createElement('img');img.className='mcd-club-badge';img.src=url(id);img.alt='';
    img.width=21;img.height=21;img.loading='lazy';img.decoding='async';img.setAttribute('aria-hidden','true');
    img.addEventListener('error',()=>{img.hidden=true;},{once:true});
    span.append(img,document.createTextNode(name));return span;
  }
  function decorateText(node){
    if(!node.parentElement?.closest(scopes)||node.parentElement.closest(excluded))return;
    const text=node.nodeValue;if(!text?.trim())return;
    // Restrict matches to whole labels or metadata segments, never prose substrings.
    const pieces=text.split(/(\s*[·|]\s*)/),fragment=document.createDocumentFragment();let changed=false;
    pieces.forEach(piece=>{
      const match=piece.match(/^(\s*)(.*?)(\s*\([HA]\))?(\s*)$/);
      const id=match&&idFor(match[2]);
      if(!id){fragment.append(document.createTextNode(piece));return;}
      changed=true;fragment.append(document.createTextNode(match[1]),label(match[2],id),document.createTextNode((match[3]||'')+match[4]));
    });
    if(changed)node.replaceWith(fragment);
  }
  function decorate(root){
    if(root.nodeType===Node.TEXT_NODE){decorateText(root);return;}
    if(root.nodeType!==Node.ELEMENT_NODE||root.closest(excluded))return;
    const walker=document.createTreeWalker(root,NodeFilter.SHOW_TEXT),nodes=[];
    while(walker.nextNode())nodes.push(walker.currentNode);
    nodes.forEach(decorateText);
  }
  function init(){
    document.querySelectorAll(scopes).forEach(decorate);
    // Only inspect changed subtrees, so sorting/filtering/rerendering keeps badges.
    const pending=new Set();let scheduled=false;
    const observer=new MutationObserver(mutations=>{
      mutations.forEach(m=>{
        if(m.target.parentElement?.closest('.mcd-club-label')||m.target.closest?.('.mcd-club-label'))return;
        if(m.type==='characterData')pending.add(m.target);
        else m.addedNodes.forEach(n=>{if(n.nodeType===1&&!n.matches('.mcd-club-label'))pending.add(n);else if(n.nodeType===3&&n.nodeValue.trim())pending.add(n);});
      });
      if(pending.size&&!scheduled){scheduled=true;setTimeout(()=>{const roots=[...pending];pending.clear();scheduled=false;roots.forEach(r=>{if(r.isConnected)decorate(r);});});}
    });
    observer.observe(document.body,{childList:true,subtree:true,characterData:true});
  }
  window.McDraftClubBadges={idFor,url,decorate};
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();
