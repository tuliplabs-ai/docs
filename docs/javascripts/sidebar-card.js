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

    // Create card element — the real tulip mark, same asset as the header
    // logo and the tuliplabs.ai brand (site-absolute path: the card mounts
    // on pages at any depth).
    const card = document.createElement('a');
    card.href = 'https://tuliplabs.ai/';
    card.target = '_blank';
    card.rel = 'noopener noreferrer';
    card.className = 'tulip-company-card';

    card.innerHTML =
      '<div class="tulip-company-card__mark">' +
        '<img src="/img/tulip-mark-pink.png" alt="tuliplabs" loading="lazy" />' +
      '</div>' +
      '<div class="tulip-company-card__body">' +
        '<span class="tulip-company-card__title">Built by <b>tuliplabs</b></span>' +
        '<span class="tulip-company-card__desc">An independent research lab training Clusiana models for governed agents.</span>' +
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