/* Offline fake Supabase transport. Never contacts a service or sends email. */
window.MCD_CHAT_CONFIG={supabaseUrl:'https://chat.invalid',publishableKey:'sb_publishable_offline_test',teamLogins:{'Verified manager':'team-a@chat.mcdraft.invalid','Other manager':'team-b@chat.mcdraft.invalid'}};
const playerSearchData=[{id:1,name:'Free <agent>',position:'MID',team:'Club',fantasy_team:'Free Agent',total_points:42,form:5,player_value:70}];
const mcdNegOffers=[{manager:'Verified manager',partner:'Other manager',category:'Ambitious',give:[{name:'A',position:'MID'}],receive:[{name:'B',position:'MID'}]}];
const MCD_MATCHUP_STATS={'Verified manager':{games:[{gw:1,opponent:'Other manager',points:50,against:40}]},'Other manager':{games:[{gw:1,opponent:'Verified manager',points:40,against:50}]}};
function currentMyTeamManager(){return 'Verified manager';}
function mcdNegDiscover(){return mcdNegOffers;}
window.chatMock={queries:0,user:null,authCallback:null,realtime:null,channelStatus:null,failSend:false,
  failQuery:false,member:true,sends:[],loginOptions:null,rows:[],nextId:151};
for(let i=1;i<=150;i++)chatMock.rows.push({id:i,user_id:'other',manager_name:'Other manager',body:'Message '+i,created_at:'2026-09-25T12:00:00Z'});
window.syncManagerSelection=function(){};
const fakeClient={
  auth:{
    onAuthStateChange(fn){chatMock.authCallback=fn;return {data:{subscription:{unsubscribe(){}}}};},
    async getSession(){return {data:{session:chatMock.user?{user:{id:chatMock.user}}:null},error:null};},
    async signInWithPassword(options){
      chatMock.loginOptions=options;
      if(options.password!=='correct-test-password' || options.email!=='team-a@chat.mcdraft.invalid')return {data:{session:null},error:{message:'Invalid login credentials'}};
      chatMock.user='manager-a';const session={user:{id:chatMock.user}};chatMock.authCallback('SIGNED_IN',session);return {data:{session},error:null};
    },
    async signOut(){chatMock.user=null;chatMock.authCallback('SIGNED_OUT',null);return {error:null};}
  },
  from(table){
    let before=null;
    return {select(){return this;},eq(){return this;},order(){return this;},lt(key,value){before=value;return this;},
      async maybeSingle(){return {data:chatMock.member?{user_id:chatMock.user,manager_name:'Verified manager',active:true}:null,error:null};},
      async limit(n){chatMock.queries++;return {data:chatMock.rows.filter(r=>before===null||r.id<before).sort((a,b)=>b.id-a.id).slice(0,n),error:chatMock.failQuery?{message:'offline'}:null};}
    };
  },
  channel(){return {on(event,filter,callback){chatMock.realtime=callback;return this;},subscribe(callback){chatMock.channelStatus=callback;setTimeout(()=>callback('SUBSCRIBED'),1);return this;}};},
  removeChannel(){return Promise.resolve();},
  async rpc(name,args){
    chatMock.sends.push(args);
    let row=chatMock.rows.find(r=>r.client_id===args.p_client_id);
    if(!row){row={id:chatMock.nextId++,client_id:args.p_client_id,user_id:chatMock.user,manager_name:'Verified manager',body:args.p_body,created_at:'2026-09-25T12:00:00Z'};chatMock.rows.push(row);}
    if(chatMock.failSend){chatMock.failSend=false;return {data:null,error:{message:'lost reply'}};}
    return {data:row,error:null};
  }
};
window.supabase={createClient(){return fakeClient;}};

window.addEventListener('load',async()=>{
  const checks=[],el=id=>document.getElementById('chat-'+id);
  const sleep=()=>new Promise(resolve=>setTimeout(resolve,20));
  async function until(condition){for(let i=0;i<100;i++){if(condition())return;await sleep();}throw Error('Timed out');}
  function check(ok,label){if(!ok)throw Error(label);checks.push(label);}
  function submit(id){el(id).dispatchEvent(new Event('submit',{bubbles:true,cancelable:true}));}
  try {
    await until(()=>!el('auth').hidden);
    check(el('room').hidden,'Signed-out visitors cannot see messages');
    window.mcdChatShareTrade(0);
    check(!el('share-preview').hidden&&el('share-text').textContent.includes('TRANSFER PROPOSAL'),'Trade opens a share preview');
    el('share-add').click();check(el('message').value==='','Sharing requires sign-in before drafting');
    el('password').value='unfinished';window.syncManagerSelection('Other manager');
    check(el('team').value==='Other manager'&&el('password').value==='','Viewed team prefills login without keeping another teams password');
    window.syncManagerSelection('Verified manager');
    el('team').value='Verified manager';el('password').value='wrong-password';submit('login-form');
    await until(()=>!el('login').disabled);
    check(el('room').hidden&&el('status').textContent.includes('Could not sign in'),'Wrong password cannot open chat');
    check(el('password').value==='','Password field cleared after failed attempt');
    el('password').value='correct-test-password';submit('login-form');
    await until(()=>!el('room').hidden&&el('messages').children.length===100);
    check(el('identity').textContent.includes('Verified manager'),'Backend identity is displayed');
    check(chatMock.loginOptions.email==='team-a@chat.mcdraft.invalid','Selected team resolves to its login alias');
    check(el('password').value==='','Password field cleared after successful attempt');
    el('share-add').click();
    check(el('message').value.includes('A (MID)')&&el('message').value.includes('B (MID)'),'Full transfer is added after sign-in');
    check(chatMock.sends.length===0,'Sharing does not send automatically');
    el('share-kind').value='result';el('share-kind').dispatchEvent(new Event('change'));
    check(el('share-item').options.length===1,'Results are deduplicated across both managers');
    el('share-pick').click();check(el('share-text').textContent.includes('50–40'),'Result preview uses completed score');el('share-cancel').click();
    el('share-kind').value='agent';el('share-kind').dispatchEvent(new Event('change'));el('share-pick').click();
    check(el('share-text').textContent.includes('Free <agent>')&&!el('share-text').querySelector('agent'),'Free agent share is safe plain text');
    el('message').value='x'.repeat(2000);el('share-add').click();
    check(el('message').value.length===2000&&!el('share-preview').hidden,'Oversized share does not overwrite draft');
    el('message').value='My take';el('share-add').click();
    check(el('message').value.startsWith('My take\n\nFREE AGENT'),'Sharing preserves existing commentary');
    window.syncManagerSelection('Other manager');
    check(el('identity').textContent.includes('Verified manager'),'Browsing another team does not change chat identity');
    el('older').click();await until(()=>el('messages').children.length===150);
    check(el('older').disabled,'History pagination reaches the start');
    el('message').value='<img src=x onerror="window.chatXss=true">';submit('compose');
    await until(()=>el('message').value==='');
    check(!el('messages').querySelector('img')&&!window.chatXss,'Message markup is rendered as plain text');
    check(!('manager_name' in chatMock.sends[0]),'Sender name is never supplied by the browser');
    const row=chatMock.rows[chatMock.rows.length-1];chatMock.realtime({new:row});
    check(el('messages').children.length===151,'Realtime echo is deduplicated');
    el('message').value='Retry me';chatMock.failSend=true;submit('compose');
    await until(()=>!el('send').disabled);
    check(el('message').value==='Retry me','Failed sends preserve draft');
    submit('compose');await until(()=>el('message').value==='');
    check(chatMock.sends[1].p_client_id===chatMock.sends[2].p_client_id,'Retry preserves idempotency key');
    check(chatMock.rows.filter(r=>r.body==='Retry me').length===1,'Lost response retry posts only once');
    el('message').value='Draft through reconnect';el('reconnect').click();
    await until(()=>!el('room').hidden);
    check(el('message').value==='Draft through reconnect','Reconnect preserves draft');
    chatMock.rows.push({id:chatMock.nextId++,user_id:'other',manager_name:'Other',body:'Missed while offline',created_at:'2026-09-25T12:10:00Z'});
    window.dispatchEvent(new Event('online'));
    await until(()=>el('messages').textContent.includes('Missed while offline'));
    check(true,'Reconnect catches up missed messages');
    const first=el('messages').firstElementChild,count=chatMock.queries;
    await until(()=>chatMock.queries>count);
    check(el('messages').firstElementChild===first,'Unchanged automatic refresh preserves message DOM');
    chatMock.rows.push({id:chatMock.nextId++,user_id:'other',manager_name:'Other',body:'Caught by one-second poll',created_at:'2026-09-25T12:11:00Z'});
    await until(()=>el('messages').textContent.includes('Caught by one-second poll'));
    check(true,'One-second polling catches messages without Realtime or manual refresh');
    chatMock.member=false;el('refresh').click();await until(()=>el('room').hidden);
    check(!el('messages').children.length,'Revoked membership clears message history');
    el('signout').click();await until(()=>!el('auth').hidden);
    check(!el('messages').children.length&&el('message').value==='','Sign-out clears messages and draft');
    check(document.documentElement.scrollWidth<=window.innerWidth,'No horizontal page overflow');
  }catch(error){checks.push('FAILED: '+error.stack);}
  const report=document.createElement('pre');report.id='chat-test-report';report.textContent=JSON.stringify(checks);report.style.whiteSpace='pre-wrap';document.body.appendChild(report);
});
