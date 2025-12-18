"""
Web views for FlexiFinance Users
User dashboard and authentication views
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout, update_session_auth_hash, login, get_user_model
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views import View
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.db import models
from apps.users.forms import (
    UserProfileForm, UserCreationForm,
    IdentityForm, ContactForm, EmploymentForm, EmergencyContactForm
)
from .signals import mark_user_verified
import logging

User = get_user_model()

logger = logging.getLogger(__name__)

@login_required
def dashboard(request):
    """User dashboard view"""
    from apps.loans.models import Loan
    from apps.payments.models import Payment
    from django.utils import timezone
    
    # Get user's loans
    user_loans = Loan.objects.filter(user=request.user)
    
    # Calculate dashboard statistics
    active_loans = user_loans.filter(status__in=['APPROVED', 'DISBURSED', 'ACTIVE']).count()
    total_borrowed = user_loans.filter(status__in=['APPROVED', 'DISBURSED', 'ACTIVE', 'COMPLETED']).aggregate(
        total=models.Sum('principal_amount')
    )['total'] or 0
    
    # Calculate current balance (total borrowed - total paid)
    total_paid = Payment.objects.filter(
        user=request.user,
        status='COMPLETED'
    ).aggregate(paid=models.Sum('amount'))['paid'] or 0
    
    current_balance = max(0, total_borrowed - total_paid)
    
    # Calculate credit score (simplified logic)
    approved_loans = user_loans.filter(status__in=['APPROVED', 'DISBURSED', 'ACTIVE', 'COMPLETED']).count()
    rejected_loans = user_loans.filter(status='REJECTED').count()
    
    # Simple credit score calculation (300-850 range)
    base_score = 300
    if approved_loans > 0:
        score = min(850, base_score + (approved_loans * 100) - (rejected_loans * 50))
    else:
        score = base_score + 100  # New user gets base score
    
    credit_score_percentage = round((score - 300) / 550 * 100)
    
    # Get recent activities (last 5 loan activities)
    recent_activities = []
    
    # Recent loan applications
    recent_loans = user_loans.order_by('-created_at')[:3]
    for loan in recent_loans:
        time_diff = timezone.now() - loan.created_at
        if time_diff.days == 0:
            time_str = f"{time_diff.seconds // 3600}h ago" if time_diff.seconds >= 3600 else f"{time_diff.seconds // 60}m ago"
        else:
            time_str = f"{time_diff.days}d ago"
        
        recent_activities.append({
            'type': 'loan_application',
            'title': f'Loan Application {loan.get_status_display()}',
            'description': f'Applied for KES {loan.principal_amount} - {loan.get_loan_type_display()}',
            'time': time_str,
            'icon': 'fa-file-alt' if loan.status == 'SUBMITTED' else 'fa-check-circle' if loan.status in ['APPROVED', 'DISBURSED'] else 'fa-times-circle',
            'color': 'primary' if loan.status == 'SUBMITTED' else 'success' if loan.status in ['APPROVED', 'DISBURSED'] else 'danger'
        })
    
    # Recent payments
    recent_payments = Payment.objects.filter(user=request.user).order_by('-created_at')[:2]
    for payment in recent_payments:
        time_diff = timezone.now() - payment.created_at
        if time_diff.days == 0:
            time_str = f"{time_diff.seconds // 3600}h ago" if time_diff.seconds >= 3600 else f"{time_diff.seconds // 60}m ago"
        else:
            time_str = f"{time_diff.days}d ago"
        
        recent_activities.append({
            'type': 'payment',
            'title': f'Payment {payment.get_status_display()}',
            'description': f'Paid KES {payment.amount} - {payment.payment_method}',
            'time': time_str,
            'icon': 'fa-credit-card',
            'color': 'success' if payment.status == 'COMPLETED' else 'warning'
        })
    
    # Sort all activities by time
    recent_activities = sorted(recent_activities, key=lambda x: x['time'], reverse=True)[:5]
    
    # Generate notifications
    notifications = []
    
    # Loan status notifications
    pending_loans = user_loans.filter(status__in=['SUBMITTED', 'UNDER_REVIEW'])
    if pending_loans.exists():
        notifications.append({
            'type': 'info',
            'title': 'Loan Under Review',
            'message': f'You have {pending_loans.count()} loan application(s) under review',
            'time': 'Recently',
            'icon': 'fa-info-circle'
        })
    
    # Payment reminders for overdue schedules
    from apps.payments.models import PaymentSchedule
    overdue_schedules = PaymentSchedule.objects.filter(
        payment__user=request.user,
        status='PENDING',
        due_date__lt=timezone.now().date()
    )
    if overdue_schedules.exists():
        notifications.append({
            'type': 'warning',
            'title': 'Overdue Payment',
            'message': f'You have {overdue_schedules.count()} overdue payment(s)',
            'time': 'Today',
            'icon': 'fa-exclamation-triangle'
        })
    
    # Welcome notification for new users with no activity
    if not recent_loans.exists() and not recent_payments.exists():
        notifications.append({
            'type': 'success',
            'title': 'Welcome to FlexiFinance',
            'message': 'Start your first loan application today!',
            'time': 'Today',
            'icon': 'fa-star'
        })
    
    context = {
        'user': request.user,
        'page_title': 'Dashboard',
        'stats': {
            'current_balance': current_balance,
            'credit_score': credit_score_percentage,
            'total_borrowed': total_borrowed,
            'active_loans': active_loans
        },
        'recent_activities': recent_activities,
        'notifications': notifications
    }
    return render(request, 'users/dashboard.html', context)

@login_required
def profile(request):
    """User profile view with comprehensive form handling"""
    user = request.user
    
    # Initialize all forms with user instance
    identity_form = IdentityForm(instance=user)
    contact_form = ContactForm(instance=user)
    employment_form = EmploymentForm(instance=user)
    emergency_form = EmergencyContactForm(instance=user)
    profile_form = UserProfileForm(instance=user)

    if request.method == 'POST':
        logger.info(f"Profile form submitted with method: {request.method}")
        logger.info(f"POST data keys: {list(request.POST.keys())}")
        
        form_type = request.POST.get('form_type')
        logger.info(f"Form type from POST: {form_type}")
        
        # Process the submitted form based on form_type
        # Keep track of which form was processed for proper context handling
        processed_form = None
        
        if form_type == 'identity':
            logger.info("Processing identity form")
            logger.info(f"POST data for identity: {dict(request.POST)}")
            
            # Debug: Log current user state before form processing
            logger.info(f"Current user state before form: first_name={user.first_name}, last_name={user.last_name}")
            
            identity_form = IdentityForm(request.POST, instance=user)
            logger.info(f"Identity form instantiated. is_valid: {identity_form.is_valid()}")
            
            if identity_form.is_valid():
                try:
                    logger.info("Identity form is valid, attempting to save...")
                    
                    # Mark this as a profile update for signal handling
                    user._profile_update = True
                    user._updated_fields = ['first_name', 'middle_name', 'last_name', 'date_of_birth', 'national_id']
                    
                    # Save the form
                    saved_user = identity_form.save()
                    logger.info(f"Identity form saved successfully!")
                    
                    # Debug: Check the saved data
                    saved_user.refresh_from_db()
                    logger.info(f"User data after save: first_name={saved_user.first_name}, last_name={saved_user.last_name}")
                    
                    messages.success(request, 'Identity information updated successfully!')
                    logger.info(f"Identity form saved successfully. User data: first_name={saved_user.first_name}, last_name={saved_user.last_name}")
                    
                    # Check if this is an AJAX request
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'status': 'success',
                            'message': 'Identity information updated successfully!',
                            'form_type': 'identity'
                        })
                    
                    return redirect('dashboard:profile')
                except Exception as e:
                    logger.error(f"Error updating identity: {str(e)}", exc_info=True)
                    messages.error(request, f'An error occurred while saving identity information: {str(e)}')
            else:
                logger.error(f"Identity form validation failed: {identity_form.errors}")
                logger.error(f"Form data: {identity_form.data}")
                messages.error(request, f'Please correct the errors in Identity Details')
                
                # Check if this is an AJAX request
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Please correct the errors in Identity Details',
                        'errors': identity_form.errors,
                        'form_type': 'identity'
                    })
                
                processed_form = 'identity'  # Mark as processed to keep form data
        
        elif form_type == 'contact':
            logger.info("Processing contact form")
            logger.info(f"POST data for contact: {dict(request.POST)}")
            
            # Debug: Log current user state before form processing
            logger.info(f"Current user state before form: phone_number={user.phone_number}, city={user.city}")
            
            contact_form = ContactForm(request.POST, instance=user)
            logger.info(f"Contact form instantiated. is_valid: {contact_form.is_valid()}")
            
            if contact_form.is_valid():
                try:
                    logger.info("Contact form is valid, attempting to save...")
                    
                    # Mark this as a profile update for signal handling
                    user._profile_update = True
                    user._updated_fields = ['phone_number', 'address', 'city', 'county', 'country']
                    
                    # Save the form
                    saved_user = contact_form.save()
                    logger.info(f"Contact form saved successfully!")
                    
                    # Debug: Check the saved data
                    saved_user.refresh_from_db()
                    logger.info(f"User data after save: phone_number={saved_user.phone_number}, city={saved_user.city}")
                    
                    messages.success(request, 'Contact information updated successfully!')
                    logger.info(f"Contact form saved successfully. User data: phone_number={saved_user.phone_number}, city={saved_user.city}")
                    
                    # Check if this is an AJAX request
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'status': 'success',
                            'message': 'Contact information updated successfully!',
                            'form_type': 'contact'
                        })
                    
                    return redirect('dashboard:profile')
                except Exception as e:
                    logger.error(f"Error updating contact: {str(e)}", exc_info=True)
                    messages.error(request, f'An error occurred while saving contact information: {str(e)}')
            else:
                logger.error(f"Contact form validation failed: {contact_form.errors}")
                logger.error(f"Form data: {contact_form.data}")
                messages.error(request, f'Please correct the errors in Contact Information')
                
                # Check if this is an AJAX request
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Please correct the errors in Contact Information',
                        'errors': contact_form.errors,
                        'form_type': 'contact'
                    })
                
                processed_form = 'contact'  # Mark as processed to keep form data
        
        elif form_type == 'employment':
            logger.info("Processing employment form")
            logger.info(f"POST data for employment: {dict(request.POST)}")
            employment_form = EmploymentForm(request.POST, instance=user)
            
            if employment_form.is_valid():
                try:
                    # Mark this as a profile update for signal handling
                    user._profile_update = True
                    user._updated_fields = ['occupation', 'employer_name', 'monthly_income', 'employment_duration']
                    
                    employment_form.save()
                    messages.success(request, 'Employment information updated successfully!')
                    logger.info(f"Employment form saved successfully. User data: occupation={user.occupation}, monthly_income={user.monthly_income}")
                    
                    # Check if this is an AJAX request
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'status': 'success',
                            'message': 'Employment information updated successfully!',
                            'form_type': 'employment'
                        })
                    
                    return redirect('dashboard:profile')
                except Exception as e:
                    logger.error(f"Error updating employment: {str(e)}", exc_info=True)
                    messages.error(request, f'An error occurred while saving employment information: {str(e)}')
            else:
                logger.error(f"Employment form validation failed: {employment_form.errors}")
                logger.error(f"Form data: {employment_form.data}")
                messages.error(request, f'Please correct the errors in Employment & Financials')
                
                # Check if this is an AJAX request
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Please correct the errors in Employment & Financials',
                        'errors': employment_form.errors,
                        'form_type': 'employment'
                    })
                
                processed_form = 'employment'  # Mark as processed to keep form data
        
        elif form_type == 'emergency':
            logger.info("Processing emergency contact form")
            logger.info(f"POST data for emergency: {dict(request.POST)}")
            emergency_form = EmergencyContactForm(request.POST, instance=user)
            
            if emergency_form.is_valid():
                try:
                    # Mark this as a profile update for signal handling
                    user._profile_update = True
                    user._updated_fields = ['emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship']
                    
                    emergency_form.save()
                    messages.success(request, 'Emergency contact information updated successfully!')
                    logger.info(f"Emergency form saved successfully. User data: emergency_contact_name={user.emergency_contact_name}")
                    
                    # Check if this is an AJAX request
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'status': 'success',
                            'message': 'Emergency contact information updated successfully!',
                            'form_type': 'emergency'
                        })
                    
                    return redirect('dashboard:profile')
                except Exception as e:
                    logger.error(f"Error updating emergency contact: {str(e)}", exc_info=True)
                    messages.error(request, f'An error occurred while saving emergency contact: {str(e)}')
            else:
                logger.error(f"Emergency form validation failed: {emergency_form.errors}")
                logger.error(f"Form data: {emergency_form.data}")
                messages.error(request, f'Please correct the errors in Emergency Contact')
                
                # Check if this is an AJAX request
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Please correct the errors in Emergency Contact',
                        'errors': emergency_form.errors,
                        'form_type': 'emergency'
                    })
                
                processed_form = 'emergency'  # Mark as processed to keep form data
        
        elif form_type == 'personal':
            logger.info("Processing personal profile form")
            profile_form = UserProfileForm(request.POST, instance=user)
            
            if profile_form.is_valid():
                try:
                    profile_form.save()
                    messages.success(request, 'Profile information updated successfully!')
                    return redirect('dashboard:profile')
                except Exception as e:
                    logger.error(f"Error updating profile: {str(e)}", exc_info=True)
                    messages.error(request, f'An error occurred while saving your profile: {str(e)}')
            else:
                messages.error(request, 'Please correct the errors below.')
                logger.info(f"Profile form errors: {profile_form.errors}")
        
        elif form_type == 'password':
            # Handle password change
            current_password = request.POST.get('current_password', '')
            new_password = request.POST.get('new_password', '')
            confirm_password = request.POST.get('confirm_password', '')
            
            # Validation
            if not current_password:
                messages.error(request, 'Current password is required.')
            elif not new_password:
                messages.error(request, 'New password is required.')
            elif new_password != confirm_password:
                messages.error(request, 'New passwords do not match.')
            elif len(new_password) < 8:
                messages.error(request, 'Password must be at least 8 characters long.')
            elif not user.check_password(current_password):
                messages.error(request, 'Current password is incorrect.')
            else:
                try:
                    user.set_password(new_password)
                    user.save()
                    # Important: Keep the user logged in after password change
                    update_session_auth_hash(request, user)
                    messages.success(request, 'Password updated successfully!')
                    return redirect('dashboard:profile')
                except Exception as e:
                    logger.error(f"Error updating password: {str(e)}")
                    messages.error(request, f'Error updating password: {str(e)}')
        
        # If no form_type specified or processing failed, re-render forms with current data
        else:
            logger.warning(f"Unknown form_type: {form_type}")
            messages.error(request, 'Invalid form submission. Please try again.')
    
    # Always refresh user data to ensure we have the latest information
    user.refresh_from_db()
    
    # Initialize all forms with current user data first
    identity_form = IdentityForm(instance=user)
    contact_form = ContactForm(instance=user)
    employment_form = EmploymentForm(instance=user)
    emergency_form = EmergencyContactForm(instance=user)
    
    # Handle form data preservation when validation fails
    # Keep the form that failed validation with its POST data, use current user data for others
    if request.method == 'POST' and processed_form:
        logger.info(f"Preserving form data for failed form: {processed_form}")
        # If a form was processed (failed validation), preserve that form's data
        if processed_form == 'identity':
            identity_form = identity_form  # Keep the form with POST data
        else:
            identity_form = IdentityForm(instance=user)
            
        if processed_form == 'contact':
            contact_form = contact_form  # Keep the form with POST data
        else:
            contact_form = ContactForm(instance=user)
            
        if processed_form == 'employment':
            employment_form = employment_form  # Keep the form with POST data
        else:
            employment_form = EmploymentForm(instance=user)
            
        if processed_form == 'emergency':
            emergency_form = emergency_form  # Keep the form with POST data
        else:
            emergency_form = EmergencyContactForm(instance=user)
    else:
        # No form was processed or GET request - use fresh user data for all forms
        identity_form = IdentityForm(instance=user)
        contact_form = ContactForm(instance=user)
        employment_form = EmploymentForm(instance=user)
        emergency_form = EmergencyContactForm(instance=user)
    
    profile_form = UserProfileForm(instance=user)
    
    context = {
        'user': user,
        'profile_form': profile_form,  # Keep for backward compatibility
        'identity_form': identity_form,
        'contact_form': contact_form,
        'employment_form': employment_form,
        'emergency_form': emergency_form,
        'page_title': 'Profile'
    }
    return render(request, 'users/profile.html', context)

@login_required
def update_kyc_status(request):
    """Admin function to update KYC status - for testing purposes"""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('dashboard:profile')
    
    if request.method == 'POST':
        new_status = request.POST.get('kyc_status')
        user_id = request.POST.get('user_id')
        
        try:
            from apps.users.models import User
            target_user = User.objects.get(id=user_id)
            target_user.set_kyc_status(new_status, reviewed_by=request.user)
            messages.success(request, f'KYC status for {target_user.username} updated to {new_status}.')
        except User.DoesNotExist:
            messages.error(request, 'User not found.')
        except Exception as e:
            messages.error(request, f'Error updating KYC status: {str(e)}')
    
    return redirect('dashboard:profile')

@login_required
def my_loans(request):
    """User loans view"""
    from apps.loans.models import Loan
    
    # Query loans for the current user
    user_loans = Loan.objects.filter(user=request.user).order_by('-created_at')
    
    # Calculate statistics
    total_applications = user_loans.count()
    approved = user_loans.filter(status__in=['APPROVED', 'DISBURSED', 'ACTIVE', 'COMPLETED']).count()
    pending = user_loans.filter(status__in=['DRAFT', 'SUBMITTED', 'UNDER_REVIEW']).count()
    rejected = user_loans.filter(status='REJECTED').count()
    
    context = {
        'user': request.user,
        'page_title': 'My Loans',
        'loans': user_loans,
        'stats': {
            'total_applications': total_applications,
            'approved': approved,
            'pending': pending,
            'rejected': rejected
        }
    }
    return render(request, 'users/my_loans.html', context)

@login_required
def payment_history(request):
    """User payment history view"""
    from apps.payments.models import Payment
    
    # Get user's payments
    user_payments = Payment.objects.filter(user=request.user).order_by('-created_at')
    
    # Calculate statistics
    total_payments = user_payments.count()
    successful_payments = user_payments.filter(status='COMPLETED').count()
    total_amount = user_payments.filter(status='COMPLETED').aggregate(
        total=models.Sum('amount')
    )['total'] or 0
    
    context = {
        'user': request.user,
        'page_title': 'Payment History',
        'payments': user_payments[:20],  # Show last 20 payments
        'stats': {
            'total_payments': total_payments,
            'successful_payments': successful_payments,
            'total_amount': total_amount
        }
    }
    return render(request, 'users/payment_history.html', context)

@require_http_methods(["POST"])
def logout_view(request):
    """Handle user logout"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('core:home')

# Removed custom login_view - Django built-in auth handles this automatically
# The login functionality is now handled by django.contrib.auth.urls

def register_view(request):
    """User registration view with form handling"""
    if request.user.is_authenticated:
        return redirect('dashboard:dashboard')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Don't log user in automatically - they need to verify email first
            messages.success(
                request, 
                'Account created successfully! Please check your email to verify your account before logging in.'
            )
            return redirect('core:home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserCreationForm()
    
    context = {
        'form': form,
        'page_title': 'Register'
    }
    return render(request, 'users/register.html', context)


def handle_unverified_user_login(request, user):
    """
    Handle login for unverified users - send verification email
    """
    logger = logging.getLogger(__name__)
    
    # Check if user needs verification
    if not user.is_verified:
        logger.info(f"Unverified user {user.username} logged in, sending verification email")
        
        # Generate verification token if missing
        if not user.email_verification_token:
            from django.utils import timezone
            import secrets
            
            user.email_verification_token = secrets.token_urlsafe(32)
            user.email_verification_sent_at = timezone.now()
            user.save(update_fields=['email_verification_token', 'email_verification_sent_at'])
            logger.info(f"Generated verification token for {user.username}")
        
        # Send verification email
        try:
            from apps.users.signals import send_verification_email
            logger.info(f"Attempting to send verification email to {user.email}")
            send_verification_email(user)
            
            messages.warning(
                request,
                'Please verify your email address to unlock all features. '
                'A verification email has been sent to your inbox.'
            )
            logger.info(f"Verification email sent successfully to {user.email}")
            
        except ImportError as e:
            logger.error(f"Import error sending verification email: {str(e)}")
            messages.error(request, f'Email system error. Please contact support.')
        except Exception as e:
            logger.error(f"Error sending verification email to {user.email}: {str(e)}", exc_info=True)
            messages.error(request, f'Error sending verification email: {str(e)}. Please contact support.')
            
        return redirect('core:home')
    
    # User is verified, proceed normally
    return redirect('dashboard:dashboard')


def custom_login_view(request):
    """
    Custom login view that handles unverified users
    """
    from django.contrib.auth import authenticate, login
    from django.contrib.auth.forms import AuthenticationForm
    
    logger = logging.getLogger(__name__)
    
    if request.user.is_authenticated:
        logger.info(f"User {request.user.username} already authenticated, redirecting to dashboard")
        return redirect('dashboard:dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            logger.info(f"Attempting authentication for username: {username}")
            
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                logger.info(f"Authentication successful for {username}")
                login(request, user)
                
                # Check if user is verified
                if not user.is_verified:
                    logger.info(f"User {username} is unverified, calling handle_unverified_user_login")
                    return handle_unverified_user_login(request, user)
                else:
                    logger.info(f"User {username} is verified, redirecting to dashboard")
                    return redirect('dashboard:dashboard')
            else:
                logger.warning(f"Authentication failed for username: {username}")
        else:
            logger.info(f"Form validation errors: {form.errors}")
    else:
        form = AuthenticationForm(request)
    
    context = {
        'form': form,
        'page_title': 'Login'
    }
    return render(request, 'registration/login.html', context)


class EmailVerificationView(View):
    """
    Handle email verification for new users
    """
    
    def get(self, request, uidb64, token):
        """
        Verify email address and activate account
        """
        try:
            # Decode the user ID
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
            
        if user is not None and token == user.email_verification_token:
            # Verify the user
            mark_user_verified(user, verified_by='email_verification_link')
            
            messages.success(
                request, 
                'Email verified successfully! Your account is now fully activated and KYC approved.'
            )
            
            # Log the user in automatically
            login(request, user)
            
            return redirect('dashboard:dashboard')
            
        else:
            messages.error(
                request, 
                'Verification link is invalid or has expired. Please request a new verification email.'
            )
            
            return redirect('core:home')


def resend_verification_email(request):
    """
    Resend verification email to user
    """
    if request.method == 'POST':
        email = request.POST.get('email')
        
        try:
            user = User.objects.get(email=email)
            
            if user.is_verified:
                messages.info(request, 'This email address is already verified.')
                return redirect('core:home')
            
            # Generate new token and send email
            from .signals import send_verification_email
            send_verification_email(user)
            
            messages.success(request, 'Verification email sent successfully! Please check your inbox.')
            
        except User.DoesNotExist:
            messages.error(request, 'No account found with this email address.')
            
        except Exception as e:
            messages.error(request, f'Error sending verification email: {str(e)}')
            
    return redirect('core:home')


def test_profile_forms(request):
    """
    Test endpoint for debugging profile forms functionality
    """
    if not request.user.is_authenticated:
        return redirect('login')
    
    user = request.user
    
    # Initialize forms with user data
    identity_form = IdentityForm(instance=user)
    contact_form = ContactForm(instance=user)
    employment_form = EmploymentForm(instance=user)
    emergency_form = EmergencyContactForm(instance=user)
    
    # Test data
    test_results = []
    
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        
        if form_type == 'identity':
            logger.info(f"Processing identity form. POST data: {dict(request.POST)}")
            identity_form = IdentityForm(request.POST, instance=user)
            if identity_form.is_valid():
                logger.info("Identity form is valid, saving...")
                saved_user = identity_form.save()
                user.refresh_from_db()
                test_results.append("✅ Identity form validation and save successful!")
                test_results.append(f"Data after save - First name: {user.first_name}, Last name: {user.last_name}")
                identity_form = IdentityForm(instance=user)  # Refresh form
            else:
                logger.error(f"Identity form errors: {identity_form.errors}")
                test_results.append(f"❌ Identity form errors: {identity_form.errors}")
        
        elif form_type == 'contact':
            logger.info(f"Processing contact form. POST data: {dict(request.POST)}")
            contact_form = ContactForm(request.POST, instance=user)
            if contact_form.is_valid():
                logger.info("Contact form is valid, saving...")
                saved_user = contact_form.save()
                user.refresh_from_db()
                test_results.append("✅ Contact form validation and save successful!")
                test_results.append(f"Data after save - Phone: {user.phone_number}, City: {user.city}")
                contact_form = ContactForm(instance=user)  # Refresh form
            else:
                logger.error(f"Contact form errors: {contact_form.errors}")
                test_results.append(f"❌ Contact form errors: {contact_form.errors}")
        
        elif form_type == 'employment':
            logger.info(f"Processing employment form. POST data: {dict(request.POST)}")
            employment_form = EmploymentForm(request.POST, instance=user)
            if employment_form.is_valid():
                logger.info("Employment form is valid, saving...")
                saved_user = employment_form.save()
                user.refresh_from_db()
                test_results.append("✅ Employment form validation and save successful!")
                test_results.append(f"Data after save - Occupation: {user.occupation}, Income: {user.monthly_income}")
                employment_form = EmploymentForm(instance=user)  # Refresh form
            else:
                logger.error(f"Employment form errors: {employment_form.errors}")
                test_results.append(f"❌ Employment form errors: {employment_form.errors}")
        
        elif form_type == 'emergency':
            logger.info(f"Processing emergency form. POST data: {dict(request.POST)}")
            emergency_form = EmergencyContactForm(request.POST, instance=user)
            if emergency_form.is_valid():
                logger.info("Emergency form is valid, saving...")
                saved_user = emergency_form.save()
                user.refresh_from_db()
                test_results.append("✅ Emergency form validation and save successful!")
                test_results.append(f"Data after save - Emergency name: {user.emergency_contact_name}")
                emergency_form = EmergencyContactForm(instance=user)  # Refresh form
            else:
                logger.error(f"Emergency form errors: {emergency_form.errors}")
                test_results.append(f"❌ Emergency form errors: {emergency_form.errors}")
    
    # Current user data
    user_data = {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'phone_number': user.phone_number,
        'occupation': user.occupation,
        'emergency_contact_name': user.emergency_contact_name
    }
    
    context = {
        'user': user,
        'identity_form': identity_form,
        'contact_form': contact_form,
        'employment_form': employment_form,
        'emergency_form': emergency_form,
        'test_results': test_results,
        'user_data': user_data,
        'page_title': 'Profile Forms Test'
    }
    
    return render(request, 'users/test_profile.html', context)


@login_required
def test_form_save(request):
    """
    Simple test endpoint to verify form saving works
    """
    user = request.user
    
    if request.method == 'POST':
        form_type = request.POST.get('form_type', 'identity')
        
        try:
            if form_type == 'identity':
                form = IdentityForm(request.POST, instance=user)
                if form.is_valid():
                    form.save()
                    messages.success(request, 'Identity form saved successfully!')
                    logger.info(f"Identity form saved successfully. User data: first_name={user.first_name}, last_name={user.last_name}")
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'status': 'success', 'message': 'Identity form saved successfully'})
                    else:
                        return redirect('dashboard:test_form_save')
                else:
                    messages.error(request, f'Identity form validation failed: {form.errors}')
                    logger.error(f"Identity form errors: {form.errors}")
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'status': 'error', 'message': 'Form validation failed', 'errors': form.errors})
                    
            elif form_type == 'contact':
                form = ContactForm(request.POST, instance=user)
                if form.is_valid():
                    form.save()
                    messages.success(request, 'Contact form saved successfully!')
                    logger.info(f"Contact form saved successfully. User data: phone_number={user.phone_number}, city={user.city}")
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'status': 'success', 'message': 'Contact form saved successfully'})
                    else:
                        return redirect('dashboard:test_form_save')
                else:
                    messages.error(request, f'Contact form validation failed: {form.errors}')
                    logger.error(f"Contact form errors: {form.errors}")
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'status': 'error', 'message': 'Form validation failed', 'errors': form.errors})
                    
            elif form_type == 'employment':
                form = EmploymentForm(request.POST, instance=user)
                if form.is_valid():
                    form.save()
                    messages.success(request, 'Employment form saved successfully!')
                    logger.info(f"Employment form saved successfully. User data: occupation={user.occupation}, monthly_income={user.monthly_income}")
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'status': 'success', 'message': 'Employment form saved successfully'})
                    else:
                        return redirect('dashboard:test_form_save')
                else:
                    messages.error(request, f'Employment form validation failed: {form.errors}')
                    logger.error(f"Employment form errors: {form.errors}")
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'status': 'error', 'message': 'Form validation failed', 'errors': form.errors})
                    
            elif form_type == 'emergency':
                form = EmergencyContactForm(request.POST, instance=user)
                if form.is_valid():
                    form.save()
                    messages.success(request, 'Emergency form saved successfully!')
                    logger.info(f"Emergency form saved successfully. User data: emergency_contact_name={user.emergency_contact_name}")
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'status': 'success', 'message': 'Emergency form saved successfully'})
                    else:
                        return redirect('dashboard:test_form_save')
                else:
                    messages.error(request, f'Emergency form validation failed: {form.errors}')
                    logger.error(f"Emergency form errors: {form.errors}")
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'status': 'error', 'message': 'Form validation failed', 'errors': form.errors})
                    
            else:
                messages.error(request, 'Unknown form type. Use: identity, contact, employment, or emergency')
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'status': 'error', 'message': 'Unknown form type. Use: identity, contact, employment, or emergency'})
                
        except Exception as e:
            logger.error(f"Test form save error: {str(e)}", exc_info=True)
            messages.error(request, f'Error saving form: {str(e)}')
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': str(e)})
    
    # GET request - render debug page
    context = {
        'user': user,
        'page_title': 'Profile Debug Test'
    }
    return render(request, 'users/debug_profile.html', context)


@login_required
def test_profile_form_submit(request):
    """
    Handle form submissions from test_profile page and redirect back to test_profile
    """
    user = request.user
    
    logger.info(f"=== TEST PROFILE FORM SUBMISSION DEBUG ===")
    logger.info(f"Request method: {request.method}")
    logger.info(f"User authenticated: {request.user.is_authenticated}")
    logger.info(f"User ID: {request.user.id if request.user.is_authenticated else 'None'}")
    
    if request.method == 'POST':
        logger.info(f"POST data received: {dict(request.POST)}")
        logger.info(f"POST data keys: {list(request.POST.keys())}")
        logger.info(f"CSRF token present: {'csrfmiddlewaretoken' in request.POST}")
        
        form_type = request.POST.get('form_type', 'identity')
        logger.info(f"Form type extracted: {form_type}")
        
        try:
            if form_type == 'identity':
                logger.info("Creating IdentityForm with POST data...")
                form = IdentityForm(request.POST, instance=user)
                logger.info(f"IdentityForm created. is_valid: {form.is_valid()}")
                
                if form.is_valid():
                    logger.info("IdentityForm is valid, calling save()...")
                    saved_user = form.save()
                    logger.info("IdentityForm.save() completed successfully")
                    
                    # Force refresh from database
                    user.refresh_from_db()
                    logger.info(f"User refreshed from DB: first_name={user.first_name}, last_name={user.last_name}")
                    
                    messages.success(request, 'Identity form saved successfully!')
                    logger.info(f"Success message added. User data: first_name={user.first_name}, last_name={user.last_name}")
                else:
                    logger.error(f"IdentityForm validation failed!")
                    logger.error(f"Form errors: {form.errors}")
                    logger.error(f"Form non_field_errors: {form.non_field_errors}")
                    messages.error(request, f'Identity form validation failed: {form.errors}')
                    
            elif form_type == 'contact':
                logger.info("Creating ContactForm with POST data...")
                form = ContactForm(request.POST, instance=user)
                logger.info(f"ContactForm created. is_valid: {form.is_valid()}")
                
                if form.is_valid():
                    logger.info("ContactForm is valid, calling save()...")
                    saved_user = form.save()
                    logger.info("ContactForm.save() completed successfully")
                    
                    user.refresh_from_db()
                    logger.info(f"User refreshed from DB: phone_number={user.phone_number}, city={user.city}")
                    
                    messages.success(request, 'Contact form saved successfully!')
                    logger.info(f"Success message added. User data: phone_number={user.phone_number}, city={user.city}")
                else:
                    logger.error(f"ContactForm validation failed!")
                    logger.error(f"Form errors: {form.errors}")
                    logger.error(f"Form non_field_errors: {form.non_field_errors}")
                    messages.error(request, f'Contact form validation failed: {form.errors}')
                    
            elif form_type == 'employment':
                logger.info("Creating EmploymentForm with POST data...")
                form = EmploymentForm(request.POST, instance=user)
                logger.info(f"EmploymentForm created. is_valid: {form.is_valid()}")
                
                if form.is_valid():
                    logger.info("EmploymentForm is valid, calling save()...")
                    saved_user = form.save()
                    logger.info("EmploymentForm.save() completed successfully")
                    
                    user.refresh_from_db()
                    logger.info(f"User refreshed from DB: occupation={user.occupation}, monthly_income={user.monthly_income}")
                    
                    messages.success(request, 'Employment form saved successfully!')
                    logger.info(f"Success message added. User data: occupation={user.occupation}, monthly_income={user.monthly_income}")
                else:
                    logger.error(f"EmploymentForm validation failed!")
                    logger.error(f"Form errors: {form.errors}")
                    logger.error(f"Form non_field_errors: {form.non_field_errors}")
                    messages.error(request, f'Employment form validation failed: {form.errors}')
                    
            elif form_type == 'emergency':
                logger.info("Creating EmergencyContactForm with POST data...")
                form = EmergencyContactForm(request.POST, instance=user)
                logger.info(f"EmergencyContactForm created. is_valid: {form.is_valid()}")
                
                if form.is_valid():
                    logger.info("EmergencyContactForm is valid, calling save()...")
                    saved_user = form.save()
                    logger.info("EmergencyContactForm.save() completed successfully")
                    
                    user.refresh_from_db()
                    logger.info(f"User refreshed from DB: emergency_contact_name={user.emergency_contact_name}")
                    
                    messages.success(request, 'Emergency form saved successfully!')
                    logger.info(f"Success message added. User data: emergency_contact_name={user.emergency_contact_name}")
                else:
                    logger.error(f"EmergencyContactForm validation failed!")
                    logger.error(f"Form errors: {form.errors}")
                    logger.error(f"Form non_field_errors: {form.non_field_errors}")
                    messages.error(request, f'Emergency form validation failed: {form.errors}')
                    
            else:
                error_msg = f'Unknown form type: {form_type}'
                logger.error(error_msg)
                messages.error(request, error_msg)
                
        except Exception as e:
            logger.error(f"Test profile form save error: {str(e)}", exc_info=True)
            messages.error(request, f'Error saving form: {str(e)}')
    else:
        logger.warning(f"Non-POST request received: {request.method}")
    
    logger.info(f"=== END TEST PROFILE FORM SUBMISSION DEBUG ===")
    
    # Check if this is an AJAX request
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    logger.info(f"Is AJAX request: {is_ajax}")
    
    if is_ajax:
        # Return JSON response for AJAX requests
        return JsonResponse({
            'status': 'success',
            'message': 'Form processed successfully',
            'form_type': form_type if 'form_type' in locals() else 'unknown'
        })
    else:
        # Redirect back to test_profile page for regular form submissions
        return redirect('dashboard:test_profile_forms')


@login_required
def debug_form_fields(request):
    """
    Debug endpoint to check what form fields are being submitted
    """
    if request.method == 'POST':
        logger.info(f"=== DEBUG FORM FIELDS ===")
        logger.info(f"POST data: {dict(request.POST)}")
        logger.info(f"All POST keys: {list(request.POST.keys())}")
        
        for key, value in request.POST.items():
            logger.info(f"Field '{key}': '{value}'")
        
        logger.info(f"=== END DEBUG FORM FIELDS ===")
        
        return JsonResponse({
            'status': 'debug_complete',
            'received_data': dict(request.POST),
            'all_keys': list(request.POST.keys())
        })
    
    # GET request - show debug form
    context = {
        'page_title': 'Debug Form Fields'
    }
    return render(request, 'users/debug_form_fields.html', context)