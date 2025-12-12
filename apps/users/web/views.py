"""
Web views for FlexiFinance Users
User dashboard and authentication views
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout, update_session_auth_hash
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import models
from apps.users.forms import UserProfileForm
import logging

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
            'description': f'Applied for KES {loan.principal_amount} - {loan.loan_product.name if loan.loan_product else "Unknown Product"}',
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
    
    # Initialize the form with user instance
    profile_form = UserProfileForm(instance=user)

    if request.method == 'POST':
        logger.info(f"Profile form submitted with method: {request.method}")
        logger.info(f"POST data: {dict(request.POST)}")
        
        form_type = request.POST.get('form_type')
        logger.info(f"Form type from POST: {form_type}")
        
        if form_type == 'personal':
            logger.info("Processing personal profile form")
            # Bind POST data to the form
            profile_form = UserProfileForm(request.POST, instance=user)
            
            logger.info(f"Form errors: {profile_form.errors}")
            logger.info(f"Form is valid: {profile_form.is_valid()}")
            
            if profile_form.is_valid():
                try:
                    logger.info("Form is valid, saving profile...")
                    profile_form.save()
                    logger.info("Profile saved successfully")
                    messages.success(request, 'Profile information updated successfully!')
                    return redirect('dashboard:profile')
                except Exception as e:
                    logger.error(f"Error updating profile: {str(e)}")
                    messages.error(request, 'An error occurred while saving your profile.')
            else:
                # If invalid, the form with errors will be rendered below
                logger.info("Form validation failed, errors will be displayed")
                messages.error(request, 'Please correct the errors below.')
        
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
    
    context = {
        'user': user,
        'profile_form': profile_form,  # Pass the form to the template
        'page_title': 'Profile'
    }
    return render(request, 'users/profile.html', context)

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

def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('dashboard:dashboard')
    
    context = {
        'page_title': 'Login'
    }
    return render(request, 'users/login.html', context)

def register_view(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('dashboard:dashboard')
    
    context = {
        'page_title': 'Register'
    }
    return render(request, 'users/register.html', context)