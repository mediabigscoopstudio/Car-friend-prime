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

  /* ---------------- How-it-works autoplay ---------------- */
  (function howItWorks() {
    var frame = document.getElementById('hiwFrame');
    var stepsWrap = document.getElementById('hiwSteps');
    if (!frame || !stepsWrap) return;

    var IMG_MS = 2000;
    var STEPS = [
      { pill: 'Exterior', title: 'Exterior scan', note: 'Walk around your car — our guide tells you exactly where to stand and shoot.' },
      { pill: 'Interior', title: 'Interior check', note: 'A quick pass through the cabin — odometer reading included automatically.' },
      { pill: 'Engine', title: 'Engine check', note: 'Pop the hood — a clear engine bay shot is what builds dealer trust.' },
      { pill: 'Documents', title: 'Documents', note: 'Snap your RC and insurance — verification happens instantly in the background.' }
    ];

    var tagEl = document.getElementById('hiwTag');
    var captionTitle = document.getElementById('hiwCaptionTitle');
    var captionNote = document.getElementById('hiwCaptionNote');
    var referenceImg = document.getElementById('hiwReference');
    var photoCount = document.getElementById('hiwPhotoCount');
    var shotWrap = document.querySelector('.hiw-shot');
    var shotImg = document.getElementById('hiwShot');
    var shotCount = document.getElementById('hiwShotCount');
    var galleryThumb = document.getElementById('hiwGalleryThumb');
    var thumbsWrap = document.getElementById('hiwThumbs');
    var groups = thumbsWrap.querySelectorAll('.hiw-thumbgroup');
    var stepButtons = document.querySelectorAll('.hiw-step');

    function pad(n) { return (n < 10 ? '0' : '') + n; }
    function realThumbs(stepIdx) { return groups[stepIdx].querySelectorAll('.hiw-thumb'); }
    function count(stepIdx) { return realThumbs(stepIdx).length; }

    var activeStep = 0;
    var activeImg = 0;
    var elapsed = 0;
    var lastTs = null;
    var running = false;
    var rafId = null;
    var visible = true;
    var lastKey = null;
    var lastStep = -1;

    function prefetchNext() {
      var nextGroup = groups[(activeStep + 1) % STEPS.length];
      Array.prototype.forEach.call(nextGroup.querySelectorAll('img'), function (img) {
        img.loading = 'eager';
      });
    }

    function render() {
      var n = count(activeStep);
      var stepFrac = (activeImg + elapsed / IMG_MS) / n;
      var key = activeStep + ':' + activeImg;

      if (key !== lastKey) {
        var s = STEPS[activeStep];
        var stepChanged = activeStep !== lastStep;
        tagEl.textContent = s.pill;
        captionTitle.textContent = s.title;
        captionNote.textContent = s.note;

        groups.forEach(function (g, i) {
          g.classList.toggle('is-active', i === activeStep);
        });

        var thumbs = realThumbs(activeStep);
        for (var i = 0; i < thumbs.length; i++) {
          thumbs[i].classList.toggle('is-focus', i === activeImg);
          thumbs[i].classList.toggle('is-shot', i < activeImg);
        }

        var thumbImg = thumbs[activeImg].querySelector('img');
        var nextSrc = thumbImg.currentSrc || thumbImg.src;
        shotWrap.classList.add('is-swapping');
        shotImg.src = nextSrc;
        galleryThumb.src = nextSrc;
        requestAnimationFrame(function () {
          shotWrap.classList.remove('is-swapping');
        });
        var countText = pad(activeImg + 1) + ' / ' + pad(n);
        shotCount.textContent = countText;
        photoCount.textContent = countText;
        if (stepChanged) {
          var firstThumbImg = thumbs[0].querySelector('img');
          referenceImg.src = firstThumbImg.currentSrc || firstThumbImg.src;
          lastStep = activeStep;
        }
        prefetchNext();
        lastKey = key;
      }

      stepButtons.forEach(function (btn, idx) {
        var ring = btn.querySelector('circle.progress');
        btn.classList.remove('is-active', 'is-done');
        if (idx === activeStep) {
          btn.classList.add('is-active');
          ring.style.strokeDashoffset = 88 * (1 - stepFrac);
        } else if (idx < activeStep) {
          btn.classList.add('is-done');
        } else {
          ring.style.strokeDashoffset = 88;
        }
      });
    }

    function tick(ts) {
      if (!running) return;
      if (lastTs === null) lastTs = ts;
      var dt = ts - lastTs;
      lastTs = ts;
      elapsed += dt;
      while (elapsed >= IMG_MS) {
        elapsed -= IMG_MS;
        activeImg += 1;
        if (activeImg >= count(activeStep)) {
          activeImg = 0;
          activeStep = (activeStep + 1) % STEPS.length;
        }
      }
      render();
      rafId = requestAnimationFrame(tick);
    }

    function start() {
      if (running || reducedMotion || !visible) return;
      running = true;
      lastTs = null;
      rafId = requestAnimationFrame(tick);
    }

    function stop() {
      running = false;
      if (rafId) cancelAnimationFrame(rafId);
    }

    stepButtons.forEach(function (btn, idx) {
      btn.addEventListener('click', function () {
        activeStep = idx;
        activeImg = 0;
        elapsed = 0;
        render();
      });
    });

    thumbsWrap.addEventListener('click', function (e) {
      var thumb = e.target.closest('.hiw-thumb');
      if (!thumb) return;
      activeStep = Number(thumb.parentNode.dataset.step);
      activeImg = Number(thumb.dataset.img);
      elapsed = 0;
      render();
    });

    render();

    if (!reducedMotion) {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          visible = entry.isIntersecting;
          if (visible) start(); else stop();
        });
      }, { threshold: 0.2 });
      io.observe(frame);
    }
  })();
})();
