"""
M-Pesa Integration Models for FlexiFinance
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

User = get_user_model()


class MpesaTransaction(models.Model):
    """
    M-Pesa Transaction Model
    Stores all M-Pesa transaction details
    """
    
    TRANSACTION_TYPES = [
        ('DISBURSEMENT', 'Loan Disbursement'),
        ('REPAYMENT', 'Loan Repayment'),
        ('FEE', 'Processing Fee'),
        ('REFUND', 'Refund'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    # Transaction identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mpesa_transactions')
    
    # Transaction details
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(1)])
    phone_number = models.CharField(max_length=15)
    
    # M-Pesa specific fields
    mpesa_receipt = models.CharField(max_length=100, unique=True, null=True, blank=True)
    checkout_request_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    merchant_request_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    
    # Transaction status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    result_code = models.CharField(max_length=10, null=True, blank=True)
    result_desc = models.CharField(max_length=255, null=True, blank=True)
    
    # Callback data
    callback_received = models.BooleanField(default=False)
    callback_data = models.JSONField(null=True, blank=True)
    callback_received_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    initiated_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'mpesa_transactions'
        verbose_name = 'M-Pesa Transaction'
        verbose_name_plural = 'M-Pesa Transactions'
        ordering = ['-initiated_at']
        indexes = [
            models.Index(fields=['mpesa_receipt']),
            models.Index(fields=['checkout_request_id']),
            models.Index(fields=['merchant_request_id']),
            models.Index(fields=['status']),
            models.Index(fields=['user', 'status']),
        ]
    
    def __str__(self):
        return f"{self.transaction_type} - KES {self.amount} - {self.phone_number}"
    
    def mark_completed(self, mpesa_receipt=None, result_code='0', result_desc='Success'):
        """Mark transaction as completed"""
        self.status = 'COMPLETED'
        self.completed_at = timezone.now()
        if mpesa_receipt:
            self.mpesa_receipt = mpesa_receipt
        self.result_code = result_code
        self.result_desc = result_desc
        self.save(update_fields=['status', 'completed_at', 'mpesa_receipt', 'result_code', 'result_desc'])
    
    def mark_failed(self, result_code=None, result_desc=None):
        """Mark transaction as failed"""
        self.status = 'FAILED'
        self.completed_at = timezone.now()
        if result_code:
            self.result_code = result_code
        if result_desc:
            self.result_desc = result_desc
        self.save(update_fields=['status', 'completed_at', 'result_code', 'result_desc'])
    
    def process_callback(self, callback_data):
        """Process M-Pesa callback data"""
        self.callback_received = True
        self.callback_received_at = timezone.now()
        self.callback_data = callback_data
        
        if 'Body' in callback_data and 'stkCallback' in callback_data['Body']:
            stk_callback = callback_data['Body']['stkCallback']
            
            # Extract transaction details
            self.result_code = str(stk_callback.get('ResultCode', ''))
            self.result_desc = stk_callback.get('ResultDesc', '')
            self.checkout_request_id = stk_callback.get('CheckoutRequestID', '')
            
            # Extract metadata
            if 'CallbackMetadata' in stk_callback:
                metadata = stk_callback['CallbackMetadata']
                for item in metadata.get('Item', []):
                    if item.get('Name') == 'MpesaReceiptNumber':
                        self.mpesa_receipt = item.get('Value')
                    elif item.get('Name') == 'TransactionDate':
                        # Parse transaction date if needed
                        pass
            
            # Update status based on result code
            if self.result_code == '0':
                self.status = 'COMPLETED'
                self.completed_at = timezone.now()
            else:
                self.status = 'FAILED'
                self.completed_at = timezone.now()
        
        self.save(update_fields=[
            'callback_received', 'callback_received_at', 'callback_data',
            'result_code', 'result_desc', 'checkout_request_id', 'mpesa_receipt', 'status', 'completed_at'
        ])


class Payment(models.Model):
    """
    Payment Model
    General payment model for all transactions
    """
    
    PAYMENT_TYPES = [
        ('DISBURSEMENT', 'Loan Disbursement'),
        ('REPAYMENT', 'Loan Repayment'),
        ('PROCESSING_FEE', 'Processing Fee'),
        ('LATE_FEE', 'Late Payment Fee'),
        ('OTHER', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    # Basic payment information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    
    # Payment details
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(1)])
    currency = models.CharField(max_length=3, default='KES')
    
    # Reference information
    reference_number = models.CharField(max_length=100, unique=True, null=True, blank=True)
    description = models.TextField(blank=True)
    
    # Payment method and status
    payment_method = models.CharField(max_length=20, default='MPESA')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # M-Pesa integration
    mpesa_transaction = models.OneToOneField(
        MpesaTransaction, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='payment'
    )
    
    # Phone number for payments
    phone_number = models.CharField(max_length=15)
    
    # Receipt and confirmation
    receipt_number = models.CharField(max_length=100, null=True, blank=True)
    confirmation_code = models.CharField(max_length=100, null=True, blank=True)
    
    # Metadata
    metadata = models.JSONField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'payments'
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['reference_number']),
            models.Index(fields=['status']),
            models.Index(fields=['user', 'status']),
            models.Index(fields=['payment_type']),
        ]
    
    def __str__(self):
        return f"{self.payment_type} - KES {self.amount} - {self.user}"
    
    def generate_reference_number(self):
        """Generate unique reference number"""
        from django.utils import timezone
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        random_part = str(uuid.uuid4()).split('-')[0][:6].upper()
        self.reference_number = f"PAY{timestamp}{random_part}"
        return self.reference_number
    
    def mark_completed(self, receipt_number=None):
        """Mark payment as completed"""
        self.status = 'COMPLETED'
        self.completed_at = timezone.now()
        if receipt_number:
            self.receipt_number = receipt_number
        self.save(update_fields=['status', 'completed_at', 'receipt_number'])
    
    def mark_failed(self):
        """Mark payment as failed"""
        self.status = 'FAILED'
        self.save(update_fields=['status'])
    
    def initiate_stk_push(self):
        """Initiate STK Push for this payment"""
        from apps.payments.services.mpesa_service import MpesaService
        
        mpesa_service = MpesaService()
        
        # Create M-Pesa transaction
        mpesa_transaction = MpesaTransaction.objects.create(
            user=self.user,
            transaction_type='REPAYMENT' if self.payment_type == 'REPAYMENT' else 'DISBURSEMENT',
            amount=self.amount,
            phone_number=self.phone_number,
            status='PROCESSING'
        )
        
        # Link to payment
        self.mpesa_transaction = mpesa_transaction
        self.save(update_fields=['mpesa_transaction'])
        
        # Initiate STK Push
        result = mpesa_service.initiate_stk_push(
            phone_number=self.phone_number,
            amount=float(self.amount),
            reference=self.reference_number,
            description=self.description or 'FlexiFinance Payment'
        )
        
        if result['success']:
            # Update transaction with M-Pesa request ID
            mpesa_transaction.merchant_request_id = result.get('merchant_request_id')
            mpesa_transaction.checkout_request_id = result.get('checkout_request_id')
            mpesa_transaction.save(update_fields=['merchant_request_id', 'checkout_request_id'])
            
            self.status = 'PROCESSING'
            self.save(update_fields=['status'])
            
            return {
                'success': True,
                'message': 'STK Push sent to your phone',
                'transaction_id': str(mpesa_transaction.id)
            }
        else:
            self.mark_failed()
            return {
                'success': False,
                'message': result.get('error', 'Failed to initiate payment')
            }


class PaymentSchedule(models.Model):
    """
    Payment Schedule Model
    Tracks scheduled payments and due dates
    """
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('OVERDUE', 'Overdue'),
        ('PARTIAL', 'Partial Payment'),
    ]
    
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='schedule_items')
    due_date = models.DateField()
    amount_due = models.DecimalField(max_digits=12, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'payment_schedules'
        verbose_name = 'Payment Schedule'
        verbose_name_plural = 'Payment Schedules'
        ordering = ['due_date']
        unique_together = ['payment', 'due_date']
    
    def __str__(self):
        return f"{self.payment} - Due: {self.due_date} - KES {self.amount_due}"
    
    @property
    def amount_remaining(self):
        from decimal import Decimal
        amount_due = Decimal(str(self.amount_due)) if self.amount_due else Decimal('0.00')
        amount_paid = Decimal(str(self.amount_paid)) if self.amount_paid else Decimal('0.00')
        return amount_due - amount_paid
    
    @property
    def is_overdue(self):
        from django.utils import timezone
        # Handle case where due_date is None
        if not self.due_date:
            return False
        return timezone.now().date() > self.due_date and self.status != 'PAID'
    
    def mark_as_paid(self, amount_paid):
        """Mark schedule item as paid"""
        from decimal import Decimal
        
        # Ensure amount_paid is a Decimal for safe operations
        amount_paid_decimal = Decimal(str(amount_paid)) if amount_paid else Decimal('0.00')
        
        # Ensure current amount_paid is also a Decimal before adding
        current_paid = Decimal(str(self.amount_paid)) if self.amount_paid else Decimal('0.00')
        self.amount_paid = current_paid + amount_paid_decimal
        
        if self.amount_paid >= self.amount_due:
            self.status = 'PAID'
        elif self.amount_paid > 0:
            self.status = 'PARTIAL'
        elif self.is_overdue:
            self.status = 'OVERDUE'
        
        self.save(update_fields=['amount_paid', 'status'])