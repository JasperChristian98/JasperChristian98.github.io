/* Shared league chat. Dashboard team selection never establishes chat identity. */
(() => {
  'use strict';
  const root = document.getElementById('page-league-chat');
  if (!root) return;
  const el = id => document.getElementById('chat-' + id);
  const config = window.MCD_CHAT_CONFIG || {};
  const PAGE_SIZE = 100;
  const state = {client:null, userId:null, member:null, epoch:0, channel:null,
    rows:new Map(), oldest:null, hasOlder:false, ready:false, sending:false,
    pending:null, unread:0, refreshPromise:null, syncVersion:0, live:false};
  let sdkPromise, startPromise, loggingIn=false, authSubscription, poll;
  const teamLogins=config.teamLogins || {};
  Object.keys(teamLogins).forEach(name=>el('team').add(new Option(name,name)));
  function selectViewedTeam(manager) {
    if(!state.userId && !loggingIn && Object.hasOwn(teamLogins,manager)) {
      el('team').value=manager;el('password').value='';
    }
  }
  selectViewedTeam(document.getElementById('mcd-header-team')?.value);
  if(typeof window.syncManagerSelection==='function') {
    const original=window.syncManagerSelection;
    window.syncManagerSelection=function(manager,source){original(manager,source);selectViewedTeam(manager);};
  }
  el('team').addEventListener('change',()=>{el('password').value='';});
  function status(message, error=false) {
    el('status').textContent = message;
    el('status').dataset.error = String(error);
  }
  function connection(message) { el('connection').textContent = message; }
  function active() { return root.classList.contains('active') && !document.hidden; }
  function atBottom() {
    const box=el('messages');
    return box.scrollHeight-box.scrollTop-box.clientHeight < 70;
  }
  function unread() {
    el('new').hidden = !state.unread;
    el('new').textContent = state.unread + ' new message' + (state.unread===1?'':'s') + ' ↓';
  }
  function latest() {
    el('messages').scrollTop = el('messages').scrollHeight;
    state.unread=0; unread();
  }
  function messageNode(row) {
    const article=document.createElement('article');
    article.className='mcd-chat-message'+(row.user_id===state.userId?' own':'');
    const header=document.createElement('header'),author=document.createElement('strong');
    author.textContent=row.manager_name;
    const time=document.createElement('time'),date=new Date(row.created_at);
    time.dateTime=row.created_at;
    time.textContent=Number.isNaN(date.valueOf())?'':date.toLocaleString([],{
      month:'short',day:'numeric',hour:'2-digit',minute:'2-digit'});
    const body=document.createElement('p'); body.textContent=row.body;
    header.append(author,time); article.append(header,body); return article;
  }
  function render(stick=false, preserve=false) {
    const box=el('messages'),height=box.scrollHeight,top=box.scrollTop;
    const rows=[...state.rows.values()].sort((a,b)=>Number(a.id)-Number(b.id));
    box.replaceChildren(...rows.map(messageNode));
    el('empty').hidden=rows.length>0 || !state.ready;
    el('older').disabled=!state.hasOlder;
    if(stick) latest();
    else box.scrollTop=preserve?top+box.scrollHeight-height:top;
    unread();
  }
  function merge(rows, notify=false) {
    const stick=active() && atBottom(); let added=0,changed=false;
    for(const row of rows) {
      const key=String(row.id);
      if(!state.rows.has(key))added++;
      if(JSON.stringify(state.rows.get(key))!==JSON.stringify(row))changed=true;
      state.rows.set(key,row);
    }
    if(notify && !stick) state.unread+=added;
    if(changed)render(stick);
  }
  function clearRoom() {
    state.epoch++; state.syncVersion++; state.refreshPromise=null;
    if(state.channel) state.client.removeChannel(state.channel);
    state.channel=null; state.rows.clear(); state.member=null; state.oldest=null;
    state.hasOlder=false; state.ready=false; state.pending=null; state.sending=false;
    state.unread=0; state.live=false;
    el('message').value=''; el('send').disabled=false;
    el('password').value='';
    el('messages').replaceChildren(); el('room').hidden=true; unread();
  }
  function denyMembership() {
    clearRoom(); connection('Membership required');
    el('identity').textContent='Signed in · awaiting league access';
    status('Your account is signed in, but the organiser has not enabled your league membership. Use Reconnect once it is ready.');
  }
  async function membership() {
    const {data,error}=await state.client.from('league_chat_members')
      .select('user_id,manager_name,active').eq('user_id',state.userId).maybeSingle();
    if(error)throw error;
    return data?.active?data:null;
  }
  async function refresh(reset=false) {
    if(!state.userId || !state.member)return;
    // Serialize refreshes; a reconnect resets the window after an in-flight poll.
    if(state.refreshPromise) {
      const waiting=state.refreshPromise;
      if(reset) {await waiting; return refresh(true);}
      return waiting;
    }
    const epoch=state.epoch;
    const work=(async()=>{
      try {
        const member=await membership(); if(epoch!==state.epoch)return;
        if(!member){denyMembership();return;}
        const {data,error}=await state.client.from('league_chat_messages')
          .select('id,user_id,manager_name,body,created_at').order('id',{ascending:false}).limit(PAGE_SIZE);
        if(epoch!==state.epoch)return;
        if(error)throw error;
        state.member=member;el('identity').textContent='Signed in as '+member.manager_name;
        el('room').hidden=false;
        if(reset || !state.ready) {
          state.syncVersion++;
          // Preserve inserts that arrived while the initial history request ran.
          const newest=data.length?Number(data[0].id):0;
          const arrivals=[...state.rows.values()].filter(r=>Number(r.id)>newest);
          state.rows.clear();for(const row of [...data,...arrivals])state.rows.set(String(row.id),row);
          state.oldest=data.length?data[data.length-1].id:null;
          state.hasOlder=data.length===PAGE_SIZE;state.ready=true;render(true);
        } else {
          merge(data,true);
        }
        el('room').hidden=false;
        connection(state.live?'Live':'Connected · checking for messages');
        if(reset)status('Live messages, with automatic catch-up every second while this room is open.');
      } catch(error) {
        if(epoch!==state.epoch)return;
        connection('Reconnecting');status('Could not refresh chat. Your draft is still here. Retrying shortly.',true);
      }
    })();
    state.refreshPromise=work;
    await work;
    if(epoch===state.epoch)state.refreshPromise=null;
  }
  async function sessionChanged(session, force=false) {
    const id=session?.user?.id || null;
    if(!force && id===state.userId)return;
    const draft=id && id===state.userId?el('message').value:'';
    const pending=id && id===state.userId?state.pending:null;
    clearRoom();state.userId=id;
    el('message').value=draft;state.pending=pending;
    el('auth').hidden=!!id;el('account').hidden=!id;
    el('identity').textContent=id?'Checking membership…':'';
    if(!id){connection('Signed out');status('Sign in to join the conversation.');return;}
    const epoch=state.epoch;
    connection('Connecting');
    try {
      const member=await membership();if(epoch!==state.epoch)return;
      if(!member){denyMembership();return;}
      state.member=member;
      state.channel=state.client.channel('mcdraft-league-chat')
        .on('postgres_changes',{event:'INSERT',schema:'public',table:'league_chat_messages'},payload=>{
          if(epoch===state.epoch && state.member)merge([payload.new],true);
        }).subscribe(channelStatus=>{
          if(epoch!==state.epoch)return;
          state.live=channelStatus==='SUBSCRIBED';
          if(state.live)void refresh(true);
          else if(['CHANNEL_ERROR','TIMED_OUT','CLOSED'].includes(channelStatus)) {
            connection('Reconnecting');status('Live connection interrupted. Checking for messages while it reconnects.');
          }
        });
      await refresh(true);
    }catch(error){if(epoch===state.epoch){connection('Connection failed');status('Could not open your league membership. Try Reconnect.',true);}}
  }
  function loadSDK() {
    if(window.supabase?.createClient)return Promise.resolve();
    if(sdkPromise)return sdkPromise;
    sdkPromise=new Promise((resolve,reject)=>{
      const script=document.createElement('script');script.src='assets/vendor/supabase-2.117.2.js';
      script.onload=()=>window.supabase?.createClient?resolve():reject(Error('Client unavailable'));
      script.onerror=()=>{script.remove();reject(Error('Client could not load'));};
      document.head.appendChild(script);
    }).catch(error=>{sdkPromise=null;throw error;});
    return sdkPromise;
  }
  async function start() {
    if(startPromise)return startPromise;
    startPromise=(async()=>{
      try {
        await loadSDK();
        if(!state.client) {
          state.client=window.supabase.createClient(config.supabaseUrl,config.publishableKey,{
            auth:{persistSession:true,autoRefreshToken:true,detectSessionInUrl:false,storageKey:'mcdraft-league-chat-auth'}
          });
          // Supabase warns against awaiting auth API calls inside this callback.
          authSubscription=state.client.auth.onAuthStateChange((event,session)=>{
            if(!loggingIn)setTimeout(()=>void sessionChanged(session),0);
          }).data.subscription;
          let ticks=0;
          poll=setInterval(()=>{
            ticks++;
            if(!document.hidden && state.member && (active() || ticks%15===0))void refresh();
          },1000);
        }
        const {data,error}=await state.client.auth.getSession();if(error)throw error;
        await sessionChanged(data.session,true);
      }catch(error){connection('Connection failed');status('Chat could not connect. Please try Reconnect.',true);}
      finally{startPromise=null;}
    })();
    return startPromise;
  }
  el('login-form').addEventListener('submit',async event=>{
    event.preventDefault();if(!state.client || loggingIn)return;
    const team=el('team').value,email=teamLogins[team],password=el('password').value;
    if(!Object.hasOwn(teamLogins,team) || !password)return;
    loggingIn=true;el('login').disabled=true;el('team').disabled=true;el('password').value='';
    try {
      const {data,error}=await state.client.auth.signInWithPassword({email,password});
      if(error)throw error;
      await sessionChanged(data.session,true);
    }catch(error){status('Could not sign in. Check the team and password, or try again shortly.',true);}
    finally{loggingIn=false;el('login').disabled=false;el('team').disabled=false;}
  });
  el('signout').addEventListener('click',async()=>{
    el('signout').disabled=true;
    try {
      const {error}=await state.client.auth.signOut({scope:'local'});if(error)throw error;
      await sessionChanged(null,true);
      el('share-preview').hidden=true;el('share-text').textContent='';
    }catch(error){status('Could not finish signing out. Please retry.',true);}
    finally{el('signout').disabled=false;}
  });
  el('compose').addEventListener('submit',async event=>{
    event.preventDefault();if(state.sending || !state.member)return;
    const body=el('message').value.trim();if(!body || body.length>2000)return;
    const epoch=state.epoch;state.sending=true;el('send').disabled=true;
    // A failed request may have committed. Reuse the key on an unchanged retry.
    if(!state.pending || state.pending.body!==body)state.pending={body,id:crypto.randomUUID()};
    try {
      const {data,error}=await state.client.rpc('send_league_chat_message',{
        p_body:body,p_client_id:state.pending.id
      });
      if(epoch!==state.epoch)return;
      if(error)throw error;
      merge([data],false);latest();
      if(el('message').value.trim()===body)el('message').value='';
      state.pending=null;status('Message sent.');
    }catch(error){
      if(epoch===state.epoch)status(error.message?.includes('three seconds')?
        'Please wait three seconds before sending again.':
        'Message not confirmed. Your text is still here; retry to confirm it without posting a duplicate.',true);
    }finally{if(epoch===state.epoch){state.sending=false;el('send').disabled=false;}}
  });
  el('message').addEventListener('keydown',event=>{
    if(event.key==='Enter' && (event.ctrlKey || event.metaKey) && !event.isComposing){event.preventDefault();el('compose').requestSubmit();}
  });
  el('older').addEventListener('click',async()=>{
    if(!state.hasOlder || !state.oldest)return;
    const epoch=state.epoch,version=state.syncVersion;el('older').disabled=true;
    try {
      const {data,error}=await state.client.from('league_chat_messages')
        .select('id,user_id,manager_name,body,created_at').lt('id',state.oldest)
        .order('id',{ascending:false}).limit(PAGE_SIZE);
      if(epoch!==state.epoch || version!==state.syncVersion)return;
      if(error)throw error;
      for(const row of data)state.rows.set(String(row.id),row);
      state.oldest=data.length?data[data.length-1].id:state.oldest;
      state.hasOlder=data.length===PAGE_SIZE;render(false,true);
    }catch(error){if(epoch===state.epoch)status('Earlier messages could not load. Try again.',true);}
    finally{if(epoch===state.epoch)el('older').disabled=!state.hasOlder;}
  });
  el('new').addEventListener('click',latest);
  el('messages').addEventListener('scroll',()=>{if(active() && atBottom()){state.unread=0;unread();}});
  el('refresh').addEventListener('click',()=>void refresh(true));
  el('reconnect').addEventListener('click',()=>void start());
  window.mcdChatDraftShare=function(text){
    el('share-text').textContent=String(text);el('share-preview').hidden=false;
    if(typeof showPage==='function')showPage('league-chat');
    if(typeof mcdNavSync==='function')mcdNavSync();
    el('share-preview').scrollIntoView({block:'nearest'});
  };
  el('share-cancel').addEventListener('click',()=>{el('share-preview').hidden=true;el('share-text').textContent='';});
  el('share-add').addEventListener('click',()=>{
    if(!state.member){status('Sign in to add this to your message. The preview will stay here.');return;}
    const text=[el('message').value.trim(),el('share-text').textContent].filter(Boolean).join('\n\n');
    if(text.length>2000){status('This would exceed 2,000 characters. Shorten your draft before adding the share.',true);return;}
    el('message').value=text;el('share-preview').hidden=true;el('share-text').textContent='';el('message').focus();
    status('Added to your draft. Edit it or press Send message when ready.');
  });
  window.addEventListener('online',()=>{if(state.member)void refresh(true);});
  window.addEventListener('offline',()=>connection('Offline · messages will reconnect'));
  document.addEventListener('visibilitychange',()=>{if(!document.hidden && state.member)void refresh(true);});
  // Only load a backend client when configured; ordinary dashboard use stays local.
  if(!config.supabaseUrl || !config.publishableKey){
    el('setup').hidden=false;connection('Coming soon');status('The league room is not open yet.');return;
  }
  try {
    const url=new URL(config.supabaseUrl);
    if(url.protocol!=='https:' || !config.publishableKey.startsWith('sb_publishable_'))throw Error('Invalid config');
  }catch(error){el('setup').hidden=false;connection('Unavailable');status('The organiser needs to check the chat connection settings.');return;}
  el('reconnect').hidden=false;
  if(!Object.keys(teamLogins).length){el('setup').hidden=false;status('The organiser needs to configure team logins.');return;}
  void start();
})();
