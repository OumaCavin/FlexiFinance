"""
Health check URLs for FlexiFinance
Separate URL configuration to avoid namespace conflicts
"""

from django.urls import path
from . import views

app_name = 'health'

urlpatterns = [
    # Health check endpoints
    path('', views.health_check, name='check'),
]