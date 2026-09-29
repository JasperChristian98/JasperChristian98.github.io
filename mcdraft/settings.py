"""Browser-local dashboard preferences and navigation."""

PAGE = '''<section class="page" id="page-settings" aria-labelledby="settings-heading">
  <div class="card mcd-settings">
    <h1 id="settings-heading">Settings</h1>
    <p class="card-description">Make this dashboard feel right for you. Changes save automatically in this browser; they do not sync between devices.</p>
    <div class="mcd-setting-row">
      <div><label for="settings-theme">Appearance</label><p id="settings-theme-help">Choose a theme or follow your device's colour scheme.</p></div>
      <select id="settings-theme" aria-describedby="settings-theme-help"><option value="system">Use device setting</option><option value="dark">Dark</option><option value="light">Light</option></select>
    </div>
    <div class="mcd-setting-row">
      <div><label for="settings-motion">Animations</label><p id="settings-motion-help">Reduce motion to disable dashboard animations and smooth scrolling. Your device's reduced-motion preference is always respected.</p></div>
      <select id="settings-motion" aria-describedby="settings-motion-help"><option value="system">Use device setting</option><option value="reduced">Reduce motion</option></select>
    </div>
    <div class="mcd-setting-row">
      <div><label for="settings-font">Dashboard font</label><p id="settings-font-help">Try a different style. Changes appear across the dashboard immediately; the exact font depends on your device.</p></div>
      <select id="settings-font" aria-describedby="settings-font-help"><option value="rounded">Rounded — default</option><option value="system">System — modern</option><option value="classic">Classic — clean</option><option value="editorial">Editorial — serif</option><option value="mono">Monospace — technical</option></select>
    </div>
    <p>Your team selection, watchlist and other saved items are kept separately.</p>
    <button type="button" class="results-button" id="settings-reset">Reset appearance, font and animations</button>
    <p id="settings-status" role="status" aria-live="polite"></p>
  </div>
</section>
'''
ASSETS = '''<link rel="stylesheet" href="assets/settings.css">
<script defer src="assets/settings.js"></script>
'''
NAV = "['League overview','overview','overview','standings'],"


def integrate_template(template):
    anchor = '<section class="page" id="page-analytics">'
    if 'id="page-settings"' in template or any(template.count(x) != 1 for x in (anchor, NAV, '</body>')):
        raise RuntimeError('Settings insertion point changed or already integrated')
    return (template.replace(anchor, PAGE + anchor, 1)
            .replace(NAV, NAV + "\n  ['Settings','settings'],", 1)
            .replace('</body>', ASSETS + '</body>', 1))
