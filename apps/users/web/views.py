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
    context = {
        'user': request.user,
        'page_title': 'Profile'
    }
    return render(request, 'users/profile.html', context)

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