"""
Admin configuration for Core app
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Company, Contact, NewsletterSubscription


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    """Company Information Admin"""
    list_display = [
        'company_name',
        'registration_number',
        'license_number',
        'cbk_registration',
        'is_active',
        'created_at'
    ]
    
    list_filter = [
        'is_active',
        'created_at',
        'updated_at'
    ]
    
    search_fields = [
        'company_name',
        'registration_number',
        'license_number',
        'cbk_registration'
    ]
    
    readonly_fields = [
        'created_at',
        'updated_at'
    ]
    
    fieldsets = [
        ('Company Information', {
            'fields': [
                'company_name',
                'registration_number',
                'license_number',
                'cbk_registration'
            ]
        }),
        ('Banking Information', {
            'fields': [
                'bank_name',
                'bank_account_name',
                'bank_account_number'
            ]
        }),
        ('Contact Information', {
            'fields': [
                'physical_address',
                'postal_address',
                'city',
                'county',
                'country',
                'phone',
                'email',
                'website'
            ]
        }),
        ('Legal and Compliance', {
            'fields': [
                'terms_version',
                'privacy_policy_version',
                'loan_agreement_version'
            ]
        }),
        ('Default Loan Terms', {
            'fields': [
                'default_interest_rate',
                'late_fee_fixed',
                'late_fee_percentage',
                'disbursement_timeframe_days'
            ]
        }),
        ('Legal Information', {
            'fields': [
                'arbitration_rules',
                'governing_law',
                'jurisdiction'
            ]
        }),
        ('System Information', {
            'fields': [
                'is_active',
                'created_at',
                'updated_at'
            ]
        })
    ]
    
    def get_queryset(self, request):
        """Optimize queries"""
        return super().get_queryset(request).select_related()
    
    class Media:
        """Include admin media"""
        css = {
            'all': ('admin/css/admin.css',),
        }
        js = ('admin/js/admin.js',)


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    """Contact Form Submission Admin"""
    list_display = ['name', 'email', 'subject', 'source', 'is_processed', 'created_at']
    list_filter = ['is_processed', 'source', 'created_at', 'subject']
    search_fields = ['name', 'email', 'message', 'phone']
    readonly_fields = ['created_at', 'updated_at', 'ip_address', 'user_agent']
    
    actions = ['mark_as_processed']

    def mark_as_processed(self, request, queryset):
        """Mark selected contact messages as processed"""
        updated = queryset.update(is_processed=True)
        self.message_user(request, f'{updated} messages marked as processed.')
    mark_as_processed.short_description = "Mark selected messages as processed"


@admin.register(NewsletterSubscription)
class NewsletterSubscriptionAdmin(admin.ModelAdmin):
    """Newsletter Subscription Admin"""
    list_display = [
        'email', 
        'first_name', 
        'last_name', 
        'subscribed_at', 
        'is_verified',
        'source'
    ]
    
    list_filter = [
        'is_verified',
        'source', 
        'subscribed_at',
        'verified_at'
    ]
    
    search_fields = [
        'email', 
        'first_name', 
        'last_name'
    ]
    
    readonly_fields = [
        'subscribed_at',
        'verified_at',
        'verification_token',
        'ip_address',
        'user_agent'
    ]
    
    fieldsets = [
        ('Personal Information', {
            'fields': [
                'email',
                'first_name',
                'last_name'
            ]
        }),
        ('Subscription Details', {
            'fields': [
                'source',
                'interests',
                'is_verified',
                'subscribed_at',
                'verified_at'
            ]
        }),
        ('Verification', {
            'fields': [
                'verification_token'
            ]
        }),
        ('Technical Information', {
            'fields': [
                'ip_address',
                'user_agent'
            ],
            'classes': ('collapse',)
        })
    ]
    
    def get_queryset(self, request):
        """Optimize queries"""
        return super().get_queryset(request)
    
    actions = ['mark_as_verified', 'send_verification_email']

    def mark_as_verified(self, request, queryset):
        """Mark selected subscriptions as verified"""
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} subscriptions marked as verified.')
    mark_as_verified.short_description = "Mark selected subscriptions as verified"

    def send_verification_email(self, request, queryset):
        """Send verification email to selected subscriptions"""
        # Add your email sending logic here
        updated = queryset.count()
        self.message_user(request, f'Verification emails sent to {updated} subscribers.')
    send_verification_email.short_description = "Send verification email"

    class Media:
        """Include admin media"""
        css = {
            'all': ('admin/css/admin.css',),
        }
        js = ('admin/js/admin.js',)