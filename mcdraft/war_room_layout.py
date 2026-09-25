"""Move War Room under My Team without touching the preserved legacy stages.

Keep legacy hidden select elements: existing renderers depend on their IDs.
"""
import re

WAR_ROOM_NAV_JS = r'''
/* Older links (including Decision Centre CTAs) now open the My Team War Room. */
const mcdOriginalShowPage = showPage;
showPage = function(pageName) {
  if (pageName === 'war-room') {
    mcdOriginalShowPage('myteam');
    const tab=document.querySelector('.myteam-tab[data-myteam-section="war-room"]');
    showMyTeamSubtab('war-room',tab);
    return;
  }
  return mcdOriginalShowPage(pageName);
};
const mcdOriginalShowMyTeamSubtab = showMyTeamSubtab;
showMyTeamSubtab = function(name, button) {
  const result=mcdOriginalShowMyTeamSubtab(name,button);
  if(name==='war-room') requestAnimationFrame(renderManagerWarRoom);
  return result;
};
'''


def move_war_room(template: str) -> str:
    """Relocate existing War Room markup, header nav and drawer entry exactly once."""
    section_pattern = (r'\s*<!-- =+\s*MANAGER WAR ROOM\s*=+ -->\s*'
                       r'<section class="page" id="page-war-room">.*?</section>')
    match = re.search(section_pattern, template, flags=re.S)
    if not match:
        raise RuntimeError('War Room standalone section insertion point changed')
    section = match.group(0)
    content = re.search(r'<section class="page" id="page-war-room">(.*?)</section>', section, flags=re.S).group(1)
    template = template[:match.start()] + template[match.end():]
    nav_pattern = (r'\s*<button\s+class="nav-button"\s+data-page="war-room"\s+'
                   r'onclick="showPage\(\'war-room\'\)"\s*>\s*War Room\s*</button>')
    template, n = re.subn(nav_pattern, '', template)
    if n != 1:
        raise RuntimeError(f'Expected one standalone War Room nav button, got {n}')
    tab_marker = '<button type="button" class="analytics-subtab myteam-tab" onclick="showMyTeamSubtab(\'planner\',this)">Five-GW Planner</button>'
    if template.count(tab_marker) != 1:
        raise RuntimeError('My Team subtab insertion point changed')
    tab = '<button type="button" class="analytics-subtab myteam-tab" data-myteam-section="war-room" onclick="showMyTeamSubtab(\'war-room\',this)">War Room</button>'
    template = template.replace(tab_marker, tab_marker+'\n                '+tab, 1)
    subpage_marker = '<div class="myteam-subpage" id="myteam-sub-medical">'
    if template.count(subpage_marker) != 1:
        raise RuntimeError('My Team War Room content insertion point changed')
    template = template.replace(subpage_marker, '<div class="myteam-subpage" id="myteam-sub-war-room">'+content+'</div>\n            '+subpage_marker, 1)
    # Remove from Home and add into My Team in the desktop/mobile unified menu.
    menu_home = "  ['Manager War Room','war-room'],"
    menu_team = "  ['Five-GW planner','myteam','myteam','planner'],"
    if template.count(menu_home) != 1 or template.count(menu_team) != 1:
        raise RuntimeError('McDraft drawer War Room menu anchor changed')
    template = template.replace(menu_home+'\n', '', 1)
    template = template.replace(menu_team, menu_team+"\n  ['Manager War Room','myteam','myteam','war-room'],", 1)
    return template
