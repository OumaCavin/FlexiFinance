"""
Core views for FlexiFinance - Kenyan MicroFinance Platform
Views for main website pages and frontend templates
"""

from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView
from django.contrib import messages
from django.conf import settings
from django.urls import reverse
import json
import logging
from datetime import datetime

# Import services
from apps.payments.services.supabase_service import SupabaseService
from apps.payments.services.resend_email_service import ResendEmailService

logger = logging.getLogger(__name__)

class HomeView(TemplateView):
    """Home page view with Kenyan market focus"""
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add Kenyan market specific context
        context.update({
            'company_name': settings.FLEXIFINANCE_CONFIG['COMPANY_NAME'],
            'phone_number': settings.FLEXIFINANCE_CONFIG['PHONE_NUMBER'],
            'loan_products': settings.LOAN_PRODUCTS,
            'support_hours': getattr(settings, 'SUPPORT_HOURS', '24/7'),
            'business_address': getattr(settings, 'BUSINESS_ADDRESS', ''),
            'social_media': getattr(settings, 'SOCIAL_MEDIA', {}),
            'payment_providers': getattr(settings, 'PAYMENT_PROVIDERS', {}),
            'seo_config': getattr(settings, 'SEO_CONFIG', {}),
            'features': getattr(settings, 'FEATURES', {}),
        })
        
        return context

class ContactView(TemplateView):
    """Contact page view with Supabase integration"""
    template_name = 'contact.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add contact page specific context
        context.update({
            'company_name': settings.FLEXIFINANCE_CONFIG['COMPANY_NAME'],
            'support_email': getattr(settings, 'SUPPORT_EMAIL', ''),
            'support_phone': getattr(settings, 'SUPPORT_PHONE', ''),
            'support_address': getattr(settings, 'SUPPORT_ADDRESS', ''),
            'support_hours': getattr(settings, 'SUPPORT_HOURS', '24/7'),
            'social_media': getattr(settings, 'SOCIAL_MEDIA', {}),
            'business_info': {
                'name': getattr(settings, 'BUSINESS_NAME', ''),
                'email': getattr(settings, 'BUSINESS_EMAIL', ''),
                'phone': getattr(settings, 'BUSINESS_PHONE', ''),
                'address': getattr(settings, 'BUSINESS_ADDRESS', ''),
                'registration': getattr(settings, 'BUSINESS_REGISTRATION', ''),
            }
        })
        
        return context

class AboutView(TemplateView):
    """About Us page view"""
    template_name = 'about.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company_name'] = settings.FLEXIFINANCE_CONFIG['COMPANY_NAME']
        return context

class HowItWorksView(TemplateView):
    """How It Works page view"""
    template_name = 'how-it-works.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['loan_products'] = settings.LOAN_PRODUCTS
        return context

class SupportView(TemplateView):
    """Support page view"""
    template_name = 'support.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'support_email': getattr(settings, 'SUPPORT_EMAIL', ''),
            'support_phone': getattr(settings, 'SUPPORT_PHONE', ''),
            'support_hours': getattr(settings, 'SUPPORT_HOURS', '24/7'),
        })
        return context

class FAQView(TemplateView):
    """FAQ page view"""
    template_name = 'faq.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add FAQ data if needed
        context['faq_items'] = getattr(settings, 'FAQ_ITEMS', [
            {
                'question': 'How do I apply for a loan?',
                'answer': 'You can apply for a loan through our online application form or visit any of our branches.'
            },
            {
                'question': 'What documents do I need?',
                'answer': 'You will need a valid ID, proof of income, and recent bank statements.'
            },
            {
                'question': 'How long does the approval process take?',
                'answer': 'Most loan applications are approved within 24-48 hours.'
            }
        ])
        return context

class LoanProductsView(TemplateView):
    """Loan Products page view"""
    template_name = 'products/loan-products.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['loan_products'] = settings.LOAN_PRODUCTS
        return context

class BusinessLoansView(TemplateView):
    """Business Loans page view"""
    template_name = 'products/business-loans.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class EmergencyLoansView(TemplateView):
    """Emergency Loans page view"""
    template_name = 'products/emergency-loans.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class LoanCalculatorView(TemplateView):
    """Loan Calculator page view"""
    template_name = 'loan-calculator.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['loan_products'] = settings.LOAN_PRODUCTS
        return context

@require_http_methods(["POST"])
def submit_contact_form(request):
    """Handle contact form submission with Supabase integration"""
    try:
        # Parse JSON data
        data = json.loads(request.body)
        
        # Validate required fields
        required_fields = ['name', 'email', 'message']
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({
                    'success': False,
                    'error': f'{field.capitalize()} is required'
                }, status=400)
        
        # Add timestamp and metadata
        contact_data = {
            'name': data.get('name', '').strip(),
            'email': data.get('email', '').strip().lower(),
            'phone': data.get('phone', '').strip(),
            'message': data.get('message', '').strip(),
            'subject': data.get('subject', 'General Inquiry'),
            'source': 'website_contact_form',
            'created_at': datetime.now().isoformat(),
            'ip_address': request.META.get('REMOTE_ADDR', ''),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
        }
        
        # Store in Supabase
        supabase_service = SupabaseService()
        result = supabase_service.submit_contact_form(contact_data)
        
        if result['success']:
            # Send notification email to support team
            resend_service = ResendEmailService()
            resend_service.send_contact_notification(contact_data)
            
            logger.info(f"Contact form submitted successfully for {contact_data['email']}")
            
            return JsonResponse({
                'success': True,
                'message': 'Thank you for your message. We will get back to you within 24 hours.',
                'data': {
                    'submitted_at': contact_data['created_at'],
                    'reference_id': result.get('data', {}).get('id', '')
                }
            })
        else:
            logger.error(f"Failed to submit contact form: {result.get('error', 'Unknown error')}")
            return JsonResponse({
                'success': False,
                'error': 'Failed to submit your message. Please try again or contact us directly.'
            }, status=500)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        logger.error(f"Error processing contact form: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'An unexpected error occurred. Please try again.'
        }, status=500)

@require_http_methods(["GET"])
def health_check(request):
    """Health check endpoint for monitoring"""
    try:
        # Check database connection
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        # Check Supabase connection
        supabase_service = SupabaseService()
        supabase_status = supabase_service.health_check()
        
        # Check email service
        resend_service = ResendEmailService()
        email_status = resend_service.health_check()
        
        health_data = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'services': {
                'database': 'connected',
                'supabase': 'connected' if supabase_status else 'disconnected',
                'email': 'connected' if email_status else 'disconnected',
            },
            'version': '1.0.0',
            'environment': getattr(settings, 'RAILWAY_ENVIRONMENT', 'development')
        }
        
        return JsonResponse(health_data)
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JsonResponse({
            'status': 'unhealthy',
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }, status=503)

@require_http_methods(["GET"])
def get_public_config(request):
    """Get public configuration for frontend"""
    try:
        public_config = {}
        
        for setting_name in getattr(settings, 'EXPORT_TO_FRONTEND', []):
            if hasattr(settings, setting_name):
                public_config[setting_name] = getattr(settings, setting_name)
        
        return JsonResponse({
            'success': True,
            'data': public_config
        })
        
    except Exception as e:
        logger.error(f"Error getting public config: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to get configuration'
        }, status=500)

class ErrorView(TemplateView):
    """Custom error pages"""
    template_name = 'errors/error.html'
    
    def get_template_names(self):
        status_code = self.kwargs.get('status_code', 500)
        return [f'errors/{status_code}.html', 'errors/error.html']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_code'] = self.kwargs.get('status_code', 500)
        return context

def handler404(request, exception):
    """Custom 404 handler"""
    return ErrorView.as_view(template_name='errors/404.html')(request, status_code=404)

def handler500(request):
    """Custom 500 handler"""
    return ErrorView.as_view(template_name='errors/500.html')(request, status_code=500)

def handler403(request, exception):
    """Custom 403 handler"""
    return ErrorView.as_view(template_name='errors/403.html')(request, status_code=403)

def handler400(request, exception):
    """Custom 400 handler"""
    return ErrorView.as_view(template_name='errors/400.html')(request, status_code=400)