(function () {
  'use strict';

  /* ---------------- Nav toggle (mobile) ---------------- */
  var navToggle = document.getElementById('navToggle');
  if (navToggle) {
    navToggle.addEventListener('click', function () {
      var links = document.getElementById('navLinks');
      var open = links.classList.toggle('is-open');
      this.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  /* ---------------- FAQ accordion (shared: home + support) ---------------- */
  var items = document.querySelectorAll('.faq-item');
  items.forEach(function (item) {
    var trigger = item.querySelector('.faq-trigger');
    var marker = item.querySelector('.faq-marker');
    trigger.addEventListener('click', function () {
      var willOpen = !item.classList.contains('is-open');
      items.forEach(function (other) {
        other.classList.remove('is-open');
        other.querySelector('.faq-trigger').setAttribute('aria-expanded', 'false');
        other.querySelector('.faq-marker').textContent = '+';
      });
      if (willOpen) {
        item.classList.add('is-open');
        trigger.setAttribute('aria-expanded', 'true');
        marker.textContent = '−';
      }
    });
  });
})();
