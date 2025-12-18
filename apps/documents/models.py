"""
Document models for FlexiFinance
Comprehensive document management for KYC, loan applications, and compliance
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
import os

User = get_user_model()

def document_upload_path(instance, filename):
    """Generate upload path for documents"""
    return f"documents/{instance.user.id}/{timezone.now().strftime('%Y/%m/%d')}/{filename}"

def validate_file_size(file_obj, max_size_mb=10):
    """Validate file size"""
    max_size = max_size_mb * 1024 * 1024  # Convert MB to bytes
    if file_obj.size > max_size:
        raise ValidationError(f"File size cannot exceed {max_size_mb}MB")

class DocumentType(models.Model):
    """Types of documents that can be uploaded"""
    DOCUMENT_PURPOSES = [
        ('KYC', 'Know Your Customer'),
        ('LOAN_APPLICATION', 'Loan Application'),
        ('INCOME_PROOF', 'Income Verification'),
        ('BUSINESS_DOCS', 'Business Documentation'),
        ('COLLATERAL', 'Collateral Documents'),
        ('ADDRESS_PROOF', 'Address Verification'),
        ('EMPLOYMENT_PROOF', 'Employment Verification'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    required_for = models.CharField(
        max_length=50, 
        choices=DOCUMENT_PURPOSES,
        default='KYC'
    )
    is_required = models.BooleanField(default=False)
    max_file_size = models.IntegerField(default=10485760)  # 10MB in bytes
    allowed_extensions = models.CharField(
        max_length=100, 
        default='pdf,jpg,jpeg,png,doc,docx',
        help_text="Comma-separated list of allowed file extensions"
    )
    verification_required = models.BooleanField(
        default=True,
        help_text="Whether this document type requires manual verification"
    )
    auto_approve = models.BooleanField(
        default=False,
        help_text="Whether documents of this type should be auto-approved"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_required_for_display()})"

    def get_allowed_extensions_list(self):
        """Return list of allowed extensions"""
        return [ext.strip().lower() for ext in self.allowed_extensions.split(',')]

    class Meta:
        verbose_name = "Document Type"
        verbose_name_plural = "Document Types"
        ordering = ['name']


class Document(models.Model):
    """Uploaded documents"""
    STATUS_CHOICES = [
        ('PENDING', 'Pending Review'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('EXPIRED', 'Expired'),
        ('AUTO_APPROVED', 'Auto-Approved'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    document_type = models.ForeignKey(DocumentType, on_delete=models.CASCADE)
    file = models.FileField(
        upload_to=document_upload_path,
        validators=[
            FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx'])
        ]
    )
    original_filename = models.CharField(max_length=255)
    file_size = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    rejection_reason = models.TextField(blank=True)
    admin_notes = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(
        User, 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL,
        related_name='verified_documents'
    )
    expires_at = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    download_count = models.IntegerField(default=0)
    last_accessed = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.document_type.name} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        """Override save to set file size and auto-approve if needed"""
        if self.file and not self.file_size:
            self.file_size = self.file.size
            
        # Auto-approve if document type allows it
        if self.document_type.auto_approve and self.status == 'PENDING':
            self.status = 'AUTO_APPROVED'
            self.verified_at = timezone.now()
            
        super().save(*args, **kwargs)

    def approve(self, verified_by, notes=None):
        """Approve the document"""
        self.status = 'APPROVED'
        self.verified_by = verified_by
        self.verified_at = timezone.now()
        if notes:
            self.admin_notes = notes
        self.save()

    def reject(self, reason, rejected_by, notes=None):
        """Reject the document"""
        self.status = 'REJECTED'
        self.rejection_reason = reason
        if notes:
            self.admin_notes = notes
        self.verified_by = rejected_by
        self.verified_at = timezone.now()
        self.save()

    def mark_expired(self):
        """Mark document as expired"""
        if self.expires_at and timezone.now() > self.expires_at:
            self.status = 'EXPIRED'
            self.save()

    def get_file_extension(self):
        """Get file extension"""
        return os.path.splitext(self.file.name)[1].lower()

    def is_valid_for_user(self, user):
        """Check if document is valid for the user"""
        return self.user == user and self.status in ['APPROVED', 'AUTO_APPROVED']

    def increment_download_count(self):
        """Increment download count"""
        self.download_count += 1
        self.last_accessed = timezone.now()
        self.save(update_fields=['download_count', 'last_accessed'])

    class Meta:
        verbose_name = "Document"
        verbose_name_plural = "Documents"
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['document_type', 'status']),
            models.Index(fields=['uploaded_at']),
        ]


class DocumentVerification(models.Model):
    """Document verification log and tracking"""
    VERIFICATION_TYPES = [
        ('MANUAL', 'Manual Verification'),
        ('AUTOMATED', 'Automated Verification'),
        ('THIRD_PARTY', 'Third Party Verification'),
        ('AUTO_APPROVAL', 'Auto-Approval'),
    ]
    
    document = models.OneToOneField(Document, on_delete=models.CASCADE, related_name='verification')
    verifier = models.ForeignKey(User, on_delete=models.CASCADE)
    verification_date = models.DateTimeField(auto_now_add=True)
    verification_type = models.CharField(
        max_length=20, 
        choices=VERIFICATION_TYPES,
        default='MANUAL'
    )
    notes = models.TextField(blank=True)
    risk_score = models.IntegerField(default=0, help_text="Risk assessment score (0-100)")
    confidence_level = models.IntegerField(
        default=100, 
        help_text="Confidence level of verification (0-100)"
    )
    ai_analysis_result = models.JSONField(default=dict, blank=True)
    verification_metadata = models.JSONField(default=dict, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Verification for {self.document}"

    def calculate_risk_level(self):
        """Calculate risk level based on score"""
        if self.risk_score <= 25:
            return 'LOW'
        elif self.risk_score <= 50:
            return 'MEDIUM'
        elif self.risk_score <= 75:
            return 'HIGH'
        else:
            return 'CRITICAL'

    def update_expiry(self, days=365):
        """Update verification expiry date"""
        self.expires_at = timezone.now() + timezone.timedelta(days=days)
        self.save()

    class Meta:
        verbose_name = "Document Verification"
        verbose_name_plural = "Document Verifications"
        ordering = ['-verification_date']


class DocumentAccessLog(models.Model):
    """Log of document access for security and audit"""
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='access_logs')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=50)  # VIEW, DOWNLOAD, DELETE, etc.
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    session_id = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.user.email} - {self.action} - {self.document}"

    class Meta:
        verbose_name = "Document Access Log"
        verbose_name_plural = "Document Access Logs"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['document', 'timestamp']),
            models.Index(fields=['user', 'timestamp']),
        ]