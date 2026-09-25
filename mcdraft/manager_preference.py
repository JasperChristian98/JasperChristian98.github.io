"""Entry-screen manager selection for the existing McDraft dashboard.

Every page load starts at the welcome screen. A saved choice is preselected, but
no dashboard content is revealed until the visitor confirms their team. After entering, the global manager picker stays beside the header search bar.
The welcome screen still appears on every fresh visit.
"""

# Welcome selection is confirmed once per visit; the header selector stays available afterwards.
MANAGER_WELCOME_HTML = '''<section id="mcd-manager-welcome" class="mcd-manager-welcome" role="dialog" aria-modal="true" aria-labelledby="mcd-welcome-heading">
  <div class="mcd-welcome-card">
    <div class="mcd-welcome-eyebrow"><span class="mcd-welcome-indicator" aria-hidden="true"></span> FPL DRAFT DASHBOARD</div>
    <h1 id="mcd-welcome-heading">Welcome to <span class="mcd-welcome-league">__LEAGUE_NAME__</span></h1>
    <p class="mcd-welcome-subtitle">Select your team to personalise your McDraft experience.</p>
    <form id="mcd-welcome-form" onsubmit="event.preventDefault(); enterManagerDashboard()">
      <label for="mcd-welcome-team">YOUR TEAM</label>
      <select id="mcd-welcome-team" required aria-required="true"><option value="">Choose your team…</option></select>
      <button id="mcd-welcome-continue" type="submit" disabled>Enter dashboard <span aria-hidden="true">→</span></button>
    </form>
    <div class="mcd-welcome-foot">Your choice sets the default for My Team, War Room, the five-GW planner and Decision Centre. You can change your team anytime beside the search bar.</div>
  </div>
</section>'''

MANAGER_HEADER_HTML = '''<label class="mcd-header-manager" for="mcd-header-team">
  <span>YOUR TEAM</span>
  <select id="mcd-header-team" aria-label="Select your manager" onchange="syncManagerSelection(this.value,'header')"></select>
</label>'''

MANAGER_PICKER_CSS = '''
/* Use the same tokens, blue accent, typography, surfaces and borders as McDraft. */
.mcd-manager-welcome{position:fixed;inset:0;z-index:999999;display:flex;align-items:center;justify-content:center;padding:24px;background:var(--bg);color:var(--text);overflow-y:auto;box-sizing:border-box}
.mcd-manager-welcome[hidden]{display:none!important}
.mcd-welcome-card{width:min(100%,560px);padding:clamp(28px,5vw,48px);border:1px solid var(--border);border-radius:18px;background:var(--card);box-shadow:0 20px 60px rgba(0,0,0,.24);text-align:left;box-sizing:border-box}
.mcd-welcome-eyebrow{display:flex;align-items:center;gap:9px;color:var(--accent);font-size:11px;font-weight:850;letter-spacing:.14em}
.mcd-welcome-indicator{width:9px;height:9px;border-radius:50%;background:var(--accent);box-shadow:0 0 0 4px color-mix(in srgb,var(--accent) 15%,transparent)}
.mcd-welcome-card h1{font-size:clamp(30px,5vw,45px);line-height:1.13;letter-spacing:-.035em;margin:23px 0 13px;color:var(--text);font-weight:850}
.mcd-welcome-league{display:block;color:var(--accent);overflow-wrap:anywhere}
.mcd-welcome-card .mcd-welcome-subtitle{color:var(--muted);font-size:15px;line-height:1.65;margin:0}
#mcd-welcome-form{display:flex;flex-direction:column;gap:13px;margin-top:35px}
#mcd-welcome-form label{font-weight:850;font-size:11px;letter-spacing:.09em;color:var(--muted)}
#mcd-welcome-team{width:100%;min-height:51px;background:var(--bg-secondary);color:var(--text);border:1px solid var(--border-light);border-radius:10px;padding:13px 14px;font:inherit;cursor:pointer}
#mcd-welcome-team:hover{border-color:var(--accent)}
#mcd-welcome-team:focus-visible,#mcd-welcome-continue:focus-visible{outline:2px solid var(--accent);outline-offset:3px}
#mcd-welcome-continue{display:flex;align-items:center;justify-content:center;gap:12px;background:var(--accent);color:#061523;border:0;border-radius:10px;min-height:51px;padding:13px 16px;font:inherit;font-weight:850;cursor:pointer;transition:filter .15s ease}
#mcd-welcome-continue:hover:not(:disabled){filter:brightness(1.08)}
#mcd-welcome-continue:disabled{opacity:.42;cursor:not-allowed}
.mcd-welcome-foot{border-top:1px solid var(--border);margin-top:29px;padding-top:19px;color:var(--muted);font-size:12px;line-height:1.55}
body.mcd-welcome-open{overflow:hidden}
/* Keep the universal manager selector alongside global search on every page. */
.mcd-header-manager{display:flex;align-items:center;gap:9px;flex:0 1 225px;min-width:155px;color:var(--muted);font-size:10px;font-weight:850;letter-spacing:.06em;white-space:nowrap}
.mcd-header-manager select{min-width:0;width:100%;min-height:40px;padding:9px 27px 9px 10px;border:1px solid var(--border);border-radius:9px;color:var(--text);background:var(--bg-secondary);font:inherit;font-size:12px;font-weight:750;letter-spacing:0;cursor:pointer}
.mcd-header-manager select:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
/* The global picker replaces the redundant My Team selector; the original select
   remains in the DOM because legacy planner and radar functions consume it. */
#page-myteam .my-team-selector-row > .my-team-select-wrap{display:none!important}
/* Single source of team selection: the header beside search. Retain the
   hidden legacy selects because existing render functions depend on them. */
#decision-centre .decision-head > label:has(#decision-manager),
#myteam-sub-war-room .war-room-manager-select{display:none!important}
@media(max-width:900px){.mcd-header-manager{flex:1 1 170px}.mcd-header-manager span{display:none}}
@media(max-width:520px){.mcd-header-manager{min-width:125px;flex:1 1 135px}.mcd-header-manager select{min-height:38px;font-size:11px}}
@media(max-width:620px){.mcd-manager-welcome{padding:14px}.mcd-welcome-card{padding:32px 24px}}
'''

MANAGER_PICKER_JS = r'''
const MCD_MANAGER_PREFERENCE_KEY = 'mcdraft-preferred-manager-v1';
let mcdPreferredManager = null;
let mcdWelcomePreviouslyFocused = null;

function preferredManagerName(){
  if(mcdPreferredManager && MANAGER_ORDER.includes(mcdPreferredManager)) return mcdPreferredManager;
  try {
    const saved=localStorage.getItem(MCD_MANAGER_PREFERENCE_KEY);
    if(saved && MANAGER_ORDER.includes(saved)) return saved;
    const legacy=localStorage.getItem('fpl-draft-my-team');
    const index=Number(legacy);
    if(legacy!==null && Number.isInteger(index) && index>=0 && index<MANAGER_ORDER.length){
      return MANAGER_ORDER[index];
    }
  }catch(e){}
  return MANAGER_ORDER[defaultMyTeamIndex] || MANAGER_ORDER[0] || null;
}

function initialiseManagerPreference(){
  const select=document.getElementById('mcd-welcome-team');
  if(!select || !MANAGER_ORDER.length) return;
  select.replaceChildren(new Option('Choose your team…',''),...MANAGER_ORDER.map(name=>new Option(name,name)));
  const header=document.getElementById('mcd-header-team');
  if(header) header.replaceChildren(...MANAGER_ORDER.map(name=>new Option(name,name)));
  const preferred=preferredManagerName();
  select.value=preferred || '';
  if(header && preferred) header.value=preferred;
  select.addEventListener('change',updateWelcomeContinue);
  updateWelcomeContinue();
  // Explicit confirmation is required on each dashboard visit, even when a
  // browser has remembered the manager from a previous visit.
  openManagerWelcome();
}

function updateWelcomeContinue(){
  const select=document.getElementById('mcd-welcome-team');
  const button=document.getElementById('mcd-welcome-continue');
  if(button) button.disabled=!select || !MANAGER_ORDER.includes(select.value);
}

function openManagerWelcome(){
  const modal=document.getElementById('mcd-manager-welcome');
  const select=document.getElementById('mcd-welcome-team');
  if(!modal || !select) return;
  mcdWelcomePreviouslyFocused=document.activeElement;
  const saved=preferredManagerName();
  if(saved && MANAGER_ORDER.includes(saved)) select.value=saved;
  updateWelcomeContinue();
  modal.hidden=false;
  document.body.classList.add('mcd-welcome-open');
  const app=document.querySelector('.app-shell');
  if(app) app.inert=true;
  select.focus();
}

function enterManagerDashboard(){
  const select=document.getElementById('mcd-welcome-team');
  const manager=select?.value;
  if(!manager || !MANAGER_ORDER.includes(manager)) return;
  syncManagerSelection(manager,'welcome');
  const modal=document.getElementById('mcd-manager-welcome');
  if(modal) modal.hidden=true;
  document.body.classList.remove('mcd-welcome-open');
  const app=document.querySelector('.app-shell');
  if(app) app.inert=false;
  const firstNav=document.querySelector('.app-shell button, .app-shell a, .app-shell select');
  if(firstNav) firstNav.focus();
}

function syncManagerSelection(manager, source){
  if(!MANAGER_ORDER.includes(manager)) return;
  mcdPreferredManager=manager;
  const index=MANAGER_ORDER.indexOf(manager);
  // Keep the permanent header control and welcome screen consistent.
  const header=document.getElementById('mcd-header-team');
  if(header && header.value!==manager) header.value=manager;
  const welcome=document.getElementById('mcd-welcome-team');
  if(welcome && welcome.value!==manager) welcome.value=manager;
  try {
    localStorage.setItem(MCD_MANAGER_PREFERENCE_KEY,manager);
    localStorage.setItem('fpl-draft-my-team',String(index));
  }catch(e){}
  const mine=document.getElementById('my-team-select');
  if(mine && Number(mine.value)!==index){
    mine.value=String(index);
    if(source!=='myteam') changeMyTeam();
  }
  const war=document.getElementById('war-room-manager');
  if(war && war.options.length && war.value!==manager){
    war.value=manager;
    if(typeof renderManagerWarRoom==='function') renderManagerWarRoom();
  }
  const decision=document.getElementById('decision-manager');
  if(decision && decision.options.length && decision.value!==manager){
    decision.value=manager;
    if(typeof renderDecisionCentre==='function') renderDecisionCentre();
  }
}

// Prevent keyboard focus from escaping the welcome screen until a team is chosen.
document.addEventListener('keydown',function(event){
  const modal=document.getElementById('mcd-manager-welcome');
  if(!modal || modal.hidden || event.key!=='Tab') return;
  const controls=[...modal.querySelectorAll('select,button:not([disabled])')];
  if(!controls.length) return;
  const first=controls[0],last=controls[controls.length-1];
  if(event.shiftKey && document.activeElement===first){event.preventDefault();last.focus();}
  else if(!event.shiftKey && document.activeElement===last){event.preventDefault();first.focus();}
});
'''


def integrate_client(javascript: str) -> str:
    """Insert explicit, checked hooks without altering the 11 preserved stages."""
    replacements = (
        ('function initialiseDashboard() {\n',
         'function initialiseDashboard() {\n    safeInit("welcome screen", initialiseManagerPreference);\n'),
        ('    renderMyTeamH2H();\n}\n\n\nfunction initialiseMyTeam()',
         '    renderMyTeamH2H();\n    if (typeof syncManagerSelection === "function" && mcdPreferredManager) syncManagerSelection(MANAGER_ORDER[selectedIndex], "myteam");\n}\n\n\nfunction initialiseMyTeam()'),
        ("else if(MANAGER_ORDER.includes('Kamararama FC')) select.value='Kamararama FC';",
         "else if(MANAGER_ORDER.includes(preferredManagerName())) select.value=preferredManagerName();"),
        ("const preferred=(typeof MY_TEAM_DEFAULT_MANAGER!=='undefined'&&MY_TEAM_DEFAULT_MANAGER)||MANAGER_ORDER[0];",
         "const preferred=preferredManagerName()||MANAGER_ORDER[0];"),
    )
    for before, after in replacements:
        count=javascript.count(before)
        if count!=1:
            raise RuntimeError(f'Manager welcome integration anchor changed: {before[:65]!r}, matches={count}')
        javascript=javascript.replace(before,after,1)
    return javascript+'\n'+MANAGER_PICKER_JS
