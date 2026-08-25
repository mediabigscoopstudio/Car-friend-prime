(function () {
  'use strict';

  var reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  var track = document.getElementById('carouselTrack');
  var dotsWrap = document.getElementById('carouselDots');
  var prevBtn = document.getElementById('carouselPrev');
  var nextBtn = document.getElementById('carouselNext');
  var carouselEl = document.getElementById('featureCarousel');
  if (!track || !dotsWrap || !carouselEl) return;

  var slides = track.querySelectorAll('.carousel-slide');
  var totalSlides = slides.length;
  if (!totalSlides) return;

  var currentSlide = 0;
  var autoTimer = null;
  var AUTO_MS = 4500;

  slides.forEach(function (_, i) {
    var dot = document.createElement('button');
    dot.type = 'button';
    dot.className = 'carousel-dot' + (i === 0 ? ' is-active' : '');
    dot.setAttribute('aria-label', 'Go to slide ' + (i + 1));
    dot.addEventListener('click', function () { goToSlide(i); });
    dotsWrap.appendChild(dot);
  });
  var dots = dotsWrap.querySelectorAll('.carousel-dot');

  function updateCarousel() {
    track.style.transform = 'translateX(-' + (currentSlide * 100) + '%)';
    dots.forEach(function (d, i) { d.classList.toggle('is-active', i === currentSlide); });
  }

  function goToSlide(i) {
    currentSlide = i;
    updateCarousel();
    resetAutoTimer();
  }

  function moveSlide(dir) {
    currentSlide = (currentSlide + dir + totalSlides) % totalSlides;
    updateCarousel();
    resetAutoTimer();
  }

  function startAutoTimer() {
    if (reducedMotion) return;
    autoTimer = setInterval(function () { moveSlide(1); }, AUTO_MS);
  }

  function resetAutoTimer() {
    clearInterval(autoTimer);
    startAutoTimer();
  }

  if (prevBtn) prevBtn.addEventListener('click', function () { moveSlide(-1); });
  if (nextBtn) nextBtn.addEventListener('click', function () { moveSlide(1); });

  carouselEl.addEventListener('mouseenter', function () { clearInterval(autoTimer); });
  carouselEl.addEventListener('mouseleave', resetAutoTimer);

  updateCarousel();
  startAutoTimer();
})();
