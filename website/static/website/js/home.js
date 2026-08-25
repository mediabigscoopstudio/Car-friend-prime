(function () {
  'use strict';

  var reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------------- Hero parallax ---------------- */
  (function heroParallax() {
    if (reducedMotion) return;
    var hero = document.getElementById('hero');
    var blobLg = document.getElementById('blobLg');
    var blobSm = document.getElementById('blobSm');
    if (!hero || !blobLg || !blobSm) return;

    hero.addEventListener('mousemove', function (e) {
      var rect = hero.getBoundingClientRect();
      var x = (e.clientX - rect.left) / rect.width - 0.5;
      var y = (e.clientY - rect.top) / rect.height - 0.5;
      blobLg.style.transform = 'translate(' + (x * 24) + 'px, ' + (y * 24) + 'px)';
      blobSm.style.transform = 'translate(' + (x * -14) + 'px, ' + (y * -14) + 'px)';
    });
  })();

  /* ---------------- Live bid ticker ---------------- */
  (function bidTicker() {
    if (reducedMotion) return;
    var el = document.getElementById('bidValue');
    if (!el) return;
    var value = 612000;
    var cap = 648000;
    setInterval(function () {
      if (value >= cap) return;
      value = Math.min(cap, value + 3500);
      el.textContent = '₹' + value.toLocaleString('en-IN');
    }, 2600);
  })();

  /* ---------------- App download modal ---------------- */
  (function appDownloadModal() {
    var overlay = document.getElementById('appDownloadOverlay');
    var closeBtn = document.getElementById('appModalClose');
    if (!overlay || !closeBtn) return;

    function openModal() {
      overlay.classList.add('is-open');
      overlay.setAttribute('aria-hidden', 'false');
      document.body.style.overflow = 'hidden';
    }
    function closeModal() {
      overlay.classList.remove('is-open');
      overlay.setAttribute('aria-hidden', 'true');
      document.body.style.overflow = '';
    }

    document.querySelectorAll('.buy-now-btn').forEach(function (btn) {
      btn.addEventListener('click', function (e) {
        e.preventDefault();
        openModal();
      });
    });
    closeBtn.addEventListener('click', closeModal);
    overlay.addEventListener('click', function (e) {
      if (e.target === overlay) closeModal();
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && overlay.classList.contains('is-open')) closeModal();
    });
  })();

  /* ---------------- How it works carousel ---------------- */
  (function howWorksCarousel() {
    var containerEl = document.getElementById('hwCarousel');
    var imgEl = document.getElementById('hwImg');
    var stepEls = document.querySelectorAll('.howworks-step');
    if (!containerEl || !imgEl || !stepEls.length) return;

    var IMAGES = [
      imgEl.getAttribute('data-exterior'),
      imgEl.getAttribute('data-interior'),
      imgEl.getAttribute('data-engine'),
      imgEl.getAttribute('data-docs')
    ];
    var ALT_TEXT = [
      'Exterior inspection step in the CarFriend app',
      'Interior inspection step in the CarFriend app',
      'Engine inspection step in the CarFriend app',
      'Documents upload step in the CarFriend app'
    ];

    var currentStep = 0;
    var intervalId = null;
    var resumeTimeoutId = null;
    var fadeTimeoutId = null;
    var AUTO_MS = 5000;
    var FADE_MS = 400;
    var RESUME_MS = 10000;

    function render() {
      imgEl.src = IMAGES[currentStep];
      imgEl.alt = ALT_TEXT[currentStep];
      stepEls.forEach(function (el, idx) {
        el.classList.toggle('is-active', idx === currentStep);
      });
    }

    function setStep(n) {
      var next = ((n % stepEls.length) + stepEls.length) % stepEls.length;
      if (next === currentStep) return;
      if (reducedMotion) {
        currentStep = next;
        render();
        return;
      }
      clearTimeout(fadeTimeoutId);
      imgEl.style.opacity = '0';
      fadeTimeoutId = setTimeout(function () {
        currentStep = next;
        render();
        imgEl.style.opacity = '1';
      }, FADE_MS);
    }

    function nextStep() { setStep(currentStep + 1); }

    function startAutoRotate() {
      if (reducedMotion || intervalId) return;
      intervalId = setInterval(nextStep, AUTO_MS);
    }
    function pauseAutoRotate() {
      if (intervalId) { clearInterval(intervalId); intervalId = null; }
    }
    function handleManualStep(n) {
      pauseAutoRotate();
      clearTimeout(resumeTimeoutId);
      setStep(n);
      resumeTimeoutId = setTimeout(startAutoRotate, RESUME_MS);
    }

    stepEls.forEach(function (el, idx) {
      el.addEventListener('click', function () { handleManualStep(idx); });
    });

    function onKeydown(e) {
      if (e.key !== 'ArrowLeft' && e.key !== 'ArrowRight') return;
      e.preventDefault();
      handleManualStep(currentStep + (e.key === 'ArrowRight' ? 1 : -1));
    }
    containerEl.addEventListener('keydown', onKeydown);

    var touchStartX = 0;
    var touchStartY = 0;
    var SWIPE_THRESHOLD = 40;
    var SWIPE_MAX_OFFAXIS = 60;
    function onTouchStart(e) {
      var t = e.changedTouches[0];
      touchStartX = t.clientX;
      touchStartY = t.clientY;
    }
    function onTouchEnd(e) {
      var t = e.changedTouches[0];
      var dx = t.clientX - touchStartX;
      var dy = t.clientY - touchStartY;
      if (Math.abs(dx) < SWIPE_THRESHOLD || Math.abs(dy) > SWIPE_MAX_OFFAXIS) return;
      handleManualStep(currentStep + (dx < 0 ? 1 : -1));
    }
    containerEl.addEventListener('touchstart', onTouchStart, { passive: true });
    containerEl.addEventListener('touchend', onTouchEnd, { passive: true });

    render();
    startAutoRotate();
  })();
})();
