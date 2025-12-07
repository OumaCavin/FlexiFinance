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
from apps.loans.models import Loan
from apps.users.models import User

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

class LoanApplicationView(TemplateView):
    """Loan Application page view"""
    template_name = 'loans/loan-application.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'loan_products': getattr(settings, 'LOAN_PRODUCTS', []),
            'max_loan_amount': getattr(settings, 'MAX_LOAN_AMOUNT', 500000),
            'min_loan_amount': getattr(settings, 'MIN_LOAN_AMOUNT', 5000),
            'interest_rates': getattr(settings, 'INTEREST_RATES', {}),
            'loan_tenures': getattr(settings, 'LOAN_TENURES', [3, 6, 12, 24]),
        })
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle loan application form submission"""
        try:
            # Parse JSON data from request
            data = json.loads(request.body)
            
            # Validate required fields
            required_fields = ['first_name', 'last_name', 'email', 'phone', 'loan_amount', 'loan_purpose']
            missing_fields = []
            for field in required_fields:
                if not data.get(field):
                    missing_fields.append(field)
            
            if missing_fields:
                return JsonResponse({
                    'success': False,
                    'error': f'Missing required fields: {", ".join(missing_fields)}'
                }, status=400)
            
            # Check if user exists or create new user
            email = data.get('email', '').strip().lower()
            phone = data.get('phone', '').strip()
            
            try:
                user = User.objects.get(email=email)
                # Update existing user with new information
                user.first_name = data.get('first_name', user.first_name)
                user.last_name = data.get('last_name', user.last_name)
                user.phone_number = phone
                
                # Update additional fields if provided
                if data.get('date_of_birth'):
                    user.date_of_birth = data.get('date_of_birth')
                if data.get('national_id'):
                    user.national_id = data.get('national_id')
                if data.get('employer_name'):
                    user.employer_name = data.get('employer_name')
                if data.get('monthly_income'):
                    user.monthly_income = data.get('monthly_income')
                if data.get('employment_duration'):
                    user.employment_duration = data.get('employment_duration')
                if data.get('ref1_name'):
                    user.emergency_contact_name = data.get('ref1_name')
                if data.get('ref1_phone'):
                    user.emergency_contact_phone = data.get('ref1_phone')
                if data.get('ref1_relationship'):
                    user.emergency_contact_relationship = data.get('ref1_relationship')
                
                user.save()
                logger.info(f"Updated existing user: {email}")
                
            except User.DoesNotExist:
                # Create new user
                try:
                    # Generate a random password for the user
                    from django.contrib.auth.hashers import make_password
                    import secrets
                    
                    user = User.objects.create_user(
                        username=email,  # Use email as username
                        email=email,
                        password=secrets.token_urlsafe(16),  # Generate random password
                        first_name=data.get('first_name', ''),
                        last_name=data.get('last_name', ''),
                        phone_number=phone,
                    )
                    
                    # Set additional fields
                    if data.get('date_of_birth'):
                        user.date_of_birth = data.get('date_of_birth')
                    if data.get('national_id'):
                        user.national_id = data.get('national_id')
                    if data.get('employer_name'):
                        user.employer_name = data.get('employer_name')
                    if data.get('monthly_income'):
                        user.monthly_income = data.get('monthly_income')
                    if data.get('employment_duration'):
                        user.employment_duration = data.get('employment_duration')
                    if data.get('ref1_name'):
                        user.emergency_contact_name = data.get('ref1_name')
                    if data.get('ref1_phone'):
                        user.emergency_contact_phone = data.get('ref1_phone')
                    if data.get('ref1_relationship'):
                        user.emergency_contact_relationship = data.get('ref1_relationship')
                    
                    user.save()
                    logger.info(f"Created new user: {email}")
                    
                except Exception as e:
                    logger.error(f"Error creating user: {str(e)}")
                    return JsonResponse({
                        'success': False,
                        'error': 'Failed to create user account. Please try again.'
                    }, status=500)
            
            # Determine loan type based on amount or purpose
            loan_amount = float(data.get('loan_amount', 0))
            loan_purpose = data.get('loan_purpose', '').lower()
            
            if loan_amount <= 50000:
                loan_type = 'QUICK_CASH'
            elif 'business' in loan_purpose or 'business' in loan_type:
                loan_type = 'BUSINESS'
            elif 'emergency' in loan_purpose or 'emergency' in loan_type:
                loan_type = 'EMERGENCY'
            else:
                loan_type = 'PERSONAL'
            
            # Set default interest rate (you might want to make this dynamic based on loan type)
            interest_rate = getattr(settings, 'DEFAULT_INTEREST_RATE', 12.5)
            
            # Create loan instance
            try:
                loan = Loan.objects.create(
                    user=user,
                    loan_type=loan_type,
                    principal_amount=loan_amount,
                    interest_rate=interest_rate,
                    loan_tenure=int(data.get('loan_tenure', 12)),
                    purpose=data.get('loan_purpose', ''),
                    description=f"Loan application from {data.get('first_name', '')} {data.get('last_name', '')}. Purpose: {data.get('loan_purpose', '')}",
                    status='SUBMITTED',
                    processing_fee=0,  # Set based on your business logic
                    risk_category='MEDIUM'  # Set based on risk assessment logic
                )
                
                logger.info(f"Created loan application: {loan.loan_reference} for user {email}")
                
                # Return success response
                return JsonResponse({
                    'success': True,
                    'message': 'Your loan application has been submitted successfully!',
                    'data': {
                        'loan_reference': loan.loan_reference,
                        'loan_type': loan.get_loan_type_display(),
                        'principal_amount': str(loan.principal_amount),
                        'interest_rate': str(loan.interest_rate),
                        'loan_tenure': loan.loan_tenure,
                        'total_amount': str(loan.total_amount),
                        'monthly_payment': str(loan.monthly_payment),
                        'status': loan.get_status_display(),
                        'application_date': loan.application_date.isoformat(),
                    },
                    'redirect_url': f"/dashboard/applications/{loan.id}/"  # You might want to create this page
                })
                
            except Exception as e:
                logger.error(f"Error creating loan: {str(e)}")
                return JsonResponse({
                    'success': False,
                    'error': 'Failed to process loan application. Please try again.'
                }, status=500)
                
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            logger.error(f"Unexpected error in loan application: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'An unexpected error occurred. Please try again.'
            }, status=500)

class PrivacyPolicyView(TemplateView):
    """Privacy Policy page view"""
    template_name = 'legal/privacy-policy.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['last_updated'] = 'December 2025'
        return context

class TermsOfServiceView(TemplateView):
    """Terms of Service page view"""
    template_name = 'legal/terms-of-service.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['last_updated'] = 'December 2025'
        return context

class LoanAgreementView(TemplateView):
    """Loan Agreement page view"""
    template_name = 'legal/loan-agreement.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['last_updated'] = 'December 2025'
        return context

class CareersView(TemplateView):
    """Careers page view"""
    template_name = 'company/careers.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company_name'] = settings.FLEXIFINANCE_CONFIG['COMPANY_NAME']
        return context

class PressView(TemplateView):
    """Press page view"""
    template_name = 'company/press.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company_name'] = settings.FLEXIFINANCE_CONFIG['COMPANY_NAME']
        return context

class BlogView(TemplateView):
    """Blog page view"""
    template_name = 'company/blog.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company_name'] = settings.FLEXIFINANCE_CONFIG['COMPANY_NAME']
        return context

class InvestorsView(TemplateView):
    """Investors page view"""
    template_name = 'company/investors.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company_name'] = settings.FLEXIFINANCE_CONFIG['COMPANY_NAME']
        return context

class PartnersView(TemplateView):
    """Partners page view"""
    template_name = 'company/partners.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company_name'] = settings.FLEXIFINANCE_CONFIG['COMPANY_NAME']
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

@require_http_methods(["POST"])
def newsletter_subscribe(request):
    """Handle newsletter subscription"""
    try:
        # Parse JSON data
        data = json.loads(request.body)
        
        email = data.get('email', '').strip().lower()
        
        if not email:
            return JsonResponse({
                'success': False,
                'error': 'Email is required'
            }, status=400)
        
        # Validate email format
        if '@' not in email or '.' not in email:
            return JsonResponse({
                'success': False,
                'error': 'Please enter a valid email address'
            }, status=400)
        
        # Add to newsletter (you can implement this with Supabase or email service)
        subscription_data = {
            'email': email,
            'source': 'website_newsletter',
            'subscribed_at': datetime.now().isoformat(),
            'status': 'active'
        }
        
        # Here you would typically store in Supabase or send to email service
        # For now, we'll just log it
        logger.info(f"Newsletter subscription: {email}")
        
        return JsonResponse({
            'success': True,
            'message': 'Thank you for subscribing to our newsletter!',
            'data': {
                'subscribed_at': subscription_data['subscribed_at']
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid data format'
        }, status=400)
    except Exception as e:
        logger.error(f"Newsletter subscription error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Subscription failed. Please try again.'
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