import json
import os
import re

import requests
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

from listings.models import Lead, SupportEnquiry

# Base "as-new" reference price (INR) per brand/model, used only to derive a
# demo depreciation estimate. Not real market data.
BRAND_MODEL_BASE_PRICE = {
    'Maruti Suzuki': {'Swift': 650000, 'Baleno': 750000, 'Dzire': 700000, 'Ertiga': 950000, 'Brezza': 1050000},
    'Hyundai': {'i20': 800000, 'Creta': 1400000, 'Venue': 900000, 'Verna': 1200000, 'i10': 600000},
    'Honda': {'City': 1200000, 'Amaze': 800000, 'WR-V': 950000, 'Civic': 1800000},
    'Tata': {'Nexon': 900000, 'Punch': 700000, 'Harrier': 1600000, 'Altroz': 750000},
    'Mahindra': {'XUV700': 1600000, 'Scorpio': 1400000, 'Thar': 1500000, 'XUV300': 950000},
    'Toyota': {'Innova Crysta': 2000000, 'Fortuner': 3500000, 'Glanza': 800000},
}
DEFAULT_BASE_PRICE = 900000
CURRENT_YEAR = 2026

_BASE_PRICE_LOOKUP = {
    (brand.upper(), model.upper()): price
    for brand, models in BRAND_MODEL_BASE_PRICE.items()
    for model, price in models.items()
}


def _lookup_base_price(brand, model):
    """Case-insensitive BRAND_MODEL_BASE_PRICE lookup.

    Surepass returns manufacturer/model names in uppercase, which won't
    match the table's title-case keys otherwise.
    """
    return _BASE_PRICE_LOOKUP.get((brand.upper(), model.upper()), DEFAULT_BASE_PRICE)


class HomeView(View):
    def get(self, request):
        return render(request, 'website/home.html')


class AboutView(View):
    def get(self, request):
        return render(request, 'website/about.html')


class DealersView(View):
    def get(self, request):
        return render(request, 'website/dealers.html')


class SupportView(View):
    def get(self, request):
        return render(request, 'website/support.html')


class PrivacyView(View):
    def get(self, request):
        return render(request, 'website/privacy.html')


class TermsView(View):
    def get(self, request):
        return render(request, 'website/terms.html')


class VehicleEstimateView(View):
    """POST /api/vehicle-estimate/ — demo price-estimate calculator.

    Deterministic heuristic (base price -> depreciation -> mileage and
    condition adjustments), not a real valuation model. Surepass plate
    auto-fill is intentionally out of scope for this phase.
    """

    def post(self, request):
        try:
            data = json.loads(request.body or '{}')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON body.'}, status=400)

        brand = str(data.get('brand', '')).strip()
        model = str(data.get('model', '')).strip()
        try:
            year = int(data.get('year'))
            mileage = int(data.get('mileage'))
        except (TypeError, ValueError):
            return JsonResponse({'error': 'year and mileage must be numbers.'}, status=400)

        if not brand or not model:
            return JsonResponse({'error': 'brand and model are required.'}, status=400)
        if year < 2000 or year > CURRENT_YEAR:
            return JsonResponse({'error': 'year out of range.'}, status=400)
        if mileage < 0:
            return JsonResponse({'error': 'mileage cannot be negative.'}, status=400)

        accident = data.get('accident') == 'yes'
        service_records = data.get('service_records') == 'yes'
        ownership = data.get('ownership', '1st')
        insurance_valid = data.get('insurance') == 'valid'

        base_price = _lookup_base_price(brand, model)

        age_years = max(0, CURRENT_YEAR - year)
        depreciated_value = base_price * (0.88 ** age_years)
        depreciated_value = max(depreciated_value, base_price * 0.15)
        depreciation = base_price - depreciated_value

        expected_mileage = age_years * 12000
        mileage_delta = mileage - expected_mileage
        mileage_adjustment = -mileage_delta * 0.5
        mileage_adjustment = max(-depreciated_value * 0.25, min(depreciated_value * 0.1, mileage_adjustment))

        condition_pct = 0.0
        condition_pct += -0.08 if accident else 0.0
        condition_pct += 0.04 if service_records else 0.0
        condition_pct += {'1st': 0.05, '2nd': 0.0, '3rd+': -0.06}.get(ownership, 0.0)
        condition_pct += 0.02 if insurance_valid else -0.03
        condition_adjustment = depreciated_value * condition_pct

        final_estimate = depreciated_value + mileage_adjustment + condition_adjustment
        final_estimate = max(final_estimate, base_price * 0.1)

        low = round(final_estimate * 0.95, -3)
        high = round(final_estimate * 1.05, -3)

        return JsonResponse({
            'min': low,
            'max': high,
            'breakdown': {
                'base_price': round(base_price),
                'age_years': age_years,
                'depreciation': round(depreciation),
                'mileage_adjustment': round(mileage_adjustment),
                'condition_adjustment': round(condition_adjustment),
                'final_estimate': round(final_estimate),
            },
        })


def _call_surepass_rc_full(registration_number):
    """Look up a vehicle by registration number via Surepass RC Full.

    Returns (found: bool, data: dict). Any failure (missing credentials,
    network error, timeout, non-200, success=false, unexpected shape) is
    treated as "not found" so the caller can fall back to manual entry
    rather than surfacing a 500.
    """
    base_url = os.getenv('SUREPASS_BASE_URL')
    token = os.getenv('SUREPASS_TOKEN')
    if not base_url or not token:
        return False, {}

    try:
        response = requests.post(
            f'{base_url.rstrip("/")}/api/v1/rc/rc-full',
            json={'id_number': registration_number},
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json',
            },
            timeout=10,
        )
        if response.status_code != 200:
            return False, {}
        result = response.json()
        if not result.get('success'):
            return False, {}
        payload = result.get('data', {})
        if not payload:
            return False, {}
        return True, payload
    except (requests.RequestException, ValueError):
        return False, {}


class FetchVehicleDetailsView(View):
    """POST /api/fetch-vehicle/ — full vehicle + owner lookup via Surepass."""

    def post(self, request):
        try:
            data = json.loads(request.body or '{}')
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON body.'}, status=400)

        registration_number = str(data.get('registration_number', '')).upper().replace(' ', '')
        if not registration_number:
            return JsonResponse({'status': 'error', 'message': 'registration_number is required.'}, status=400)

        found, vehicle_data = _call_surepass_rc_full(registration_number)
        if not found:
            return JsonResponse({
                'status': 'success',
                'found': False,
                'message': 'Vehicle not found. Please enter manually.',
            })

        mfg_date = vehicle_data.get('manufacturing_date_formatted') or vehicle_data.get('registration_date') or ''
        year = ''
        if mfg_date:
            year_part = str(mfg_date).split('-')[0]
            year = year_part if year_part.isdigit() else ''

        return JsonResponse({
            'status': 'success',
            'found': True,
            'data': {
                'rc_number': vehicle_data.get('rc_number', ''),
                'owner_name': vehicle_data.get('owner_name', ''),
                'father_name': vehicle_data.get('father_name', ''),
                'present_address': vehicle_data.get('present_address', ''),
                'permanent_address': vehicle_data.get('permanent_address', ''),
                'maker_description': vehicle_data.get('maker_description', ''),
                'maker_model': vehicle_data.get('maker_model', ''),
                'year': year,
                'body_type': vehicle_data.get('body_type', ''),
                'fuel_type': vehicle_data.get('fuel_type', ''),
                'color': vehicle_data.get('color', ''),
                'vehicle_category_description': vehicle_data.get('vehicle_category_description', ''),
                'insurance_company': vehicle_data.get('insurance_company', ''),
                'insurance_upto': vehicle_data.get('insurance_upto', ''),
                'registration_date': vehicle_data.get('registration_date', ''),
                'registration_number': registration_number,
            },
        })


class CalculatePriceEstimateView(View):
    """POST /api/calculate-estimate/ — same pricing heuristic as
    VehicleEstimateView, kept as a separate endpoint for the new lead-capture
    flow but sharing BRAND_MODEL_BASE_PRICE/DEFAULT_BASE_PRICE/CURRENT_YEAR
    above so the two endpoints can't drift apart on pricing.
    """

    def post(self, request):
        try:
            data = json.loads(request.body or '{}')
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON body.'}, status=400)

        brand = str(data.get('brand', '')).strip()
        model = str(data.get('model', '')).strip()
        try:
            year = int(data.get('year'))
            mileage = int(data.get('mileage'))
        except (TypeError, ValueError):
            return JsonResponse({'status': 'error', 'message': 'year and mileage must be numbers.'}, status=400)

        if not brand or not model:
            return JsonResponse({'status': 'error', 'message': 'brand and model are required.'}, status=400)
        if year < 2000 or year > CURRENT_YEAR:
            return JsonResponse({'status': 'error', 'message': 'year out of range.'}, status=400)
        if mileage < 0:
            return JsonResponse({'status': 'error', 'message': 'mileage cannot be negative.'}, status=400)

        accident = data.get('accident') == 'yes'
        service_records = data.get('service_records') == 'yes'
        ownership = data.get('ownership', '1st')
        insurance_valid = data.get('insurance') == 'valid'

        base_price = _lookup_base_price(brand, model)

        age_years = max(0, CURRENT_YEAR - year)
        depreciated_value = base_price * (0.88 ** age_years)
        depreciated_value = max(depreciated_value, base_price * 0.15)
        depreciation = base_price - depreciated_value

        expected_mileage = age_years * 12000
        mileage_delta = mileage - expected_mileage
        mileage_adjustment = -mileage_delta * 0.5
        mileage_adjustment = max(-depreciated_value * 0.25, min(depreciated_value * 0.1, mileage_adjustment))

        condition_pct = 0.0
        condition_pct += -0.08 if accident else 0.0
        condition_pct += 0.04 if service_records else 0.0
        condition_pct += {'1st': 0.05, '2nd': 0.0, '3rd+': -0.06}.get(ownership, 0.0)
        condition_pct += 0.02 if insurance_valid else -0.03
        condition_adjustment = depreciated_value * condition_pct

        final_estimate = depreciated_value + mileage_adjustment + condition_adjustment
        final_estimate = max(final_estimate, base_price * 0.1)

        low = round(final_estimate * 0.95, -3)
        high = round(final_estimate * 1.05, -3)

        return JsonResponse({
            'min': low,
            'max': high,
            'breakdown': {
                'base_price': round(base_price),
                'age_years': age_years,
                'depreciation': round(depreciation),
                'mileage_adjustment': round(mileage_adjustment),
                'condition_adjustment': round(condition_adjustment),
                'final_estimate': round(final_estimate),
            },
        })


class CaptureLeadView(View):
    """POST /api/capture-lead/ — save a lead from the price estimator."""

    def post(self, request):
        try:
            data = json.loads(request.body or '{}')
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON body.'}, status=400)

        phone = str(data.get('phone', '')).strip()
        if not phone:
            return JsonResponse({'status': 'error', 'message': 'Phone number is required.'}, status=400)

        try:
            lead = Lead.objects.create(
                phone=phone,
                name=data.get('name') or None,
                registration_number=data.get('registration_number') or None,
                brand=data.get('brand'),
                model=data.get('model'),
                year=data.get('year'),
                mileage=data.get('mileage'),
                accident_history=data.get('accident_history'),
                service_records=data.get('service_records'),
                ownership=data.get('ownership'),
                insurance_status=data.get('insurance_status'),
                estimated_price_min=data.get('estimated_price_min'),
                estimated_price_max=data.get('estimated_price_max'),
                estimated_value=data.get('estimated_value'),
                base_price=data.get('base_price'),
                depreciation_adjustment=data.get('depreciation_adjustment'),
                mileage_adjustment=data.get('mileage_adjustment'),
                condition_adjustment=data.get('condition_adjustment'),
                status=Lead.Status.LEAD_CAPTURED,
            )
        except (TypeError, ValueError) as exc:
            return JsonResponse({'status': 'error', 'message': str(exc)}, status=400)

        return JsonResponse({
            'status': 'success',
            'message': 'Lead captured successfully',
            'lead_id': str(lead.id),
        })


class CaptureDealerLeadView(View):
    """POST /api/dealer-lead/ — save a lead from the /dealers/ signup form."""

    PHONE_RE = re.compile(r'^[6-9]\d{9}$')

    def post(self, request):
        try:
            data = json.loads(request.body or '{}')
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON body.'}, status=400)

        name = str(data.get('name', '')).strip()
        phone = str(data.get('phone', '')).strip()

        if len(name) < 2:
            return JsonResponse({'status': 'error', 'message': 'Enter your name.'}, status=400)
        if not self.PHONE_RE.match(phone):
            return JsonResponse({'status': 'error', 'message': 'Enter a valid 10-digit number.'}, status=400)

        lead = Lead.objects.create(
            phone=phone,
            name=name,
            source=Lead.Source.DEALER_SIGNUP,
            status=Lead.Status.LEAD_CAPTURED,
        )

        return JsonResponse({
            'status': 'success',
            'message': 'Lead captured successfully',
            'lead_id': str(lead.id),
        })


class SupportEnquiryView(View):
    """POST /api/support-enquiry/ — save an enquiry from the /support/ contact form."""

    NAME_MIN = 2
    SUBJECT_MIN = 3
    MESSAGE_MIN = 10
    PHONE_RE = re.compile(r'^[6-9]\d{9}$')
    EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')

    def post(self, request):
        import logging
        logger = logging.getLogger(__name__)
    
    try:
        try:
            data = json.loads(request.body or '{}')
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON body.'}, status=400)

        name = str(data.get('name', '')).strip()
        phone = str(data.get('phone', '')).strip()
        email = str(data.get('email', '')).strip()
        account_number = str(data.get('account_number', '')).strip()
        source = str(data.get('source', '')).strip() or SupportEnquiry.Source.WEBSITE
        subject = str(data.get('subject', '')).strip()
        message = str(data.get('message', '')).strip()

        errors = {}
        if len(name) < self.NAME_MIN:
            errors['name'] = 'Enter your name.'
        if not self.PHONE_RE.match(phone):
            errors['phone'] = 'Enter a valid 10-digit number.'
        if not self.EMAIL_RE.match(email):
            errors['email'] = 'Enter a valid email address.'
        if len(subject) < self.SUBJECT_MIN:
            errors['subject'] = 'Enter a subject.'
        if len(message) < self.MESSAGE_MIN:
            errors['message'] = 'Message must be at least 10 characters.'
        if source not in SupportEnquiry.Source.values:
            source = SupportEnquiry.Source.WEBSITE

        if errors:
            return JsonResponse({
                'status': 'error',
                'message': 'Please fix the errors below.',
                'errors': errors,
            }, status=400)

        enquiry = SupportEnquiry.objects.create(
            name=name,
            phone=phone,
            email=email,
            account_number=account_number or None,
            source=source,
            subject=subject,
            message=message,
        )

        return JsonResponse({
            'status': 'success',
            'message': f'Thank you, {name}! Our team is connecting with you under 12 hours.',
            'enquiry_id': str(enquiry.id),
            'enquiry': {
                'name': enquiry.name,
                'phone': enquiry.phone,
                'email': enquiry.email,
                'subject': enquiry.subject,
                'created_time': enquiry.created_time,
            },
        })
    
    except Exception as e:
        logger.error(f"SupportEnquiryView error: {str(e)}", exc_info=True)
        return JsonResponse({
            'status': 'error', 
            'message': f'Server error: {str(e)}'
        }, status=500)
