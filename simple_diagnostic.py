#!/usr/bin/env python3
"""
Simple FlexiFinance Diagnostic Script
Runs basic checks without requiring full Django setup
"""
import os
import subprocess
import sys
from pathlib import Path

def check_python_packages():
    """Check if required packages are installed"""
    print("📦 PYTHON PACKAGES CHECK")
    print("-" * 30)
    
    required_packages = [
        'django',
        'django-allauth', 
        'django-crispy-forms',
        'crispy-bootstrap5',
        'python-decouple',
        'dj-database-url',
        'python-dotenv',
        'pymysql',
        'djangorestframework',
        'djangorestframework-simplejwt',
        'pyjwt',
        'django-cors-headers',
        'django-extensions',
        'whitenoise',
        'django-filter',
    ]
    
    optional_packages = [
        'debug_toolbar',
        'celery',
        'import-export',
    ]
    
    print("Required packages:")
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - NOT INSTALLED")
    
    print("\nOptional packages:")
    for package in optional_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ⚠️  {package} - NOT INSTALLED (optional)")

def check_mailpit():
    """Check if Mailpit is running"""
    print("\n📧 MAILPIT SMTP SERVER CHECK")
    print("-" * 30)
    
    # Check if Mailpit process is running
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        mailpit_running = 'mailpit' in result.stdout.lower()
        
        if mailpit_running:
            print("✅ Mailpit SMTP server is RUNNING")
            print("   Access Mailpit UI: http://localhost:8080")
        else:
            print("❌ Mailpit SMTP server is NOT running")
            print("\nTo start Mailpit:")
            print("  1. Install: curl -fsSL https://raw.githubusercontent.com/axllent/mailpit/develop/install.sh | sh")
            print("  2. Run: mailpit --http :8080 --smtp :2526")
            print("  3. Or use: python smtp_test_server.py")
    except Exception as e:
        print(f"⚠️  Could not check Mailpit status: {e}")

def check_project_structure():
    """Check if required project files exist"""
    print("\n📁 PROJECT STRUCTURE CHECK")
    print("-" * 30)
    
    base_path = Path(__file__).parent
    
    required_files = [
        'manage.py',
        'flexifinance/settings.py',
        'flexifinance/urls.py',
        'apps/users/models.py',
        'apps/users/views.py',
        'apps/users/web_urls.py',
        'apps/notifications/models.py',
        'apps/notifications/services/notification_service.py',
        'apps/users/signals.py',
        'apps/notifications/signals.py',
    ]
    
    for file_path in required_files:
        full_path = base_path / file_path
        if full_path.exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} - MISSING")

def check_settings_configuration():
    """Check Django settings configuration"""
    print("\n⚙️  SETTINGS CONFIGURATION CHECK")
    print("-" * 30)
    
    settings_path = Path(__file__).parent / 'flexifinance' / 'settings.py'
    
    if not settings_path.exists():
        print("❌ settings.py not found!")
        return
    
    with open(settings_path, 'r') as f:
        content = f.read()
    
    # Check email settings
    email_checks = [
        ('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend'),
        ('EMAIL_HOST', 'localhost'),
        ('EMAIL_PORT', '2526'),
        ('EMAIL_USE_TLS', 'False'),
    ]
    
    print("Email configuration:")
    for setting, expected in email_checks:
        if f"{setting} = " in content:
            # Extract the value
            import re
            match = re.search(rf'{setting}\s*=\s*[\'"](.*?)[\'"]', content)
            if match:
                value = match.group(1)
                if expected.lower() in value.lower():
                    print(f"  ✅ {setting}: {value}")
                else:
                    print(f"  ⚠️  {setting}: {value} (expected: {expected})")
            else:
                print(f"  ⚠️  {setting}: Found but couldn't parse value")
        else:
            print(f"  ❌ {setting}: Not found")
    
    # Check if problematic apps are commented out
    problematic_apps = ['celery', 'import_export', 'debug_toolbar']
    print("\nProblematic apps status:")
    for app in problematic_apps:
        if f"# '{app}'," in content:
            print(f"  ✅ {app}: Commented out (disabled)")
        elif f"'{app}'" in content:
            print(f"  ⚠️  {app}: Active (may cause import errors)")
        else:
            print(f"  ℹ️  {app}: Not in settings")

def check_url_configuration():
    """Check URL configuration for registration"""
    print("\n🔗 URL CONFIGURATION CHECK")
    print("-" * 30)
    
    web_urls_path = Path(__file__).parent / 'apps' / 'users' / 'web_urls.py'
    
    if not web_urls_path.exists():
        print("❌ web_urls.py not found!")
        return
    
    with open(web_urls_path, 'r') as f:
        content = f.read()
    
    # Check import statement
    if 'from . import views' in content:
        print("✅ URL import: Correct (from . import views)")
        print("   Uses view with registration logic")
    elif 'from .web import views' in content:
        print("❌ URL import: Wrong (from .web import views)")
        print("   Uses placeholder view without registration logic")
        print("   Should be: from . import views")
    else:
        print("⚠️  URL import: Unknown structure")
    
    # Check if register URL exists
    if "path('register/'," in content:
        print("✅ Registration URL: Found")
    else:
        print("❌ Registration URL: Not found")

def main():
    """Run all diagnostic checks"""
    print("🔍 FlexiFinance Simple Diagnostic Report")
    print("=" * 50)
    
    check_python_packages()
    check_mailpit()
    check_project_structure()
    check_settings_configuration()
    check_url_configuration()
    
    print("\n" + "=" * 50)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 50)
    print("Next steps to fix issues:")
    print("1. Install missing packages: pip install <package_name>")
    print("2. Start Mailpit: python start_mailpit.py")
    print("3. Fix URL configuration if needed: python fix_registration_urls.py")
    print("4. Create notification templates: python manage.py create_default_templates")
    print("5. Test user registration and email functionality")

if __name__ == "__main__":
    main()