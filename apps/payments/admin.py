"""
Django admin configuration for Payments app
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import MpesaTransaction, Payment, PaymentSchedule

@admin.register(MpesaTransaction)
class MpesaTransactionAdmin(admin.ModelAdmin):
    """
    Admin interface for MpesaTransaction model
    """
    list_display = [
        'transaction_type',
        'user_name',
        'amount',
        'phone_number',
        'status',
        'mpesa_receipt',
        'initiated_at'
    ]
    
    list_filter = [
        'transaction_type',
        'status',
        'initiated_at',
        'completed_at'
    ]
    
    search_fields = [
        'user__first_name',
        'user__last_name',
        'user__email',
        'phone_number',
        'mpesa_receipt',
        'checkout_request_id',
        'merchant_request_id'
    ]
    
    readonly_fields = [
        'id',
        'initiated_at',
        'completed_at',
        'updated_at',
        'callback_received_at'
    ]
    
    fieldsets = (
        ('Transaction Information', {
            'fields': (
                'id',
                'user',
                'transaction_type',
                'amount',
                'phone_number'
            )
        }),
        ('M-Pesa Details', {
            'fields': (
                'mpesa_receipt',
                'checkout_request_id',
                'merchant_request_id'
            )
        }),
        ('Status & Response', {
            'fields': (
                'status',
                'result_code',
                'result_desc'
            )
        }),
        ('Callback Information', {
            'fields': (
                'callback_received',
                'callback_received_at',
                'callback_data'
            )
        }),
        ('Timestamps', {
            'fields': (
                'initiated_at',
                'completed_at',
                'updated_at'
            )
        })
    )
    
    actions = ['mark_as_completed', 'mark_as_failed']
    
    def user_name(self, obj):
        """Display user name with link to user admin"""
        url = reverse('admin:users_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.get_full_name())
    user_name.short_description = 'User'
    
    def mark_as_completed(self, request, queryset):
        """Bulk action to mark transactions as completed"""
        updated = 0
        for transaction in queryset:
            if transaction.status not in ['COMPLETED', 'FAILED']:
                transaction.mark_completed()
                updated += 1
        self.message_user(request, f'Successfully marked {updated} transactions as completed.')
    mark_as_completed.short_description = 'Mark selected transactions as completed'
    
    def mark_as_failed(self, request, queryset):
        """Bulk action to mark transactions as failed"""
        updated = 0
        for transaction in queryset:
            if transaction.status not in ['COMPLETED', 'FAILED']:
                transaction.mark_failed(result_code='999', result_desc='Manual failure from admin')
                updated += 1
        self.message_user(request, f'Successfully marked {updated} transactions as failed.')
    mark_as_failed.short_description = 'Mark selected transactions as failed'

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """
    Admin interface for Payment model
    """
    list_display = [
        'reference_number',
        'user_name',
        'payment_type',
        'amount',
        'payment_method',
        'status',
        'phone_number',
        'created_at'
    ]
    
    list_filter = [
        'payment_type',
        'payment_method',
        'status',
        'currency',
        'created_at',
        'completed_at'
    ]
    
    search_fields = [
        'reference_number',
        'user__first_name',
        'user__last_name',
        'user__email',
        'phone_number',
        'receipt_number',
        'confirmation_code'
    ]
    
    readonly_fields = [
        'id',
        'reference_number',
        'created_at',
        'updated_at',
        'completed_at'
    ]
    
    fieldsets = (
        ('Payment Information', {
            'fields': (
                'id',
                'reference_number',
                'user',
                'payment_type',
                'amount',
                'currency',
                'description'
            )
        }),
        ('Payment Method & Status', {
            'fields': (
                'payment_method',
                'status',
                'phone_number'
            )
        }),
        ('Receipt & Confirmation', {
            'fields': (
                'receipt_number',
                'confirmation_code'
            )
        }),
        ('M-Pesa Integration', {
            'fields': ('mpesa_transaction',)
        }),
        ('Metadata', {
            'fields': ('metadata',)
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at',
                'completed_at'
            )
        })
    )
    
    actions = ['mark_as_completed', 'mark_as_failed', 'initiate_stk_push']
    
    def user_name(self, obj):
        """Display user name with link to user admin"""
        url = reverse('admin:users_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.get_full_name())
    user_name.short_description = 'User'
    
    def mark_as_completed(self, request, queryset):
        """Bulk action to mark payments as completed"""
        updated = 0
        for payment in queryset:
            if payment.status not in ['COMPLETED', 'FAILED', 'REFUNDED']:
                payment.mark_completed()
                updated += 1
        self.message_user(request, f'Successfully marked {updated} payments as completed.')
    mark_as_completed.short_description = 'Mark selected payments as completed'
    
    def mark_as_failed(self, request, queryset):
        """Bulk action to mark payments as failed"""
        updated = 0
        for payment in queryset:
            if payment.status not in ['COMPLETED', 'FAILED', 'REFUNDED']:
                payment.mark_failed()
                updated += 1
        self.message_user(request, f'Successfully marked {updated} payments as failed.')
    mark_as_failed.short_description = 'Mark selected payments as failed'
    
    def initiate_stk_push(self, request, queryset):
        """Bulk action to initiate STK Push for payments"""
        success_count = 0
        error_count = 0
        
        for payment in queryset:
            if payment.status == 'PENDING' and payment.payment_method == 'MPESA':
                try:
                    result = payment.initiate_stk_push()
                    if result['success']:
                        success_count += 1
                    else:
                        error_count += 1
                except Exception as e:
                    error_count += 1
        
        message = f'STK Push initiated for {success_count} payments'
        if error_count > 0:
            message += f', {error_count} failed'
        self.message_user(request, message)
    initiate_stk_push.short_description = 'Initiate STK Push for selected payments'

@admin.register(PaymentSchedule)
class PaymentScheduleAdmin(admin.ModelAdmin):
    """
    Admin interface for PaymentSchedule model
    """
    list_display = [
        'payment_reference',
        'due_date',
        'amount_due',
        'amount_paid',
        'amount_remaining',
        'status',
        'is_overdue_display',
        'created_at'
    ]
    
    list_filter = [
        'status',
        'due_date',
        'created_at'
    ]
    
    search_fields = [
        'payment__reference_number',
        'payment__user__first_name',
        'payment__user__last_name',
        'payment__user__email'
    ]
    
    readonly_fields = [
        'amount_remaining',
        'created_at',
        'is_overdue_display'
    ]
    
    actions = ['mark_as_paid', 'mark_as_overdue']
    
    def payment_reference(self, obj):
        """Display payment reference with link"""
        url = reverse('admin:payments_payment_change', args=[obj.payment.id])
        return format_html('<a href="{}">{}</a>', url, obj.payment.reference_number)
    payment_reference.short_description = 'Payment Reference'
    
    def is_overdue_display(self, obj):
        """Display overdue status"""
        if obj.is_overdue:
            return format_html('<span style="color: red;">Yes</span>')
        else:
            return format_html('<span style="color: green;">No</span>')
    is_overdue_display.short_description = 'Overdue'
    
    def mark_as_paid(self, request, queryset):
        """Bulk action to mark schedule items as paid"""
        updated = 0
        for schedule in queryset:
            if schedule.status != 'PAID':
                remaining_amount = schedule.amount_remaining
                if remaining_amount > 0:
                    schedule.mark_as_paid(remaining_amount)
                    updated += 1
        self.message_user(request, f'Successfully marked {updated} schedule items as paid.')
    mark_as_paid.short_description = 'Mark selected items as paid'
    
    def mark_as_overdue(self, request, queryset):
        """Bulk action to mark schedule items as overdue"""
        updated = 0
        from django.utils import timezone
        today = timezone.now().date()
        
        for schedule in queryset:
            if schedule.due_date < today and schedule.status not in ['PAID']:
                schedule.status = 'OVERDUE'
                schedule.save(update_fields=['status'])
                updated += 1
        self.message_user(request, f'Successfully marked {updated} schedule items as overdue.')
    mark_as_overdue.short_description = 'Mark selected items as overdue'