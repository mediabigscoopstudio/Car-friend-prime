from django.contrib import admin
from .models import (
    Seller, Dealer, Admin, KYC, Vehicle, Listing,
    Auction, Bid, OCB, Deal, DealerListing, Subscription,
    Payment, Notification, Lead, SupportEnquiry
)

# ============================================
# 1. SELLER ADMIN
# ============================================
@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'city', 'is_verified', 'average_rating', 'total_listings', 'created_at')
    search_fields = ('name', 'email', 'phone', 'city')
    list_filter = ('is_verified', 'city', 'created_at')
    readonly_fields = ('id', 'created_at', 'updated_at', 'average_rating', 'total_listings', 'total_auctions_completed')
    fieldsets = (
        ('Personal Info', {
            'fields': ('name', 'email', 'phone')
        }),
        ('KYC', {
            'fields': ('is_verified', 'kyc_data')
        }),
        ('Details', {
            'fields': ('pan_number', 'city', 'state')
        }),
        ('Stats', {
            'fields': ('average_rating', 'total_listings', 'total_auctions_completed')
        }),
        ('System', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    ordering = ('-created_at',)


# ============================================
# 2. DEALER ADMIN
# ============================================
@admin.register(Dealer)
class DealerAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'email', 'phone', 'subscription_status', 'subscription_end_date', 'rating', 'total_bids_placed', 'auctions_won', 'created_at')
    search_fields = ('company_name', 'email', 'phone')
    list_filter = ('subscription_status', 'rating', 'created_at')
    readonly_fields = ('id', 'created_at', 'updated_at', 'total_bids_placed', 'auctions_won')
    fieldsets = (
        ('Personal Info', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Company', {
            'fields': ('company_name', 'dealership_license_number')
        }),
        ('Subscription', {
            'fields': ('subscription_status', 'subscription_end_date')
        }),
        ('Stats', {
            'fields': ('rating', 'total_bids_placed', 'auctions_won')
        }),
        ('System', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    ordering = ('-created_at',)


# ============================================
# 3. ADMIN USER ADMIN
# ============================================
@admin.register(Admin)
class AdminUserAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'role', 'approved_by', 'approval_date', 'created_at')
    search_fields = ('name', 'email')
    list_filter = ('role', 'approval_date', 'created_at')
    readonly_fields = ('id', 'created_at', 'updated_at', 'approval_date')
    fieldsets = (
        ('Personal Info', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Admin Details', {
            'fields': ('role', 'approved_by', 'approval_date')
        }),
        ('System', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    ordering = ('-created_at',)


# ============================================
# 4. KYC ADMIN
# ============================================
@admin.register(KYC)
class KYCAdmin(admin.ModelAdmin):
    list_display = ('id', 'provider', 'status', 'verified_at', 'created_at')
    search_fields = ('provider',)
    list_filter = ('status', 'provider', 'verified_at')
    readonly_fields = ('id', 'created_at', 'updated_at', 'verified_at')
    fieldsets = (
        ('Provider', {
            'fields': ('provider',)
        }),
        ('Verification Data', {
            'fields': ('aadhaar_token', 'pan_token', 'vehicle_verification_token')
        }),
        ('Status', {
            'fields': ('status', 'verified_at')
        }),
        ('System', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    ordering = ('-created_at',)


# ============================================
# 5. VEHICLE ADMIN
# ============================================
@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('registration_number', 'body_type', 'fuel_type', 'transmission', 'color', 'manufacture_year', 'mileage', 'surepass_verification_status', 'created_at')
    search_fields = ('registration_number', 'listing__title')
    list_filter = ('body_type', 'fuel_type', 'transmission', 'surepass_verification_status', 'manufacture_year')
    readonly_fields = ('id', 'created_at', 'updated_at', 'verified_at', 'surepass_verification_status')
    fieldsets = (
        ('Registration', {
            'fields': ('registration_number', 'registration_state', 'owner_type')
        }),
        ('Specs', {
            'fields': ('body_type', 'fuel_type', 'transmission', 'color', 'manufacture_year', 'mileage')
        }),
        ('Verification', {
            'fields': ('surepass_verification_status', 'ownership_transfer_status', 'verified_at')
        }),
        ('System', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    ordering = ('registration_number',)


# ============================================
# 6. LISTING ADMIN
# ============================================
@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'seller', 'status', 'auto_grade', 'asking_price', 'created_at')
    search_fields = ('title', 'seller__name', 'seller__email')
    list_filter = ('status', 'auto_grade', 'created_at')
    readonly_fields = ('id', 'created_at', 'updated_at', 'auto_grade', 'inspection_data', 'inspection_timestamp')
    fieldsets = (
        ('Listing Info', {
            'fields': ('seller', 'title', 'description')
        }),
        ('Pricing', {
            'fields': ('asking_price',)
        }),
        ('Auction Schedule', {
            'fields': ('auction_start_date', 'auction_end_date')
        }),
        ('Status & Grade', {
            'fields': ('status', 'auto_grade')
        }),
        ('Inspection', {
            'fields': ('inspection_data', 'inspection_timestamp')
        }),
        ('Photos', {
            'fields': ('photos',)
        }),
        ('System', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    ordering = ('-created_at',)


# ============================================
# 7. AUCTION ADMIN
# ============================================
@admin.register(Auction)
class AuctionAdmin(admin.ModelAdmin):
    list_display = ('id', 'listing', 'status', 'start_price', 'current_highest_bid', 'highest_bidder', 'bid_count', 'end_time')
    search_fields = ('listing__title', 'seller__name', 'highest_bidder__company_name')
    list_filter = ('status', 'created_at', 'end_time')
    readonly_fields = ('id', 'created_at', 'updated_at', 'bid_count')
    fieldsets = (
        ('Auction', {
            'fields': ('listing', 'seller', 'status')
        }),
        ('Pricing', {
            'fields': ('start_price', 'current_highest_bid', 'highest_bidder')
        }),
        ('Timing', {
            'fields': ('start_time', 'end_time', 'duration')
        }),
        ('Stats', {
            'fields': ('bid_count',)
        }),
        ('System', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    ordering = ('-end_time',)
    actions = ['cancel_auction_action']

    def cancel_auction_action(self, request, queryset):
        updated = queryset.filter(status='active').update(status='cancelled')
        self.message_user(request, f'{updated} auctions cancelled.')
    cancel_auction_action.short_description = 'Cancel selected auctions'


# ============================================
# 8. BID ADMIN
# ============================================
@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ('id', 'auction', 'dealer', 'amount', 'timestamp', 'is_current_highest')
    search_fields = ('auction__listing__title', 'dealer__company_name')
    list_filter = ('is_current_highest', 'timestamp')
    readonly_fields = ('id', 'timestamp')
    fieldsets = (
        ('Bid Info', {
            'fields': ('auction', 'dealer', 'amount')
        }),
        ('Status', {
            'fields': ('is_current_highest',)
        }),
        ('System', {
            'fields': ('id', 'timestamp'),
            'classes': ('collapse',)
        }),
    )
    ordering = ('-timestamp',)


# ============================================
# 9. OCB ADMIN
# ============================================
@admin.register(OCB)
class OCBAdmin(admin.ModelAdmin):
    list_display = ('id', 'listing', 'status', 'initial_offer_amount', 'counter_offer_amount', 'final_accepted_by', 'end_time')
    search_fields = ('listing__title', 'seller__name', 'initial_offer_by__company_name')
    list_filter = ('status', 'created_at', 'end_time')
    readonly_fields = ('id', 'created_at', 'updated_at', 'triggered_by_auction')
    fieldsets = (
        ('OCB', {
            'fields': ('listing', 'seller', 'status')
        }),
        ('Initial Offer', {
            'fields': ('triggered_by_auction', 'initial_offer_by', 'initial_offer_amount')
        }),
        ('Counter Offer', {
            'fields': ('counter_offer_from', 'counter_offer_amount', 'counter_offer_timestamp')
        }),
        ('Resolution', {
            'fields': ('seller_response', 'final_accepted_by', 'final_accepted_at')
        }),
        ('Timing', {
            'fields': ('start_time', 'end_time')
        }),
        ('System', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    ordering = ('-end_time',)


# ============================================
# 10. DEAL ADMIN
# ============================================
@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    list_display = ('id', 'listing', 'seller', 'buyer', 'sale_source', 'final_price', 'agreed_at')
    search_fields = ('listing__title', 'seller__name', 'buyer__company_name')
    list_filter = ('sale_source', 'agreed_at', 'created_at')
    readonly_fields = ('id', 'created_at', 'updated_at')
    fieldsets = (
        ('Deal', {
            'fields': ('listing', 'seller', 'buyer')
        }),
        ('Sale Info', {
            'fields': ('sale_source', 'final_price', 'agreed_at')
        }),
        ('Settlement Status', {
            'fields': ('payment_status', 'rc_transfer_status')
        }),
        ('System', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    ordering = ('-agreed_at',)


# ============================================
# 11. DEALER LISTING ADMIN
# ============================================
@admin.register(DealerListing)
class DealerListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'dealer', 'price', 'status', 'created_at')
    search_fields = ('title', 'dealer__company_name')
    list_filter = ('status', 'created_at')
    readonly_fields = ('id', 'created_at', 'updated_at')
    fieldsets = (
        ('Listing', {
            'fields': ('dealer', 'title', 'description')
        }),
        ('Pricing & Details', {
            'fields': ('price',)
        }),
        ('Contact', {
            'fields': ('contact_phone', 'contact_email')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Photos', {
            'fields': ('photos',)
        }),
        ('System', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    ordering = ('-created_at',)
    actions = ['flag_listing_action']

    def flag_listing_action(self, request, queryset):
        self.message_user(request, f'{queryset.count()} listings flagged for review.')
    flag_listing_action.short_description = 'Flag listings for admin review'


# ============================================
# 12. SUBSCRIPTION ADMIN
# ============================================
@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'dealer', 'plan_tier', 'status', 'start_date', 'end_date', 'auto_renew')
    search_fields = ('dealer__company_name', 'dealer__email')
    list_filter = ('plan_tier', 'status', 'auto_renew')
    readonly_fields = ('id', 'created_at', 'updated_at')
    fieldsets = (
        ('Subscription', {
            'fields': ('dealer', 'plan_tier', 'status')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date')
        }),
        ('Renewal', {
            'fields': ('auto_renew', 'razorpay_subscription_id')
        }),
        ('System', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    ordering = ('-end_date',)


# ============================================
# 13. PAYMENT ADMIN
# ============================================
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'seller', 'dealer', 'payment_type', 'amount', 'status', 'created_at')
    search_fields = ('seller__email', 'dealer__email', 'razorpay_payment_id')
    list_filter = ('payment_type', 'status', 'created_at')
    readonly_fields = ('id', 'created_at', 'updated_at')
    fieldsets = (
        ('Payment', {
            'fields': ('seller', 'dealer', 'payment_type', 'amount', 'status')
        }),
        ('Razorpay', {
            'fields': ('razorpay_payment_id', 'razorpay_order_id')
        }),
        ('Related', {
            'fields': ('related_listing', 'related_subscription')
        }),
        ('System', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    ordering = ('-created_at',)


# ============================================
# 14. NOTIFICATION ADMIN
# ============================================
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'seller', 'dealer', 'admin', 'notification_type', 'is_read', 'created_at')
    search_fields = ('seller__email', 'dealer__email', 'admin__email', 'title')
    list_filter = ('notification_type', 'is_read', 'created_at')
    readonly_fields = ('id', 'created_at')
    fieldsets = (
        ('Notification', {
            'fields': ('seller', 'dealer', 'admin', 'notification_type', 'title', 'message')
        }),
        ('Related', {
            'fields': ('related_auction', 'related_ocb', 'related_deal')
        }),
        ('Status', {
            'fields': ('is_read',)
        }),
        ('System', {
            'fields': ('id', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    ordering = ('-created_at',)


# ============================================
# 15. LEAD ADMIN
# ============================================
@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('phone', 'name', 'source', 'brand', 'model', 'year', 'estimated_value', 'status', 'created_at')
    search_fields = ('phone', 'name', 'brand', 'model', 'registration_number')
    list_filter = ('source', 'status', 'brand', 'created_at')
    readonly_fields = ('id', 'created_at', 'updated_at')
    fieldsets = (
        ('Contact', {
            'fields': ('phone', 'name', 'source')
        }),
        ('Vehicle', {
            'fields': ('registration_number', 'brand', 'model', 'year', 'mileage')
        }),
        ('Condition', {
            'fields': ('accident_history', 'service_records', 'ownership', 'insurance_status')
        }),
        ('Estimate', {
            'fields': (
                'estimated_value', 'estimated_price_min', 'estimated_price_max',
                'base_price', 'depreciation_adjustment', 'mileage_adjustment', 'condition_adjustment',
            )
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('System', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    ordering = ('-created_at',)

# ============================================
# 16. SUPPORT ENQUIRY ADMIN
# ============================================
@admin.register(SupportEnquiry)
class SupportEnquiryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'phone', 'source', 'subject', 'created_at']
    list_filter = ['source', 'created_at']
    search_fields = ['name', 'phone', 'email']
    readonly_fields = ('id', 'created_at')
    fieldsets = (
        ('Contact', {
            'fields': ('name', 'phone', 'email', 'account_number', 'source')
        }),
        ('Enquiry', {
            'fields': ('subject', 'message')
        }),
        ('System', {
            'fields': ('id', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    ordering = ('-created_at',)
