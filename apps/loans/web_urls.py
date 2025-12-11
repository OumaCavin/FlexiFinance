"""
Web URLs for FlexiFinance Loans
URL patterns for loan web interface
"""
from django.urls import path
from . import web_views

app_name = 'loans'

urlpatterns = [
    # Loan Application Form
    path('apply/', web_views.loan_application, name='loan_application'),
    
    # Loan Details (Redirect destination)
    path('application/<uuid:loan_id>/', web_views.loan_detail, name='loan_detail'),
    
    # List of loans
    path('my-loans/', web_views.my_loans, name='my_loans'),
]