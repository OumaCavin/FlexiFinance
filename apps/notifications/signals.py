"""
Django Signals for Notification System
Automatically handles user preferences and notification events
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from apps.notifications.models import UserNotificationPreference, Notification
from apps.notifications.services.notification_service import notification_service

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_notification_preferences(sender, instance, created, **kwargs):
    """
    Automatically create notification preferences for new users
    """
    if created:
        UserNotificationPreference.objects.get_or_create(user=instance)
        
        # Send welcome notification
        try:
            notification_service.send_notification(
                user=instance,
                notification_type='WELCOME_EMAIL',
                channel='EMAIL',
                template_name='welcome_email'
            )
        except Exception as e:
            # Log error but don't fail user creation
            print(f"Failed to send welcome notification: {e}")


@receiver(post_save, sender=Notification)
def update_notification_metrics(sender, instance, created, **kwargs):
    """
    Update metrics when notifications are created or status changes
    """
    if not created:
        # Update analytics when notification status changes
        if instance.status == 'DELIVERED':
            notification_service._update_analytics(instance, 'delivered')
        elif instance.status == 'FAILED':
            notification_service._update_analytics(instance, 'failed')
        elif instance.status == 'BOUNCED':
            notification_service._update_analytics(instance, 'bounced')


# Signal configuration
def setup_notification_signals():
    """
    Connect all notification signals
    """
    pass  # Signals are connected via decorators above