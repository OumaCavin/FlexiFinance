"""
Core URLs for FlexiFinance - Kenyan MicroFinance Platform
URL patterns for main website pages
"""

from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Main website pages
    path('', views.HomeView.as_view(), name='home'),
    path('home/', views.HomeView.as_view(), name='home_page'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    
    # API endpoints for frontend
    path('api/contact/submit/', views.submit_contact_form, name='submit_contact'),
    path('api/health/', views.health_check, name='health_check'),
    path('api/config/', views.get_public_config, name='public_config'),
]