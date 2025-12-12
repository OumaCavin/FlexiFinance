"""
Django admin configuration for Loans app
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Loan, LoanProduct, RepaymentSchedule

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    """
    Admin interface for Loan model
    """
    list_display = [
        'loan_reference', 
        'user_name', 
        'loan_type', 
        'principal_amount', 
        'status', 
        'application_date',
        'remaining_balance_display'
    ]
    
    list_filter = [
        'status', 
        'loan_type', 
        'risk_category', 
        'application_date',
        'approval_date'
    ]
    
    search_fields = [
        'loan_reference', 
        'user__first_name', 
        'user__last_name', 
        'user__email',
        'user__phone_number'
    ]
    
    readonly_fields = [
        'loan_reference', 
        'created_at', 
        'updated_at',
        'application_date',
        'remaining_balance'
    ]
    
    fieldsets = (
        ('Loan Information', {
            'fields': (
                'loan_reference',
                'user',
                'loan_type',
                'principal_amount',
                'interest_rate',
                'loan_tenure',
                'total_amount',
                'monthly_payment',
                'remaining_balance'
            )
        }),
        ('Status & Risk', {
            'fields': (
                'status',
                'risk_category',
                'credit_score_assigned'
            )
        }),
        ('Purpose & Description', {
            'fields': (
                'purpose',
                'description'
            )
        }),
        ('Dates', {
            'fields': (
                'application_date',
                'approval_date',
                'disbursement_date',
                'due_date',
                'completion_date'
            )
        }),
        ('Fees & Notes', {
            'fields': (
                'processing_fee',
                'admin_notes',
                'rejected_reason'
            )
        }),
        ('System Fields', {
            'fields': (
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        })
    )
    
    actions = ['approve_selected_loans', 'reject_selected_loans', 'mark_as_disbursed']
    
    def user_name(self, obj):
        """Display user name with link to user admin"""
        url = reverse('admin:users_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.get_full_name())
    user_name.short_description = 'User'
    
    def remaining_balance_display(self, obj):
        """Display remaining balance with color coding"""
        # 1. Force conversion to string first to strip wrapper
        raw_val = str(obj.remaining_balance if obj.remaining_balance is not None else 0)
        
        # 2. Convert to float safely
        try:
            balance = float(raw_val)
        except (ValueError, TypeError):
            balance = 0.0

        # 3. Format using f-string (Calculates string HERE, not inside format_html)
        formatted_money = f"KES {balance:,.2f}"

        # 4. Pass the plain string to format_html
        if balance <= 0:
            return format_html('<span style="color: green;">{}</span>', formatted_money)
        elif obj.is_overdue:
            return format_html('<span style="color: red;">{}</span>', formatted_money)
        else:
            return format_html('<span style="color: orange;">{}</span>', formatted_money)
    remaining_balance_display.short_description = 'Remaining Balance'
    
    def approve_selected_loans(self, request, queryset):
        """Bulk action to approve loans"""
        updated = 0
        for loan in queryset:
            if loan.status == 'SUBMITTED' or loan.status == 'UNDER_REVIEW':
                loan.approve()
                updated += 1
        self.message_user(request, f'Successfully approved {updated} loans.')
    approve_selected_loans.short_description = 'Approve selected loans'
    
    def reject_selected_loans(self, request, queryset):
        """Bulk action to reject loans"""
        updated = 0
        for loan in queryset:
            if loan.status in ['SUBMITTED', 'UNDER_REVIEW']:
                loan.reject('Bulk rejection from admin')
                updated += 1
        self.message_user(request, f'Successfully rejected {updated} loans.')
    reject_selected_loans.short_description = 'Reject selected loans'
    
    def mark_as_disbursed(self, request, queryset):
        """Bulk action to mark loans as disbursed"""
        updated = 0
        for loan in queryset:
            if loan.status == 'APPROVED':
                loan.disburse()
                updated += 1
        self.message_user(request, f'Successfully marked {updated} loans as disbursed.')
    mark_as_disbursed.short_description = 'Mark as disbursed'

@admin.register(LoanProduct)
class LoanProductAdmin(admin.ModelAdmin):
    """
    Admin interface for LoanProduct model
    """
    list_display = [
        'name', 
        'product_code', 
        'min_amount', 
        'max_amount', 
        'interest_rate', 
        'is_active',
        'created_at'
    ]
    
    list_filter = [
        'is_active', 
        'requires_documents', 
        'created_at'
    ]
    
    search_fields = [
        'name', 
        'product_code', 
        'description'
    ]
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Product Information', {
            'fields': (
                'product_code',
                'name',
                'description'
            )
        }),
        ('Loan Limits', {
            'fields': (
                'min_amount',
                'max_amount',
                'min_tenure',
                'max_tenure'
            )
        }),
        ('Interest & Fees', {
            'fields': (
                'interest_rate',
                'processing_fee',
                'late_fee_rate'
            )
        }),
        ('Eligibility Requirements', {
            'fields': (
                'min_income',
                'min_employment_duration',
                'min_credit_score'
            )
        }),
        ('Configuration', {
            'fields': (
                'is_active',
                'requires_documents'
            )
        }),
        ('System Fields', {
            'fields': (
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        })
    )

@admin.register(RepaymentSchedule)
class RepaymentScheduleAdmin(admin.ModelAdmin):
    """
    Admin interface for RepaymentSchedule model
    """
    list_display = [
        'loan_reference',
        'installment_number',
        'due_date',
        'total_amount',
        'paid_amount',
        'remaining_amount',
        'status',
        'paid_date'
    ]
    
    list_filter = [
        'status',
        'due_date',
        'paid_date'
    ]
    
    search_fields = [
        'loan__loan_reference',
        'loan__user__first_name',
        'loan__user__last_name',
        'loan__user__email'
    ]
    
    readonly_fields = [
        'remaining_amount',
        'created_at'
    ]
    
    actions = ['mark_as_paid']
    
    def loan_reference(self, obj):
        """Display loan reference with link"""
        url = reverse('admin:loans_loan_change', args=[obj.loan.id])
        return format_html('<a href="{}">{}</a>', url, obj.loan.loan_reference)
    loan_reference.short_description = 'Loan Reference'
    
    def mark_as_paid(self, request, queryset):
        """Bulk action to mark installments as paid"""
        updated = 0
        for schedule in queryset:
            if schedule.status != 'PAID':
                remaining = schedule.total_amount - schedule.paid_amount
                if remaining > 0:
                    schedule.record_payment(remaining)
                    updated += 1
        self.message_user(request, f'Successfully marked {updated} installments as paid.')
    mark_as_paid.short_description = 'Mark selected installments as paid'