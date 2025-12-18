"""
Document management admin interface for FlexiFinance
Comprehensive admin for document types, uploads, verification, and audit
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.http import HttpResponse
import csv
from datetime import datetime, timedelta
from .models import DocumentType, Document, DocumentVerification, DocumentAccessLog


@admin.register(DocumentType)
class DocumentTypeAdmin(admin.ModelAdmin):
    """Admin interface for document types"""
    list_display = [
        'name', 
        'required_for', 
        'is_required', 
        'verification_required',
        'auto_approve',
        'max_file_size_display',
        'created_at'
    ]
    list_filter = [
        'required_for', 
        'is_required', 
        'verification_required',
        'auto_approve',
        'created_at'
    ]
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'required_for')
        }),
        ('Requirements', {
            'fields': ('is_required', 'verification_required', 'auto_approve')
        }),
        ('File Constraints', {
            'fields': ('max_file_size', 'allowed_extensions')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def max_file_size_display(self, obj):
        """Display file size in MB"""
        size_mb = obj.max_file_size / (1024 * 1024)
        return f"{size_mb:.1f} MB"
    max_file_size_display.short_description = 'Max File Size'
    
    actions = ['export_document_types']


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """Main admin interface for documents"""
    list_display = [
        'user_display',
        'document_type',
        'status_badge',
        'file_info',
        'upload_info',
        'verification_info'
    ]
    list_filter = [
        'status', 
        'document_type', 
        'uploaded_at',
        'verified_at',
        'document_type__required_for'
    ]
    search_fields = [
        'user__email', 
        'user__first_name', 
        'user__last_name',
        'original_filename',
        'user__phone_number'
    ]
    readonly_fields = [
        'file_size',
        'uploaded_at',
        'verified_at',
        'download_count',
        'last_accessed',
        'file_url'
    ]
    
    fieldsets = (
        ('Document Information', {
            'fields': (
                'user',
                'document_type',
                'file',
                'file_url',
                'original_filename'
            )
        }),
        ('File Details', {
            'fields': (
                'file_size',
                'expires_at'
            ),
            'classes': ('collapse',)
        }),
        ('Verification Status', {
            'fields': (
                'status',
                'verified_by',
                'verified_at',
                'admin_notes'
            )
        }),
        ('Rejection Details', {
            'fields': (
                'rejection_reason',
            ),
            'classes': ('collapse',)
        }),
        ('Technical Details', {
            'fields': (
                'metadata',
                'download_count',
                'last_accessed'
            ),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': (
                'uploaded_at',
            ),
            'classes': ('collapse',)
        }),
    )
    
    actions = [
        'approve_documents', 
        'reject_documents',
        'mark_as_expired',
        'export_documents_csv',
        'mark_as_auto_approved'
    ]
    
    def user_display(self, obj):
        """Display user information with link"""
        url = reverse('admin:users_user_change', args=[obj.user.id])
        return format_html(
            '<a href="{}">{}</a><br><small>{}</small>',
            url,
            obj.user.get_full_name() or obj.user.username,
            obj.user.email
        )
    user_display.short_description = 'User'
    user_display.admin_order_field = 'user__email'
    
    def status_badge(self, obj):
        """Display status with color coding"""
        colors = {
            'PENDING': '#ffc107',    # yellow
            'APPROVED': '#28a745',   # green
            'REJECTED': '#dc3545',   # red
            'EXPIRED': '#6c757d',    # gray
            'AUTO_APPROVED': '#17a2b8',  # blue
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 4px; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def file_info(self, obj):
        """Display file information"""
        size_kb = obj.file_size / 1024 if obj.file_size else 0
        extension = obj.get_file_extension()
        return format_html(
            '{}<br><small>{} ({:.1f} KB)</small>',
            obj.original_filename,
            extension,
            size_kb
        )
    file_info.short_description = 'File'
    
    def upload_info(self, obj):
        """Display upload information"""
        return format_html(
            '{}<br><small>{}</small>',
            obj.uploaded_at.strftime('%Y-%m-%d %H:%M'),
            obj.uploaded_at.strftime('%A')
        )
    upload_info.short_description = 'Uploaded'
    
    def verification_info(self, obj):
        """Display verification information"""
        if obj.verified_by:
            return format_html(
                '{}<br><small>by {}</small>',
                obj.verified_at.strftime('%Y-%m-%d %H:%M') if obj.verified_at else 'N/A',
                obj.verified_by.get_full_name() or obj.verified_by.username
            )
        return 'Not verified'
    verification_info.short_description = 'Verified'
    
    def file_url(self, obj):
        """Display file download URL"""
        if obj.file:
            url = reverse('documents:download', args=[obj.id])
            return format_html('<a href="{}" target="_blank">Download File</a>', url)
        return 'No file'
    file_url.short_description = 'File URL'
    
    def approve_documents(self, request, queryset):
        """Bulk approve documents"""
        approved = 0
        for doc in queryset.filter(status__in=['PENDING', 'REJECTED']):
            doc.approve(request.user, notes='Bulk approved from admin')
            approved += 1
        self.message_user(request, f'{approved} documents approved successfully.')
    approve_documents.short_description = 'Approve selected documents'
    
    def reject_documents(self, request, queryset):
        """Bulk reject documents"""
        rejected = queryset.filter(status__in=['PENDING', 'APPROVED']).update(
            status='REJECTED',
            rejection_reason='Bulk rejection from admin',
            verified_by=request.user,
            verified_at=timezone.now()
        )
        self.message_user(request, f'{rejected} documents rejected.')
    reject_documents.short_description = 'Reject selected documents'
    
    def mark_as_expired(self, request, queryset):
        """Mark documents as expired"""
        updated = queryset.filter(
            status__in=['APPROVED', 'AUTO_APPROVED'],
            expires_at__isnull=False,
            expires_at__lt=timezone.now()
        ).update(status='EXPIRED')
        self.message_user(request, f'{updated} documents marked as expired.')
    mark_as_expired.short_description = 'Mark selected documents as expired'
    
    def mark_as_auto_approved(self, request, queryset):
        """Mark documents as auto-approved"""
        updated = queryset.filter(
            status='PENDING',
            document_type__auto_approve=True
        ).update(
            status='AUTO_APPROVED',
            verified_by=request.user,
            verified_at=timezone.now()
        )
        self.message_user(request, f'{updated} documents marked as auto-approved.')
    mark_as_auto_approved.short_description = 'Mark as auto-approved'
    
    def export_documents_csv(self, request, queryset):
        """Export documents to CSV"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="documents_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'User Email', 'User Name', 'Document Type', 'Status', 
            'File Name', 'File Size (KB)', 'Uploaded At', 'Verified At',
            'Verified By', 'Expiry Date'
        ])
        
        for doc in queryset:
            writer.writerow([
                doc.user.email,
                doc.user.get_full_name(),
                doc.document_type.name,
                doc.get_status_display(),
                doc.original_filename,
                doc.file_size / 1024 if doc.file_size else 0,
                doc.uploaded_at,
                doc.verified_at,
                doc.verified_by.get_full_name() if doc.verified_by else '',
                doc.expires_at
            ])
        
        return response
    export_documents_csv.short_description = 'Export selected documents to CSV'


@admin.register(DocumentVerification)
class DocumentVerificationAdmin(admin.ModelAdmin):
    """Admin interface for document verifications"""
    list_display = [
        'document_link',
        'verifier',
        'verification_type',
        'risk_score_display',
        'verification_date'
    ]
    list_filter = [
        'verification_type',
        'risk_score',
        'verification_date',
        'is_active'
    ]
    search_fields = [
        'document__user__email',
        'document__user__first_name',
        'document__user__last_name',
        'verifier__email',
        'notes'
    ]
    readonly_fields = ['verification_date']
    
    fieldsets = (
        ('Document Information', {
            'fields': ('document', 'verifier', 'verification_type')
        }),
        ('Verification Details', {
            'fields': ('notes', 'risk_score', 'confidence_level')
        }),
        ('AI Analysis', {
            'fields': ('ai_analysis_result',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('verification_metadata',),
            'classes': ('collapse',)
        }),
        ('Expiry', {
            'fields': ('expires_at', 'is_active')
        }),
        ('System Information', {
            'fields': ('verification_date',),
            'classes': ('collapse',)
        }),
    )
    
    def document_link(self, obj):
        """Display document link"""
        url = reverse('admin:documents_document_change', args=[obj.document.id])
        return format_html(
            '<a href="{}">{}</a><br><small>{}</small>',
            url,
            obj.document.document_type.name,
            obj.document.user.get_full_name()
        )
    document_link.short_description = 'Document'
    
    def risk_score_display(self, obj):
        """Display risk score with color coding"""
        score = obj.risk_score
        if score <= 25:
            color = '#28a745'  # green
            level = 'Low'
        elif score <= 50:
            color = '#ffc107'  # yellow
            level = 'Medium'
        elif score <= 75:
            color = '#fd7e14'  # orange
            level = 'High'
        else:
            color = '#dc3545'  # red
            level = 'Critical'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} ({})</span>',
            color,
            score,
            level
        )
    risk_score_display.short_description = 'Risk Score'


@admin.register(DocumentAccessLog)
class DocumentAccessLogAdmin(admin.ModelAdmin):
    """Admin interface for document access logs"""
    list_display = [
        'document_link',
        'user',
        'action',
        'ip_address',
        'timestamp'
    ]
    list_filter = [
        'action',
        'timestamp',
        'document__document_type'
    ]
    search_fields = [
        'document__user__email',
        'user__email',
        'ip_address',
        'session_id'
    ]
    readonly_fields = ['timestamp']
    
    def document_link(self, obj):
        """Display document link"""
        url = reverse('admin:documents_document_change', args=[obj.document.id])
        return format_html(
            '<a href="{}">{}</a><br><small>{}</small>',
            url,
            obj.document.document_type.name,
            obj.document.user.get_full_name()
        )
    document_link.short_description = 'Document'
    
    actions = ['export_access_logs_csv']
    
    def export_access_logs_csv(self, request, queryset):
        """Export access logs to CSV"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="document_access_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Document', 'User', 'Action', 'IP Address', 'Timestamp', 'Session ID'
        ])
        
        for log in queryset:
            writer.writerow([
                f"{log.document.document_type.name} - {log.document.user.get_full_name()}",
                log.user.email,
                log.action,
                log.ip_address or 'N/A',
                log.timestamp,
                log.session_id or 'N/A'
            ])
        
        return response
    export_access_logs_csv.short_description = 'Export selected logs to CSV'


# Custom admin site configuration
admin.site.site_header = "FlexiFinance Document Management"
admin.site.site_title = "Documents Admin"
admin.site.index_title = "Document Management Dashboard"