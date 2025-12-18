"""
User model signals for FlexiFinance
Email verification and KYC workflow
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
import secrets
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
        
        # Generate email verification token
        instance.email_verification_token = secrets.token_urlsafe(32)
        instance.email_verification_sent_at = timezone.now()
        instance.save(update_fields=['email_verification_token', 'email_verification_sent_at'])
        
        # Send verification email
        send_verification_email(instance)
        
        logger.info(f"Email verification sent to {instance.email}")
        
    else:
        # Check if this is a profile update (not just authentication-related changes)
        if hasattr(instance, '_profile_update') and instance._profile_update:
            logger.info(f"Profile updated for user: {instance.username}")
            send_profile_update_notification(instance, instance._updated_fields)
            # Clean up the temporary attribute
            delattr(instance, '_profile_update')
            if hasattr(instance, '_updated_fields'):
                delattr(instance, '_updated_fields')
        else:
            logger.debug(f"User updated: {instance.username}")


@receiver(post_save, sender=User)
def profile_update_detector(sender, instance, created, **kwargs):
    """
    Detect profile field updates and prepare for notification
    This runs before the main user_created_or_updated handler
    """
    if not created:
        # Get the list of fields that were updated
        updated_fields = kwargs.get('update_fields', [])
        
        # Define profile-related fields
        profile_fields = {
            'first_name', 'middle_name', 'last_name', 'date_of_birth', 'national_id',
            'phone_number', 'address', 'city', 'county', 'country',
            'occupation', 'employer_name', 'monthly_income', 'employment_duration',
            'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship'
        }
        
        # Check if any profile fields were updated
        if updated_fields and any(field in profile_fields for field in updated_fields):
            # Store info for the main handler
            instance._profile_update = True
            instance._updated_fields = [field for field in updated_fields if field in profile_fields]
            logger.info(f"Profile fields updated for {instance.username}: {instance._updated_fields}")


def send_profile_update_notification(user, updated_fields):
    """
    Send email notification when user profile is updated
    """
    try:
        # Map field names to display names
        field_display_names = {
            'first_name': 'First Name',
            'middle_name': 'Middle Name', 
            'last_name': 'Last Name',
            'date_of_birth': 'Date of Birth',
            'national_id': 'National ID',
            'phone_number': 'Phone Number',
            'address': 'Address',
            'city': 'City',
            'county': 'County',
            'country': 'Country',
            'occupation': 'Occupation',
            'employer_name': 'Employer Name',
            'monthly_income': 'Monthly Income',
            'employment_duration': 'Employment Duration',
            'emergency_contact_name': 'Emergency Contact Name',
            'emergency_contact_phone': 'Emergency Contact Phone',
            'emergency_contact_relationship': 'Emergency Contact Relationship'
        }
        
        # Get updated field display names
        updated_display_fields = [field_display_names.get(field, field) for field in updated_fields]
        
        # Prepare email context
        context = {
            'user': user,
            'updated_fields': updated_display_fields,
            'first_name': user.first_name or user.username,
            'site_name': 'FlexiFinance',
            'profile_url': 'http://127.0.0.1:8000/dashboard/profile/',
            'update_time': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
        }
        
        # Render email templates
        subject = render_to_string('emails/profile_update_subject.txt', context).strip()
        html_message = render_to_string('emails/profile_update_email.html', context)
        text_message = render_to_string('emails/profile_update_email.txt', context)
        
        # Send email
        send_mail(
            subject=subject,
            message=text_message,
            from_email=None,  # Use default from email
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Profile update notification sent to {user.email} for fields: {updated_fields}")
        
    except Exception as e:
        logger.error(f"Error sending profile update notification to {user.email}: {str(e)}")


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


def send_verification_email(user):
    """
    Send email verification to user
    """
    try:
        # Generate verification URL - use correct URL name with namespace
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = user.email_verification_token
        
        logger.info(f"Generating verification URL for user {user.username}")
        logger.info(f"User ID (encoded): {uid}")
        logger.info(f"Token: {token[:10]}...")
        
        verification_url = reverse('dashboard:verify_email', kwargs={'uidb64': uid, 'token': token})
        full_verification_url = f"http://127.0.0.1:8000{verification_url}"
        
        logger.info(f"Generated verification URL: {full_verification_url}")
        
        # Prepare email context
        context = {
            'user': user,
            'verification_url': full_verification_url,
            'first_name': user.first_name or user.username,
            'site_name': 'FlexiFinance',
        }
        
        # Render email templates
        subject = render_to_string('emails/verification_subject.txt', context).strip()
        html_message = render_to_string('emails/verification_email.html', context)
        text_message = render_to_string('emails/verification_email.txt', context)
        
        # Send email
        send_mail(
            subject=subject,
            message=text_message,
            from_email=None,  # Use default from email
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Verification email sent successfully to {user.email}")
        
    except Exception as e:
        logger.error(f"Error sending verification email to {user.email}: {str(e)}")


def mark_user_verified(user, verified_by='email_verification'):
    """
    Mark user as verified and update KYC status
    """
    try:
        logger.info(f"Marking user {user.username} as verified via {verified_by}")
        
        # Update user verification status
        user.mark_verified()  # This sets is_verified=True and verification_date
        
        # Also set KYC status to approved since email is verified
        if user.kyc_status == 'PENDING':
            user.set_kyc_status('APPROVED', reviewed_by=None)
            logger.info(f"Updated KYC status to APPROVED for user {user.username}")
        
        # Clear verification token
        user.email_verification_token = ''
        user.save(update_fields=['is_verified', 'verification_date', 'kyc_status', 'email_verification_token'])
        
        logger.info(f"User {user.username} successfully verified and KYC approved")
        
    except Exception as e:
        logger.error(f"Error marking user verified: {str(e)}")
        raise