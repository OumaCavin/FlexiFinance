"""
Company Information Model for FlexiFinance
"""
from django.db import models
from django.utils import timezone


class Company(models.Model):
    """
    Company information for legal documents and compliance
    """
    company_name = models.CharField(max_length=200, default='FlexiFinance Limited')
    registration_number = models.CharField(max_length=50, unique=True)
    license_number = models.CharField(max_length=100)
    
    # Banking and Financial Information
    cbk_registration = models.CharField(max_length=100, help_text='Central Bank of Kenya Registration Number')
    bank_name = models.CharField(max_length=200, default='Kenya Commercial Bank')
    bank_account_name = models.CharField(max_length=200, default='FlexiFinance Limited')
    bank_account_number = models.CharField(max_length=50)
    
    # Contact Information
    physical_address = models.TextField()
    postal_address = models.TextField()
    city = models.CharField(max_length=100, default='Nairobi')
    county = models.CharField(max_length=100, default='Nairobi County')
    country = models.CharField(max_length=100, default='Kenya')
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    website = models.URLField(blank=True)
    
    # Legal and Compliance
    terms_version = models.CharField(max_length=20, default='1.0')
    privacy_policy_version = models.CharField(max_length=20, default='1.0')
    loan_agreement_version = models.CharField(max_length=20, default='1.0')
    
    # Default Loan Terms
    default_interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=12.5)
    late_fee_fixed = models.DecimalField(max_digits=10, decimal_places=2, default=500.00)
    late_fee_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=2.0)
    disbursement_timeframe_days = models.PositiveIntegerField(default=3)
    
    # Legal Information
    arbitration_rules = models.CharField(max_length=200, default='Kenyan Centre for Arbitration Rules')
    governing_law = models.CharField(max_length=100, default='Laws of Kenya')
    jurisdiction = models.CharField(max_length=100, default='Nairobi, Kenya')
    
    # System fields
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'company'
        verbose_name = 'Company'
        verbose_name_plural = 'Company Information'
    
    def __str__(self):
        return self.company_name
    
    @classmethod
    def get_default_company(cls):
        """Get the default active company or create one"""
        company = cls.objects.filter(is_active=True).first()
        if not company:
            company = cls.objects.create(
                registration_number='CPR/2018/234567',
                license_number='P05123456789',
                cbk_registration='CBK/RG/234567',
                bank_account_number='1234567890',
                physical_address='Westlands Business Park, House No. 24',
                postal_address='P.O. Box 12345-00100',
                phone='+254 700 123 456',
                email='info@flexifinance.co.ke'
            )
        return company


class Contact(models.Model):
    """
    Contact form submissions model
    """
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    subject = models.CharField(max_length=200, default='General Inquiry')
    message = models.TextField()
    source = models.CharField(max_length=100, default='website_contact_form')
    
    # Metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # System fields
    is_processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'contact'
        verbose_name = 'Contact Form Submission'
        verbose_name_plural = 'Contact Form Submissions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.subject} ({self.email})"


class NewsletterSubscription(models.Model):
    """
    Newsletter subscription model for email marketing
    """
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    
    # Subscription preferences
    interests = models.JSONField(default=list, blank=True, help_text="List of interest areas")
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=100, blank=True)
    
    # Metadata
    source = models.CharField(max_length=100, default='website_footer')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Dates
    subscribed_at = models.DateTimeField(default=timezone.now)
    verified_at = models.DateTimeField(null=True, blank=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'newsletter_subscription'
        verbose_name = 'Newsletter Subscription'
        verbose_name_plural = 'Newsletter Subscriptions'
        ordering = ['-subscribed_at']
    
    def __str__(self):
        return f"{self.email} - {'Active' if self.is_active else 'Inactive'}"
    
    def verify(self):
        """Mark subscription as verified"""
        self.is_verified = True
        self.verified_at = timezone.now()
        self.verification_token = ''
        self.save(update_fields=['is_verified', 'verified_at', 'verification_token'])
    
    def unsubscribe(self):
        """Mark subscription as unsubscribed"""
        self.is_active = False
        self.unsubscribed_at = timezone.now()
        self.save(update_fields=['is_active', 'unsubscribed_at'])