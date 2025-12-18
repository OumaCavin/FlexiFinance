"""
Template context processors for the FlexiFinance project.
"""
from django.utils import timezone
from django.conf import settings


def notification_context(request):
    """
    Add common context variables for notifications and site information.
    This context processor is available to all templates.
    """
    context = {
        'current_year': timezone.now().year,
        'site_name': 'FlexiFinance',
        'app_version': '1.0.0',
    }
    
    # Add user-specific context if user is authenticated
    if request.user.is_authenticated:
        context.update({
            'user_display_name': getattr(request.user, 'get_full_name', lambda: request.user.username)(),
        })
    
    return context


def site_context(request):
    """
    Add site-wide context variables for all templates including AllAuth.
    This fixes template errors when extending base.html in AllAuth templates.
    """
    context = {
        'current_year': timezone.now().year,
        'site_name': 'FlexiFinance',
        'app_version': '1.0.0',
        
        # Analytics & Tracking (expected by base.html)
        'GOOGLE_ANALYTICS_ID': getattr(settings, 'GOOGLE_ANALYTICS_ID', ''),
        'FACEBOOK_PIXEL_ID': getattr(settings, 'FACEBOOK_PIXEL_ID', ''),
        
        # Feature Flags (expected by base.html)
        'FEATURES': getattr(settings, 'FEATURES', {
            'ENABLE_CHAT_SUPPORT': False,
            'ENABLE_NEWSLETTER': True,
            'ENABLE_ANALYTICS': True,
            'ENABLE_SOCIAL_LOGIN': False,
        }),
    }
    
    # Add user-specific context if user is authenticated
    if request.user.is_authenticated:
        context.update({
            'user_display_name': getattr(request.user, 'get_full_name', lambda: request.user.username)(),
        })
    
    return context