"""
Document management URLs for FlexiFinance
URL patterns for document upload, verification, and management
"""

from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    # Root path for documents dashboard
    path('', views.document_list, name='list'),
    
    # Document Management for Users
    path('upload/', views.document_upload, name='upload'),
    path('list/', views.document_list, name='list'),
    path('detail/<int:document_id>/', views.document_detail, name='detail'),
    path('download/<int:document_id>/', views.document_download, name='download'),
    path('delete/<int:document_id>/', views.document_delete, name='delete'),
    
    # Document Verification for Staff
    path('verify/<int:document_id>/', views.document_verification, name='verify'),
    
    # Analytics and Reporting
    path('analytics/', views.document_analytics, name='analytics'),
    
    # API Endpoints
    path('api/status/', views.document_status_api, name='api_status'),
    path('api/upload/', views.api_document_upload, name='api_upload'),
    
    # Additional utility paths
    path('api/', views.document_status_api, name='api_root'),
]