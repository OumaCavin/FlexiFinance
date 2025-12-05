"""
URL patterns for Payments API
"""
from django.urls import path
from apps.payments.api import views

app_name = 'payments'

urlpatterns = [
    # M-Pesa callbacks (public endpoints)
    path('mpesa/callback/', views.MpesaCallbackView.as_view(), name='mpesa-callback'),
    path('mpesa/validate/', views.MpesaValidationView.as_view(), name='mpesa-validation'),
    
    # Payment endpoints (authenticated)
    path('stk-push/', views.InitiateSTKPushView.as_view(), name='initiate-stk-push'),
    path('history/', views.PaymentHistoryView.as_view(), name='payment-history'),
    path('<uuid:payment_id>/status/', views.PaymentStatusView.as_view(), name='payment-status'),
    
    # Test endpoints
    path('test/', views.TestMpesaView.as_view(), name='test-mpesa'),
]

# Additional URLs for function-based views
function_based_urls = [
    path('stk-push/simple/', views.initiate_stk_push, name='initiate-stk-push-simple'),
    path('<uuid:payment_id>/status/simple/', views.payment_status, name='payment-status-simple'),
    path('history/simple/', views.payment_history, name='payment-history-simple'),
    path('test/simple/', views.test_mpesa, name='test-mpesa-simple'),
]

urlpatterns.extend(function_based_urls)