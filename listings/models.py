import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


# ---------------------------------------------------------------------------
# User hierarchy
# ---------------------------------------------------------------------------

class User(models.Model):
    """Shared abstract base for Seller, Dealer, and Admin.

    Abstract (not multi-table) inheritance: each concrete subclass gets its
    own table with these fields copied in, so there is no shared `User`
    table or FK to a base row.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=13, unique=True)  # e.g. +91XXXXXXXXXX
    name = models.CharField(max_length=255)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Seller(User):
    pan_number = models.CharField(max_length=10, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    # `kyc_data` points to the KYC record verifying this seller; nullable
    # until KYC is initiated/completed.
    kyc_data = models.ForeignKey(
        'KYC', on_delete=models.SET_NULL, null=True, blank=True, related_name='sellers'
    )
    average_rating = models.DecimalField(
        max_digits=3, decimal_places=2, default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
    )
    total_listings = models.IntegerField(default=0)
    total_auctions_completed = models.IntegerField(default=0)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Sellers'

    def __str__(self):
        return f'{self.name} ({self.city})'


class Dealer(User):
    class SubscriptionStatus(models.TextChoices):
        ACTIVE = 'active', 'Active'
        INACTIVE = 'inactive', 'Inactive'
        EXPIRED = 'expired', 'Expired'

    company_name = models.CharField(max_length=255)
    dealership_license_number = models.CharField(max_length=100, blank=True, null=True)
    kyc_data = models.ForeignKey(
        'KYC', on_delete=models.SET_NULL, null=True, blank=True, related_name='dealers'
    )
    subscription_status = models.CharField(
        max_length=20, choices=SubscriptionStatus.choices, default=SubscriptionStatus.INACTIVE
    )
    subscription_end_date = models.DateTimeField(null=True, blank=True)
    total_bids_placed = models.IntegerField(default=0)
    auctions_won = models.IntegerField(default=0)
    rating = models.DecimalField(
        max_digits=3, decimal_places=2, default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Dealers'

    def __str__(self):
        return f'{self.company_name} ({self.name})'


class Admin(User):
    class Role(models.TextChoices):
        SUPER = 'super', 'Super Admin'
        STANDARD = 'standard', 'Standard Admin'

    kyc_data = models.ForeignKey(
        'KYC', on_delete=models.SET_NULL, null=True, blank=True, related_name='admins'
    )
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STANDARD)
    approved_by = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_admins'
    )
    approval_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Admins'

    def __str__(self):
        return f'{self.name} ({self.role})'


# ---------------------------------------------------------------------------
# KYC
# ---------------------------------------------------------------------------

class KYC(models.Model):
    """KYC verification record. Each Seller/Dealer/Admin links to at most
    one KYC row via their `kyc_data` FK (User is abstract, so this side
    can't hold a single generic FK back to "User")."""

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        VERIFIED = 'verified', 'Verified'
        REJECTED = 'rejected', 'Rejected'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider = models.CharField(max_length=50, default='surepass')
    aadhaar_token = models.CharField(max_length=255, blank=True, null=True)
    pan_token = models.CharField(max_length=255, blank=True, null=True)
    vehicle_verification_token = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'KYC Records'

    def __str__(self):
        return f'KYC {self.id} ({self.status})'


# ---------------------------------------------------------------------------
# Vehicle -> Listing
# ---------------------------------------------------------------------------

class Vehicle(models.Model):
    """One vehicle per listing. NOTE: the prompt specifies a OneToOneField
    in both directions (Vehicle.listing and Listing.vehicle), which is a
    circular dependency Django can't express as two required OneToOne FKs
    pointing at each other. Resolved here by keeping a single FK:
    `Listing.vehicle -> Vehicle`. Use `vehicle.listing` (the reverse
    accessor) instead of a `Vehicle.listing` field."""

    class FuelType(models.TextChoices):
        PETROL = 'petrol', 'Petrol'
        DIESEL = 'diesel', 'Diesel'
        CNG = 'cng', 'CNG'
        ELECTRIC = 'electric', 'Electric'

    class Transmission(models.TextChoices):
        MANUAL = 'manual', 'Manual'
        AUTOMATIC = 'automatic', 'Automatic'

    class BodyType(models.TextChoices):
        SEDAN = 'sedan', 'Sedan'
        SUV = 'suv', 'SUV'
        HATCHBACK = 'hatchback', 'Hatchback'
        MPV = 'mpv', 'MPV'
        COUPE = 'coupe', 'Coupe'
        CONVERTIBLE = 'convertible', 'Convertible'

    class OwnerType(models.TextChoices):
        INDIVIDUAL = 'individual', 'Individual'
        COMPANY = 'company', 'Company'

    class VerificationStatus(models.TextChoices):
        VERIFIED = 'verified', 'Verified'
        PENDING = 'pending', 'Pending'
        FAILED = 'failed', 'Failed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    registration_number = models.CharField(max_length=20, unique=True)
    registration_state = models.CharField(max_length=100)
    fuel_type = models.CharField(max_length=20, choices=FuelType.choices)
    transmission = models.CharField(max_length=20, choices=Transmission.choices)
    body_type = models.CharField(max_length=20, choices=BodyType.choices)
    color = models.CharField(max_length=50)
    manufacture_year = models.IntegerField()
    mileage = models.IntegerField(help_text='Odometer reading in km')
    owner_type = models.CharField(max_length=20, choices=OwnerType.choices)
    ownership_transfer_status = models.CharField(
        max_length=20, choices=VerificationStatus.choices, default=VerificationStatus.PENDING
    )
    surepass_verification_status = models.CharField(
        max_length=20, choices=VerificationStatus.choices, default=VerificationStatus.PENDING
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Vehicles'

    def __str__(self):
        return f'{self.registration_number} ({self.manufacture_year})'


class Listing(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        ACTIVE = 'active', 'Active'
        AUCTION_IN_PROGRESS = 'auction_in_progress', 'Auction In Progress'
        AUCTION_ENDED = 'auction_ended', 'Auction Ended'
        OCB_IN_PROGRESS = 'ocb_in_progress', 'OCB In Progress'
        SOLD = 'sold', 'Sold'
        WITHDRAWN = 'withdrawn', 'Withdrawn'

    class AutoGrade(models.TextChoices):
        A = 'A', 'A'
        B = 'B', 'B'
        C = 'C', 'C'
        D = 'D', 'D'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='listings')
    vehicle = models.OneToOneField(Vehicle, on_delete=models.CASCADE, related_name='listing')
    title = models.CharField(max_length=255)
    description = models.TextField()
    asking_price = models.DecimalField(max_digits=10, decimal_places=2)
    # Array of S3 URLs, max 10 photos; length enforced at the serializer/view layer.
    photos = models.JSONField(default=list)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.DRAFT)
    # System-computed grade from inspection data; not editable by the seller.
    auto_grade = models.CharField(max_length=1, choices=AutoGrade.choices, blank=True, null=True)
    # Structured inspection results: damage_score, mileage_check, title_check, etc.
    inspection_data = models.JSONField(default=dict, blank=True)
    inspection_timestamp = models.DateTimeField(null=True, blank=True)
    auction_start_date = models.DateTimeField(null=True, blank=True)
    auction_end_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Listings'
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['seller', 'status']),
        ]

    def __str__(self):
        return f'{self.title} ({self.status})'


# ---------------------------------------------------------------------------
# Auction, Bid
# ---------------------------------------------------------------------------

class Auction(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        ENDED = 'ended', 'Ended'
        PASSED_TO_OCB = 'passed_to_ocb', 'Passed to OCB'
        CANCELLED = 'cancelled', 'Cancelled'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='auctions')
    # Denormalized from listing.seller for quick queries without a join.
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='auctions')
    start_price = models.DecimalField(max_digits=10, decimal_places=2, help_text='Reserve price')
    current_highest_bid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    highest_bidder = models.ForeignKey(
        Dealer, on_delete=models.SET_NULL, null=True, blank=True, related_name='auctions_leading'
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    start_time = models.DateTimeField()
    # Auto-calculated as start_time + duration; computed by application logic
    # in a later phase (models carry no business logic yet).
    end_time = models.DateTimeField()
    duration = models.IntegerField(default=24, help_text='Auction duration in hours')
    bid_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_time']
        verbose_name_plural = 'Auctions'
        indexes = [
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f'Auction for {self.listing.title} ({self.status})'


class Bid(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='bids')
    dealer = models.ForeignKey(Dealer, on_delete=models.CASCADE, related_name='bids')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_current_highest = models.BooleanField(default=False)

    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = 'Bids'
        indexes = [
            models.Index(fields=['auction', '-amount']),
        ]

    def __str__(self):
        return f'{self.dealer.company_name} bid {self.amount} on {self.auction_id}'


# ---------------------------------------------------------------------------
# OCB (One Click Buy)
# ---------------------------------------------------------------------------

class OCB(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        ACCEPTED = 'accepted', 'Accepted'
        REJECTED = 'rejected', 'Rejected'
        EXPIRED = 'expired', 'Expired'

    class SellerResponse(models.TextChoices):
        ACCEPT = 'accept', 'Accept'
        REJECT = 'reject', 'Reject'
        COUNTERED = 'countered', 'Countered'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='ocbs')
    # Denormalized from listing.seller for quick queries without a join.
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='ocbs')
    triggered_by_auction = models.ForeignKey(
        Auction, on_delete=models.SET_NULL, null=True, blank=True, related_name='ocbs'
    )
    auction_winning_bid = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    # The auction-winning dealer who made the initial OCB offer.
    initial_offer_by = models.ForeignKey(
        Dealer, on_delete=models.SET_NULL, null=True, blank=True, related_name='ocb_initial_offers'
    )
    initial_offer_amount = models.DecimalField(max_digits=10, decimal_places=2)
    counter_offer_from = models.ForeignKey(
        Dealer, on_delete=models.SET_NULL, null=True, blank=True, related_name='ocb_counter_offers'
    )
    counter_offer_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    counter_offer_timestamp = models.DateTimeField(null=True, blank=True)
    seller_response = models.CharField(
        max_length=20, choices=SellerResponse.choices, null=True, blank=True
    )
    final_accepted_by = models.ForeignKey(
        Dealer, on_delete=models.SET_NULL, null=True, blank=True, related_name='ocb_final_acceptances'
    )
    final_accepted_at = models.DateTimeField(null=True, blank=True)
    start_time = models.DateTimeField()
    # Auto-calculated as start_time + 4 hours; computed by application logic
    # in a later phase.
    end_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_time']
        verbose_name_plural = 'OCBs'
        indexes = [
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f'OCB for {self.listing.title} ({self.status})'


# ---------------------------------------------------------------------------
# Deal
# ---------------------------------------------------------------------------

class Deal(models.Model):
    class SaleSource(models.TextChoices):
        AUCTION = 'auction', 'Auction'
        OCB = 'ocb', 'OCB'
        DEALER_LISTING = 'dealer_listing', 'Dealer Listing'

    class PaymentStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PAID = 'paid', 'Paid'
        FAILED = 'failed', 'Failed'

    class RCTransferStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        INITIATED = 'initiated', 'Initiated'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='deals')
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='deals')
    buyer = models.ForeignKey(Dealer, on_delete=models.CASCADE, related_name='deals')
    sale_source = models.CharField(max_length=20, choices=SaleSource.choices)
    final_price = models.DecimalField(max_digits=10, decimal_places=2)
    agreed_at = models.DateTimeField()
    # Platform doesn't process payment, just tracks status for visibility.
    payment_status = models.CharField(
        max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING
    )
    # Platform doesn't process RC transfer, just tracks status for visibility.
    rc_transfer_status = models.CharField(
        max_length=20, choices=RCTransferStatus.choices, default=RCTransferStatus.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-agreed_at']
        verbose_name_plural = 'Deals'

    def __str__(self):
        return f'Deal for {self.listing.title} @ {self.final_price}'


# ---------------------------------------------------------------------------
# DealerListing (OLX-style dealer car sales)
# ---------------------------------------------------------------------------

class DealerListing(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        SOLD = 'sold', 'Sold'
        WITHDRAWN = 'withdrawn', 'Withdrawn'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dealer = models.ForeignKey(Dealer, on_delete=models.CASCADE, related_name='dealer_listings')
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    # Array of S3 URLs, max 2 photos; length enforced at the serializer/view layer.
    photos = models.JSONField(default=list)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    # Contact details shown directly to interested sellers/buyers.
    contact_phone = models.CharField(max_length=13)
    contact_email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Dealer Listings'

    def __str__(self):
        return f'{self.title} ({self.status})'


# ---------------------------------------------------------------------------
# Subscription (Dealer monthly billing)
# ---------------------------------------------------------------------------

class Subscription(models.Model):
    class PlanTier(models.TextChoices):
        BASIC = 'basic', 'Basic (₹5000)'
        PRO = 'pro', 'Pro (₹10000)'

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        EXPIRED = 'expired', 'Expired'
        CANCELLED = 'cancelled', 'Cancelled'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dealer = models.ForeignKey(Dealer, on_delete=models.CASCADE, related_name='subscriptions')
    plan_tier = models.CharField(max_length=10, choices=PlanTier.choices)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    razorpay_subscription_id = models.CharField(max_length=255, blank=True, null=True)
    auto_renew = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']
        verbose_name_plural = 'Subscriptions'

    def __str__(self):
        return f'{self.dealer.company_name} - {self.plan_tier} ({self.status})'


# ---------------------------------------------------------------------------
# Payment (Track all transactions)
# ---------------------------------------------------------------------------

class Payment(models.Model):
    class PaymentType(models.TextChoices):
        LISTING_FEE = 'listing_fee', 'Listing Fee'
        SUBSCRIPTION = 'subscription', 'Subscription'
        OCB_FEE = 'ocb_fee', 'OCB Fee'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Payments can originate from any user type, but User is abstract, so we
    # can't FK to it directly. Track the concrete payer via three nullable
    # FKs (exactly one populated), analogous to the KYC linkage on User.
    seller = models.ForeignKey(
        Seller, on_delete=models.CASCADE, null=True, blank=True, related_name='payments'
    )
    dealer = models.ForeignKey(
        Dealer, on_delete=models.CASCADE, null=True, blank=True, related_name='payments'
    )
    payment_type = models.CharField(max_length=20, choices=PaymentType.choices)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    razorpay_payment_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_order_id = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    related_listing = models.ForeignKey(
        Listing, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments'
    )
    related_subscription = models.ForeignKey(
        Subscription, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Payments'

    def __str__(self):
        return f'{self.payment_type} - {self.amount} ({self.status})'


# ---------------------------------------------------------------------------
# Notification
# ---------------------------------------------------------------------------

class Notification(models.Model):
    class NotificationType(models.TextChoices):
        AUCTION_BID = 'auction_bid', 'Auction Bid'
        AUCTION_ENDED = 'auction_ended', 'Auction Ended'
        OCB_TRIGGERED = 'ocb_triggered', 'OCB Triggered'
        OCB_COUNTERED = 'ocb_countered', 'OCB Countered'
        DEAL_CLOSED = 'deal_closed', 'Deal Closed'
        SUBSCRIPTION_RENEWAL = 'subscription_renewal', 'Subscription Renewal'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Same reasoning as Payment: User is abstract, so track the concrete
    # recipient via nullable per-role FKs (exactly one populated).
    seller = models.ForeignKey(
        Seller, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications'
    )
    dealer = models.ForeignKey(
        Dealer, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications'
    )
    admin = models.ForeignKey(
        Admin, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications'
    )
    notification_type = models.CharField(max_length=30, choices=NotificationType.choices)
    title = models.CharField(max_length=255)
    message = models.TextField()
    related_auction = models.ForeignKey(
        Auction, on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications'
    )
    related_ocb = models.ForeignKey(
        OCB, on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications'
    )
    related_deal = models.ForeignKey(
        Deal, on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications'
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Notifications'
        indexes = [
            models.Index(fields=['is_read']),
        ]

    def __str__(self):
        return f'{self.notification_type}: {self.title}'


# ---------------------------------------------------------------------------
# Lead (price estimator)
# ---------------------------------------------------------------------------

class Lead(models.Model):
    """Organic leads captured from the home page price estimator."""

    class ConditionChoice(models.TextChoices):
        YES = 'yes', 'Yes'
        NO = 'no', 'No'

    class Ownership(models.TextChoices):
        FIRST = '1st', '1st'
        SECOND = '2nd', '2nd'
        THIRD_PLUS = '3rd+', '3rd owner or more'

    class InsuranceStatus(models.TextChoices):
        VALID = 'valid', 'Valid'
        EXPIRED = 'expired', 'Expired'

    class Status(models.TextChoices):
        LEAD_CAPTURED = 'lead_captured', 'Lead Captured'
        CONTACTED = 'contacted', 'Contacted'
        INTERESTED = 'interested', 'Interested'
        CONVERTED = 'converted', 'Converted'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Contact info
    phone = models.CharField(max_length=15)
    name = models.CharField(max_length=100, blank=True, null=True)

    # Vehicle info
    registration_number = models.CharField(max_length=20, blank=True, null=True)
    brand = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.IntegerField()
    mileage = models.IntegerField(help_text='Odometer reading in km')

    # Condition
    accident_history = models.CharField(max_length=3, choices=ConditionChoice.choices)
    service_records = models.CharField(max_length=3, choices=ConditionChoice.choices)
    ownership = models.CharField(max_length=10, choices=Ownership.choices)
    insurance_status = models.CharField(max_length=10, choices=InsuranceStatus.choices)

    # Estimated price
    estimated_price_min = models.DecimalField(max_digits=12, decimal_places=2)
    estimated_price_max = models.DecimalField(max_digits=12, decimal_places=2)
    estimated_value = models.DecimalField(max_digits=12, decimal_places=2)

    # Pricing breakdown
    base_price = models.DecimalField(max_digits=12, decimal_places=2)
    depreciation_adjustment = models.DecimalField(max_digits=12, decimal_places=2)
    mileage_adjustment = models.DecimalField(max_digits=12, decimal_places=2)
    condition_adjustment = models.DecimalField(max_digits=12, decimal_places=2)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.LEAD_CAPTURED)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Lead'
        verbose_name_plural = 'Leads'

    def __str__(self):
        return f'{self.brand} {self.model} ({self.year}) - {self.phone}'
