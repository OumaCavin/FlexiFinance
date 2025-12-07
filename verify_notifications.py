"""
Verify notification models and default templates
"""
import os
import sys
import django

# Setup Django
sys.path.append('/workspace/django-microfinance-mpsa')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flexifinance.settings')
django.setup()

from apps.notifications.models import *

print('=== NOTIFICATION MODELS VERIFICATION ===')
print(f'NotificationTemplate count: {NotificationTemplate.objects.count()}')
print(f'Notification count: {Notification.objects.count()}')
print(f'UserNotificationPreference count: {UserNotificationPreference.objects.count()}')
print(f'NotificationAnalytics count: {NotificationAnalytics.objects.count()}')
print(f'NotificationQueue count: {NotificationQueue.objects.count()}')
print(f'NotificationLog count: {NotificationLog.objects.count()}')
print()
print('=== DEFAULT TEMPLATES ===')
for template in NotificationTemplate.objects.all():
    print(f'- {template.name}: {template.get_notification_type_display()}')
print()
print('=== SAMPLE USAGE TEST ===')
from django.contrib.auth import get_user_model
User = get_user_model()

# Create a test user if none exists
if User.objects.count() == 0:
    test_user = User.objects.create_user(
        email='test@example.com',
        username='testuser',
        password='testpass123'
    )
    print(f'Created test user: {test_user.email}')
else:
    test_user = User.objects.first()
    print(f'Using existing user: {test_user.email}')

# Test notification sending
from apps.notifications.services.notification_service import notification_service

try:
    notification = notification_service.send_notification(
        user=test_user,
        notification_type='WELCOME_EMAIL',
        channel='EMAIL',
        template_name='welcome_email',
        metadata={'test': True}
    )
    print(f'✅ Test notification created: {notification.id}')
    print(f'   Status: {notification.get_status_display()}')
    print(f'   Channel: {notification.get_channel_display()}')
except Exception as e:
    print(f'❌ Error creating test notification: {e}')

print()
print('=== NOTIFICATION SYSTEM READY! ===')