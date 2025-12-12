"""
Web Views for Users app
Django template-based views for user authentication and dashboard
"""

import logging
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import User

logger = logging.getLogger(__name__)


# def login_view(request):
#     """User login view - DISABLED: Using AllAuth defaults"""
#     # This view is disabled to use AllAuth default authentication
#     pass


# def register_view(request):
#     """User registration view - DISABLED: Using AllAuth defaults"""
#     # This view is disabled to use AllAuth default authentication
#     pass


# def logout_view(request):
#     """User logout view - DISABLED: Using AllAuth defaults"""
#     # This view is disabled to use AllAuth default authentication
#     pass


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
            
            form_type = data.get('form_type', 'personal')
            logger.info(f"Profile update request - form_type: {form_type}")
            
            if form_type == 'personal':
                # Update personal information only
                first_name = data.get('first_name', '')
                last_name = data.get('last_name', '')
                phone_number = data.get('phone_number', '')
                
                logger.info(f"Updating personal info - first_name: {first_name}, last_name: {last_name}, phone: {phone_number}")
                
                # Update basic information
                request.user.first_name = first_name
                request.user.last_name = last_name
                if hasattr(request.user, 'phone_number'):
                    request.user.phone_number = phone_number
                
                request.user.save()
                
                logger.info("Personal info updated successfully")
                if request.headers.get('content-type', '').startswith('application/json'):
                    from django.http import JsonResponse
                    return JsonResponse({
                        'success': True,
                        'message': 'Personal information updated successfully!'
                    })
                else:
                    messages.success(request, 'Personal information updated successfully!')
                    return redirect('dashboard:profile')
                    
            elif form_type == 'password':
                # Handle password change
                current_password = data.get('current_password', '')
                new_password = data.get('new_password', '')
                confirm_password = data.get('confirm_password', '')
                
                if new_password != confirm_password:
                    if request.headers.get('content-type', '').startswith('application/json'):
                        from django.http import JsonResponse
                        return JsonResponse({
                            'success': False,
                            'error': 'Passwords do not match'
                        }, status=400)
                    else:
                        messages.error(request, 'Passwords do not match.')
                        return redirect('dashboard:profile')
                
                if not current_password:
                    if request.headers.get('content-type', '').startswith('application/json'):
                        from django.http import JsonResponse
                        return JsonResponse({
                            'success': False,
                            'error': 'Current password is required to set a new password'
                        }, status=400)
                    else:
                        messages.error(request, 'Current password is required to set a new password.')
                        return redirect('dashboard:profile')
                
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
                        return redirect('dashboard:profile')
                
                # Set new password
                request.user.set_password(new_password)
                request.user.save()
                
                if request.headers.get('content-type', '').startswith('application/json'):
                    from django.http import JsonResponse
                    return JsonResponse({
                        'success': True,
                        'message': 'Password updated successfully!'
                    })
                else:
                    messages.success(request, 'Password updated successfully!')
                    return redirect('dashboard:profile')
            else:
                logger.error(f"Unknown form_type: {form_type}")
                if request.headers.get('content-type', '').startswith('application/json'):
                    from django.http import JsonResponse
                    return JsonResponse({
                        'success': False,
                        'error': 'Invalid form type'
                    }, status=400)
                else:
                    messages.error(request, 'Invalid form submission.')
                    return redirect('dashboard:profile')
                
        except Exception as e:
            logger.error(f"Profile update error: {str(e)}", exc_info=True)
            if request.headers.get('content-type', '').startswith('application/json'):
                from django.http import JsonResponse
                return JsonResponse({
                    'success': False,
                    'error': 'An error occurred while updating your profile'
                }, status=500)
            else:
                messages.error(request, 'An error occurred while updating your profile.')
                return redirect('dashboard:profile')
    
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