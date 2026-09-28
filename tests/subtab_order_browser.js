window.addEventListener('DOMContentLoaded', () => setTimeout(() => {
  const selectors = [
    '#page-overview > .overview-tabs',
    '#overview-sub-intelligence > .overview-insight-tabs',
    '#page-myteam > .myteam-tabs',
    '#page-players > .player-page-tabs',
    '#page-clubs > .club-explorer-tabs',
    '#page-transfers > .transfer-subtabs',
    '#page-season-summary > .season-summary-tabs',
    '#page-draft-centre > .draft-centre-tabs',
    '#page-analytics > .analytics-subtabs'
  ];
  const collator = new Intl.Collator('en-GB', {sensitivity: 'base', numeric: true});
  const checks = selectors.map(selector => {
    const bar = document.querySelector(selector);
    if (!bar) return 'FAILED: missing ' + selector;
    const labels = [...bar.children].filter(child => child.matches('button'))
      .map(button => button.textContent.replace(/\s+/g, ' ').trim());
    const sorted = [...labels].sort(collator.compare);
    return labels.every((label, index) => label === sorted[index])
      ? 'OK: ' + selector
      : 'FAILED: ' + selector + ' => ' + labels.join(' | ');
  });
  const report = document.createElement('pre');
  report.id = 'subtab-order-report';
  report.textContent = JSON.stringify(checks);
  document.body.append(report);
}, 100));
