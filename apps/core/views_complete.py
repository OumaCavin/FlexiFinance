"""
Core Views for FlexiFinance
All website pages and functionality
"""

from django.shortcuts import render, redirect
from django.views.generic import TemplateView, FormView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.conf import settings
from django.urls import reverse_lazy
import json
import logging

# Configure logging
logger = logging.getLogger(__name__)

class HomeView(TemplateView):
    """Home page view"""
    template_name = 'home.html'
    
    def get(self, request, *args, **kwargs):
        context = {
            'featured_products': self.get_featured_products(),
            'testimonials': self.get_testimonials(),
            'stats': self.get_company_stats(),
        }
        return render(request, self.template_name, context)
    
    def get_featured_products(self):
        """Get featured loan products"""
        return [
            {
                'name': 'Quick Cash Loan',
                'amount': 'KES 1,000 - 20,000',
                'term': '1-6 months',
                'rate': '15% APR',
                'features': ['Fast approval', 'No collateral', 'Flexible repayment']
            },
            {
                'name': 'Business Loan',
                'amount': 'KES 10,000 - 100,000',
                'term': '3-12 months',
                'rate': '12% APR',
                'features': ['Business growth', 'Low interest', 'Expert support']
            },
            {
                'name': 'Emergency Loan',
                'amount': 'KES 500 - 5,000',
                'term': '1-3 months',
                'rate': '18% APR',
                'features': ['24-hour approval', 'Minimal paperwork', 'Instant disbursement']
            }
        ]
    
    def get_testimonials(self):
        """Get customer testimonials"""
        return [
            {
                'name': 'Grace Wanjiku',
                'business': 'Retail Shop Owner',
                'content': 'FlexiFinance helped me expand my business when traditional banks said no. The process was smooth and the support team was excellent.',
                'rating': 5
            },
            {
                'name': 'James Kiprotich',
                'business': 'Farmer',
                'content': 'Got the funds I needed for farm inputs within 24 hours. Highly recommend their emergency loan service.',
                'rating': 5
            },
            {
                'name': 'Mary Akinyi',
                'business': 'Teacher',
                'content': 'Their loan calculator helped me plan my finances perfectly. Great service and transparent terms.',
                'rating': 5
            }
        ]
    
    def get_company_stats(self):
        """Get company statistics"""
        return {
            'loans_disbursed': '10,000+',
            'approval_rate': '95%',
            'satisfied_customers': '8,500+',
            'average_processing': '24 hours'
        }

class AboutView(TemplateView):
    """About page view"""
    template_name = 'about.html'
    
    def get(self, request, *args, **kwargs):
        context = {
            'mission': 'To provide accessible, fast, and transparent financial solutions to individuals and small businesses across Kenya.',
            'vision': 'To be the leading microfinance platform in East Africa, empowering communities through financial inclusion.',
            'values': [
                'Transparency in all our dealings',
                'Customer-first approach',
                'Innovation in financial services',
                'Social responsibility',
                'Integrity and trust'
            ],
            'team': self.get_team_members(),
            'milestones': self.get_company_milestones()
        }
        return render(request, self.template_name, context)
    
    def get_team_members(self):
        """Get team member information"""
        return [
            {
                'name': 'David Kimani',
                'position': 'Chief Executive Officer',
                'bio': '15+ years in banking and fintech',
                'image': '/static/images/team/david.jpg'
            },
            {
                'name': 'Grace Mutua',
                'position': 'Head of Operations',
                'bio': 'Expert in microfinance operations',
                'image': '/static/images/team/grace.jpg'
            },
            {
                'name': 'John Omondi',
                'position': 'Chief Technology Officer',
                'bio': 'Software engineer and fintech innovator',
                'image': '/static/images/team/john.jpg'
            }
        ]
    
    def get_company_milestones(self):
        """Get company milestones"""
        return [
            {'year': '2020', 'event': 'Company founded'},
            {'year': '2021', 'event': 'First 1,000 customers'},
            {'year': '2022', 'event': 'M-Pesa integration'},
            {'year': '2023', 'event': 'KES 100M disbursed'},
            {'year': '2024', 'event': '10,000+ loans approved'},
            {'year': '2025', 'event': 'Expanding to Uganda'}
        ]

class HowItWorksView(TemplateView):
    """How it works page view"""
    template_name = 'how-it-works.html'
    
    def get(self, request, *args, **kwargs):
        context = {
            'steps': self.get_process_steps(),
            'requirements': self.get_requirements(),
            'faq': self.get_faq()
        }
        return render(request, self.template_name, context)
    
    def get_process_steps(self):
        """Get the loan application process steps"""
        return [
            {
                'number': '01',
                'title': 'Apply Online',
                'description': 'Complete our simple online application form with your details and loan requirements.',
                'icon': 'fas fa-edit',
                'duration': '5 minutes'
            },
            {
                'number': '02',
                'title': 'Document Verification',
                'description': 'Our team reviews your documents and verifies your information for quick approval.',
                'icon': 'fas fa-shield-alt',
                'duration': '2-4 hours'
            },
            {
                'number': '03',
                'title': 'Get Approved',
                'description': 'Once approved, receive your funds directly to your M-Pesa or bank account.',
                'icon': 'fas fa-check-circle',
                'duration': '24 hours'
            }
        ]
    
    def get_requirements(self):
        """Get loan requirements"""
        return {
            'basic_requirements': [
                'Valid Kenyan ID',
                '18 years and above',
                'Active M-Pesa number',
                'Regular income source'
            ],
            'documents': [
                'National ID (copy)',
                'KRA PIN certificate',
                'Bank statements (3 months)',
                'Employment letter/income proof'
            ]
        }
    
    def get_faq(self):
        """Get frequently asked questions"""
        return [
            {
                'question': 'How long does it take to get approved?',
                'answer': 'Most applications are approved within 24 hours. Emergency loans can be approved within 2-4 hours.'
            },
            {
                'question': 'What is the maximum loan amount I can get?',
                'answer': 'New customers can get up to KES 20,000. Returning customers with good credit history can access up to KES 500,000.'
            },
            {
                'question': 'Do you charge any hidden fees?',
                'answer': 'No, we are transparent about all costs. The only fees are the interest rate and a small processing fee (2% of loan amount).'
            },
            {
                'question': 'Can I pay my loan early?',
                'answer': 'Yes, you can pay your loan early without any penalty charges. This will also improve your credit score for future loans.'
            }
        ]

class SupportView(TemplateView):
    """Support page view"""
    template_name = 'support.html'
    
    def get(self, request, *args, **kwargs):
        context = {
            'contact_methods': self.get_contact_methods(),
            'support_hours': 'Monday - Friday: 8:00 AM - 6:00 PM<br>Saturday: 9:00 AM - 4:00 PM<br>Sunday: Closed',
            'help_topics': self.get_help_topics()
        }
        return render(request, self.template_name, context)
    
    def get_contact_methods(self):
        """Get available contact methods"""
        return [
            {
                'type': 'Phone',
                'value': '+254 708 101 604',
                'description': 'Call us for immediate assistance',
                'icon': 'fas fa-phone'
            },
            {
                'type': 'Email',
                'value': 'support@flexifinance.com',
                'description': 'Send us an email and we\'ll respond within 2 hours',
                'icon': 'fas fa-envelope'
            },
            {
                'type': 'WhatsApp',
                'value': '+254 708 101 604',
                'description': 'Chat with us on WhatsApp',
                'icon': 'fab fa-whatsapp'
            },
            {
                'type': 'Live Chat',
                'value': 'Available on our website',
                'description': 'Chat with our support team in real-time',
                'icon': 'fas fa-comments'
            }
        ]
    
    def get_help_topics(self):
        """Get help topics"""
        return [
            {
                'category': 'Account Management',
                'topics': ['Login issues', 'Password reset', 'Account verification', 'Profile updates']
            },
            {
                'category': 'Loans',
                'topics': ['Loan application', 'Approval status', 'Loan terms', 'Repayment']
            },
            {
                'category': 'Payments',
                'topics': ['M-Pesa integration', 'Bank transfers', 'Payment methods', 'Late payments']
            },
            {
                'category': 'Technical',
                'topics': ['Website issues', 'Mobile app', 'Data security', 'Technical support']
            }
        ]

class FAQView(TemplateView):
    """FAQ page view"""
    template_name = 'faq.html'

class LoanProductsView(TemplateView):
    """Loan products page view"""
    template_name = 'products/loan-products.html'
    
    def get(self, request, *args, **kwargs):
        context = {
            'products': self.get_all_products(),
            'comparison_table': self.get_comparison_data()
        }
        return render(request, self.template_name, context)
    
    def get_all_products(self):
        """Get all available loan products"""
        return [
            {
                'id': 'quick_cash',
                'name': 'Quick Cash Loan',
                'short_description': 'Fast approval loans for urgent needs',
                'amount_range': 'KES 1,000 - 20,000',
                'term_range': '1 - 6 months',
                'interest_rate': '15% APR',
                'processing_fee': '2%',
                'approval_time': '24 hours',
                'features': [
                    'Same-day approval',
                    'No collateral required',
                    'Flexible repayment',
                    'M-Pesa disbursement'
                ],
                'eligibility': [
                    '18+ years old',
                    'Kenyan citizen',
                    'Regular income',
                    'Active M-Pesa'
                ]
            },
            {
                'id': 'business_loan',
                'name': 'Business Loan',
                'short_description': 'Grow your business with flexible funding',
                'amount_range': 'KES 10,000 - 100,000',
                'term_range': '3 - 12 months',
                'interest_rate': '12% APR',
                'processing_fee': '2%',
                'approval_time': '48 hours',
                'features': [
                    'Business growth funding',
                    'Lower interest rates',
                    'Flexible repayment terms',
                    'Business support services'
                ],
                'eligibility': [
                    'Registered business',
                    '6+ months operation',
                    'Business bank statements',
                    'KRA compliance'
                ]
            },
            {
                'id': 'emergency_loan',
                'name': 'Emergency Loan',
                'short_description': 'Quick access to funds during emergencies',
                'amount_range': 'KES 500 - 5,000',
                'term_range': '1 - 3 months',
                'interest_rate': '18% APR',
                'processing_fee': '2%',
                'approval_time': '2-4 hours',
                'features': [
                    'Fastest approval',
                    'Minimal paperwork',
                    'Instant disbursement',
                    'Emergency support'
                ],
                'eligibility': [
                    '18+ years old',
                    'Valid ID',
                    'Active phone number',
                    'Emergency documentation'
                ]
            }
        ]
    
    def get_comparison_data(self):
        """Get product comparison table data"""
        return [
            {
                'feature': 'Loan Amount',
                'quick_cash': 'KES 1,000 - 20,000',
                'business_loan': 'KES 10,000 - 100,000',
                'emergency_loan': 'KES 500 - 5,000'
            },
            {
                'feature': 'Repayment Period',
                'quick_cash': '1-6 months',
                'business_loan': '3-12 months',
                'emergency_loan': '1-3 months'
            },
            {
                'feature': 'Interest Rate',
                'quick_cash': '15% APR',
                'business_loan': '12% APR',
                'emergency_loan': '18% APR'
            },
            {
                'feature': 'Approval Time',
                'quick_cash': '24 hours',
                'business_loan': '48 hours',
                'emergency_loan': '2-4 hours'
            },
            {
                'feature': 'Collateral Required',
                'quick_cash': 'No',
                'business_loan': 'No',
                'emergency_loan': 'No'
            },
            {
                'feature': 'M-Pesa Support',
                'quick_cash': 'Yes',
                'business_loan': 'Yes',
                'emergency_loan': 'Yes'
            }
        ]

class BusinessLoansView(TemplateView):
    """Business loans page view"""
    template_name = 'products/business-loans.html'

class EmergencyLoansView(TemplateView):
    """Emergency loans page view"""
    template_name = 'products/emergency-loans.html'

class LoanCalculatorView(TemplateView):
    """Loan calculator page view"""
    template_name = 'loan-calculator.html'

class LoanApplicationView(TemplateView):
    """Loan application page view"""
    template_name = 'loan-application.html'

# Legal Pages
class PrivacyPolicyView(TemplateView):
    """Privacy Policy page view"""
    template_name = 'privacy_policy.html'

class TermsOfServiceView(TemplateView):
    """Terms of Service page view"""
    template_name = 'terms_of_service.html'

class LoanAgreementView(TemplateView):
    """Loan Agreement page view"""
    template_name = 'loan_agreement.html'

class CareersView(TemplateView):
    """Careers page view"""
    template_name = 'careers.html'

class PressView(TemplateView):
    """Press page view"""
    template_name = 'press.html'

class BlogView(TemplateView):
    """Blog page view"""
    template_name = 'blog.html'

class InvestorsView(TemplateView):
    """Investors page view"""
    template_name = 'investors.html'

class PartnersView(TemplateView):
    """Partners page view"""
    template_name = 'partners.html'

# Utility Views
def newsletter_subscribe(request):
    """Newsletter subscription handler"""
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            # Add email to newsletter list
            messages.success(request, 'Thank you for subscribing to our newsletter!')
            logger.info(f'Newsletter subscription: {email}')
        else:
            messages.error(request, 'Please provide a valid email address.')
        return redirect('home')
    return redirect('home')

# Error Handlers
def handler404(request, exception):
    """Custom 404 error handler"""
    return render(request, '404.html', status=404)

def handler500(request):
    """Custom 500 error handler"""
    return render(request, '500.html', status=500)

def handler403(request, exception):
    """Custom 403 error handler"""
    return render(request, '403.html', status=403)

def handler400(request, exception):
    """Custom 400 error handler"""
    return render(request, '400.html', status=400)