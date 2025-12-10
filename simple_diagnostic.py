#!/usr/bin/env python3
"""
Simple FlexiFinance Diagnostic Script
Runs basic checks without requiring full Django setup
"""
import os
import subprocess
import sys
import re
from pathlib import Path

def extract_setting_value(content, setting_name):
    """Extract setting value handling all Python value types"""
    # Pattern to match: setting_name = value
    # Handles: strings (quoted), integers, booleans, None, etc.
    pattern = rf'^{setting_name}\s*=\s*(.+?)(?:\s*#.*)?$'
    match = re.search(pattern, content, re.MULTILINE)
    
    if match:
        value_str = match.group(1).strip()
        
        # Remove trailing commas (common in Python settings)
        if value_str.endswith(','):
            value_str = value_str[:-1].strip()
        
        # Try to determine the actual value type and return it
        if value_str.startswith('"') and value_str.endswith('"'):
            # Double-quoted string
            return value_str[1:-1]
        elif value_str.startswith("'") and value_str.endswith("'"):
            # Single-quoted string
            return value_str[1:-1]
        elif value_str in ['True', 'False']:
            # Boolean
            return value_str == 'True'
        elif value_str in ['None']:
            # None value
            return None
        elif value_str.isdigit() or (value_str.startswith('-') and value_str[1:].isdigit()):
            # Integer
            return int(value_str)
        else:
            # Return as-is for other cases
            return value_str
    
    return None

def check_python_packages():
    """Check if required packages are installed"""
    print("📦 PYTHON PACKAGES CHECK")
    print("-" * 30)
    
    required_packages = [
        'django',
        'allauth',               # Import name for django-allauth
        'crispy_forms',          # Import name for django-crispy-forms
        'crispy-bootstrap5',
        'decouple',              # Import name for python-decouple
        'dj-database-url',
        'dotenv',                # Import name for python-dotenv
        'pymysql',
        'rest_framework',        # CORRECT: Imports as 'rest_framework'
        'rest_framework_simplejwt', 
        'pyjwt',
        'corsheaders',           # CORRECT: Imports as 'corsheaders'
        'django_extensions',      # CORRECT: Imports as 'django_extensions'
        'whitenoise',
        'django_filters',        # CORRECT: Imports as 'django_filters'
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

def check_mailpit_server():
    """Check if Mailpit SMTP server is running"""
    print("\n📧 MAILPIT SMTP SERVER CHECK")
    print("-" * 30)
    
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('localhost', 2526))
        sock.close()
        
        if result == 0:
            print("  ✅ Mailpit SMTP server is RUNNING")
            print("     Access Mailpit UI: http://localhost:8080")
        else:
            print("  ❌ Mailpit SMTP server is NOT running")
            print("     Start it with: mailpit --http :8080 --smtp :2526")
    except Exception as e:
        print(f"  ❌ Mailpit check error: {e}")

def check_project_structure():
    """Check if project structure exists"""
    print("\n📁 PROJECT STRUCTURE CHECK")
    print("-" * 30)
    
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
        if Path(file_path).exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} - NOT FOUND")

def check_settings_configuration():
    """Check settings configuration with improved parsing"""
    print("\n⚙️  SETTINGS CONFIGURATION CHECK")
    print("-" * 30)
    
    settings_path = Path(__file__).parent / 'flexifinance' / 'settings.py'
    
    if not settings_path.exists():
        print("❌ settings.py not found!")
        return
    
    with open(settings_path, 'r') as f:
        content = f.read()
    
    # Check email settings with proper value type handling
    email_checks = [
        ('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend'),
        ('EMAIL_HOST', 'localhost'),
        ('EMAIL_PORT', 2526),  # Integer value
        ('EMAIL_USE_TLS', False),  # Boolean value
    ]
    
    print("Email configuration:")
    for setting, expected in email_checks:
        actual_value = extract_setting_value(content, setting)
        
        if actual_value is not None:
            if actual_value == expected:
                print(f"  ✅ {setting}: {actual_value}")
            else:
                print(f"  ⚠️  {setting}: {actual_value} (expected: {expected})")
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
    
    urls_path = Path(__file__).parent / 'flexifinance' / 'urls.py'
    if not urls_path.exists():
        print("❌ urls.py not found!")
        return
    
    with open(urls_path, 'r') as f:
        content = f.read()
    
    # Check for URL imports and configuration
    if "from . import views" in content or "import views" in content:
        print("  ✅ URL import: Correct (from . import views)")
        print("     Uses view with registration logic")
    else:
        print("  ❌ URL import: Incorrect or missing")
    
    if "register" in content.lower():
        print("  ✅ Registration URL: Found")
    else:
        print("  ❌ Registration URL: Not found")

def main():
    """Main diagnostic function"""
    print("🔍 FlexiFinance Simple Diagnostic Report")
    print("=" * 50)
    
    check_python_packages()
    check_mailpit_server()
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
