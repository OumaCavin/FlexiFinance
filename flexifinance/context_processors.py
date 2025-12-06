"""
Template context processors for the FlexiFinance project.
"""
from django.utils import timezone


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