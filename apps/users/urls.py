"""
Web URLs for FlexiFinance Users
URL patterns for user authentication and dashboard
"""

from django.urls import path
from apps.users import views

app_name = 'dashboard'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    
    # Email Verification
    path('verify-email/<str:uidb64>/<str:token>/', views.EmailVerificationView.as_view(), name='verify_email'),
    path('resend-verification/', views.resend_verification_email, name='resend_verification'),
    
    # KYC Management (admin only)
    path('update-kyc/', views.update_kyc_status, name='update_kyc_status'),
    
    # Loan-related URLs
    path('my-loans/', views.my_loans, name='my_loans'),
    path('payment-history/', views.payment_history, name='payment_history'),
    
    # Test endpoint for debugging profile forms
    path('test-profile/', views.test_profile_forms, name='test_profile_forms'),
    
    # Handle form submissions from test_profile page
    path('test-profile-submit/', views.test_profile_form_submit, name='test_profile_form_submit'),
    
    # Debug endpoint to check form fields
    path('debug-form-fields/', views.debug_form_fields, name='debug_form_fields'),
    
    # Simple test endpoint for form saving
    path('test-form-save/', views.test_form_save, name='test_form_save'),
]