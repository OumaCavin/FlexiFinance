"""
Document management API URLs for FlexiFinance
URL patterns for document API endpoints
"""

from django.urls import path
from . import views

app_name = 'documents_api'  # Different namespace for API

urlpatterns = [
    # Document API Endpoints
    path('status/', views.document_status_api, name='api_status'),
    path('upload/', views.api_document_upload, name='api_upload'),
    
    # Root API endpoint
    path('', views.document_status_api, name='api_root'),
]