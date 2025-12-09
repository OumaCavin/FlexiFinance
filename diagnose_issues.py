#!/usr/bin/env python3
"""
FlexiFinance Diagnostic Script
Run this script to identify email and user registration issues
"""
import os
import sys
import django
import subprocess
from pathlib import Path

# Add the project to Python path
project_path = Path(__file__).parent
sys.path.insert(0, str(project_path))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flexifinance.settings')
django.setup()

from django.conf import settings
from django.core.mail import send_mail
from apps.users.models import User
from apps.notifications.models import NotificationTemplate

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def check_mailpit():
    """Check if Mailpit SMTP server is running"""
    print_header("MAILPIT SMTP SERVER CHECK")
    
    # Check if Mailpit process is running
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        mailpit_running = 'mailpit' in result.stdout.lower()
        
        if mailpit_running:
            print("✅ Mailpit SMTP server is RUNNING")
        else:
            print("❌ Mailpit SMTP server is NOT running")
            print("\nTo start Mailpit:")
            print("  mailpit --http :8080 --smtp :2526")
            print("\nOr use the built-in test server:")
            print("  python smtp_test_server.py")
    except Exception as e:
        print(f"⚠️  Could not check Mailpit status: {e}")

def check_email_settings():
    """Check Django email configuration"""
    print_header("EMAIL CONFIGURATION CHECK")
    
    email_settings = {
        'BACKEND': getattr(settings, 'EMAIL_BACKEND', 'Not set'),
        'HOST': getattr(settings, 'EMAIL_HOST', 'Not set'),
        'PORT': getattr(settings, 'EMAIL_PORT', 'Not set'),
        'USE_TLS': getattr(settings, 'EMAIL_USE_TLS', 'Not set'),
        'HOST_USER': getattr(settings, 'EMAIL_HOST_USER', 'Not set'),
    }
    
    for key, value in email_settings.items():
        print(f"{key:12}: {value}")
    
    # Test email sending
    print("\n📧 Testing email sending...")
    try:
        result = send_mail(
            subject='FlexiFinance Diagnostic Test',
            message='This is a test email from FlexiFinance diagnostic script.',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.EMAIL_HOST_USER],
            fail_silently=False
        )
        print("✅ Email sent successfully!")
        print(f"   Check your Mailpit UI at http://localhost:8080")
    except Exception as e:
        print(f"❌ Email sending failed: {e}")
        print("   This could mean Mailpit is not running or SMTP settings are incorrect.")

def check_notification_templates():
    """Check if notification templates exist"""
    print_header("NOTIFICATION TEMPLATES CHECK")
    
    templates = NotificationTemplate.objects.all()
    print(f"Total templates in database: {len(templates)}")
    
    if len(templates) == 0:
        print("❌ No notification templates found!")
        print("\nTo create templates, run:")
        print("  python manage.py create_default_templates")
    else:
        print("✅ Notification templates exist:")
        for template in templates:
            print(f"   - {template.name} ({template.notification_type})")

def check_user_model():
    """Check User model configuration"""
    print_header("USER MODEL CHECK")
    
    # Check User model fields
    user_fields = [field.name for field in User._meta.fields]
    print(f"User model fields: {', '.join(user_fields)}")
    
    # Check if phone_number field exists
    has_phone = 'phone_number' in user_fields
    if has_phone:
        print("✅ phone_number field exists in User model")
    else:
        print("❌ phone_number field missing from User model")
    
    # Check user authentication
    users = User.objects.all()
    print(f"\nTotal users in database: {len(users)}")
    
    if len(users) > 0:
        print("Users found:")
        for user in users[:5]:  # Show first 5 users
            print(f"   - {user.username} ({user.email}) - Active: {user.is_active}")

def check_signals():
    """Check if signals are properly connected"""
    print_header("SIGNAL CONFIGURATION CHECK")
    
    try:
        # Import signals to ensure they're connected
        import apps.users.signals
        import apps.notifications.signals
        
        print("✅ User signals imported successfully")
        print("✅ Notification signals imported successfully")
        print("   Signals should be active for new user registration")
        
    except ImportError as e:
        print(f"❌ Signal import failed: {e}")

def test_user_registration():
    """Test user registration process"""
    print_header("USER REGISTRATION TEST")
    
    test_email = "diagnostic_test@example.com"
    
    try:
        # Try to create a test user
        user, created = User.objects.get_or_create(
            username=test_email,
            defaults={
                'email': test_email,
                'first_name': 'Diagnostic',
                'last_name': 'Test'
            }
        )
        
        if created:
            user.set_password('testpass123')
            user.save()
            print("✅ Test user created successfully")
            print(f"   Username: {user.username}")
            print(f"   Email: {user.email}")
            print(f"   Password set: Yes")
            
            # Clean up test user
            user.delete()
            print("✅ Test user cleaned up")
        else:
            print("ℹ️  Test user already exists")
            
    except Exception as e:
        print(f"❌ User registration test failed: {e}")

def main():
    """Run all diagnostic checks"""
    print("🔍 FlexiFinance Diagnostic Report")
    print(f"Generated at: {django.utils.timezone.now()}")
    
    check_mailpit()
    check_email_settings()
    check_notification_templates()
    check_user_model()
    check_signals()
    test_user_registration()
    
    print_header("DIAGNOSTIC COMPLETE")
    print("Review the results above to identify and fix issues.")
    print("\nNext steps:")
    print("1. Start Mailpit if not running: mailpit --http :8080 --smtp :2526")
    print("2. Create notification templates: python manage.py create_default_templates")
    print("3. Test user registration via web interface")
    print("4. Check Django logs during registration: python manage.py runserver")

if __name__ == "__main__":
    main()