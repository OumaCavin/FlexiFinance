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
from apps.users.forms import UserProfileForm
import logging

logger = logging.getLogger(__name__)

@login_required
def dashboard(request):
    """User dashboard view"""
    context = {
        'user': request.user,
        'page_title': 'Dashboard'
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