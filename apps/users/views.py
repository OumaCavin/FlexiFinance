"""
Web Views for Users app
Django template-based views for user authentication and dashboard
"""

import logging
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate
from .models import User

logger = logging.getLogger(__name__)


def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials')
    
    return render(request, 'users/login.html')


def register_view(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        phone_number = request.POST.get('phone', '')
        id_number = request.POST.get('id_number', '')
        terms = request.POST.get('terms', '')
        
        # Validate required fields
        if not all([email, password1, password2, first_name, last_name, phone_number]):
            messages.error(request, 'All required fields must be filled.')
            return render(request, 'users/register.html')
        
        # Check if passwords match
        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'users/register.html')
        
        # Check if terms are accepted
        if not terms:
            messages.error(request, 'You must accept the Terms of Service and Privacy Policy.')
            return render(request, 'users/register.html')
        
        try:
            # Create user with all fields (username is email for simplicity)
            user = User.objects.create_user(
                username=email,  # Use email as username
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name,
            )
            
            # Set additional fields if they exist
            if hasattr(user, 'phone_number'):
                user.phone_number = phone_number
            if hasattr(user, 'national_id'):
                user.national_id = id_number
            
            user.save()
            
            messages.success(request, 'Registration successful! Please log in.')
            return redirect('login')
        except Exception as e:
            messages.error(request, f'Registration failed: {str(e)}')
    
    return render(request, 'users/register.html')


def logout_view(request):
    """User logout view"""
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    """User dashboard view"""
    context = {
        'user': request.user,
    }
    return render(request, 'users/dashboard.html', context)


@login_required
def profile(request):
    """User profile view"""
    if request.method == 'POST':
        try:
            # Handle both JSON and form data
            if request.headers.get('content-type', '').startswith('application/json'):
                import json
                data = json.loads(request.body)
            else:
                data = request.POST
            
            first_name = data.get('first_name', '')
            last_name = data.get('last_name', '')
            phone_number = data.get('phone_number', '')
            current_password = data.get('current_password', '')
            new_password = data.get('new_password', '')
            confirm_password = data.get('confirm_password', '')
            
            # Update basic information
            request.user.first_name = first_name
            request.user.last_name = last_name
            if hasattr(request.user, 'phone_number'):
                request.user.phone_number = phone_number
            
            # Handle password change
            if new_password:
                if new_password != confirm_password:
                    if request.headers.get('content-type', '').startswith('application/json'):
                        from django.http import JsonResponse
                        return JsonResponse({
                            'success': False,
                            'error': 'Passwords do not match'
                        }, status=400)
                    else:
                        messages.error(request, 'Passwords do not match.')
                        return redirect('profile')
                
                if not current_password:
                    if request.headers.get('content-type', '').startswith('application/json'):
                        from django.http import JsonResponse
                        return JsonResponse({
                            'success': False,
                            'error': 'Current password is required to set a new password'
                        }, status=400)
                    else:
                        messages.error(request, 'Current password is required to set a new password.')
                        return redirect('profile')
                
                # Verify current password
                if not request.user.check_password(current_password):
                    if request.headers.get('content-type', '').startswith('application/json'):
                        from django.http import JsonResponse
                        return JsonResponse({
                            'success': False,
                            'error': 'Current password is incorrect'
                        }, status=400)
                    else:
                        messages.error(request, 'Current password is incorrect.')
                        return redirect('profile')
                
                # Set new password
                request.user.set_password(new_password)
            
            request.user.save()
            
            if request.headers.get('content-type', '').startswith('application/json'):
                from django.http import JsonResponse
                return JsonResponse({
                    'success': True,
                    'message': 'Profile updated successfully!'
                })
            else:
                messages.success(request, 'Profile updated successfully!')
                return redirect('profile')
                
        except Exception as e:
            logger.error(f"Profile update error: {str(e)}")
            if request.headers.get('content-type', '').startswith('application/json'):
                from django.http import JsonResponse
                return JsonResponse({
                    'success': False,
                    'error': 'An error occurred while updating your profile'
                }, status=500)
            else:
                messages.error(request, 'An error occurred while updating your profile.')
                return redirect('profile')
    
    context = {
        'user': request.user,
    }
    return render(request, 'users/profile.html', context)


@login_required
def my_loans(request):
    """User loans view"""
    context = {
        'user': request.user,
        'loans': []  # TODO: Fetch user's loans from database
    }
    return render(request, 'users/my_loans.html', context)