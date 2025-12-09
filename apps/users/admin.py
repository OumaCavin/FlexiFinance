"""
Admin configuration for User model
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils import timezone
from .models import User


# Removed UserProfileInline to avoid circular reference
# The User model contains all fields, so no separate profile inline is needed


class UserAdmin(BaseUserAdmin):
    # inlines removed to avoid circular reference
    list_display = (
        'username', 'email', 'first_name', 'last_name', 'phone_number',
        'is_verified', 'kyc_status', 'credit_score', 'is_staff', 'is_active', 'date_joined'
    )
    list_filter = (
        'is_staff', 'is_superuser', 'is_active', 'is_verified',
        'kyc_status', 'date_joined', 'last_login'
    )
    search_fields = ('username', 'first_name', 'last_name', 'email', 'phone_number', 'national_id')
    readonly_fields = (
        'date_joined', 'last_login', 'verification_date', 'email_verification_sent_at',
        'credit_score_updated', 'total_loans_taken', 'active_loans_count'
    )
    # Override add_fieldsets to include phone_number in user creation
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Information', {
            'classes': ('wide',),
            'fields': ('phone_number', 'email', 'first_name', 'last_name'),
        }),
    )
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Personal Information', {
            'classes': ('wide',),
            'fields': (
                'phone_number', 'middle_name', 'date_of_birth', 'national_id',
                'email_verification_token', 'email_verification_sent_at'
            )
        }),
        ('Contact Information', {
            'classes': ('wide',),
            'fields': (
                'address', 'city', 'county', 'country',
                'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship'
            )
        }),
        ('Employment Information', {
            'classes': ('wide',),
            'fields': (
                'occupation', 'employer_name', 'monthly_income', 'employment_duration'
            )
        }),
        ('FlexiFinance Verification', {
            'classes': ('wide',),
            'fields': (
                'is_verified', 'verification_date', 'kyc_status',
                'credit_score', 'credit_score_updated'
            )
        }),
        ('FlexiFinance System Information', {
            'classes': ('wide',),
            'fields': (
                'total_loans_taken', 'active_loans_count',
                'registration_ip', 'last_login_ip',
                'email_notifications', 'sms_notifications', 'marketing_emails',
                'two_factor_enabled', 'two_factor_secret'
            )
        }),
    )
    
    actions = ['verify_users', 'approve_kyc', 'reject_kyc']
    
    def verify_users(self, request, queryset):
        """Bulk verify users"""
        count = queryset.filter(is_verified=False).update(
            is_verified=True,
            verification_date=timezone.now()
        )
        self.message_user(request, f'{count} users verified successfully.')
    verify_users.short_description = "Verify selected users"
    
    def approve_kyc(self, request, queryset):
        """Bulk approve KYC"""
        count = queryset.filter(kyc_status__in=['PENDING', 'REJECTED']).update(
            kyc_status='APPROVED',
            is_verified=True,
            verification_date=timezone.now()
        )
        self.message_user(request, f'{count} KYC applications approved successfully.')
    approve_kyc.short_description = "Approve KYC for selected users"
    
    def reject_kyc(self, request, queryset):
        """Bulk reject KYC"""
        count = queryset.filter(kyc_status__in=['PENDING', 'APPROVED']).update(
            kyc_status='REJECTED'
        )
        self.message_user(request, f'{count} KYC applications rejected.')
    reject_kyc.short_description = "Reject KYC for selected users"


# Register the custom User model
admin.site.register(User, UserAdmin)