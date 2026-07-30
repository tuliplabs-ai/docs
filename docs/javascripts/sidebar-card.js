/**
 * Sidebar — "About tuliplabs" card.
 *
 * Injected at the bottom of the primary sidebar nav tree, after the content
 * section scrolls are exhausted.  The card carries the tulip mark, a short
 * description of the company, and an external link to tuliplabs.ai.
 */

(function () {
  'use strict';

  function install() {
    const nav = document.querySelector('.md-sidebar--primary .md-sidebar__scrollwrap');
    // Presence check against the DOM, not a flag — Material's instant nav
    // swaps the container, which would strand a stale "mounted" flag.
    if (!nav || nav.querySelector('.tulip-company-card')) return;

    // Create card element — inline SVG mark so it works without extra assets.
    const card = document.createElement('a');
    card.href = 'https://tuliplabs.ai/';
    card.target = '_blank';
    card.rel = 'noopener noreferrer';
    card.className = 'tulip-company-card';

    card.innerHTML =
      '<div class="tulip-company-card__mark">' +
        '<svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">' +
          '<path d="M32 8C28 8 24 14 22 22C20 30 22 38 24 44C26 50 29 56 32 56" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" fill="none"/>' +
          '<path d="M32 8C36 8 40 14 42 22C44 30 42 38 40 44C38 50 35 56 32 56" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" fill="none"/>' +
          '<path d="M32 8C28 18 20 24 20 32C20 40 26 44 32 44C38 44 44 40 44 32C44 24 36 18 32 8Z" fill="currentColor" opacity="0.15" stroke="currentColor" stroke-width="2"/>' +
          '<path d="M32 16C30 22 26 28 26 32C26 38 29 42 32 42" stroke="currentColor" stroke-width="2" stroke-linecap="round" fill="none"/>' +
          '<path d="M32 16C34 22 38 28 38 32C38 38 35 42 32 42" stroke="currentColor" stroke-width="2" stroke-linecap="round" fill="none"/>' +
        '</svg>' +
      '</div>' +
      '<div class="tulip-company-card__body">' +
        '<span class="tulip-company-card__title">Built by <b>tuliplabs</b></span>' +
        '<span class="tulip-company-card__desc">A research company training Clusiana models for governed agents.</span>' +
      '</div>' +
      '<svg class="tulip-company-card__arrow" viewBox="0 0 24 24" aria-hidden="true">' +
        '<path d="M7 17 17 7M8 7h9v9" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>' +
      '</svg>'

    nav.appendChild(card);
  }

  // document$ fires on initial load AND after every instant-nav swap.
  if (typeof document$ !== 'undefined') {
    document$.subscribe(install);
  } else if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', install);
  } else {
    install();
  }
})();