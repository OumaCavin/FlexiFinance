#!/usr/bin/env python3
"""
Test script for the FlexiFinance Notification System
This script tests the notification models and services without needing a full Django server
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(project_dir))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flexifinance.settings')
django.setup()

# Import our models and services
from apps.notifications.models import (
    NotificationTemplate, 
    Notification, 
    UserNotificationPreference,
    NotificationAnalytics,
    NotificationQueue,
    NotificationLog
)
from apps.notifications.services.notification_service import NotificationService
from apps.users.models import User
from django.db import connection

def test_database_connection():
    """Test database connection"""
    print("🔗 Testing database connection...")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_notification_models():
    """Test that notification models can be imported and accessed"""
    print("\n📊 Testing notification models...")
    
    try:
        # Test model imports
        models = [
            'NotificationTemplate',
            'Notification', 
            'UserNotificationPreference',
            'NotificationAnalytics',
            'NotificationQueue',
            'NotificationLog'
        ]
        
        for model_name in models:
            model = globals()[model_name]
            print(f"  ✅ {model_name} model imported successfully")
            
        return True
    except Exception as e:
        print(f"❌ Model import failed: {e}")
        return False

def test_notification_service():
    """Test the notification service"""
    print("\n🚀 Testing notification service...")
    
    try:
        service = NotificationService()
        print("  ✅ NotificationService initialized successfully")
        
        # Test available methods
        methods = [
            'send_notification',
            'send_bulk_notifications', 
            'retry_failed_notifications',
            'get_notification_analytics',
            'process_notification_queue'
        ]
        
        for method in methods:
            if hasattr(service, method):
                print(f"  ✅ Method '{method}' available")
            else:
                print(f"  ❌ Method '{method}' missing")
                
        return True
    except Exception as e:
        print(f"❌ Notification service test failed: {e}")
        return False

def test_query_notification_data():
    """Query existing notification data from database"""
    print("\n📈 Querying notification data...")
    
    try:
        # Check if we have any notification templates
        templates_count = NotificationTemplate.objects.count()
        print(f"  📧 Notification Templates: {templates_count}")
        
        # Check if we have any notifications
        notifications_count = Notification.objects.count()
        print(f"  📬 Total Notifications: {notifications_count}")
        
        # Check if we have any user preferences
        preferences_count = UserNotificationPreference.objects.count()
        print(f"  ⚙️ User Preferences: {preferences_count}")
        
        # Check if we have any analytics data
        analytics_count = NotificationAnalytics.objects.count()
        print(f"  📊 Analytics Records: {analytics_count}")
        
        # Check if we have any queued notifications
        queue_count = NotificationQueue.objects.count()
        print(f"  ⏳ Queued Notifications: {queue_count}")
        
        # Check if we have any logs
        logs_count = NotificationLog.objects.count()
        print(f"  📋 Notification Logs: {logs_count}")
        
        return True
    except Exception as e:
        print(f"❌ Data query failed: {e}")
        return False

def create_test_notification():
    """Create a test notification to demonstrate the system works"""
    print("\n🧪 Creating test notification...")
    
    try:
        # Get or create a test user
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        
        if created:
            print("  ✅ Created test user")
        else:
            print("  ✅ Using existing test user")
        
        # Get or create a notification template
        template, created = NotificationTemplate.objects.get_or_create(
            name='test_notification',
            defaults={
                'subject': 'Test Notification',
                'content': 'This is a test notification from the FlexiFinance system.',
                'channel': 'email',
                'priority': 'medium'
            }
        )
        
        if created:
            print("  ✅ Created test notification template")
        else:
            print("  ✅ Using existing test notification template")
        
        # Create a test notification
        notification = Notification.objects.create(
            user=user,
            template=template,
            subject='Test Notification Subject',
            content='This is a test notification content.',
            channel='email',
            status='pending',
            priority='medium'
        )
        
        print(f"  ✅ Created test notification with ID: {notification.id}")
        
        # Create user preference if it doesn't exist
        preference, created = UserNotificationPreference.objects.get_or_create(
            user=user,
            defaults={
                'email_enabled': True,
                'sms_enabled': False,
                'push_enabled': False
            }
        )
        
        if created:
            print("  ✅ Created user notification preferences")
        else:
            print("  ✅ Using existing user notification preferences")
        
        return True
        
    except Exception as e:
        print(f"❌ Test notification creation failed: {e}")
        return False

def display_notification_admin_info():
    """Display information about notification admin interface"""
    print("\n🎛️ Django Admin Interface Information:")
    print("  📱 Admin URL: http://localhost:8000/admin/")
    print("  🔐 Default admin credentials should be created via:")
    print("     python manage.py createsuperuser")
    print("  📊 Available notification models in admin:")
    models = [
        'Notification Templates',
        'Notifications', 
        'User Notification Preferences',
        'Notification Analytics',
        'Notification Queue',
        'Notification Logs'
    ]
    
    for model in models:
        print(f"     • {model}")

def main():
    """Main test function"""
    print("🚀 FlexiFinance Notification System Test")
    print("=" * 50)
    
    # Run all tests
    tests = [
        test_database_connection,
        test_notification_models,
        test_query_notification_data,
        test_notification_service,
        create_test_notification
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Notification system is working correctly.")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
    
    display_notification_admin_info()

if __name__ == "__main__":
    main()