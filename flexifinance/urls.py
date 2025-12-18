"""
FlexiFinance URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views
from apps.core import views
from apps.users.views import register_view, custom_login_view  # Import for custom login

# Admin site customization
admin.site.site_header = "FlexiFinance Administration"
admin.site.site_title = "FlexiFinance Admin"
admin.site.index_title = "FlexiFinance Dashboard"

urlpatterns = [
    # Admin interface
    path(settings.ADMIN_URL, admin.site.urls),
    
    # User authentication (Django built-in auth)
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('accounts/reset/<str:uidb64>/<str:token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('accounts/password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('accounts/password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    
    # Custom login URL to handle unverified users
    path('accounts/login/', custom_login_view, name='login'),
    
    # Custom registration route
    path('accounts/signup/', register_view, name='signup'),
    
    # Redirect /accounts/profile/ to /dashboard/profile/ for user convenience
    path('accounts/profile/', RedirectView.as_view(url='/dashboard/profile/', permanent=True)),
    
    # Main website pages (including contact)
    path('', include('apps.core.urls')),
    
    # Additional website pages
    path('about/', views.AboutView.as_view(), name='about'),
    path('how-it-works/', views.HowItWorksView.as_view(), name='how_it_works'),
    path('support/', views.SupportView.as_view(), name='support'),
    path('faq/', views.FAQView.as_view(), name='faq'),
    path('products/', views.LoanProductsView.as_view(), name='loan_products'),
    path('personal-loans/', views.PersonalLoansView.as_view(), name='personal_loans'),
    path('quick-cash-loans/', views.QuickCashLoansView.as_view(), name='quick_cash_loans'),
    path('business-loans/', views.BusinessLoansView.as_view(), name='business_loans'),
    path('emergency-loans/', views.EmergencyLoansView.as_view(), name='emergency_loans'),
    path('education-loans/', views.EducationLoansView.as_view(), name='education_loans'),
    path('loan-calculator/', views.LoanCalculatorView.as_view(), name='loan_calculator'),
    


    
    # Legal and company pages
    path('privacy-policy/', views.PrivacyPolicyView.as_view(), name='privacy_policy'),
    path('terms-of-service/', views.TermsOfServiceView.as_view(), name='terms_of_service'),
    path('loan-agreement/', views.LoanAgreementView.as_view(), name='loan_agreement'),
    path('careers/', views.CareersView.as_view(), name='careers'),
    path('press/', views.PressView.as_view(), name='press'),
    path('blog/', views.BlogView.as_view(), name='blog'),
    path('investors/', views.InvestorsView.as_view(), name='investors'),
    path('partners/', views.PartnersView.as_view(), name='partners'),
    
    # Newsletter subscription endpoint
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),
    
    # API endpoints
    path('api/v1/users/', include('apps.users.api_urls')),
    path('api/v1/loans/', include('apps.loans.urls')),
    path('api/v1/payments/', include('apps.payments.urls')),
    path('api/v1/notifications/', include('apps.notifications.urls')),
    path('api/v1/documents/', include('apps.documents.api_urls')),
    
    # Web URLs
    path('dashboard/', include('apps.users.urls')),
    path('loans/', include('apps.loans.web_urls')),
    path('payments/', include('apps.payments.web_urls')),
    
    # Document Management URLs
    path('documents/', include('apps.documents.urls')),
    
    # Health check endpoints
    path('health/', include('apps.core.health_urls')),
    

]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Django Debug Toolbar
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]

# Custom error handlers
handler404 = views.handler404
handler500 = views.handler500
handler403 = views.handler403
handler400 = views.handler400
