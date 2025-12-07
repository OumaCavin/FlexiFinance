"""
Admin configuration for Core app
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Company


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