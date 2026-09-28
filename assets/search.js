/* Universal, local dashboard search. No private chat content is indexed. */
(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const text = el => (el?.textContent || '').replace(/\s+/g, ' ').trim();
  const node = (tag, value, cls) => { const el = document.createElement(tag); if (value != null) el.textContent = value; if (cls) el.className = cls; return el; };
  const kinds = {all:'All',page:'Pages',section:'Sections',player:'Players',team:'Fantasy teams',club:'Clubs',favourites:'Favourites'};
  const panels = [
    ['overview-sub-', 'showOverviewSubtab'], ['overview-insight-', 'showOverviewInsightSubtab'],
    ['myteam-sub-', 'showMyTeamSubtab'], ['player-sub-', 'showPlayerSubtab'],
    ['club-sub-', 'showClubSubtab'], ['transfer-subpanel-', 'showTransferSubtab'],
    ['season-summary-sub-', 'showSeasonSummarySubtab'], ['draft-centre-sub-', 'showDraftCentreSubtab'],
    ['analytics-sub-', 'showAnalyticsSubtab'], ['live-centre-match-', 'showLiveCentreMatch']
  ];
  const aliases = [
    [/\b(?:man utd|man united|manchester utd|mufc)\b/g,'manchester united'],
    [/\b(?:man city|mcfc)\b/g,'manchester city'], [/\b(?:spurs|tottenham hotspur)\b/g,'tottenham'],
    [/\b(?:wolves|wolverhampton wanderers)\b/g,'wolverhampton'],
    [/\b(?:nott m forest|nottm forest|notts forest)\b/g,'nottingham forest'],
    [/\b(?:newcastle united)\b/g,'newcastle'], [/\b(?:brighton and hove albion)\b/g,'brighton'],
    [/\b(?:west ham united)\b/g,'west ham'], [/\b(?:afc bournemouth)\b/g,'bournemouth'],
    [/\b(?:gk|goalkeeper|goalkeepers)\b/g,'gkp'], [/\b(?:defender|defenders)\b/g,'def'],
    [/\b(?:midfielder|midfielders)\b/g,'mid'], [/\b(?:forward|forwards|striker|strikers)\b/g,'fwd']
  ];
  function normalise(value) {
    let s = String(value || '').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase()
      .replace(/ø/g,'o').replace(/ł/g,'l').replace(/ß/g,'ss').replace(/æ/g,'ae').replace(/[^a-z0-9]+/g,' ').trim();
    aliases.forEach(([pattern, replacement]) => { s = s.replace(pattern, replacement); });
    return s;
  }
  function read(key) { try { const v = JSON.parse(localStorage.getItem(key) || '[]'); return Array.isArray(v) ? v.filter(x=>typeof x==='string') : []; } catch { return []; } }
  function save(key, value) { try { localStorage.setItem(key, JSON.stringify(value)); } catch { /* Search works without storage. */ } }
  let favourites = new Set(read('mcd-search-favourites'));
  let recent = read('mcd-search-recent').slice(0,6);
  let records = [], byId = new Map(), query = '', category = 'all', limit = 30, navigating = false;
  const pageLabels = new Map();
  const routeButtons = new Map();
  function routesFor(el) {
    const routes = [];
    for (let p = el; p && !p.classList.contains('page'); p = p.parentElement) {
      const spec = panels.find(([prefix]) => p.id?.startsWith(prefix));
      if (spec) routes.unshift({fn:spec[1], tab:p.id.slice(spec[0].length), target:p.id});
    }
    return routes;
  }
  const pretty = value => value.replace(/^page-/, '').replace(/-/g,' ').replace(/\b\w/g,c=>c.toUpperCase());
  function headingId(el, page, routes) {
    if (el.id) return el.id;
    const base = 'search-' + page + '-' + (routes.at(-1)?.tab || '') + '-' + normalise(text(el)).replace(/ /g,'-');
    let id = base, suffix = 2;
    while ($(id) && $(id) !== el) id = base + '-' + suffix++;
    el.id = id; return id;
  }
  function rebuild() {
    const list = new Map(); routeButtons.clear(); pageLabels.clear();
    document.querySelectorAll('.page button[onclick]').forEach(btn => {
      const m = btn.getAttribute('onclick').match(/\b(show\w+Subtab|showLiveCentreMatch)\(['"]?([^'",)]+)['"]?/);
      if (m) routeButtons.set(m[1] + ':' + m[2], btn);
    });
    const menu = typeof MCD_MENU === 'undefined' ? [] : MCD_MENU;
    const entries = menu.flatMap(g=>g.items);
    function add(r) {
      if (list.has(r.id)) return;
      r.breadcrumb = r.breadcrumb || [pageLabels.get(r.page) || pretty(r.page), ...(r.routes || []).map(t=>text(routeButtons.get(t.fn+':'+t.tab)) || pretty(t.tab))].join(' → ');
      r.name = normalise(r.label);
      r.haystack = normalise([r.label,r.description,r.breadcrumb,r.keywords].join(' '));
      list.set(r.id,r);
    }
    document.querySelectorAll('.page[id]').forEach(page => {
      const value = page.id.slice(5); if (value === 'search') return;
      const legacyLabel = typeof GLOBAL_PAGES==='undefined' ? '' : GLOBAL_PAGES.find(p=>p[1]===value)?.[0];
      const label = text(page.querySelector('.page-heading h1,.page-header h1,h1')) || legacyLabel || entries.find(e=>e[1]===value&&!e[2])?.[0] || pretty(value);
      pageLabels.set(value,label);
      add({id:'page:'+value,type:'page',label,page:value,routes:[],description:'Open '+label+'.',keywords:entries.filter(e=>e[1]===value).map(e=>e[0]).join(' ')});
    });
    document.querySelectorAll('.page[id]').forEach(page => {
      const value = page.id.slice(5); if (value === 'search') return;
      // All tab panels are destinations, even before their contents render.
      page.querySelectorAll('[id]').forEach(panel => {
        if (!panels.some(([prefix])=>panel.id.startsWith(prefix))) return;
        const routes = routesFor(panel), last = routes.at(-1);
        if (!last) return;
        const label = text(routeButtons.get(last.fn+':'+last.tab)) || pretty(last.tab);
        add({id:'section:'+panel.id,type:'section',label,page:value,routes,target:panel.id,description:'Explore '+label+' in '+pageLabels.get(value)+'.'});
      });
      // Chat is indexed as a page; authenticated conversation contents stay private.
      if (value === 'league-chat') return;
      page.querySelectorAll('h2,h3,h4,[data-search-title]').forEach(h => {
        if (h.closest('[data-search-exclude],.js-plotly-plot,svg')) return;
        const label = h.dataset.searchTitle || text(h); if (!label) return;
        const routes = routesFor(h), target = headingId(h,value,routes);
        const description = text(h.closest('.card')?.querySelector('.card-description'));
        add({id:'section:'+target,type:'section',label,page:value,routes,target,description:description.slice(0,230) || 'View '+label+' in '+pageLabels.get(value)+'.'});
      });
    });
    // Menu entries also cover destinations with no heading or panel of their own.
    entries.forEach(entry => {
      const [label,page,kind,tab,target] = entry;
      if (!pageLabels.has(page) || (!kind && !target)) return;
      const handler = typeof mcdSubtabHandler==='function' && kind ? mcdSubtabHandler(kind) : null;
      const fn = handler?.name;
      const spec = panels.find(p=>p[1]===fn);
      const el = $(target || (spec ? spec[0]+tab : ''));
      if (!el) return;
      const id = 'section:'+el.id;
      if (list.has(id)) { list.get(id).haystack += ' '+normalise(label); return; }
      add({id,type:'section',label,page,routes:routesFor(el),target:el.id,description:'Open '+label+'.'});
    });
    const players = typeof playerSearchData==='undefined' ? [] : playerSearchData;
    const teams = new Set(typeof MANAGER_ORDER==='undefined' ? [] : MANAGER_ORDER);
    Array.from($('my-team-select')?.options || []).forEach(o=>{if(o.text)teams.add(o.text);});
    teams.forEach(label => add({id:'team:'+label,type:'team',label,page:'myteam',description:'Fantasy team · Squad, planner, medical room and team statistics.',keywords:'manager fantasy team squad',value:label}));
    Object.values(typeof CLUB_EXPLORER_DATA==='undefined' ? {} : CLUB_EXPLORER_DATA).forEach(c =>
      add({id:'club:'+c.id,type:'club',label:c.name,page:'clubs',value:String(c.id),description:'Club · Squad, fixtures and performance.',keywords:c.short_name || ''}));
    players.forEach(p => add({id:'player:'+p.id,type:'player',label:p.name,page:'players',value:String(p.id),player:p,
      description:[p.position,p.team,p.fantasy_team || 'Ownership unavailable'].filter(Boolean).join(' · '),keywords:[p.first_name,p.second_name,p.web_name,p.full_name].filter(Boolean).join(' ')}));
    records = [...list.values()]; byId = list;
    return records;
  }
  function near(a,b) {
    if (a.length<4 || Math.abs(a.length-b.length)>1) return false;
    if(a.length===b.length) {
      const diffs=[];for(let i=0;i<a.length;i++)if(a[i]!==b[i])diffs.push(i);
      return diffs.length<=1 || (diffs.length===2 && diffs[1]===diffs[0]+1 && a[diffs[0]]===b[diffs[1]] && a[diffs[1]]===b[diffs[0]]);
    }
    const short=a.length<b.length?a:b, long=a.length<b.length?b:a;
    let i=0,j=0;while(i<short.length&&j<long.length){if(short[i]===long[j])i++;j++;if(j-i>1)return false;}return true;
  }
  function match(q) {
    const n = normalise(q), tokens = n.split(' ').filter(Boolean);
    return records.map(r => {
      if (!n) return {r,score:0};
      let fuzzy=false;
      if (!tokens.every(t => r.haystack.includes(t) || (t.length>=4 && r.name.split(' ').some(w=>near(t,w)) && (fuzzy=true)))) return null;
      return {r,score:(r.name===n?1000:r.name.startsWith(n)?800:r.name.includes(n)?600:tokens.every(t=>r.name.includes(t))?500:100)-(fuzzy?80:0),fuzzy};
    }).filter(Boolean).sort((a,b)=>b.score-a.score || a.r.label.localeCompare(b.r.label) || a.r.id.localeCompare(b.r.id));
  }
  function href(id) { return '#mcd-result='+encodeURIComponent(id); }
  function searchHash(q,kind) { return '#mcd-search='+new URLSearchParams({q,type:kind}).toString(); }
  function updateHash(hash) {
    if(location.hash!==hash) history.pushState(null,'',location.pathname+location.search+hash);
  }
  function hideSuggestions() { $('global-search-results')?.classList.remove('active'); $('global-search')?.setAttribute('aria-expanded','false'); }
  function openTab(fn,tab) { const btn=routeButtons.get(fn+':'+tab); if(typeof window[fn]==='function')window[fn](tab,btn||null); }
  function navigate(r) {
    if (!r) return;
    navigating=true;
    try {
      window.showPage(r.page);
      if(r.type==='team') {
        const select=$('my-team-select'), option=Array.from(select?.options||[]).find(o=>o.text===r.value);
        if(option){select.value=option.value;window.changeMyTeam();}openTab('showMyTeamSubtab','squad');
      } else if(r.type==='club') {
        const select=$('club-explorer-select');if(select){select.value=r.value;window.renderClubExplorer();}openTab('showClubSubtab','overview');
      } else if(r.type==='player') {
        openTab('showPlayerSubtab','directory');
        // Clear directory filters so a search result cannot remain hidden.
        ['player-position-filter','player-club-filter','player-fantasy-filter'].forEach(id=>{if($(id))$(id).value='';});
        if($('player-search'))$('player-search').value=r.label;
        window.filterPlayers();
      } else (r.routes||[]).forEach(t=>openTab(t.fn,t.tab));
      if(typeof mcdNavSync==='function')mcdNavSync(r.page);
    } finally { navigating=false; }
    hideSuggestions();
    requestAnimationFrame(()=>requestAnimationFrame(()=>{
      if(r.type==='player' && $('player-search-results') && typeof renderPlayerDirectoryCard==='function') {
        $('player-search-results').innerHTML=renderPlayerDirectoryCard(r.player);
        if($('player-directory-count'))$('player-directory-count').textContent='1 player';
      }
      const target=$(r.target || (r.type==='player'?'player-search-results':'page-'+r.page));
      if(!target)return;
      for(let p=target.parentElement;p;p=p.parentElement)if(p.tagName==='DETAILS')p.open=true;
      target.scrollIntoView({block:'start',behavior:'auto'});target.setAttribute('tabindex','-1');target.focus({preventScroll:true});
      target.classList.add('search-hit');setTimeout(()=>target.classList.remove('search-hit'),1600);
    }));
  }
  function link(r,label) { const a=node('a',label||r.label);a.href=href(r.id);a.addEventListener('click',event=>{
    if(event.ctrlKey||event.metaKey||event.shiftKey||event.altKey)return;
    event.preventDefault();updateHash(a.hash);navigate(r);
  });return a; }
  function related(r) {
    if(r.type!=='player')return null;
    const group=node('div',null,'search-related'), p=r.player;
    const club=records.find(c=>c.type==='club'&&normalise(c.label)===normalise(p.team));
    const owner=byId.get('team:'+p.fantasy_team);
    if(club)group.append(link(club,'Club'));if(owner)group.append(link(owner,'Fantasy team'));
    // A player-specific search is retained for the analytics tools to consume.
    [['Passport','passport'],['Rating','rating']].forEach(([label,term])=>{
      const section=records.find(c=>c.type==='section'&&c.page==='analytics'&&normalise(c.label).includes(term));
      if(!section)return;
      const a=node('a',label);a.href=href(r.id)+'&view='+term;
      a.addEventListener('click',e=>{if(e.ctrlKey||e.metaKey||e.shiftKey||e.altKey)return;e.preventDefault();updateHash(a.hash);openPlayerView(r,term);});group.append(a);
    });return group;
  }
  function openPlayerView(r,view) {
    const section=records.find(c=>c.type==='section'&&c.page==='analytics'&&normalise(c.label).includes(view));
    if(!section){navigate(r);return;}navigate(section);
    if(view==='passport' && $('passport-player-search')) {
      $('passport-player-search').value=r.label;window.focusPassportSearch?.();
    } else if(view==='rating' && $('rating-lab-search')) {
      $('rating-lab-search').value=r.label;window.ratingLabFind?.();
    }
  }
  function shortcuts() {
    const wrap=$('search-shortcuts');wrap.replaceChildren();
    if(!recent.length)return;wrap.append(node('span','Recent:'));
    recent.forEach(q=>{const b=node('button',q);b.type='button';b.addEventListener('click',()=>openSearch(q,'all'));wrap.append(b);});
    const clear=node('button','Clear history');clear.type='button';clear.addEventListener('click',()=>{recent=[];save('mcd-search-recent',recent);shortcuts();});wrap.append(clear);
  }
  function render() {
    const found=match(query), filters=$('search-filters');filters.replaceChildren();
    Object.entries(kinds).forEach(([kind,label])=>{
      const count=found.filter(({r})=>kind==='all'||(kind==='favourites'?favourites.has(r.id):r.type===kind)).length;
      const btn=node('button',label+' ('+count+')');btn.type='button';btn.setAttribute('aria-pressed',String(category===kind));
      btn.addEventListener('click',()=>openSearch(query,kind,false));filters.append(btn);
    });
    const matches=found.filter(({r})=>category==='all'||(category==='favourites'?favourites.has(r.id):r.type===category));
    $('search-count').textContent=(query?'Results for “'+query+'”':'Browse everything A–Z')+' · '+matches.length+' result'+(matches.length===1?'':'s')+' · Showing '+Math.min(limit,matches.length);
    const list=$('search-list');list.replaceChildren();
    matches.slice(0,limit).forEach(({r,fuzzy})=>{
      const article=node('article',null,'search-result'), content=node('div',null,'search-result-content');
      content.append(node('small',kinds[r.type]+' · '+r.breadcrumb));const h=node('h2');h.append(link(r));content.append(h,node('p',(fuzzy?'Similar match · ':'')+r.description));
      const rel=related(r);if(rel)content.append(rel);
      if(r.type==='player'&&window.McDraftCompare)content.append(window.McDraftCompare.button(r.value));
      const fav=node('button',favourites.has(r.id)?'★':'☆','search-favourite');fav.type='button';
      fav.setAttribute('aria-label',(favourites.has(r.id)?'Remove favourite: ':'Save favourite: ')+r.label);fav.setAttribute('aria-pressed',String(favourites.has(r.id)));
      fav.addEventListener('click',()=>{favourites.has(r.id)?favourites.delete(r.id):favourites.add(r.id);save('mcd-search-favourites',[...favourites]);render();const replacement=Array.from($('search-list').querySelectorAll('.search-favourite')).find(b=>b.getAttribute('aria-label').endsWith(': '+r.label));(replacement||$('search-title')).focus();});
      article.append(content,fav);list.append(article);
    });
    if(!matches.length)list.append(node('p',category==='favourites'?'No saved favourites match. Use the star beside a result to save it.':'No matches. Try a shorter name, a club, or a feature such as planner.'));
    $('search-more').hidden=matches.length<=limit;shortcuts();
  }
  function openSearch(q='',kind='all',remember=true,write=true) {
    query=q.trim().slice(0,240);category=Object.hasOwn(kinds,kind)?kind:'all';limit=30;rebuild();
    if(remember&&query){recent=[query,...recent.filter(x=>x!==query)].slice(0,6);save('mcd-search-recent',recent);}
    if(write)updateHash(searchHash(query,category));
    navigating=true;try{window.showPage('search');}finally{navigating=false;}
    $('search-query').value=query;hideSuggestions();render();$('search-title').focus({preventScroll:true});
  }
  function restore() {
    const hash=location.hash;
    if(hash.startsWith('#mcd-search=')){const params=new URLSearchParams(hash.slice(12));openSearch(params.get('q')||'',params.get('type')||'all',false,false);}
    else if(hash.startsWith('#mcd-result=')){
      const params=new URLSearchParams(hash.slice(1)), r=byId.get(params.get('mcd-result'));
      if(r){const view=params.get('view');view&&r.type==='player'?openPlayerView(r,view):navigate(r);}else openSearch('', 'all',false,false);
    } else if($('page-search').classList.contains('active') || hash.startsWith('#mcd-page=') || (!hash&&history.state?.mcdSearchPage)) {
      const page=hash.startsWith('#mcd-page=')?new URLSearchParams(hash.slice(1)).get('mcd-page'):(history.state?.mcdSearchPage||'overview');
      navigating=true;try{window.showPage(pageLabels.has(page)?page:'overview');}finally{navigating=false;}
    }
  }
  function suggest() {
    const input=$('global-search'), box=$('global-search-results'), q=input.value.trim();box.replaceChildren();
    const results=q?match(q).slice(0,7):[];
    const all=node('button',q?'View all results for “'+q+'” ↵':'Browse every page, section and player','global-search-result');all.type='button';all.addEventListener('click',()=>openSearch(q));box.append(all);
    results.forEach(({r})=>{const b=node('button',null,'global-search-result');b.type='button';b.append(node('strong',r.label),node('span',kinds[r.type]+' · '+r.breadcrumb));b.addEventListener('click',()=>{updateHash(href(r.id));navigate(r);});box.append(b);});
    box.classList.add('active');input.setAttribute('aria-expanded','true');
  }
  function audit() {
    rebuild();const missing=[];
    document.querySelectorAll('.page[id]:not(#page-search)').forEach(p=>{if(!byId.has('page:'+p.id.slice(5)))missing.push(p.id);});
    document.querySelectorAll('.page [id]').forEach(p=>{if(panels.some(([prefix])=>p.id.startsWith(prefix))&&!byId.has('section:'+p.id))missing.push(p.id);});
    records.forEach(r=>{if(!r.label||!$('page-'+r.page)||(r.target&&!$(r.target))||(r.routes||[]).some(t=>typeof window[t.fn]!=='function'))missing.push(r.id);});
    document.querySelectorAll('.page:not(#page-search):not(#page-league-chat) h2,.page:not(#page-search):not(#page-league-chat) h3,.page:not(#page-search):not(#page-league-chat) h4').forEach(h=>{
      if(text(h)&&!h.closest('[data-search-exclude],.js-plotly-plot,svg')&&!byId.has('section:'+h.id))missing.push(text(h));
    });
    routeButtons.forEach((btn,key)=>{if(!panels.some(p=>key.startsWith(p[1]+':')))missing.push('Unregistered tab: '+text(btn));});
    return {total:records.length,counts:Object.fromEntries(Object.keys(kinds).map(k=>[k,records.filter(r=>r.type===k).length])),missing};
  }
  function init() {
    if(!$('page-search')||!$('global-search'))return;
    rebuild();
    if(!location.hash.startsWith('#mcd-'))history.replaceState({...history.state,mcdSearchPage:document.querySelector('.page.active')?.id.slice(5)||'overview'},'',location.href);
    const input=$('global-search'), box=$('global-search-results');
    input.removeAttribute('oninput');input.removeAttribute('onfocus');input.placeholder='Search pages, sections, players, teams, clubs…';
    input.setAttribute('aria-label','Search McDraft');input.setAttribute('aria-controls',box.id);input.setAttribute('aria-expanded','false');
    window.runGlobalSearch=suggest;input.addEventListener('input',suggest);input.addEventListener('focus',suggest);
    input.addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();openSearch(input.value);}else if(e.key==='ArrowDown'){e.preventDefault();if(!box.classList.contains('active'))suggest();box.querySelector('button')?.focus();}else if(e.key==='Escape')hideSuggestions();});
    box.addEventListener('keydown',e=>{const buttons=[...box.querySelectorAll('button')],i=buttons.indexOf(document.activeElement);if(e.key==='Escape'){input.focus();hideSuggestions();}else if(e.key==='ArrowDown'||e.key==='ArrowUp'){e.preventDefault();const next=i+(e.key==='ArrowDown'?1:-1);if(next<0)input.focus();else buttons[Math.min(next,buttons.length-1)]?.focus();}});
    document.addEventListener('click',e=>{if(!e.target.closest('.global-search-wrap'))hideSuggestions();});
    document.addEventListener('keydown',e=>{if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='k'){e.preventDefault();input.focus();input.select();}});
    $('search-form').addEventListener('submit',e=>{e.preventDefault();openSearch($('search-query').value,category);});
    $('search-more').addEventListener('click',()=>{const previous=limit;limit+=30;render();$('search-list').children[previous]?.querySelector('a')?.focus();});
    const browse=node('button','Browse all','search-browse');browse.type='button';browse.addEventListener('click',()=>openSearch());input.parentElement.append(browse);
    const original=window.showPage;
    window.showPage=function(page){
      if(!navigating && /#mcd-(search|result)=/.test(location.hash))updateHash('#mcd-page='+encodeURIComponent(page));
      const result=original.apply(this,arguments);
      if(page!=='search')$('page-search').classList.remove('active');return result;
    };
    window.addEventListener('popstate',restore);window.addEventListener('hashchange',restore);restore();
    window.McDraftSearch={rebuild,audit,search:q=>match(q).map(x=>x.r),open:openSearch,normalise};
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();
