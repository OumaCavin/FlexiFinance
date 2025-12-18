"""
Basic Loan Model for FlexiFinance
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
import random

User = get_user_model()


class Loan(models.Model):
    """
    Loan Model for FlexiFinance
    """
    
    LOAN_STATUSES = [
        ('DRAFT', 'Draft'),
        ('SUBMITTED', 'Submitted'),
        ('UNDER_REVIEW', 'Under Review'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('DISBURSED', 'Disbursed'),
        ('ACTIVE', 'Active'),
        ('COMPLETED', 'Completed'),
        ('DEFAULTED', 'Defaulted'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    LOAN_TYPES = [
        ('QUICK_CASH', 'Quick Cash Loan'),
        ('BUSINESS', 'Business Loan'),
        ('EMERGENCY', 'Emergency Loan'),
        ('PERSONAL', 'Personal Loan'),
        ('EDUCATION', 'Education Loan'),
    ]
    
    RISK_CATEGORIES = [
        ('LOW', 'Low Risk'),
        ('MEDIUM', 'Medium Risk'),
        ('HIGH', 'High Risk'),
    ]
    
    # Basic loan information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='loans')
    
    # Loan details
    loan_type = models.CharField(max_length=20, choices=LOAN_TYPES)
    principal_amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(1)])
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0)])
    loan_tenure = models.PositiveIntegerField(help_text="Tenure in months")
    
    # FIX: Added null=True, blank=True because these are calculated automatically
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    # Loan reference and status
    loan_reference = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=20, choices=LOAN_STATUSES, default='DRAFT')
    
    # Repayment information
    remaining_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    monthly_payment = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Purpose and description
    purpose = models.TextField()
    description = models.TextField(blank=True)
    
    # Risk assessment
    risk_category = models.CharField(max_length=10, choices=RISK_CATEGORIES, default='MEDIUM')
    credit_score_assigned = models.PositiveIntegerField(null=True, blank=True)
    
    # Dates
    application_date = models.DateTimeField(default=timezone.now)
    approval_date = models.DateTimeField(null=True, blank=True)
    disbursement_date = models.DateTimeField(null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    completion_date = models.DateTimeField(null=True, blank=True)
    
    # Additional fields
    processing_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    admin_notes = models.TextField(blank=True)
    rejected_reason = models.TextField(blank=True)
    
    # System fields
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'loans'
        verbose_name = 'Loan'
        verbose_name_plural = 'Loans'
        ordering = ['-application_date']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['loan_reference']),
            models.Index(fields=['status', 'application_date']),
        ]
    
    def __str__(self):
        return f"{self.loan_reference} - KES {self.principal_amount} - {self.user.get_full_name()}"
    
    def save(self, *args, **kwargs):
        # Generate loan reference if not exists
        if not self.loan_reference:
            timestamp = timezone.now().strftime('%Y%m%d')
            # FIX: Added random component to prevent duplicates (Race Condition)
            unique_suffix = random.randint(1000, 9999) 
            self.loan_reference = f"LF{timestamp}{unique_suffix}"
        
        # Calculate total amount if not set
        if not self.total_amount or self.total_amount == 0:
            from decimal import Decimal
            principal_amount = Decimal(str(self.principal_amount)) if self.principal_amount else Decimal('0.00')
            interest_rate = Decimal(str(self.interest_rate)) if self.interest_rate else Decimal('0.00')
            loan_tenure = Decimal(str(self.loan_tenure)) if self.loan_tenure else Decimal('0.00')
            processing_fee = Decimal(str(self.processing_fee)) if self.processing_fee else Decimal('0.00')
            
            interest_amount = (principal_amount * interest_rate * loan_tenure) / (Decimal('100') * Decimal('12'))
            self.total_amount = principal_amount + interest_amount + processing_fee
        
        # Calculate monthly payment
        if self.total_amount and self.loan_tenure:
            from decimal import Decimal
            total_amount = Decimal(str(self.total_amount)) if self.total_amount else Decimal('0.00')
            loan_tenure = Decimal(str(self.loan_tenure)) if self.loan_tenure else Decimal('0.00')
            self.monthly_payment = total_amount / loan_tenure
        
        # Set remaining balance
        if self.status in ['APPROVED', 'DISBURSED', 'ACTIVE'] and self.remaining_balance == 0:
            self.remaining_balance = self.total_amount
        
        super().save(*args, **kwargs)
    
    def approve(self):
        """Approve the loan"""
        self.status = 'APPROVED'
        self.approval_date = timezone.now()
        self.save(update_fields=['status', 'approval_date'])
    
    def reject(self, reason=''):
        """Reject the loan"""
        self.status = 'REJECTED'
        self.rejected_reason = reason
        self.save(update_fields=['status', 'rejected_reason'])
    
    def disburse(self):
        """Mark loan as disbursed"""
        self.status = 'DISBURSED'
        self.disbursement_date = timezone.now()
        if not self.due_date:
            self.due_date = timezone.now() + timezone.timedelta(days=30)
        self.save(update_fields=['status', 'disbursement_date', 'due_date'])
    
    def mark_active(self):
        """Mark loan as active"""
        self.status = 'ACTIVE'
        self.save(update_fields=['status'])
    
    def complete(self):
        """Mark loan as completed"""
        self.status = 'COMPLETED'
        self.completion_date = timezone.now()
        self.remaining_balance = 0
        self.save(update_fields=['status', 'completion_date', 'remaining_balance'])
    
    @property
    def is_approved(self):
        return self.status in ['APPROVED', 'DISBURSED', 'ACTIVE', 'COMPLETED']
    
    @property
    def is_active(self):
        return self.status in ['ACTIVE', 'COMPLETED']
    
    @property
    def is_overdue(self):
        from django.utils import timezone
        if self.due_date and self.remaining_balance > 0:
            return timezone.now() > self.due_date
        return False
    
    @property
    def days_since_application(self):
        from django.utils import timezone
        delta = timezone.now() - self.application_date
        return delta.days
    
    @property
    def outstanding_amount(self):
        return self.remaining_balance
    
    def calculate_interest(self):
        """Calculate total interest amount"""
        from decimal import Decimal
        total_amount = Decimal(str(self.total_amount)) if self.total_amount else Decimal('0.00')
        principal_amount = Decimal(str(self.principal_amount)) if self.principal_amount else Decimal('0.00')
        processing_fee = Decimal(str(self.processing_fee)) if self.processing_fee else Decimal('0.00')
        return total_amount - principal_amount - processing_fee


class LoanProduct(models.Model):
    """
    Loan Product Configuration
    """
    
    product_code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Loan limits
    min_amount = models.DecimalField(max_digits=12, decimal_places=2)
    max_amount = models.DecimalField(max_digits=12, decimal_places=2)
    min_tenure = models.PositiveIntegerField(help_text="Minimum tenure in months")
    max_tenure = models.PositiveIntegerField(help_text="Maximum tenure in months")
    
    # Interest and fees
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, help_text="Annual interest rate (%)")
    processing_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    late_fee_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Late fee rate (%)")
    
    # Requirements
    min_income = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    min_employment_duration = models.PositiveIntegerField(default=0, help_text="Minimum employment duration in months")
    min_credit_score = models.PositiveIntegerField(default=600)
    
    # Status
    is_active = models.BooleanField(default=True)
    requires_documents = models.BooleanField(default=False)
    
    # Metadata
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'loan_products'
        verbose_name = 'Loan Product'
        verbose_name_plural = 'Loan Products'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def is_user_eligible(self, user):
        """Check if user is eligible for this loan product"""
        if not user.is_loan_eligible:
            return False
        
        if user.monthly_income and user.monthly_income < self.min_income:
            return False
        
        if user.employment_duration and user.employment_duration < self.min_employment_duration:
            return False
        
        if user.credit_score and user.credit_score < self.min_credit_score:
            return False
        
        return True
    
    def calculate_loan_amount(self, requested_amount, tenure_months):
        """Calculate loan details based on requested amount and tenure"""
        from decimal import Decimal
        
        # Convert inputs to Decimal for safe calculations
        requested_amount_decimal = Decimal(str(requested_amount)) if requested_amount else Decimal('0.00')
        tenure_months_decimal = Decimal(str(tenure_months)) if tenure_months else Decimal('0.00')
        min_amount = Decimal(str(self.min_amount)) if self.min_amount else Decimal('0.00')
        max_amount = Decimal(str(self.max_amount)) if self.max_amount else Decimal('0.00')
        interest_rate = Decimal(str(self.interest_rate)) if self.interest_rate else Decimal('0.00')
        processing_fee = Decimal(str(self.processing_fee)) if self.processing_fee else Decimal('0.00')
        
        if requested_amount_decimal < min_amount or requested_amount_decimal > max_amount:
            return None
        
        if Decimal(str(tenure_months)) < self.min_tenure or Decimal(str(tenure_months)) > self.max_tenure:
            return None
        
        # Calculate interest
        interest_amount = (requested_amount_decimal * interest_rate * tenure_months_decimal) / (Decimal('100') * Decimal('12'))
        total_amount = requested_amount_decimal + interest_amount + processing_fee
        monthly_payment = total_amount / tenure_months_decimal
        
        return {
            'principal_amount': requested_amount_decimal,
            'interest_amount': interest_amount,
            'processing_fee': processing_fee,
            'total_amount': total_amount,
            'monthly_payment': monthly_payment,
            'tenure_months': tenure_months
        }


class RepaymentSchedule(models.Model):
    """
    Loan Repayment Schedule
    """
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('OVERDUE', 'Overdue'),
        ('PARTIAL', 'Partial Payment'),
    ]
    
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='repayment_schedule')
    installment_number = models.PositiveIntegerField()
    due_date = models.DateField()
    
    # Payment breakdown
    principal_amount = models.DecimalField(max_digits=12, decimal_places=2)
    interest_amount = models.DecimalField(max_digits=12, decimal_places=2)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Payment tracking
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    remaining_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Dates
    paid_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'repayment_schedules'
        verbose_name = 'Repayment Schedule'
        verbose_name_plural = 'Repayment Schedules'
        unique_together = ['loan', 'installment_number']
        ordering = ['due_date']
    
    def __str__(self):
        return f"{self.loan.loan_reference} - Installment {self.installment_number} - KES {self.total_amount}"
    
    def save(self, *args, **kwargs):
        # Calculate remaining amount (ensure both are Decimal objects)
        from decimal import Decimal
        total_amount = Decimal(str(self.total_amount)) if self.total_amount else Decimal('0.00')
        paid_amount = Decimal(str(self.paid_amount)) if self.paid_amount else Decimal('0.00')
        self.remaining_amount = total_amount - paid_amount
        
        # Update status
        from django.utils import timezone
        if self.paid_amount >= self.total_amount:
            self.status = 'PAID'
            if not self.paid_date:
                self.paid_date = timezone.now()
        elif self.paid_amount > 0:
            self.status = 'PARTIAL'
        elif timezone.now().date() > self.due_date:
            self.status = 'OVERDUE'
        else:
            self.status = 'PENDING'
        
        super().save(*args, **kwargs)
    
    def record_payment(self, amount):
        """Record a payment for this installment"""
        from decimal import Decimal
        
        # Ensure amount is a Decimal for safe operations
        amount_decimal = Decimal(str(amount)) if amount else Decimal('0.00')
        
        # Ensure paid_amount is also a Decimal before adding
        current_paid = Decimal(str(self.paid_amount)) if self.paid_amount else Decimal('0.00')
        self.paid_amount = current_paid + amount_decimal
        
        self.save()
        
        # Update loan remaining balance
        self.loan.remaining_balance -= amount_decimal
        self.loan.save(update_fields=['remaining_balance'])
        
        # Check if loan is fully paid
        if self.loan.remaining_balance <= 0:
            self.loan.complete()
    
    @property
    def is_overdue(self):
        from django.utils import timezone
        return timezone.now().date() > self.due_date and self.status != 'PAID'