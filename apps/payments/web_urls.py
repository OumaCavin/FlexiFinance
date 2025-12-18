"""
Web URLs for FlexiFinance Payments
URL patterns for web interfaces and payment processing
"""

from django.urls import path
from . import views

app_name = 'payments_web'

urlpatterns = [
    # M-PESA webhook endpoints
    path('webhooks/mpesa/callback/', views.mpesa_callback, name='mpesa_callback'),
    path('webhooks/mpesa/validate/', views.mpesa_validation, name='mpesa_validation'),
    
    # Stripe webhook endpoints  
    path('webhooks/stripe/', views.stripe_webhook, name='stripe_webhook'),
    
    # Payment status check
    path('status/<str:provider>/<str:transaction_id>/', views.payment_status_check, name='payment_status'),
]