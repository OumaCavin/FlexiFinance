#!/usr/bin/env python3
"""
Manual FlexiFinance Configuration Test
Run this in your local environment to verify fixes
"""
import os
import re
from pathlib import Path

def test_configuration():
    print("🔍 FLEXIFINANCE CONFIGURATION TEST")
    print("=" * 50)
    
    # Test 1: Check settings.py email configuration
    print("\n📧 EMAIL CONFIGURATION CHECK")
    print("-" * 30)
    
    settings_path = Path("flexifinance/settings.py")
    if settings_path.exists():
        with open(settings_path, 'r') as f:
            content = f.read()
        
        # Check for direct email configuration (good)
        if "EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'" in content:
            print("✅ Email backend set to SMTP")
        else:
            print("❌ Email backend not set correctly")
        
        if "EMAIL_HOST = 'localhost'" in content:
            print("✅ Email host set to localhost")
        else:
            print("❌ Email host not set to localhost")
        
        if "EMAIL_PORT = 2526" in content:
            print("✅ Email port set to 2526")
        else:
            print("❌ Email port not set to 2526")
        
        # Check if debug toolbar is disabled
        if "# debug_toolbar" in content.lower() and "# debug_toolbar" in content.lower():
            print("✅ Debug toolbar is disabled")
        else:
            print("❌ Debug toolbar might still be active")
    else:
        print("❌ settings.py not found")
    
    # Test 2: Check .env file
    print("\n🔍 .ENV FILE CHECK")
    print("-" * 30)
    
    env_path = Path(".env")
    if env_path.exists():
        with open(env_path, 'r') as f:
            env_content = f.read()
        
        if "EMAIL_HOST=localhost" in env_content:
            print("✅ .env has correct email host")
        else:
            print("❌ .env email host incorrect")
        
        if "EMAIL_PORT=2526" in env_content:
            print("✅ .env has correct email port")
        else:
            print("❌ .env email port incorrect")
    else:
        print("⚠️ .env file not found (optional)")
    
    # Test 3: Check if packages are installed
    print("\n📦 PACKAGE CHECK")
    print("-" * 30)
    
    packages_to_check = [
        'django', 'django-allauth', 'django-crispy-forms', 
        'python-decouple', 'python-dotenv', 'djangorestframework',
        'djangorestframework-simplejwt', 'pyjwt', 'django-cors-headers',
        'django-filter'
    ]
    
    for package in packages_to_check:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - NOT INSTALLED")
    
    # Test 4: Check Mailpit
    print("\n🔧 MAILPIT CHECK")
    print("-" * 30)
    
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
    print("📋 FINAL TEST INSTRUCTIONS")
    print("=" * 50)
    print("1. If all checks show ✅, proceed with Django tests:")
    print("2. Run: python manage.py runserver")
    print("3. Test registration: http://localhost:8000/dashboard/register/")
    print("4. Check emails: http://localhost:8080")
    print("5. Test login: http://localhost:8000/dashboard/login/")
    
    print("\nIf any checks show ❌, fix those issues first!")

if __name__ == "__main__":
    test_configuration()
