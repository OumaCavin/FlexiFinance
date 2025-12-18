"""
Document management views for FlexiFinance
Comprehensive document upload, verification, and management functionality
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden, FileResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError, PermissionDenied
from django.core.paginator import Paginator
from django.utils import timezone
from django.conf import settings
import json
import logging
from datetime import datetime, timedelta
import mimetypes

from .models import Document, DocumentType, DocumentVerification, DocumentAccessLog
from apps.users.models import User

logger = logging.getLogger(__name__)


@login_required
def document_upload(request):
    """Handle document upload for authenticated users"""
    if request.method == 'GET':
        return render_upload_form(request)
    elif request.method == 'POST':
        return handle_document_upload(request)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


def render_upload_form(request):
    """Render the document upload form"""
    # Get document types available for the user
    if request.user.is_staff:
        # Staff can upload any document type
        document_types = DocumentType.objects.all()
    else:
        # Regular users see document types relevant to their status
        document_types = DocumentType.objects.filter(
            required_for__in=['KYC', 'LOAN_APPLICATION', 'INCOME_PROOF', 'ADDRESS_PROOF', 'EMPLOYMENT_PROOF']
        )
    
    # Get user's existing documents
    user_documents = Document.objects.filter(user=request.user)
    
    return render(request, 'documents/upload.html', {
        'document_types': document_types,
        'user_documents': user_documents,
        'max_file_size': max(dt.max_file_size for dt in document_types) if document_types else 10485760,
        'allowed_extensions': ','.join([ext for dt in document_types for ext in dt.get_allowed_extensions_list()])
    })


def handle_document_upload(request):
    """Handle document upload POST request"""
    logger.info(f"=== DOCUMENT UPLOAD START ===")
    logger.info(f"User: {request.user.email if hasattr(request.user, 'email') else 'Anonymous'}")
    logger.info(f"Method: {request.method}")
    logger.info(f"POST keys: {list(request.POST.keys())}")
    logger.info(f"FILES keys: {list(request.FILES.keys())}")
    
    try:
        # Validate required fields
        document_type_id = request.POST.get('document_type')
        if not document_type_id:
            return JsonResponse({'error': 'Document type is required'}, status=400)
        
        # Get document type
        document_type = get_object_or_404(DocumentType, id=document_type_id)
        
        # Check if user can upload this document type
        if not request.user.is_staff:
            allowed_types = ['KYC', 'LOAN_APPLICATION', 'INCOME_PROOF', 'ADDRESS_PROOF', 'EMPLOYMENT_PROOF']
            if document_type.required_for not in allowed_types:
                return JsonResponse({'error': 'Invalid document type'}, status=400)
        
        # Get uploaded file
        uploaded_file = request.FILES.get('document')
        if not uploaded_file:
            return JsonResponse({'error': 'No file uploaded'}, status=400)
        
        # Validate file
        validate_uploaded_file(uploaded_file, document_type)
        
        # Check for existing documents of same type
        existing_docs = Document.objects.filter(
            user=request.user,
            document_type=document_type,
            status__in=['PENDING', 'APPROVED', 'AUTO_APPROVED']
        )
        
        if existing_docs.exists() and not request.user.is_staff:
            return JsonResponse({
                'error': f'You already have a {document_type.name} document. Please wait for approval or contact support.'
            }, status=400)
        
        # Create document record
        document = Document.objects.create(
            user=request.user,
            document_type=document_type,
            file=uploaded_file,
            original_filename=uploaded_file.name,
            file_size=uploaded_file.size,
            expires_at=get_expiry_date(document_type)
        )
        
        # Log access
        log_document_access(request, document, 'UPLOAD')
        
        # Create verification record if manual verification required
        if document_type.verification_required:
            DocumentVerification.objects.create(
                document=document,
                verifier=request.user,  # Self-upload
                verification_type='MANUAL'
            )
        
        logger.info(f"Document uploaded: {document} by {request.user.email}")
        
        return JsonResponse({
            'success': True,
            'document_id': document.id,
            'message': f'{document_type.name} uploaded successfully',
            'status': document.get_status_display(),
            'auto_approved': document_type.auto_approve
        })
        
    except ValidationError as e:
        logger.error(f"Validation error in document upload: {str(e)} for user {request.user.email}")
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        logger.error(f"Document upload error for user {request.user.email}: {str(e)}", exc_info=True)
        return JsonResponse({'error': f'Upload failed: {str(e)}. Please try again.'}, status=500)


@login_required
def document_list(request):
    """Display user's documents with filtering and pagination"""
    documents = Document.objects.filter(user=request.user).select_related('document_type')
    
    # Apply filters
    status_filter = request.GET.get('status')
    if status_filter:
        documents = documents.filter(status=status_filter)
    
    type_filter = request.GET.get('type')
    if type_filter:
        documents = documents.filter(document_type_id=type_filter)
    
    # Pagination
    paginator = Paginator(documents, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get document types for filter dropdown
    document_types = DocumentType.objects.all()
    
    return render(request, 'documents/list.html', {
        'page_obj': page_obj,
        'document_types': document_types,
        'current_status': status_filter,
        'current_type': type_filter
    })


@login_required
def document_detail(request, document_id):
    """Display document details"""
    document = get_object_or_404(Document, id=document_id)
    
    # Check permission
    if document.user != request.user and not request.user.is_staff:
        raise PermissionDenied("You don't have permission to view this document")
    
    # Log access
    log_document_access(request, document, 'VIEW')
    
    return render(request, 'documents/detail.html', {
        'document': document
    })


@login_required
def document_download(request, document_id):
    """Handle secure document download"""
    document = get_object_or_404(Document, id=document_id)
    
    # Check permission
    if document.user != request.user and not request.user.is_staff:
        raise PermissionDenied("You don't have permission to download this document")
    
    # Check if document is approved
    if document.status not in ['APPROVED', 'AUTO_APPROVED'] and not request.user.is_staff:
        return HttpResponseForbidden("Document not approved for download")
    
    # Check if document is expired
    if document.expires_at and timezone.now() > document.expires_at:
        return HttpResponseForbidden("Document has expired")
    
    try:
        # Increment download count
        document.increment_download_count()
        
        # Log access
        log_document_access(request, document, 'DOWNLOAD')
        
        # Serve file
        response = FileResponse(document.file.open('rb'))
        response['Content-Type'] = mimetypes.guess_type(document.file.name)[0] or 'application/octet-stream'
        response['Content-Disposition'] = f'attachment; filename="{document.original_filename}"'
        
        logger.info(f"Document downloaded: {document} by {request.user.email}")
        return response
        
    except Exception as e:
        logger.error(f"Document download error: {str(e)}")
        return HttpResponse("File not found", status=404)


@login_required
@require_http_methods(["POST"])
def document_delete(request, document_id):
    """Handle document deletion"""
    document = get_object_or_404(Document, id=document_id)
    
    # Check permission
    if document.user != request.user and not request.user.is_staff:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    # Check if document can be deleted
    if document.status == 'APPROVED' and not request.user.is_staff:
        return JsonResponse({
            'error': 'Approved documents cannot be deleted. Contact support.'
        }, status=400)
    
    # Log access
    log_document_access(request, document, 'DELETE')
    
    # Delete file and record
    document.file.delete(save=False)
    document.delete()
    
    logger.info(f"Document deleted: {document} by {request.user.email}")
    
    return JsonResponse({'success': True, 'message': 'Document deleted successfully'})


@login_required
def document_verification(request, document_id):
    """Admin view for document verification"""
    if not request.user.is_staff:
        raise PermissionDenied("Staff access required")
    
    document = get_object_or_404(Document, id=document_id)
    
    if request.method == 'GET':
        return render_verification_form(request, document)
    elif request.method == 'POST':
        return handle_verification_action(request, document)
    
    return JsonResponse({'error': 'Invalid method'}, status=405)


def render_verification_form(request, document):
    """Render document verification form for staff"""
    return render(request, 'documents/verify.html', {
        'document': document,
        'verification': getattr(document, 'verification', None)
    })


def handle_verification_action(request, document):
    """Handle document verification actions"""
    action = request.POST.get('action')
    notes = request.POST.get('notes', '')
    
    try:
        if action == 'approve':
            document.approve(request.user, notes)
            message = 'Document approved successfully'
        elif action == 'reject':
            reason = request.POST.get('reason', 'Rejected by admin')
            document.reject(reason, request.user, notes)
            message = 'Document rejected successfully'
        else:
            return JsonResponse({'error': 'Invalid action'}, status=400)
        
        # Log verification
        log_document_access(request, document, f'VERIFY_{action.upper()}')
        
        logger.info(f"Document {action}ed: {document} by {request.user.email}")
        
        return JsonResponse({
            'success': True,
            'message': message,
            'new_status': document.get_status_display()
        })
        
    except Exception as e:
        logger.error(f"Verification error: {str(e)}")
        return JsonResponse({'error': 'Verification failed'}, status=500)


@login_required
def document_status_api(request):
    """API endpoint for checking document status"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Staff access required'}, status=403)
    
    user_id = request.GET.get('user_id')
    if not user_id:
        return JsonResponse({'error': 'User ID required'}, status=400)
    
    try:
        user = User.objects.get(id=user_id)
        documents = Document.objects.filter(user=user).select_related('document_type')
        
        status_data = []
        for doc in documents:
            status_data.append({
                'id': doc.id,
                'type': doc.document_type.name,
                'status': doc.get_status_display(),
                'uploaded_at': doc.uploaded_at.isoformat(),
                'verified_at': doc.verified_at.isoformat() if doc.verified_at else None
            })
        
        return JsonResponse({
            'success': True,
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.get_full_name()
            },
            'documents': status_data
        })
        
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except Exception as e:
        logger.error(f"Status API error: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)


@login_required
def document_analytics(request):
    """Document analytics dashboard for staff"""
    if not request.user.is_staff:
        raise PermissionDenied("Staff access required")
    
    # Get date range
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)
    
    # Get statistics
    total_documents = Document.objects.count()
    pending_documents = Document.objects.filter(status='PENDING').count()
    approved_documents = Document.objects.filter(status__in=['APPROVED', 'AUTO_APPROVED']).count()
    rejected_documents = Document.objects.filter(status='REJECTED').count()
    
    # Get recent activity
    recent_documents = Document.objects.select_related('user', 'document_type').order_by('-uploaded_at')[:10]
    
    # Get documents by type
    documents_by_type = Document.objects.values('document_type__name').annotate(
        count=models.Count('id')
    ).order_by('-count')
    
    return render(request, 'documents/analytics.html', {
        'total_documents': total_documents,
        'pending_documents': pending_documents,
        'approved_documents': approved_documents,
        'rejected_documents': rejected_documents,
        'recent_documents': recent_documents,
        'documents_by_type': documents_by_type,
        'date_range': {
            'start': start_date,
            'end': end_date
        }
    })


# Utility functions
def validate_uploaded_file(file_obj, document_type):
    """Validate uploaded file"""
    # Check file size
    if file_obj.size > document_type.max_file_size:
        raise ValidationError(f"File size cannot exceed {document_type.max_file_size / (1024*1024):.1f}MB")
    
    # Check file extension
    file_ext = file_obj.name.split('.')[-1].lower() if '.' in file_obj.name else ''
    allowed_extensions = document_type.get_allowed_extensions_list()
    
    if file_ext not in allowed_extensions:
        raise ValidationError(f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}")
    
    # Additional security checks
    if file_obj.size < 1024:  # Less than 1KB
        raise ValidationError("File is too small")
    
    if file_obj.size > 50 * 1024 * 1024:  # More than 50MB
        raise ValidationError("File is too large")


def get_expiry_date(document_type):
    """Get expiry date for document based on type"""
    # Most documents expire after 1 year
    default_expiry_days = 365
    
    # KYC documents might have different expiry
    if document_type.required_for == 'KYC':
        default_expiry_days = 730  # 2 years
    
    return timezone.now() + timedelta(days=default_expiry_days)


def log_document_access(request, document, action):
    """Log document access for security and audit"""
    DocumentAccessLog.objects.create(
        document=document,
        user=request.user,
        action=action,
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        session_id=request.session.session_key or ''
    )


def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# API views for mobile apps
@csrf_exempt
@require_http_methods(["POST"])
def api_document_upload(request):
    """API endpoint for document upload"""
    try:
        data = json.loads(request.body)
        
        # Get user (this should use proper authentication in production)
        user_id = data.get('user_id')
        user = get_object_or_404(User, id=user_id)
        
        document_type_id = data.get('document_type_id')
        document_type = get_object_or_404(DocumentType, id=document_type_id)
        
        # Handle file upload (simplified for API)
        # In production, you'd handle multipart form data properly
        file_data = data.get('file_data')
        if not file_data:
            return JsonResponse({'error': 'No file data provided'}, status=400)
        
        # Create document (simplified)
        document = Document.objects.create(
            user=user,
            document_type=document_type,
            original_filename=data.get('filename', 'uploaded_file'),
            file_size=len(file_data),
            metadata={'api_upload': True}
        )
        
        return JsonResponse({
            'success': True,
            'document_id': document.id,
            'message': 'Document uploaded successfully'
        })
        
    except Exception as e:
        logger.error(f"API upload error: {str(e)}")
        return JsonResponse({'error': 'Upload failed'}, status=500)