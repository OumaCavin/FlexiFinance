"""
Enhanced Notification Service with Database Tracking
Integrates with existing email services and adds comprehensive analytics
"""
import logging
import json
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.conf import settings
from django.db.models import F

from apps.notifications.models import (
    NotificationTemplate, 
    Notification, 
    UserNotificationPreference,
    NotificationAnalytics,
    NotificationQueue,
    NotificationLog
)
from apps.payments.services.resend_email_service import ResendEmailService

logger = logging.getLogger(__name__)
User = get_user_model()


class NotificationService:
    """
    Comprehensive notification service with database tracking and analytics
    """
    
    def __init__(self):
        self.email_service = ResendEmailService()
        
    def send_notification(
        self, 
        user, 
        notification_type, 
        channel='EMAIL',
        subject=None, 
        message=None, 
        html_content=None,
        priority='NORMAL',
        scheduled_for=None,
        metadata=None,
        template_name=None
    ):
        """
        Send notification with full tracking and database logging
        
        Args:
            user: User instance
            notification_type: Type of notification (from NotificationTemplate.NOTIFICATION_TYPES)
            channel: Delivery channel (EMAIL, SMS, PUSH, IN_APP)
            subject: Email subject (auto-generated from template if not provided)
            message: Message content (auto-generated from template if not provided)
            html_content: HTML content for email
            priority: Priority level (LOW, NORMAL, HIGH, URGENT)
            scheduled_for: Schedule delivery for specific time
            metadata: Additional data to store with notification
            template_name: Specific template to use
            
        Returns:
            Notification instance
        """
        try:
            # Get or create template
            template = None
            if template_name:
                template = NotificationTemplate.objects.get(name=template_name, is_active=True)
            else:
                template = NotificationTemplate.objects.filter(
                    notification_type=notification_type,
                    is_active=True
                ).first()
            
            # Generate content if not provided
            if not subject or not message:
                if template:
                    subject = subject or template.subject_template
                    message = message or template.message_template
                    html_content = html_content or template.html_template
                else:
                    raise ValidationError(f"No template found for notification type: {notification_type}")
            
            # Check user preferences
            if not self._can_send_to_user(user, notification_type, channel):
                logger.info(f"Notification blocked by user preferences: {user.email} - {notification_type}")
                return None
            
            # Create notification record
            notification = Notification.objects.create(
                template=template,
                recipient=user,
                subject=subject,
                message=message,
                html_content=html_content or '',
                channel=channel,
                priority=priority,
                scheduled_at=scheduled_for or timezone.now(),
                metadata=metadata or {}
            )
            
            # Queue for delivery
            self._queue_notification(notification)
            
            # Log the creation
            self._log_notification(
                notification, 
                'INFO', 
                f'Notification created: {notification_type} for {user.email}'
            )
            
            # Update template usage count
            if template:
                template.usage_count += 1
                template.save()
            
            return notification
            
        except Exception as e:
            logger.error(f"Failed to create notification: {str(e)}")
            self._log_notification(
                None, 
                'ERROR', 
                f'Failed to create notification: {str(e)}',
                details={'user_id': user.id, 'notification_type': notification_type}
            )
            raise
    
    def process_queue(self, batch_size=50):
        """
        Process notification queue and send pending notifications
        """
        queued_notifications = NotificationQueue.objects.filter(
            status='PENDING',
            scheduled_for__lte=timezone.now()
        ).order_by('priority', 'scheduled_for')[:batch_size]
        
        processed = 0
        for queue_item in queued_notifications:
            try:
                self._send_notification(queue_item.notification)
                queue_item.status = 'COMPLETED'
                queue_item.processed_at = timezone.now()
                queue_item.save()
                processed += 1
                
            except Exception as e:
                logger.error(f"Failed to send notification {queue_item.notification.id}: {str(e)}")
                queue_item.attempts += 1
                queue_item.status = 'FAILED' if queue_item.attempts >= queue_item.max_attempts else 'PENDING'
                queue_item.save()
        
        return processed
    
    def _send_notification(self, notification):
        """
        Send notification through appropriate channel
        """
        start_time = timezone.now()
        
        try:
            if notification.channel == 'EMAIL':
                self._send_email_notification(notification)
            elif notification.channel == 'SMS':
                self._send_sms_notification(notification)
            elif notification.channel == 'PUSH':
                self._send_push_notification(notification)
            elif notification.channel == 'IN_APP':
                self._send_in_app_notification(notification)
            else:
                raise ValueError(f"Unsupported channel: {notification.channel}")
            
            # Mark as sent
            notification.mark_sent()
            
            # Log successful delivery
            self._log_notification(
                notification, 
                'INFO', 
                f'Notification sent successfully via {notification.get_channel_display()}'
            )
            
            # Update analytics
            self._update_analytics(notification, 'sent')
            
        except Exception as e:
            # Mark as failed
            notification.mark_failed(str(e))
            
            # Log failure
            self._log_notification(
                notification, 
                'ERROR', 
                f'Notification delivery failed: {str(e)}'
            )
            
            # Update analytics
            self._update_analytics(notification, 'failed')
            
            # Schedule retry if possible
            if notification.schedule_retry():
                self._log_notification(
                    notification, 
                    'WARNING', 
                    f'Notification scheduled for retry (attempt {notification.retry_count})'
                )
            else:
                self._log_notification(
                    notification, 
                    'ERROR', 
                    f'Max retries reached for notification'
                )
            
            raise
    
    def _send_email_notification(self, notification):
        """
        Send email notification using existing email service
        """
        user = notification.recipient
        
        # Use existing ResendEmailService
        result = self.email_service.send_email(
            to_email=user.email,
            subject=notification.subject,
            html_content=notification.html_content or f"<p>{notification.message}</p>",
            text_content=notification.message
        )
        
        if result.get('success'):
            notification.mark_delivered()
        else:
            raise Exception(f"Email service failed: {result.get('error', 'Unknown error')}")
    
    def _send_sms_notification(self, notification):
        """
        Send SMS notification (placeholder for SMS service integration)
        """
        # TODO: Implement SMS service (e.g., Twilio, Africa's Talking)
        # For now, just simulate success
        notification.mark_delivered()
    
    def _send_push_notification(self, notification):
        """
        Send push notification (placeholder for push service integration)
        """
        # TODO: Implement push notification service (e.g., Firebase, OneSignal)
        # For now, just simulate success
        notification.mark_delivered()
    
    def _send_in_app_notification(self, notification):
        """
        Send in-app notification (stored in database for user session)
        """
        # In-app notifications are marked as delivered immediately
        # They will be displayed when user logs in
        notification.mark_delivered()
    
    def _queue_notification(self, notification):
        """
        Add notification to delivery queue
        """
        priority_map = {'URGENT': 1, 'HIGH': 3, 'NORMAL': 5, 'LOW': 8}
        priority = priority_map.get(notification.priority, 5)
        
        NotificationQueue.objects.create(
            notification=notification,
            priority=priority,
            scheduled_for=notification.scheduled_at
        )
    
    def _can_send_to_user(self, user, notification_type, channel):
        """
        Check if user allows notifications of this type and channel
        """
        try:
            preferences = user.notification_preferences
            
            # Check if user has disabled notifications for this channel
            if channel == 'EMAIL' and not preferences.email_notifications:
                return False
            elif channel == 'SMS' and not preferences.sms_notifications:
                return False
            elif channel == 'PUSH' and not preferences.push_notifications:
                return False
            elif channel == 'IN_APP' and not preferences.in_app_notifications:
                return False
            
            # Check notification type preference
            if not preferences.get_preference(notification_type, channel):
                return False
            
            # Check quiet hours
            if self._in_quiet_hours(preferences):
                return False
            
            return True
            
        except UserNotificationPreference.DoesNotExist:
            # No preferences set, allow by default
            return True
    
    def _in_quiet_hours(self, preferences):
        """
        Check if current time is within user's quiet hours
        """
        if not preferences.quiet_hours_enabled:
            return False
        
        now = timezone.now().time()
        start = preferences.quiet_hours_start
        end = preferences.quiet_hours_end
        
        # Handle overnight quiet hours (e.g., 10 PM to 8 AM)
        if start > end:
            return now >= start or now <= end
        else:
            return start <= now <= end
    
    def _log_notification(self, notification, level, message, details=None):
        """
        Log notification event
        """
        NotificationLog.objects.create(
            notification=notification,
            level=level,
            message=message,
            details=details or {}
        )
    
    def _update_analytics(self, notification, event_type):
        """
        Update analytics for the notification event
        """
        today = timezone.now().date()
        
        analytics, created = NotificationAnalytics.objects.get_or_create(date=today)
        
        if event_type == 'sent':
            analytics.total_sent += 1
            if notification.channel == 'EMAIL':
                analytics.email_sent += 1
            elif notification.channel == 'SMS':
                analytics.sms_sent += 1
        elif event_type == 'delivered':
            analytics.total_delivered += 1
            if notification.channel == 'EMAIL':
                analytics.email_delivered += 1
            elif notification.channel == 'SMS':
                analytics.sms_delivered += 1
        elif event_type == 'failed':
            analytics.total_failed += 1
        elif event_type == 'bounced':
            analytics.total_bounced += 1
        
        # Update unique recipients
        unique_today = Notification.objects.filter(
            created_at__date=today
        ).values('recipient').distinct().count()
        analytics.unique_recipients = unique_today
        
        analytics.save()
    
    def get_notification_analytics(self, days=30):
        """
        Get analytics data for specified number of days
        """
        start_date = timezone.now().date() - timedelta(days=days)
        return NotificationAnalytics.objects.filter(
            date__gte=start_date
        ).order_by('date')
    
    def get_user_notification_history(self, user, limit=50):
        """
        Get notification history for a specific user
        """
        return Notification.objects.filter(
            recipient=user
        ).select_related('template')[:limit]
    
    def retry_failed_notifications(self, max_age_hours=24):
        """
        Retry failed notifications within the specified time window
        """
        cutoff_time = timezone.now() - timedelta(hours=max_age_hours)
        
        failed_notifications = Notification.objects.filter(
            status='FAILED',
            failed_at__gte=cutoff_time,
            retry_count__lt=models.F('max_retries')
        )
        
        retried = 0
        for notification in failed_notifications:
            if notification.schedule_retry():
                retried += 1
        
        return retried
    
    def create_default_templates(self):
        """
        Create default notification templates for common use cases
        """
        templates_data = [
            {
                'name': 'welcome_email',
                'notification_type': 'WELCOME_EMAIL',
                'channels': ['EMAIL'],
                'subject_template': 'Welcome to FlexiFinance - Your Financial Journey Starts Here',
                'message_template': 'Welcome {{user_name}}! Thank you for joining FlexiFinance. Your account has been successfully created and you can now apply for loans.',
                'html_template': '<h1>Welcome to FlexiFinance!</h1><p>Hi {{user_name}},</p><p>Thank you for joining FlexiFinance. Your account has been successfully created and you can now apply for loans.</p>',
                'priority': 5
            },
            {
                'name': 'loan_approval',
                'notification_type': 'LOAN_APPROVAL',
                'channels': ['EMAIL', 'SMS'],
                'subject_template': 'Congratulations! YouriFinance Loan Has Been Approved',
                'message_template': 'Congratulations {{ Flexuser_name}}! Your loan application for KES {{amount}} has been approved. You will receive the funds within 24 hours.',
                'html_template': '<h1>Loan Approved!</h1><p>Hi {{user_name}},</p><p>Congratulations! Your loan application for KES {{amount}} has been approved. You will receive the funds within 24 hours.</p>',
                'priority': 3
            },
            {
                'name': 'payment_confirmation',
                'notification_type': 'PAYMENT_CONFIRMATION',
                'channels': ['EMAIL', 'SMS'],
                'subject_template': 'Payment Confirmed - FlexiFinance',
                'message_template': 'Hi {{user_name}}, your payment of KES {{amount}} has been confirmed. Transaction ID: {{transaction_id}}',
                'html_template': '<h1>Payment Confirmed</h1><p>Hi {{user_name}},</p><p>Your payment of KES {{amount}} has been confirmed.</p><p>Transaction ID: {{transaction_id}}</p>',
                'priority': 4
            }
        ]
        
        created_count = 0
        for template_data in templates_data:
            if not NotificationTemplate.objects.filter(name=template_data['name']).exists():
                NotificationTemplate.objects.create(**template_data)
                created_count += 1
        
        return created_count


# Global service instance
notification_service = NotificationService()