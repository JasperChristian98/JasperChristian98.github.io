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

  function sortButtons(container) {
    const buttons = [...container.children].filter(child => child.matches('button'));
    const sorted = [...buttons].sort((a, b) => collator.compare(label(a), label(b)));
    if (buttons.every((button, index) => button === sorted[index])) return;
    sorted.forEach(button => container.appendChild(button));
  }

  function sortMcDraftSubtabs() {
    selectors.forEach(selector => document.querySelectorAll(selector).forEach(sortButtons));
  }

  function sortMcDraftQuickLinks() {
    document.querySelectorAll('#mcd-sidebar-sections .mcd-nav-children').forEach(sortButtons);
  }

  function sortMcDraftNavigation() {
    sortMcDraftSubtabs();
    sortMcDraftQuickLinks();
  }

  window.sortMcDraftSubtabs = sortMcDraftSubtabs;
  window.sortMcDraftQuickLinks = sortMcDraftQuickLinks;
  const quickLinkRoot = document.getElementById('mcd-sidebar-sections');
  if (quickLinkRoot) {
    new MutationObserver(sortMcDraftQuickLinks).observe(quickLinkRoot, {childList: true, subtree: true});
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      sortMcDraftNavigation();
      // The sidebar is also assembled on DOMContentLoaded. Run once more after
      // every listener in that event has had a chance to build its links.
      setTimeout(sortMcDraftQuickLinks, 0);
    }, {once: true});
  } else {
    sortMcDraftNavigation();
  }
})();
