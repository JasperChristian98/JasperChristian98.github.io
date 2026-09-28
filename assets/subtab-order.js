(() => {
  'use strict';

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
  const label = button => button.textContent.replace(/\s+/g, ' ').trim();

  function sortBar(bar) {
    const buttons = [...bar.children].filter(child => child.matches('button'));
    const sorted = [...buttons].sort((a, b) => collator.compare(label(a), label(b)));
    sorted.forEach(button => bar.appendChild(button));
  }

  function sortMcDraftSubtabs() {
    selectors.forEach(selector => document.querySelectorAll(selector).forEach(sortBar));
  }

  window.sortMcDraftSubtabs = sortMcDraftSubtabs;
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', sortMcDraftSubtabs, {once: true});
  } else {
    sortMcDraftSubtabs();
  }
})();
