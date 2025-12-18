"""
Core views for FlexiFinance - Kenyan MicroFinance Platform
Views for main website pages and frontend templates
"""

from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.contrib import messages
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
import json
import logging
from datetime import datetime

# Import services
from apps.payments.services.resend_email_service import ResendEmailService
from apps.loans.models import Loan, LoanProduct
from apps.users.models import User

logger = logging.getLogger(__name__)

class ProductHelperMixin:
    """Helper methods for loan product display across multiple views"""
    
    def _get_icon_for_product(self, product_code):
        """Map product code to appropriate icon"""
        icon_mapping = {
            'PERSONAL': 'fa-user',
            'BUSINESS': 'fa-briefcase', 
            'EMERGENCY': 'fa-heartbeat',
            'EDUCATION': 'fa-graduation-cap',
            'QUICK_CASH': 'fa-bolt',
            'PERSONAL_5K_100K': 'user',
            'EMERGENCY_5K_50K': 'exclamation-triangle',
            'BUSINESS_50K_500K': 'briefcase',
            'EDUCATION_25K_300K': 'graduation-cap',
            'QUICK_CASH_5K_25K': 'bolt',
        }
        return icon_mapping.get(str(product_code).upper(), 'fa-money-bill-wave')

    def _format_interest_rate(self, rate):
        """Format interest rate for display"""
        if rate:
            return f"{float(rate):.1f}"
        return "12.0"

    def _get_features_for_product(self, product_code):
        """Get features based on product type"""
        features_mapping = {
            'PERSONAL': [
                'No collateral required', 'Quick approval process', 
                'Flexible repayment terms', 'Direct M-Pesa disbursement'
            ],
            'EMERGENCY': [
                'Same-day approval', 'Instant M-Pesa transfer', 
                'Minimal documentation', '24/7 application process'
            ],
            'BUSINESS': [
                'Lower interest rates', 'Longer repayment terms', 
                'Business plan assistance', 'Financial advisory support'
            ],
            'EDUCATION': [
                'Grace period after graduation', 'Low interest rates for students', 
                'No co-signer required', 'Career development support'
            ],
            'QUICK_CASH': [
                'Instant approval', 'Quick M-Pesa transfer', 
                'Minimal requirements', 'Short-term solution'
            ]
        }
        return features_mapping.get(str(product_code).upper(), [
            'Flexible financing', 'Quick approval', 
            'Competitive rates', 'M-Pesa disbursement'
        ])

class HomeView(ProductHelperMixin, TemplateView):
    """Home page view with Kenyan market focus"""
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get loan products from database
        try:
            db_products = LoanProduct.objects.filter(is_active=True).order_by('name')
            
            # Transform database products to template format
            loan_products = []
            for product in db_products:
                # Map database fields to template format
                loan_product = {
                    'name': product.name,
                    'description': product.description or f"Flexible {product.name.lower()} for your financial needs",
                    'icon': self._get_icon_for_product(product.product_code),
                    'min_amount': int(product.min_amount),
                    'max_amount': int(product.max_amount),
                    'interest_rate': product.interest_rate,
                    'max_term': product.max_tenure,
                    'min_term': product.min_tenure,
                    'processing_fee': product.processing_fee,
                    'product_code': product.product_code,
                    'features': self._get_features_for_product(product.product_code)
                }
                loan_products.append(loan_product)
        except Exception as e:
            # Fallback to empty list if database query fails
            loan_products = []
            logger.error(f"Error fetching loan products: {e}")
        
        # Add newsletter subscription form to context
        from .forms import NewsletterSubscriptionForm
        context['newsletter_form'] = NewsletterSubscriptionForm()
        
        # Add Kenyan market specific context
        context.update({
            'company_name': settings.FLEXIFINANCE_CONFIG['COMPANY_NAME'],
            'phone_number': settings.FLEXIFINANCE_CONFIG['PHONE_NUMBER'],
            'loan_products': loan_products,
            'support_hours': getattr(settings, 'SUPPORT_HOURS', '24/7'),
            'business_address': getattr(settings, 'BUSINESS_ADDRESS', ''),
            'social_media': getattr(settings, 'SOCIAL_MEDIA', {}),
            'payment_providers': getattr(settings, 'PAYMENT_PROVIDERS', {}),
            'seo_config': getattr(settings, 'SEO_CONFIG', {}),
            'features': getattr(settings, 'FEATURES', {}),
        })
        
        return context

class ContactView(TemplateView):
    """Contact page view with form handling"""
    template_name = 'contact.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add contact form to context
        from .forms import ContactForm
        context['contact_form'] = ContactForm()
        
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
    
    def post(self, request, *args, **kwargs):
        """Handle contact form submission"""
        from .forms import ContactForm
        from .models import Contact
        
        form = ContactForm(request.POST)
        if form.is_valid():
            try:
                # Save contact form
                contact = form.save(commit=False)
                contact.source = 'website_contact_page'
                contact.ip_address = request.META.get('REMOTE_ADDR', '')
                contact.user_agent = request.META.get('HTTP_USER_AGENT', '')
                contact.save()
                
                # Send email notification
                try:
                    resend_service = ResendEmailService()
                    contact_data = {
                        'name': contact.name,
                        'email': contact.email,
                        'phone': contact.phone,
                        'message': contact.message,
                        'subject': contact.subject,
                        'source': contact.source,
                    }
                    resend_service.send_contact_notification(contact_data)
                except Exception as e:
                    logger.warning(f"Email notification failed: {str(e)}")
                
                messages.success(request, 'Thank you for your message! We will get back to you within 24 hours.')
                return redirect('contact')
            except Exception as e:
                logger.error(f"Error saving contact form: {str(e)}")
                messages.error(request, 'Sorry, there was an error processing your message. Please try again.')
        else:
            messages.error(request, 'Please correct the errors below.')
        
        context = self.get_context_data(**kwargs)
        context['contact_form'] = form
        return render(request, self.template_name, context)

class AboutView(TemplateView):
    """About Us page view"""
    template_name = 'about.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company_name'] = settings.FLEXIFINANCE_CONFIG['COMPANY_NAME']
        return context

class HowItWorksView(ProductHelperMixin, TemplateView):
    """How It Works page view"""
    template_name = 'how-it-works.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get loan products from database
        try:
            db_products = LoanProduct.objects.filter(is_active=True).order_by('name')
            
            # Transform database products to template format
            loan_products = []
            for product in db_products:
                loan_product = {
                    'name': product.name,
                    'description': product.description or f"Flexible {product.name.lower()} for your financial needs",
                    'icon': self._get_icon_for_product(product.product_code),
                    'min_amount': int(product.min_amount),
                    'max_amount': int(product.max_amount),
                    'interest_rate': product.interest_rate,
                    'max_term': product.max_tenure,
                    'min_term': product.min_tenure,
                    'processing_fee': product.processing_fee,
                    'product_code': product.product_code,
                    'features': self._get_features_for_product(product.product_code)
                }
                loan_products.append(loan_product)
        except Exception as e:
            loan_products = []
            logger.error(f"Error fetching loan products: {e}")
        
        context['loan_products'] = loan_products
        return context

class SupportView(TemplateView):
    """Support page view with form handling"""
    template_name = 'support.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add support form to context
        from .forms import SupportForm
        context['support_form'] = SupportForm()
        
        context.update({
            'support_email': getattr(settings, 'SUPPORT_EMAIL', ''),
            'support_phone': getattr(settings, 'SUPPORT_PHONE', ''),
            'support_hours': getattr(settings, 'SUPPORT_HOURS', '24/7'),
        })
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle support form submission"""
        from .forms import SupportForm
        from .models import Contact
        
        form = SupportForm(request.POST)
        if form.is_valid():
            try:
                # Save support form
                contact = form.save(commit=False)
                contact.source = 'website_support_page'
                contact.subject = f"[{contact.issue_type}] {contact.subject}"
                contact.ip_address = request.META.get('REMOTE_ADDR', '')
                contact.user_agent = request.META.get('HTTP_USER_AGENT', '')
                contact.save()
                
                # Send email notification with higher priority
                try:
                    resend_service = ResendEmailService()
                    contact_data = {
                        'name': contact.name,
                        'email': contact.email,
                        'phone': contact.phone,
                        'message': f"Priority: {contact.priority}\n\n{contact.message}",
                        'subject': f"[{contact.issue_type}] {contact.subject}",
                        'source': contact.source,
                        'priority': contact.priority,
                    }
                    resend_service.send_contact_notification(contact_data)
                except Exception as e:
                    logger.warning(f"Email notification failed: {str(e)}")
                
                messages.success(request, 'Your support request has been submitted successfully! Our team will respond within 24 hours.')
                return redirect('support')
            except Exception as e:
                logger.error(f"Error saving support form: {str(e)}")
                messages.error(request, 'Sorry, there was an error processing your request. Please try again.')
        else:
            messages.error(request, 'Please correct the errors below.')
        
        context = self.get_context_data(**kwargs)
        context['support_form'] = form
        return render(request, self.template_name, context)

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

class LoanProductsView(ProductHelperMixin, TemplateView):
    """Loan Products page view"""
    template_name = 'products/loan-products.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get loan products from database
        try:
            db_products = LoanProduct.objects.filter(is_active=True).order_by('name')
            
            # Transform database products to template format
            loan_products = []
            for product in db_products:
                # Map database fields to template format
                loan_product = {
                    'name': product.name,
                    'description': product.description or f"Flexible {product.name.lower()} for your financial needs",
                    'icon': self._get_icon_for_product(product.product_code),
                    'min_amount': int(product.min_amount),
                    'max_amount': int(product.max_amount),
                    'interest_rate': self._format_interest_rate(product.interest_rate),
                    'max_term': product.max_tenure,
                    'features': self._get_features_for_product(product.product_code),
                    'product_code': product.product_code,
                    'processing_fee': int(product.processing_fee),
                    'min_income': int(product.min_income),
                    'requirements': product.requires_documents,
                }
                loan_products.append(loan_product)
                
        except Exception as e:
            # Log error and use fallback
            logger.error(f"Error querying loan products from database: {str(e)}")
            loan_products = []
        
        # If no database products, provide a meaningful fallback
        if not loan_products:
            loan_products = [
                {
                    'name': 'Education Loan',
                    'description': 'Invest in your future with student-friendly financing for education and skill development',
                    'icon': 'graduation-cap',
                    'min_amount': 25000,
                    'max_amount': 300000,
                    'interest_rate': '9-12',
                    'max_term': 48,
                    'features': [
                        'Grace period after graduation',
                        'Low interest rates for students',
                        'No co-signer required',
                        'Career development support'
                    ]
                }
            ]
        
        context['loan_products'] = loan_products
        return context
    
    def _get_icon_for_product(self, product_code):
        """Map product code to appropriate icon"""
        icon_mapping = {
            'PERSONAL_5K_100K': 'user',
            'EMERGENCY_5K_50K': 'exclamation-triangle',
            'BUSINESS_50K_500K': 'briefcase',
            'EDUCATION_25K_300K': 'graduation-cap',
            'QUICK_CASH_5K_25K': 'bolt',
        }
        return icon_mapping.get(product_code.upper(), 'money-bill-wave')
    
    def _format_interest_rate(self, rate):
        """Format interest rate for display"""
        if rate:
            return f"{float(rate):.1f}"
        return "12.0"
    
    def _get_features_for_product(self, product_code):
        """Get features based on product type"""
        features_mapping = {
            'PERSONAL_5K_100K': [
                'No collateral required',
                'Quick approval process',
                'Flexible repayment terms',
                'Direct M-Pesa disbursement'
            ],
            'EMERGENCY_5K_50K': [
                'Same-day approval',
                'Instant M-Pesa transfer',
                'Minimal documentation',
                '24/7 application process'
            ],
            'BUSINESS_50K_500K': [
                'Lower interest rates',
                'Longer repayment terms',
                'Business plan assistance',
                'Financial advisory support'
            ],
            'EDUCATION_25K_300K': [
                'Grace period after graduation',
                'Low interest rates for students',
                'No co-signer required',
                'Career development support'
            ],
            'QUICK_CASH_5K_25K': [
                'Instant approval',
                'Quick M-Pesa transfer',
                'Minimal requirements',
                'Short-term solution'
            ]
        }
        return features_mapping.get(product_code.upper(), [
            'Flexible financing',
            'Quick approval',
            'Competitive rates',
            'M-Pesa disbursement'
        ])

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

class QuickCashLoansView(TemplateView):
    """Quick Cash Loans page view"""
    template_name = 'products/quick-cash-loans.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class PersonalLoansView(TemplateView):
    """Personal Loans page view"""
    template_name = 'products/personal-loans.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class EducationLoansView(TemplateView):
    """Education Loans page view"""
    template_name = 'products/education-loans.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class LoanCalculatorView(TemplateView):
    """Loan Calculator page view"""
    template_name = 'loan-calculator.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

@method_decorator(csrf_exempt, name='dispatch')
class LoanApplicationView(ProductHelperMixin, TemplateView):
    """Loan Application page view"""
    template_name = 'loans/loan-application.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get loan products from database
        try:
            db_products = LoanProduct.objects.filter(is_active=True).order_by('name')
            
            # Transform database products to template format
            loan_products = []
            for product in db_products:
                loan_product = {
                    'name': product.name,
                    'description': product.description or f"Flexible {product.name.lower()} for your financial needs",
                    'icon': self._get_icon_for_product(product.product_code),
                    'min_amount': int(product.min_amount),
                    'max_amount': int(product.max_amount),
                    'interest_rate': product.interest_rate,
                    'max_term': product.max_tenure,
                    'min_term': product.min_tenure,
                    'processing_fee': product.processing_fee,
                    'product_code': product.product_code,
                    'features': self._get_features_for_product(product.product_code)
                }
                loan_products.append(loan_product)
        except Exception as e:
            loan_products = []
            logger.error(f"Error fetching loan products: {e}")
        
        context.update({
            'loan_products': loan_products,
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
            logger.info(f"Received loan application data: {data.keys()}")  # Debug logging
            
            # Validate required fields (using actual form field names)
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
            phone = data.get('phone', '').strip()  # Form field name
            id_number = data.get('id_number', '').strip()  # Form field name
            
            try:
                user = User.objects.get(email=email)
                # Update existing user with new information
                user.first_name = data.get('first_name', user.first_name)
                user.last_name = data.get('last_name', user.last_name)
                user.phone_number = phone  # Map form field 'phone' to User field 'phone_number'
                
                # Update additional fields if provided
                if data.get('date_of_birth'):
                    user.date_of_birth = data.get('date_of_birth')
                if id_number:  # Map form field 'id_number' to User field 'national_id'
                    user.national_id = id_number
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
                        phone_number=phone,  # Map form field 'phone' to User field 'phone_number'
                    )
                    
                    # Set additional fields
                    if data.get('date_of_birth'):
                        user.date_of_birth = data.get('date_of_birth')
                    if id_number:  # Map form field 'id_number' to User field 'national_id'
                        user.national_id = id_number
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
            
            # Determine loan type based on purpose FIRST, then amount
            loan_amount = float(data.get('loan_amount', 0))
            loan_purpose = data.get('loan_purpose', '').lower()
            
            # Priority 1: Business loans (any amount)
            if 'business' in loan_purpose:
                loan_type = 'BUSINESS'
            # Priority 2: Emergency loans
            elif 'emergency' in loan_purpose:
                loan_type = 'EMERGENCY'
            # Priority 3: Education loans (education-related purposes)
            elif any(keyword in loan_purpose for keyword in ['education', 'school', 'tuition', 'student', 'course', 'training']):
                loan_type = 'EDUCATION'
            # Priority 4: Amount-based classification (Quick Cash for smaller amounts)
            elif loan_amount <= 25000:
                loan_type = 'QUICK_CASH'
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
                    'redirect_url': f"/loans/application/{loan.id}/"
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
        
        # Import here to avoid circular imports
        try:
            from apps.core.models import Company
            company = Company.get_default_company()
            context['company'] = company
            context['last_updated'] = f'{company.loan_agreement_version} - {timezone.now().strftime("%B %Y")}'
        except ImportError:
            # Fallback if model doesn't exist yet
            from django.conf import settings
            context['company'] = {
                'company_name': getattr(settings, 'FLEXIFINANCE_CONFIG', {}).get('COMPANY_NAME', 'FlexiFinance Limited'),
                'license_number': 'P05123456789',
                'cbk_registration': 'CBK/RG/234567',
                'default_interest_rate': getattr(settings, 'DEFAULT_INTEREST_RATE', 12.5),
                'late_fee_fixed': 500.00,
                'late_fee_percentage': 2.0,
                'disbursement_timeframe_days': 3,
                'arbitration_rules': 'Kenyan Centre for Arbitration Rules',
                'governing_law': 'Laws of Kenya',
                'jurisdiction': 'Nairobi, Kenya',
            }
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

@csrf_exempt
@require_http_methods(["POST"])
def submit_contact_form(request):
    """Handle contact form submission with fallback mechanism"""
    try:
        # Parse JSON data
        data = json.loads(request.body)
        logger.info(f"Contact form submission received: {list(data.keys())}")  # Debug logging
        
        # Validate required fields
        required_fields = ['name', 'email', 'message']
        for field in required_fields:
            if not data.get(field):
                logger.warning(f"Missing required field: {field}")  # Debug logging
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
        
        # Store contact form data in local database
        # You can create a Contact model for this, for now we'll log it
        try:
            from apps.core.models import Contact
            contact = Contact.objects.create(
                name=contact_data['name'],
                email=contact_data['email'],
                phone=contact_data.get('phone', ''),
                message=contact_data['message'],
                subject=contact_data['subject'],
                source=contact_data['source'],
                ip_address=contact_data['ip_address'],
                user_agent=contact_data['user_agent'],
            )
            logger.info(f"Contact form saved to database with ID: {contact.id}")
            db_success = True
        except ImportError:
            # If Contact model doesn't exist, just log the data
            logger.info(f"Contact form data (model not found): {contact_data}")
            db_success = False
        except Exception as e:
            logger.warning(f"Database contact form storage failed: {str(e)}")
            db_success = False
        
        # Try to send email notification, but continue even if it fails
        email_success = False
        try:
            resend_service = ResendEmailService()
            email_result = resend_service.send_contact_notification(contact_data)
            email_success = email_result if isinstance(email_result, bool) else True
        except Exception as e:
            logger.warning(f"Email notification failed: {str(e)}")
        
        # Always return success since we've captured the data
        logger.info(f"Contact form processed for {contact_data['email']} (Database: {db_success}, Email: {email_success})")
        
        response_data = {
            'success': True,
            'message': 'Thank you for your message. We will get back to you within 24 hours.',
            'data': {
                'submitted_at': contact_data['created_at'],
                'reference_id': f'CF-{int(datetime.now().timestamp())}'  # Simple reference ID
            }
        }
        logger.info(f"Sending success response: {response_data}")  # Debug logging
        return JsonResponse(response_data)
            
    except json.JSONDecodeError:
        logger.error("Contact form: Invalid JSON data received")  # Debug logging
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
        
        # Check email service
        email_status = False
        try:
            resend_service = ResendEmailService()
            email_status = resend_service.health_check()
        except Exception as e:
            logger.warning(f"Email service health check failed: {str(e)}")
        
        health_data = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'services': {
                'database': 'connected',
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

@csrf_exempt
@require_http_methods(["POST"])
def newsletter_subscribe(request):
    """Handle newsletter subscription with form validation"""
    try:
        # Parse JSON data
        data = json.loads(request.body)
        
        from .forms import NewsletterSubscriptionForm
        from .models import NewsletterSubscription
        
        # Create form with data
        form = NewsletterSubscriptionForm(data)
        
        if form.is_valid():
            email = form.cleaned_data['email'].lower()
            first_name = form.cleaned_data.get('first_name', '')
            last_name = form.cleaned_data.get('last_name', '')
            interests = form.cleaned_data.get('interests', [])
            
            # Check if subscription already exists
            try:
                subscription = NewsletterSubscription.objects.get(email=email)
                if subscription.is_active:
                    return JsonResponse({
                        'success': False,
                        'error': 'This email is already subscribed to our newsletter.'
                    }, status=400)
                else:
                    # Reactivate existing subscription
                    subscription.is_active = True
                    subscription.first_name = first_name
                    subscription.last_name = last_name
                    subscription.interests = interests
                    subscription.ip_address = request.META.get('REMOTE_ADDR', '')
                    subscription.user_agent = request.META.get('HTTP_USER_AGENT', '')
                    subscription.save()
                    
                    logger.info(f"Reactivated newsletter subscription: {email}")
                    
            except NewsletterSubscription.DoesNotExist:
                # Create new subscription
                subscription = NewsletterSubscription.objects.create(
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    interests=interests,
                    source='website_footer',
                    ip_address=request.META.get('REMOTE_ADDR', ''),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
                logger.info(f"New newsletter subscription: {email}")
            
            # Send welcome email (optional)
            try:
                resend_service = ResendEmailService()
                welcome_data = {
                    'email': email,
                    'first_name': first_name,
                    'interests': interests,
                    'subscription_date': subscription.subscribed_at.isoformat()
                }
                # You can implement a welcome email function here
                # resend_service.send_welcome_email(welcome_data)
            except Exception as e:
                logger.warning(f"Welcome email failed: {str(e)}")
            
            return JsonResponse({
                'success': True,
                'message': 'Thank you for subscribing to our newsletter!',
                'data': {
                    'subscribed_at': subscription.subscribed_at.isoformat(),
                    'email': subscription.email
                }
            })
        else:
            # Return form errors
            errors = {}
            for field, error_list in form.errors.items():
                errors[field] = str(error_list[0])
            
            return JsonResponse({
                'success': False,
                'error': 'Please correct the errors below.',
                'errors': errors
            }, status=400)
        
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