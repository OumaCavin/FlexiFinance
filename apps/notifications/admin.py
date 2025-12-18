"""
Django Admin Configuration for Notification System
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    NotificationTemplate, 
    Notification, 
    UserNotificationPreference,
    NotificationAnalytics,
    NotificationQueue,
    NotificationLog
)


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = [
        'name', 
        'notification_type', 
        'channels_display', 
        'priority', 
        'is_active', 
        'usage_count',
        'created_at'
    ]
    list_filter = ['notification_type', 'is_active', 'priority', 'created_at']
    search_fields = ['name', 'subject_template', 'message_template']
    readonly_fields = ['usage_count', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'notification_type', 'channels')
        }),
        ('Content', {
            'fields': ('subject_template', 'message_template', 'html_template')
        }),
        ('Configuration', {
            'fields': ('is_active', 'priority', 'retry_attempts', 'retry_delay_minutes')
        }),
        ('Analytics', {
            'fields': ('usage_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def channels_display(self, obj):
        return ', '.join(obj.channels)
    channels_display.short_description = 'Channels'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = [
        'recipient_email',
        'subject_preview', 
        'channel', 
        'priority',
        'status_badge',
        'scheduled_at',
        'sent_at',
        'delivery_time'
    ]
    list_filter = [
        'channel', 
        'status', 
        'priority', 
        'scheduled_at', 
        'sent_at',
        'created_at'
    ]
    search_fields = ['recipient__email', 'subject', 'message', 'provider_id']
    readonly_fields = [
        'id', 'created_at', 'updated_at', 'sent_at', 
        'delivered_at', 'failed_at', 'retry_count'
    ]
    
    fieldsets = (
        ('Core Information', {
            'fields': ('id', 'template', 'recipient', 'subject', 'message')
        }),
        ('Content', {
            'fields': ('html_content', 'channel', 'priority', 'metadata')
        }),
        ('Delivery Status', {
            'fields': ('status', 'retry_count', 'max_retries', 'scheduled_at')
        }),
        ('Timestamps', {
            'fields': ('sent_at', 'delivered_at', 'failed_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('External Tracking', {
            'fields': ('provider_id', 'provider_response'),
            'classes': ('collapse',)
        }),
    )
    
    def recipient_email(self, obj):
        return obj.recipient.email
    recipient_email.short_description = 'Recipient'
    
    def subject_preview(self, obj):
        return obj.subject[:50] + '...' if len(obj.subject) > 50 else obj.subject
    subject_preview.short_description = 'Subject'
    
    def status_badge(self, obj):
        colors = {
            'PENDING': '#ffc107',    # yellow
            'SENT': '#17a2b8',       # blue
            'DELIVERED': '#28a745',  # green
            'FAILED': '#dc3545',     # red
            'BOUNCED': '#fd7e14',    # orange
            'CANCELLED': '#6c757d',  # gray
            'RETRYING': '#007bff',   # primary blue
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def delivery_time(self, obj):
        if obj.sent_at and obj.delivered_at:
            delta = obj.delivered_at - obj.sent_at
            minutes = int(delta.total_seconds() / 60)
            return f"{minutes}m"
        return "-"
    delivery_time.short_description = 'Delivery Time'


@admin.register(UserNotificationPreference)
class UserNotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = [
        'user_email',
        'email_notifications',
        'sms_notifications', 
        'push_notifications',
        'in_app_notifications',
        'email_frequency',
        'quiet_hours_enabled',
        'updated_at'
    ]
    list_filter = [
        'email_notifications',
        'sms_notifications',
        'push_notifications', 
        'in_app_notifications',
        'email_frequency',
        'quiet_hours_enabled',
        'updated_at'
    ]
    search_fields = ['user__email']
    readonly_fields = ['created_at', 'updated_at']
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'


@admin.register(NotificationAnalytics)
class NotificationAnalyticsAdmin(admin.ModelAdmin):
    list_display = [
        'date',
        'total_sent',
        'total_delivered',
        'delivery_rate',
        'unique_recipients',
        'email_delivered',
        'sms_delivered'
    ]
    list_filter = ['date']
    readonly_fields = [
        'created_at',
        'delivery_rate',
        'bounce_rate'
    ]
    
    def delivery_rate(self, obj):
        rate = obj.delivery_rate
        return f"{rate:.1f}%"
    delivery_rate.short_description = 'Delivery Rate'


@admin.register(NotificationQueue)
class NotificationQueueAdmin(admin.ModelAdmin):
    list_display = [
        'notification_recipient',
        'notification_subject',
        'priority',
        'status',
        'scheduled_for',
        'attempts',
        'created_at'
    ]
    list_filter = ['status', 'priority', 'scheduled_for', 'created_at']
    search_fields = ['notification__recipient__email', 'notification__subject']
    readonly_fields = ['created_at', 'processed_at']
    
    def notification_recipient(self, obj):
        return obj.notification.recipient.email
    notification_recipient.short_description = 'Recipient'
    
    def notification_subject(self, obj):
        return obj.notification.subject[:50] + '...' if len(obj.notification.subject) > 50 else obj.notification.subject
    notification_subject.short_description = 'Subject'


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = [
        'level_badge',
        'message_preview',
        'notification_recipient',
        'created_at'
    ]
    list_filter = ['level', 'created_at']
    search_fields = ['message', 'notification__recipient__email']
    readonly_fields = ['created_at']
    
    def level_badge(self, obj):
        colors = {
            'DEBUG': '#6c757d',
            'INFO': '#17a2b8',
            'WARNING': '#ffc107',
            'ERROR': '#dc3545',
            'CRITICAL': '#721c24'
        }
        color = colors.get(obj.level, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px;">{}</span>',
            color,
            obj.level
        )
    level_badge.short_description = 'Level'
    
    def message_preview(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Message'
    
    def notification_recipient(self, obj):
        if obj.notification:
            return obj.notification.recipient.email
        return "-"
    notification_recipient.short_description = 'Notification'


# Custom admin site header
admin.site.site_header = "FlexiFinance Notification System"
admin.site.site_title = "Notifications Admin"
admin.site.index_title = "Notification Management Dashboard"