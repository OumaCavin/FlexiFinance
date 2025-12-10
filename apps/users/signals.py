"""
User model signals for FlexiFinance
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.utils import timezone
from allauth.account.signals import email_confirmed
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def user_created_or_updated(sender, instance, created, **kwargs):
    """
    Handle user creation and updates
    """
    if created:
        logger.info(f"New user created: {instance.username} ({instance.email})")
        
        # Send welcome email (async task would be ideal)
        # send_welcome_email.delay(instance.id)
        
    else:
        logger.debug(f"User updated: {instance.username}")


@receiver(post_save, sender=User)
def update_user_stats(sender, instance, **kwargs):
    """
    Update user statistics after certain actions
    """
    if hasattr(instance, '_update_stats') and instance._update_stats:
        # This would be called when loans are created/updated
        from apps.loans.models import Loan
        
        # Update total loans count
        instance.total_loans_taken = Loan.objects.filter(user=instance).count()
        
        # Update active loans count
        instance.active_loans_count = Loan.objects.filter(
            user=instance, 
            status__in=['APPROVED', 'ACTIVE']
        ).count()
        
        instance.save(update_fields=['total_loans_taken', 'active_loans_count'])


@receiver(email_confirmed)
def mark_user_verified_on_email_confirmation(sender, request, email_address, **kwargs):
    """
    Mark user as verified when email is confirmed through AllAuth
    """
    try:
        user = email_address.user
        logger.info(f"Marking user {user.username} as verified after email confirmation")
        
        # Update user verification status
        user.mark_verified()  # This sets is_verified=True and verification_date
        
        # Also set KYC status to approved since email is verified
        if user.kyc_status == 'PENDING':
            user.set_kyc_status('APPROVED')
            logger.info(f"Updated KYC status to APPROVED for user {user.username}")
        
        logger.info(f"User {user.username} successfully verified via email confirmation")
        
    except Exception as e:
        logger.error(f"Error marking user verified on email confirmation: {e}")