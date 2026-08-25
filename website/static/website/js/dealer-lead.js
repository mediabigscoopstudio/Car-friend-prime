(function () {
  'use strict';

  var overlay = document.getElementById('dealerModalOverlay');
  var openBtn = document.getElementById('openDealerModal');
  var closeBtn = document.getElementById('dealerModalClose');
  var form = document.getElementById('dealerLeadForm');
  var successState = document.getElementById('dealerModalSuccess');
  if (!overlay || !openBtn || !closeBtn || !form || !successState) return;

  var nameInput = document.getElementById('dealerLeadName');
  var phoneInput = document.getElementById('dealerLeadPhone');
  var nameError = document.getElementById('dealerNameError');
  var phoneError = document.getElementById('dealerPhoneError');
  var submitBtn = form.querySelector('button[type="submit"]');

  function getCsrfToken() {
    var input = form.querySelector('input[name=csrfmiddlewaretoken]');
    return input ? input.value : '';
  }

  function resetModal() {
    form.reset();
    form.classList.remove('is-hidden');
    successState.classList.remove('is-visible');
    nameError.classList.remove('is-visible');
    phoneError.classList.remove('is-visible');
  }

  function openModal() {
    resetModal();
    overlay.classList.add('is-open');
    overlay.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
  }

  function closeModal() {
    overlay.classList.remove('is-open');
    overlay.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
  }

  openBtn.addEventListener('click', openModal);
  closeBtn.addEventListener('click', closeModal);
  overlay.addEventListener('click', function (e) {
    if (e.target === overlay) closeModal();
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && overlay.classList.contains('is-open')) closeModal();
  });

  form.addEventListener('submit', function (e) {
    e.preventDefault();

    var name = nameInput.value.trim();
    var phone = phoneInput.value.trim().replace(/\s+/g, '');
    var valid = true;

    if (name.length < 2) {
      nameError.classList.add('is-visible');
      valid = false;
    } else {
      nameError.classList.remove('is-visible');
    }

    if (!/^[6-9]\d{9}$/.test(phone)) {
      phoneError.classList.add('is-visible');
      valid = false;
    } else {
      phoneError.classList.remove('is-visible');
    }

    if (!valid) return;

    submitBtn.disabled = true;
    submitBtn.textContent = 'Locking price…';

    fetch('/api/dealer-lead/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken()
      },
      body: JSON.stringify({ name: name, phone: phone })
    })
      .then(function (res) { return res.json(); })
      .then(function (data) {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Aa price pakki kari do';
        if (data.status !== 'success') {
          phoneError.textContent = data.message || 'Something went wrong — please try again.';
          phoneError.classList.add('is-visible');
          return;
        }
        form.classList.add('is-hidden');
        successState.classList.add('is-visible');
      })
      .catch(function () {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Aa price pakki kari do';
        phoneError.textContent = 'Something went wrong — please try again.';
        phoneError.classList.add('is-visible');
      });
  });
})();
