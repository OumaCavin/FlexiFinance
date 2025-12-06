"""
URL patterns for Payments app
"""
from django.urls import path, include
from apps.payments import api_urls

app_name = 'payments_main'

urlpatterns = [
    # API endpoints
    path('', include(api_urls)),
]