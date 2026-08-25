(function () {
  'use strict';

  var form = document.getElementById('supportForm');
  var overlay = document.getElementById('supportModalOverlay');
  var closeBtn = document.getElementById('supportModalClose');
  var submitBtn = document.getElementById('supportSubmitBtn');
  if (!form || !overlay || !closeBtn || !submitBtn) return;

  var nameInput = document.getElementById('se-name');
  var phoneInput = document.getElementById('se-phone');
  var emailInput = document.getElementById('se-email');
  var accountNumberInput = document.getElementById('se-account-number');
  var sourceSelect = document.getElementById('se-source');
  var subjectInput = document.getElementById('se-subject');
  var messageInput = document.getElementById('se-message');

  var errors = {
    name: document.getElementById('se-name-error'),
    phone: document.getElementById('se-phone-error'),
    email: document.getElementById('se-email-error'),
    subject: document.getElementById('se-subject-error'),
    message: document.getElementById('se-message-error')
  };
  var formError = document.getElementById('se-form-error');

  var PHONE_RE = /^[6-9]\d{9}$/;
  var EMAIL_RE = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;

  function clearErrors() {
    Object.keys(errors).forEach(function (key) {
      errors[key].classList.remove('is-visible');
    });
    formError.classList.remove('is-visible');
  }

  function getCsrfToken() {
    var input = form.querySelector('input[name=csrfmiddlewaretoken]');
    return input ? input.value : '';
  }

  // Pre-fill source from ?source=seller / ?source=dealer (default: website).
  (function prefillSource() {
    var params = new URLSearchParams(window.location.search);
    var source = (params.get('source') || '').toLowerCase();
    if (source === 'seller' || source === 'dealer') {
      sourceSelect.value = source;
    }
  })();

  function openModal(enquiry) {
    document.getElementById('supportModalThanks').textContent = 'Thank you, ' + enquiry.name + '!';
    document.getElementById('supportModalName').textContent = enquiry.name;
    document.getElementById('supportModalPhone').textContent = enquiry.phone;
    document.getElementById('supportModalEmail').textContent = enquiry.email;
    document.getElementById('supportModalSubject').textContent = enquiry.subject;
    document.getElementById('supportModalTime').textContent = enquiry.created_time;

    overlay.classList.add('is-open');
    overlay.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
  }

  function closeModal() {
    overlay.classList.remove('is-open');
    overlay.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
  }

  closeBtn.addEventListener('click', closeModal);
  overlay.addEventListener('click', function (e) {
    if (e.target === overlay) closeModal();
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && overlay.classList.contains('is-open')) closeModal();
  });

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    clearErrors();

    var name = nameInput.value.trim();
    var phone = phoneInput.value.trim().replace(/\s+/g, '');
    var email = emailInput.value.trim();
    var subject = subjectInput.value.trim();
    var message = messageInput.value.trim();
    var valid = true;

    if (name.length < 2) { errors.name.classList.add('is-visible'); valid = false; }
    if (!PHONE_RE.test(phone)) { errors.phone.classList.add('is-visible'); valid = false; }
    if (!EMAIL_RE.test(email)) { errors.email.classList.add('is-visible'); valid = false; }
    if (subject.length < 3) { errors.subject.classList.add('is-visible'); valid = false; }
    if (message.length < 10) { errors.message.classList.add('is-visible'); valid = false; }

    if (!valid) return;

    submitBtn.disabled = true;
    submitBtn.textContent = 'Sending…';

    fetch('/api/support-enquiry/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken()
      },
      body: JSON.stringify({
        name: name,
        phone: phone,
        email: email,
        account_number: accountNumberInput.value.trim(),
        source: sourceSelect.value,
        subject: subject,
        message: message
      })
    })
      .then(function (res) { return res.json(); })
      .then(function (data) {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Send message';

        if (data.status !== 'success') {
          if (data.errors) {
            Object.keys(data.errors).forEach(function (field) {
              if (errors[field]) {
                errors[field].textContent = data.errors[field];
                errors[field].classList.add('is-visible');
              }
            });
          } else {
            formError.textContent = data.message || 'Something went wrong — please try again.';
            formError.classList.add('is-visible');
          }
          return;
        }

        openModal(data.enquiry);
        form.reset();
      })
      .catch(function () {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Send message';
        formError.classList.add('is-visible');
      });
  });
})();
