"""
URL patterns for Users app
"""
from django.urls import path, include
from apps.users import api_urls

app_name = 'users'

urlpatterns = [
    # API endpoints
    path('', include(api_urls)),
]