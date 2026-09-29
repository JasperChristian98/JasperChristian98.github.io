"""Small header and typography improvements outside the preserved stages."""

SHORTCUT = '''<button id="header-calendar" class="header-calendar" type="button" onclick="showPage('calendar'); if(window.mcdNavSync) window.mcdNavSync();" title="Open fixture calendar" aria-label="Open fixture calendar">
<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M16 3v4M8 3v4M3 11h18M8 15h2M14 15h2"/></svg></button>
<button id="header-settings" class="header-calendar" type="button" onclick="showPage('settings'); if(window.mcdNavSync) window.mcdNavSync();" title="Open settings" aria-label="Open settings"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="7"/><circle cx="12" cy="12" r="2.5"/><path d="M12 2v3m0 14v3M2 12h3m14 0h3M5 5l2 2m10 10 2 2M5 19l2-2M17 7l2-2"/></svg></button>'''


def integrate_template(template):
    anchor = '<div class="theme-control" aria-label="Dashboard colour theme">'
    if 'id="header-calendar"' in template or template.count(anchor) != 1 or template.count('</body>') != 1:
        raise RuntimeError('Dashboard polish insertion point changed or already integrated')
    return template.replace(anchor, '<div class="theme-control" aria-label="Dashboard shortcuts">' + SHORTCUT, 1).replace('</body>', '<link rel="stylesheet" href="assets/dashboard-polish.css">\n</body>', 1)
