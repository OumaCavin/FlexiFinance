"""
Custom User Model for FlexiFinance
Enhanced user model with additional fields for micro-finance platform
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone


class User(AbstractUser):
    """
    Custom User model for FlexiFinance
    Extends Django's AbstractUser with additional fields
    """
    
    # Basic Information
    phone_number = models.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$')],
        unique=True,
        null=True,  # Allow null temporarily for testing
        blank=True,  # Allow blank temporarily for testing
        help_text="M-Pesa registered phone number"
    )
    
    # Personal Details
    middle_name = models.CharField(max_length=50, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    national_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    
    # Contact Information
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    county = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, default='Kenya')
    
    # Employment Information
    occupation = models.CharField(max_length=100, blank=True)
    employer_name = models.CharField(max_length=200, blank=True)
    monthly_income = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    employment_duration = models.PositiveIntegerField(null=True, blank=True, help_text="Duration in months")
    
    # Emergency Contact
    emergency_contact_name = models.CharField(max_length=200, blank=True)
    emergency_contact_phone = models.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$')],
        blank=True
    )
    emergency_contact_relationship = models.CharField(max_length=50, blank=True)
    
    # Account Status
    is_verified = models.BooleanField(default=False)
    verification_date = models.DateTimeField(null=True, blank=True)
    kyc_status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending Verification'),
            ('APPROVED', 'Approved'),
            ('REJECTED', 'Rejected'),
            ('EXPIRED', 'Expired')
        ],
        default='PENDING'
    )
    
    # Financial Information
    credit_score = models.PositiveIntegerField(null=True, blank=True)
    credit_score_updated = models.DateTimeField(null=True, blank=True)
    total_loans_taken = models.PositiveIntegerField(default=0)
    active_loans_count = models.PositiveIntegerField(default=0)
    
    # System Fields
    registration_ip = models.GenericIPAddressField(null=True, blank=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    email_verification_token = models.CharField(max_length=100, blank=True)
    email_verification_sent_at = models.DateTimeField(null=True, blank=True)
    
    # Privacy and Settings
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=True)
    marketing_emails = models.BooleanField(default=False)
    two_factor_enabled = models.BooleanField(default=False)
    two_factor_secret = models.CharField(max_length=32, blank=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        indexes = [
            models.Index(fields=['phone_number']),
            models.Index(fields=['national_id']),
            models.Index(fields=['kyc_status']),
            models.Index(fields=['credit_score']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.username})"
    
    def get_full_name(self):
        """Return full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}".strip()
        return f"{self.username}"
    
    def get_short_name(self):
        """Return short name"""
        return self.first_name or self.username
    
    @property
    def is_loan_eligible(self):
        """Check if user is eligible for loans"""
        return (
            self.is_verified and
            self.kyc_status == 'APPROVED' and
            self.is_active and
            not self.is_staff
        )
    
    @property
    def can_apply_for_loan(self):
        """Check if user can apply for new loan"""
        from apps.loans.models import Loan
        active_loans = Loan.objects.filter(user=self, status__in=['APPROVED', 'ACTIVE']).count()
        return self.is_loan_eligible and active_loans < 3  # Max 3 active loans
    
    def update_credit_score(self, new_score):
        """Update user's credit score"""
        self.credit_score = new_score
        self.credit_score_updated = timezone.now()
        self.save(update_fields=['credit_score', 'credit_score_updated'])
    
    def mark_verified(self):
        """Mark user as verified"""
        self.is_verified = True
        self.verification_date = timezone.now()
        self.save(update_fields=['is_verified', 'verification_date'])
    
    def set_kyc_status(self, status, reviewed_by=None):
        """Set KYC status"""
        self.kyc_status = status
        if status == 'APPROVED':
            self.is_verified = True
            self.verification_date = timezone.now()
        self.save(update_fields=['kyc_status', 'is_verified', 'verification_date'])
    
    def get_annual_income(self):
        """Calculate annual monthly_income"""
        if self.monthly_income:
            return self.monthly_income * 12
        return 0
    
    def get_max_loan_amount(self):
        """Calculate maximum loan amount based on income"""
        if not self.monthly_income:
            return 0
        return min(self.monthly_income * 3, 500000)  # Max 3x monthly income or 500k
    
    def get_outstanding_balance(self):
        """Get total outstanding loan balance"""
        from apps.loans.models import Loan
        active_loans = Loan.objects.filter(user=self, status__in=['APPROVED', 'ACTIVE'])
        return sum(loan.remaining_balance for loan in active_loans)
    
    def get_debt_to_income_ratio(self):
        """Calculate debt-to-income ratio"""
        if not self.monthly_income or self.monthly_income == 0:
            return 0
        return self.get_outstanding_balance() / (self.monthly_income * 12)