/* app.js — the small amount of behaviour a per-app page needs.

   The home page runs its own richer script (parallax, counters, act tracking).
   These pages only need three things, so they share this instead. Everything
   here is defensive: if an element is missing the page still works. */
(function () {
  'use strict';

  var y = document.getElementById('y');
  if (y) { y.textContent = new Date().getFullYear(); }

  /* the mobile menu */
  var burger = document.getElementById('burger');
  var sheet = document.getElementById('sheet');
  if (burger && sheet) {
    burger.addEventListener('click', function () {
      var open = sheet.classList.toggle('open');
      burger.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    sheet.addEventListener('click', function (e) {
      if (e.target.tagName === 'A') {
        sheet.classList.remove('open');
        burger.setAttribute('aria-expanded', 'false');
      }
    });
  }

  /* the nav grows a shadow once it is actually sitting over content */
  var nav = document.getElementById('nav');
  if (nav) {
    var onScroll = function () {
      nav.classList.toggle('stuck', window.scrollY > 8);
    };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }
})();
