"""
Comprehensive Notification System for FlexiFinance
Handles notification history, preferences, delivery tracking, and analytics
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
import json

User = get_user_model()


class NotificationTemplate(models.Model):
    """
    Predefined notification templates for consistent messaging
    """
    NOTIFICATION_TYPES = [
        ('LOAN_APPROVAL', 'Loan Approval'),
        ('LOAN_REJECTION', 'Loan Rejection'),
        ('LOAN_DISBURSEMENT', 'Loan Disbursement'),
        ('PAYMENT_CONFIRMATION', 'Payment Confirmation'),
        ('PAYMENT_REMINDER', 'Payment Reminder'),
        ('OVERDUE_NOTICE', 'Overdue Notice'),
        ('WELCOME_EMAIL', 'Welcome Email'),
        ('PASSWORD_RESET', 'Password Reset'),
        ('ACCOUNT_VERIFICATION', 'Account Verification'),
        ('SECURITY_ALERT', 'Security Alert'),
        ('SYSTEM_MAINTENANCE', 'System Maintenance'),
        ('MARKETING', 'Marketing Communication'),
        ('SUPPORT_TICKET', 'Support Ticket Response'),
        ('CUSTOM', 'Custom Notification'),
    ]

    CHANNELS = [
        ('EMAIL', 'Email'),
        ('SMS', 'SMS'),
        ('PUSH', 'Push Notification'),
        ('IN_APP', 'In-App Notification'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    channels = models.JSONField(default=list, help_text='List of delivery channels')
    
    # Template content
    subject_template = models.CharField(max_length=200, blank=True)
    message_template = models.TextField()
    html_template = models.TextField(blank=True)
    
    # Configuration
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=5, validators=[MinValueValidator(1), MaxValueValidator(10)])
    retry_attempts = models.IntegerField(default=3)
    retry_delay_minutes = models.IntegerField(default=30)
    
    # Analytics
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    usage_count = models.IntegerField(default=0)

    class Meta:
        ordering = ['-usage_count', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_notification_type_display()})"


class Notification(models.Model):
    """
    Individual notification instance with full tracking and delivery history
    """
    DELIVERY_STATUS = [
        ('PENDING', 'Pending'),
        ('SENT', 'Sent'),
        ('DELIVERED', 'Delivered'),
        ('FAILED', 'Failed'),
        ('BOUNCED', 'Bounced'),
        ('CANCELLED', 'Cancelled'),
        ('RETRYING', 'Retrying'),
    ]

    PRIORITY_LEVELS = [
        ('LOW', 'Low'),
        ('NORMAL', 'Normal'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Core notification data
    template = models.ForeignKey(NotificationTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    
    # Content
    subject = models.CharField(max_length=200)
    message = models.TextField()
    html_content = models.TextField(blank=True)
    
    # Delivery information
    channel = models.CharField(max_length=20, choices=NotificationTemplate.CHANNELS)
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='NORMAL')
    
    # Status tracking
    status = models.CharField(max_length=15, choices=DELIVERY_STATUS, default='PENDING')
    retry_count = models.IntegerField(default=0)
    max_retries = models.IntegerField(default=3)
    
    # Delivery timestamps
    scheduled_at = models.DateTimeField(default=timezone.now)
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)
    
    # External tracking
    provider_id = models.CharField(max_length=100, blank=True, help_text='External provider message ID')
    provider_response = models.JSONField(default=dict, blank=True)
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['status', 'scheduled_at']),
            models.Index(fields=['channel']),
        ]

    def __str__(self):
        return f"{self.get_channel_display()} to {self.recipient.email} - {self.get_status_display()}"

    @property
    def is_pending(self):
        return self.status == 'PENDING'

    @property
    def is_sent(self):
        return self.status in ['SENT', 'DELIVERED']

    @property
    def has_failed(self):
        return self.status in ['FAILED', 'BOUNCED']

    @property
    def can_retry(self):
        return self.status in ['FAILED', 'BOUNCED'] and self.retry_count < self.max_retries

    def mark_sent(self, provider_id=None, provider_response=None):
        """Mark notification as sent"""
        self.status = 'SENT'
        self.sent_at = timezone.now()
        self.provider_id = provider_id or ''
        self.provider_response = provider_response or {}
        self.save()

    def mark_delivered(self):
        """Mark notification as delivered"""
        self.status = 'DELIVERED'
        self.delivered_at = timezone.now()
        self.save()

    def mark_failed(self, error_message=None):
        """Mark notification as failed"""
        self.status = 'FAILED'
        self.failed_at = timezone.now()
        if error_message:
            self.metadata['last_error'] = error_message
        self.save()

    def schedule_retry(self):
        """Schedule notification for retry"""
        if self.can_retry:
            self.retry_count += 1
            self.status = 'RETRYING'
            self.scheduled_at = timezone.now() + timezone.timedelta(
                minutes=self.template.retry_delay_minutes if self.template else 30
            )
            self.save()
            return True
        return False


class UserNotificationPreference(models.Model):
    """
    User preferences for notification types and channels
    """
    EMAIL_FREQUENCY = [
        ('IMMEDIATE', 'Immediate'),
        ('HOURLY', 'Hourly Digest'),
        ('DAILY', 'Daily Digest'),
        ('WEEKLY', 'Weekly Digest'),
        ('NEVER', 'Never'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    
    # Email preferences
    email_notifications = models.BooleanField(default=True)
    email_frequency = models.CharField(max_length=15, choices=EMAIL_FREQUENCY, default='IMMEDIATE')
    
    # SMS preferences
    sms_notifications = models.BooleanField(default=False)
    sms_phone_number = models.CharField(max_length=15, blank=True)
    
    # Push notification preferences
    push_notifications = models.BooleanField(default=True)
    
    # In-app preferences
    in_app_notifications = models.BooleanField(default=True)
    
    # Quiet hours (no notifications during these hours)
    quiet_hours_enabled = models.BooleanField(default=False)
    quiet_hours_start = models.TimeField(default=timezone.datetime.strptime('22:00', '%H:%M').time())
    quiet_hours_end = models.TimeField(default=timezone.datetime.strptime('08:00', '%H:%M').time())
    
    # Notification type preferences
    notification_type_preferences = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Preferences for {self.user.email}"

    def get_preference(self, notification_type, channel):
        """Get user preference for specific notification type and channel"""
        prefs = self.notification_type_preferences.get(notification_type, {})
        return prefs.get(channel, True)  # Default to True if not specified


class NotificationAnalytics(models.Model):
    """
    Analytics data for notification performance and insights
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Date for aggregation
    date = models.DateField()
    
    # Metrics
    total_sent = models.IntegerField(default=0)
    total_delivered = models.IntegerField(default=0)
    total_failed = models.IntegerField(default=0)
    total_bounced = models.IntegerField(default=0)
    
    # Channel breakdown
    email_sent = models.IntegerField(default=0)
    email_delivered = models.IntegerField(default=0)
    sms_sent = models.IntegerField(default=0)
    sms_delivered = models.IntegerField(default=0)
    
    # Template performance
    template_performance = models.JSONField(default=dict, blank=True)
    
    # User engagement
    unique_recipients = models.IntegerField(default=0)
    average_delivery_time = models.FloatField(default=0.0)  # in minutes
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['date']
        ordering = ['-date']

    def __str__(self):
        return f"Analytics for {self.date}"

    @property
    def delivery_rate(self):
        if self.total_sent == 0:
            return 0.0
        return (self.total_delivered / self.total_sent) * 100

    @property
    def bounce_rate(self):
        if self.total_sent == 0:
            return 0.0
        return (self.total_bounced / self.total_sent) * 100


class NotificationQueue(models.Model):
    """
    Queue for managing notification delivery order and priorities
    """
    QUEUE_STATUS = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    notification = models.OneToOneField(Notification, on_delete=models.CASCADE, related_name='queue_item')
    priority = models.IntegerField(default=5, help_text='1=Highest, 10=Lowest')
    status = models.CharField(max_length=15, choices=QUEUE_STATUS, default='PENDING')
    scheduled_for = models.DateTimeField(default=timezone.now)
    attempts = models.IntegerField(default=0)
    max_attempts = models.IntegerField(default=3)
    
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['priority', 'scheduled_for']

    def __str__(self):
        return f"Queue item for {self.notification}"


class NotificationLog(models.Model):
    """
    Detailed logging for debugging and monitoring
    """
    LOG_LEVELS = [
        ('DEBUG', 'Debug'),
        ('INFO', 'Info'),
        ('WARNING', 'Warning'),
        ('ERROR', 'Error'),
        ('CRITICAL', 'Critical'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name='logs', null=True, blank=True)
    level = models.CharField(max_length=10, choices=LOG_LEVELS)
    message = models.TextField()
    details = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['level']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.get_level_display()}: {self.message[:50]}..."