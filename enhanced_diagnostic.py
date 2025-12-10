#!/usr/bin/env python3
"""
Enhanced FlexiFinance Diagnostic Script
Runs within the Django environment to get accurate results
"""
import os
import sys
import django
import subprocess
from pathlib import Path

# Add the project directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flexifinance.settings')
django.setup()

def run_diagnostic():
    print("🔍 FLEXIFINANCE ENHANCED DIAGNOSTIC REPORT")
    print("=" * 50)
    
    print("\n📦 DJANGO APP CONFIGURATION CHECK")
    print("-" * 30)
    
    try:
        from django.conf import settings
        print(f"✅ Django is properly configured")
        print(f"✅ Debug mode: {settings.DEBUG}")
        print(f"✅ Email backend: {settings.EMAIL_BACKEND}")
        print(f"✅ Email host: {settings.EMAIL_HOST}")
        print(f"✅ Email port: {settings.EMAIL_PORT}")
        print(f"✅ Email TLS: {settings.EMAIL_USE_TLS}")
    except Exception as e:
        print(f"❌ Django configuration error: {e}")
        return
    
    print("\n📧 EMAIL CONFIGURATION VERIFICATION")
    print("-" * 30)
    
    # Test email configuration
    try:
        from django.core.mail import send_mail
        from django.conf import settings
        
        if hasattr(settings, 'EMAIL_HOST'):
            if settings.EMAIL_HOST == 'localhost' and settings.EMAIL_PORT == 2526:
                print("✅ Email configuration is set for Mailpit")
                print(f"   Host: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
            else:
                print(f"⚠️ Email host is not Mailpit: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
        else:
            print("❌ Email host not configured")
            
    except Exception as e:
        print(f"❌ Email configuration error: {e}")
    
    print("\n🔧 DJANGO APP STATUS")
    print("-" * 30)
    
    try:
        from django.apps import apps
        installed_apps = [app.name for app in apps.get_app_configs()]
        print(f"✅ {len(installed_apps)} Django apps installed")
        
        required_apps = ['users', 'notifications', 'loans', 'payments']
        for app in required_apps:
            if app in installed_apps:
                print(f"✅ {app} app is installed")
            else:
                print(f"❌ {app} app is missing")
                
    except Exception as e:
        print(f"❌ Apps check error: {e}")
    
    print("\n👥 USER MODEL CHECK")
    print("-" * 30)
    
    try:
        from apps.users.models import User
        user_count = User.objects.count()
        print(f"✅ User model is accessible")
        print(f"📊 Total users in database: {user_count}")
        
        if user_count > 0:
            admin_user = User.objects.filter(username='admin').first()
            if admin_user:
                print(f"✅ Admin user found: {admin_user.username}")
                print(f"   Active: {admin_user.is_active}")
                print(f"   Staff: {admin_user.is_staff}")
                print(f"   Superuser: {admin_user.is_superuser}")
            else:
                print("⚠️ Admin user not found")
        
    except Exception as e:
        print(f"❌ User model error: {e}")
    
    print("\n📧 NOTIFICATION TEMPLATES CHECK")
    print("-" * 30)
    
    try:
        from apps.notifications.models import NotificationTemplate
        templates = NotificationTemplate.objects.all()
        print(f"✅ NotificationTemplate model is accessible")
        print(f"📊 Total templates: {templates.count()}")
        
        if templates.count() == 0:
            print("⚠️ No notification templates found")
            print("   Run: python manage.py create_default_templates")
        else:
            print("✅ Notification templates exist")
            for template in templates:
                print(f"   - {template.name}")
                
    except Exception as e:
        print(f"❌ Notification templates error: {e}")
    
    print("\n🔗 URL CONFIGURATION CHECK")
    print("-" * 30)
    
    try:
        from django.urls import resolve, reverse
        print("✅ Django URLs are accessible")
        
        # Test registration URL
        try:
            registration_url = reverse('register')
            print(f"✅ Registration URL found: {registration_url}")
        except Exception:
            print("❌ Registration URL not found")
            
        # Test login URL
        try:
            login_url = reverse('login')
            print(f"✅ Login URL found: {login_url}")
        except Exception:
            print("❌ Login URL not found")
            
    except Exception as e:
        print(f"❌ URL configuration error: {e}")
    
    print("\n🔧 EXTERNAL SERVICES CHECK")
    print("-" * 30)
    
    # Check Mailpit
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('localhost', 2526))
        sock.close()
        
        if result == 0:
            print("✅ Mailpit SMTP server is running on port 2526")
        else:
            print("❌ Mailpit SMTP server is NOT running")
            print("   Start it with: mailpit --http :8080 --smtp :2526")
    except Exception as e:
        print(f"❌ Mailpit check error: {e}")
    
    print("\n" + "=" * 50)
    print("📋 DIAGNOSTIC SUMMARY")
    print("=" * 50)
    print("If all checks show ✅, your FlexiFinance should be working correctly!")
    print("If you see ❌ or ⚠️, follow the suggested fixes above.")

if __name__ == "__main__":
    run_diagnostic()
