(function () {
  'use strict';

  var overlay = document.getElementById('estimatorOverlay');
  var openBtn = document.getElementById('openEstimator');
  var closeBtn = document.getElementById('estimatorClose');
  var form = document.getElementById('estimatorForm');
  if (!overlay || !openBtn || !form) return;

  var BRAND_MODELS = {
    'Maruti Suzuki': ['Swift', 'Baleno', 'Dzire', 'Ertiga', 'Brezza'],
    'Hyundai': ['i20', 'Creta', 'Venue', 'Verna', 'i10'],
    'Honda': ['City', 'Amaze', 'WR-V', 'Civic'],
    'Tata': ['Nexon', 'Punch', 'Harrier', 'Altroz'],
    'Mahindra': ['XUV700', 'Scorpio', 'Thar', 'XUV300'],
    'Toyota': ['Innova Crysta', 'Fortuner', 'Glanza']
  };

  var steps = form.querySelectorAll('.modal-step');
  var dots = overlay.querySelectorAll('.modal-steps .dot');
  var brandSelect = document.getElementById('est-brand');
  var modelSelect = document.getElementById('est-model');
  var yearSelect = document.getElementById('est-year');
  var mileageInput = document.getElementById('est-mileage');
  var step2Error = document.getElementById('step2Error');
  var step3Error = document.getElementById('step3Error');
  var loadingEl = document.getElementById('estimatorLoading');
  var resultEl = document.getElementById('estimatorResult');
  var rangeEl = document.getElementById('estimateRange');
  var breakdownEl = document.getElementById('estimateBreakdown');

  var regnoInput = document.getElementById('est-regno');
  var fetchVehicleBtn = document.getElementById('fetchVehicleBtn');
  var regnoError = document.getElementById('regnoError');

  var slide2Subtitle = document.getElementById('slide2Subtitle');
  var vehicleSummaryCard = document.getElementById('vehicleSummaryCard');
  var editFieldsWrap = document.getElementById('editFieldsWrap');
  var editDetailsBtn = document.getElementById('editDetailsBtn');
  var slide2NextBtn = document.getElementById('slide2NextBtn');

  var contactCapture = document.getElementById('contactCapture');
  var contactSuccess = document.getElementById('contactSuccess');
  var contactSuccessMessage = document.getElementById('contactSuccessMessage');
  var leadNameInput = document.getElementById('lead-name');
  var leadPhoneInput = document.getElementById('lead-phone');
  var leadError = document.getElementById('leadError');
  var connectTeamBtn = document.getElementById('connectTeamBtn');

  var currentStep = 0;
  var lastEstimate = null;
  var vehicleVerified = false;

  function populateStaticOptions() {
    Object.keys(BRAND_MODELS).forEach(function (brand) {
      var opt = document.createElement('option');
      opt.value = brand;
      opt.textContent = brand;
      brandSelect.appendChild(opt);
    });

    var currentYear = 2026;
    for (var y = currentYear; y >= 2015; y--) {
      var opt = document.createElement('option');
      opt.value = y;
      opt.textContent = y;
      yearSelect.appendChild(opt);
    }
  }
  populateStaticOptions();

  brandSelect.addEventListener('change', function () {
    var models = BRAND_MODELS[brandSelect.value] || [];
    modelSelect.innerHTML = '';
    if (!models.length) {
      modelSelect.disabled = true;
      var opt = document.createElement('option');
      opt.value = '';
      opt.textContent = 'Select a brand first';
      modelSelect.appendChild(opt);
      return;
    }
    modelSelect.disabled = false;
    var placeholder = document.createElement('option');
    placeholder.value = '';
    placeholder.textContent = 'Select model';
    modelSelect.appendChild(placeholder);
    models.forEach(function (model) {
      var opt = document.createElement('option');
      opt.value = model;
      opt.textContent = model;
      modelSelect.appendChild(opt);
    });
  });

  function ensureOption(select, value, label) {
    var exists = Array.prototype.some.call(select.options, function (o) { return o.value === String(value); });
    if (!exists) {
      var opt = document.createElement('option');
      opt.value = value;
      opt.textContent = label || value;
      select.appendChild(opt);
    }
    select.value = value;
  }

  function showStep(idx) {
    currentStep = idx;
    steps.forEach(function (step) {
      var isActive = Number(step.dataset.step) === idx;
      step.classList.toggle('is-active', isActive);
      step.style.display = isActive ? 'block' : 'none';
    });
    dots.forEach(function (dot) {
      var n = Number(dot.dataset.dot);
      dot.classList.toggle('is-active', n === idx);
      dot.classList.toggle('is-done', n < idx);
    });
  }

  function resetVehicleLookup() {
    regnoInput.value = '';
    regnoError.classList.remove('is-visible');
    fetchVehicleBtn.disabled = false;
    fetchVehicleBtn.textContent = 'Verify & Get Price';

    vehicleVerified = false;
    vehicleSummaryCard.style.display = 'none';
    vehicleSummaryCard.innerHTML = '';
    editDetailsBtn.style.display = 'none';
    editFieldsWrap.style.display = '';
    slide2Subtitle.textContent = '✓ Vehicle verified';
    brandSelect.value = '';
    modelSelect.innerHTML = '<option value="">Select a brand first</option>';
    modelSelect.disabled = true;
    yearSelect.value = '';
    mileageInput.value = '';
    step2Error.classList.remove('is-visible');
  }

  function resetContactCapture() {
    leadNameInput.value = '';
    leadPhoneInput.value = '';
    leadError.classList.remove('is-visible');
    contactCapture.style.display = '';
    contactCapture.classList.remove('is-leaving');
    contactSuccess.style.display = 'none';
    contactSuccess.classList.remove('is-entering');
    connectTeamBtn.disabled = false;
    connectTeamBtn.textContent = 'Connect our team';
  }

  function openModal() {
    overlay.classList.add('is-open');
    overlay.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
    showStep(0);
    step3Error.classList.remove('is-visible');
    resultEl.style.display = 'none';
    loadingEl.style.display = 'none';
    resetVehicleLookup();
    resetContactCapture();
    lastEstimate = null;

    var heroPlateInput = document.getElementById('plate');
    if (heroPlateInput && heroPlateInput.value.trim()) {
      regnoInput.value = heroPlateInput.value.trim();
      fetchVehicle();
    }
  }

  function closeModal() {
    overlay.classList.remove('is-open');
    overlay.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
  }

  openBtn.addEventListener('click', function (e) {
    e.preventDefault();
    openModal();
  });
  closeBtn.addEventListener('click', closeModal);
  overlay.addEventListener('click', function (e) {
    if (e.target === overlay) closeModal();
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && overlay.classList.contains('is-open')) closeModal();
  });
  overlay.querySelectorAll('[data-close]').forEach(function (btn) {
    btn.addEventListener('click', closeModal);
  });

  function getCsrfToken() {
    var input = form.querySelector('input[name=csrfmiddlewaretoken]');
    return input ? input.value : '';
  }

  function matchBrand(raw) {
    if (!raw) return null;
    var rawLower = String(raw).toLowerCase();
    var keys = Object.keys(BRAND_MODELS);
    for (var i = 0; i < keys.length; i++) {
      if (rawLower.indexOf(keys[i].toLowerCase().split(' ')[0]) !== -1) return keys[i];
    }
    return null;
  }

  function matchModel(brandKey, raw) {
    if (!brandKey || !raw) return null;
    var rawLower = String(raw).toLowerCase();
    var models = BRAND_MODELS[brandKey] || [];
    for (var i = 0; i < models.length; i++) {
      if (rawLower.indexOf(models[i].toLowerCase()) !== -1) return models[i];
    }
    return null;
  }

  function summaryRow(label, value) {
    if (!value) return '';
    return '<div class="row"><span>' + label + '</span><span>' + value + '</span></div>';
  }

  function renderVehicleSummary(data) {
    var insuranceText = data.insurance_company
      ? data.insurance_company + (data.insurance_upto ? ' valid until ' + data.insurance_upto : '')
      : '';
    vehicleSummaryCard.innerHTML =
      summaryRow('Owner name', data.owner_name) +
      summaryRow('Father name', data.father_name) +
      summaryRow('Address', data.present_address) +
      summaryRow('Brand', data.maker_description) +
      summaryRow('Model', data.maker_model) +
      summaryRow('Year', data.year) +
      summaryRow('Body type', data.body_type) +
      summaryRow('Fuel type', data.fuel_type) +
      summaryRow('Color', data.color) +
      summaryRow('Insurance', insuranceText) +
      summaryRow('Registration date', data.registration_date);
    vehicleSummaryCard.style.display = '';
  }

  function applyVehicleFields(data) {
    var brandKey = matchBrand(data.maker_description);
    if (brandKey) {
      ensureOption(brandSelect, brandKey, brandKey);
      brandSelect.dispatchEvent(new Event('change'));
      var modelKey = matchModel(brandKey, data.maker_model);
      if (modelKey) ensureOption(modelSelect, modelKey, modelKey);
      else if (data.maker_model) ensureOption(modelSelect, data.maker_model, data.maker_model);
    } else if (data.maker_description) {
      ensureOption(brandSelect, data.maker_description, data.maker_description);
      brandSelect.dispatchEvent(new Event('change'));
      if (data.maker_model) ensureOption(modelSelect, data.maker_model, data.maker_model);
    }
    if (data.year) ensureOption(yearSelect, data.year, data.year);
  }

  function fetchVehicle() {
    var registrationNumber = regnoInput.value.trim();
    if (!registrationNumber) {
      regnoError.textContent = 'Please enter a registration number.';
      regnoError.classList.add('is-visible');
      return;
    }
    regnoError.classList.remove('is-visible');
    fetchVehicleBtn.disabled = true;
    fetchVehicleBtn.textContent = 'Verifying…';

    fetch('/api/fetch-vehicle/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken()
      },
      body: JSON.stringify({ registration_number: registrationNumber })
    })
      .then(function (res) { return res.json(); })
      .then(function (data) {
        fetchVehicleBtn.disabled = false;
        fetchVehicleBtn.textContent = 'Verify & Get Price';

        if (!data.found) {
          vehicleVerified = false;
          slide2Subtitle.textContent = 'Vehicle not found — please enter details manually.';
          vehicleSummaryCard.style.display = 'none';
          editDetailsBtn.style.display = 'none';
          editFieldsWrap.style.display = '';
          showStep(1);
          return;
        }

        vehicleVerified = true;
        applyVehicleFields(data.data);
        renderVehicleSummary(data.data);
        editFieldsWrap.style.display = 'none';
        editDetailsBtn.style.display = 'inline-block';
        editDetailsBtn.textContent = 'Edit details';
        showStep(1);
      })
      .catch(function () {
        fetchVehicleBtn.disabled = false;
        fetchVehicleBtn.textContent = 'Verify & Get Price';
        vehicleVerified = false;
        slide2Subtitle.textContent = 'Vehicle not found — please enter details manually.';
        vehicleSummaryCard.style.display = 'none';
        editDetailsBtn.style.display = 'none';
        editFieldsWrap.style.display = '';
        showStep(1);
      });
  }

  fetchVehicleBtn.addEventListener('click', fetchVehicle);

  editDetailsBtn.addEventListener('click', function () {
    var editing = editFieldsWrap.style.display !== 'none';
    if (editing) {
      editFieldsWrap.style.display = 'none';
      vehicleSummaryCard.style.display = '';
      editDetailsBtn.textContent = 'Edit details';
    } else {
      editFieldsWrap.style.display = '';
      vehicleSummaryCard.style.display = 'none';
      editDetailsBtn.textContent = 'Cancel';
    }
  });

  slide2NextBtn.addEventListener('click', function () {
    if (!brandSelect.value || !modelSelect.value || !yearSelect.value || !mileageInput.value) {
      step2Error.classList.add('is-visible');
      return;
    }
    step2Error.classList.remove('is-visible');
    showStep(2);
  });

  overlay.querySelector('[data-back]').addEventListener('click', function () {
    showStep(0);
  });

  function getFormData() {
    var fd = new FormData(form);
    return {
      brand: fd.get('brand'),
      model: fd.get('model'),
      year: Number(fd.get('year')),
      mileage: Number(fd.get('mileage')),
      accident: fd.get('accident'),
      service_records: fd.get('service_records'),
      ownership: fd.get('ownership'),
      insurance: fd.get('insurance'),
      registration_number: regnoInput.value.trim()
    };
  }

  function formatInr(n) {
    return '₹' + Math.round(n).toLocaleString('en-IN');
  }

  function renderResult(data) {
    rangeEl.textContent = formatInr(data.min) + ' – ' + formatInr(data.max);
    breakdownEl.innerHTML =
      '<div class="row"><span>Base price</span><span>' + formatInr(data.breakdown.base_price) + '</span></div>' +
      '<div class="row"><span>Depreciation (' + data.breakdown.age_years + ' yrs)</span><span>-' + formatInr(data.breakdown.depreciation) + '</span></div>' +
      '<div class="row"><span>Mileage adjustment</span><span>' + (data.breakdown.mileage_adjustment >= 0 ? '+' : '') + formatInr(data.breakdown.mileage_adjustment) + '</span></div>' +
      '<div class="row"><span>Condition adjustment</span><span>' + (data.breakdown.condition_adjustment >= 0 ? '+' : '') + formatInr(data.breakdown.condition_adjustment) + '</span></div>' +
      '<div class="row total"><span>Estimated value</span><span>' + formatInr(data.breakdown.final_estimate) + '</span></div>';
  }

  function calculate() {
    showStep(3);
    step3Error.classList.remove('is-visible');
    resultEl.style.display = 'none';
    loadingEl.style.display = 'block';
    resetContactCapture();

    var formData = getFormData();

    fetch('/api/calculate-estimate/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken()
      },
      body: JSON.stringify(formData)
    })
      .then(function (res) {
        if (!res.ok) throw new Error('Request failed');
        return res.json();
      })
      .then(function (data) {
        loadingEl.style.display = 'none';
        resultEl.style.display = 'block';
        renderResult(data);
        lastEstimate = {
          registration_number: formData.registration_number,
          brand: formData.brand,
          model: formData.model,
          year: formData.year,
          mileage: formData.mileage,
          accident_history: formData.accident,
          service_records: formData.service_records,
          ownership: formData.ownership,
          insurance_status: formData.insurance,
          estimated_price_min: data.min,
          estimated_price_max: data.max,
          estimated_value: data.breakdown.final_estimate,
          base_price: data.breakdown.base_price,
          depreciation_adjustment: -data.breakdown.depreciation,
          mileage_adjustment: data.breakdown.mileage_adjustment,
          condition_adjustment: data.breakdown.condition_adjustment
        };
      })
      .catch(function () {
        loadingEl.style.display = 'none';
        step3Error.classList.add('is-visible');
      });
  }

  overlay.querySelector('[data-calculate]').addEventListener('click', calculate);
  var retryBtn = overlay.querySelector('[data-retry]');
  if (retryBtn) {
    retryBtn.addEventListener('click', function () {
      step3Error.classList.remove('is-visible');
      calculate();
    });
  }

  connectTeamBtn.addEventListener('click', function () {
    var phone = leadPhoneInput.value.trim();
    if (!/^\d{7,15}$/.test(phone.replace(/[\s+-]/g, ''))) {
      leadError.classList.add('is-visible');
      return;
    }
    leadError.classList.remove('is-visible');
    connectTeamBtn.disabled = true;
    connectTeamBtn.textContent = 'Connecting…';

    var payload = Object.assign({}, lastEstimate, {
      phone: phone,
      name: leadNameInput.value.trim()
    });

    fetch('/api/capture-lead/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken()
      },
      body: JSON.stringify(payload)
    })
      .then(function (res) { return res.json(); })
      .then(function (data) {
        connectTeamBtn.disabled = false;
        connectTeamBtn.textContent = 'Connect our team';
        if (data.status !== 'success') {
          leadError.textContent = data.message || 'Something went wrong — please try again.';
          leadError.classList.add('is-visible');
          return;
        }
        contactSuccessMessage.textContent = data.message || 'Thanks! Our team will reach out in 12 hours.';
        contactCapture.classList.add('is-leaving');
        setTimeout(function () {
          contactCapture.style.display = 'none';
          contactSuccess.style.display = 'block';
          contactSuccess.classList.add('is-entering');
        }, 300);
      })
      .catch(function () {
        connectTeamBtn.disabled = false;
        connectTeamBtn.textContent = 'Connect our team';
        leadError.textContent = 'Something went wrong — please try again.';
        leadError.classList.add('is-visible');
      });
  });
})();
