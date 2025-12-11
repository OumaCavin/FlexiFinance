"""
Web views for FlexiFinance Users
User dashboard and authentication views
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
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
    """User profile view"""
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        
        if form_type == 'personal':
            # Handle personal information update
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            phone_number = request.POST.get('phone_number', '').strip()
            
            # Validation
            if not first_name or not last_name:
                messages.error(request, 'First name and last name are required.')
            else:
                # Update user fields
                user = request.user
                user.first_name = first_name
                user.last_name = last_name
                
                # Handle phone_number (it's optional)
                if phone_number:
                    user.phone_number = phone_number
                else:
                    user.phone_number = None
                
                try:
                    user.save()
                    messages.success(request, 'Personal information updated successfully!')
                except Exception as e:
                    messages.error(request, f'Error updating profile: {str(e)}')
            
        elif form_type == 'password':
            # Handle password update
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
            elif not current_password or not request.user.check_password(current_password):
                messages.error(request, 'Current password is incorrect.')
            else:
                # Update password
                try:
                    request.user.set_password(new_password)
                    request.user.save()
                    messages.success(request, 'Password updated successfully!')
                except Exception as e:
                    messages.error(request, f'Error updating password: {str(e)}')
        
        # Redirect to prevent form resubmission
        return redirect('dashboard:profile')
    
    # GET request - just show the profile page
    context = {
        'user': request.user,
        'page_title': 'Profile'
    }
    return render(request, 'users/profile.html', context)

@login_required
def my_loans(request):
    """User loans view"""
    context = {
        'user': request.user,
        'page_title': 'My Loans',
        'loans': []  # Empty for now, will be populated when loan models are implemented
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
        return redirect('users:dashboard')
    
    context = {
        'page_title': 'Login'
    }
    return render(request, 'users/login.html', context)

def register_view(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('users:dashboard')
    
    context = {
        'page_title': 'Register'
    }
    return render(request, 'users/register.html', context)