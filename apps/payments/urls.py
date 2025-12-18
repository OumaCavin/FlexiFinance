"""
URL patterns for Payments app
"""
from django.urls import path, include
from apps.payments import api_urls

urlpatterns = [
    # API endpoints
    path('', include(api_urls)),
]