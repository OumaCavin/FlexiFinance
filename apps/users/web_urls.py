"""
Web URLs for FlexiFinance Users
URL patterns for user authentication and dashboard
"""

from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    
    # Loan-related URLs
    path('my-loans/', views.my_loans, name='my_loans'),
]