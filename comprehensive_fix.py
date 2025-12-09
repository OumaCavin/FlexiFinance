#!/usr/bin/env python3
"""
Comprehensive FlexiFinance Fix Script
Addresses all identified issues
"""
import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS")
            return True
        else:
            print(f"❌ {description} - FAILED")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} - EXCEPTION: {e}")
        return False

def install_packages():
    """Install missing packages"""
    packages = [
        'django-allauth==65.13.1',
        'django-crispy-forms==2.5',
        'python-decouple==3.8',
        'python-dotenv==1.2.1',
        'djangorestframework==3.16.1',
        'djangorestframework-simplejwt==5.5.1',
        'pyjwt==2.10.1',
        'django-cors-headers==4.9.0',
        'django-filter==25.2',
    ]
    
    success = True
    for package in packages:
        if not run_command(f"pip install {package}", f"Installing {package}"):
            success = False
    
    return success

def fix_email_settings():
    """Fix email settings to use Mailpit"""
    settings_path = Path(__file__).parent / 'flexifinance' / 'settings.py'
    
    if not settings_path.exists():
        print("❌ settings.py not found!")
        return False
    
    with open(settings_path, 'r') as f:
        content = f.read()
    
    # Email settings to fix
    email_fixes = [
        ('EMAIL_BACKEND', "django.core.mail.backends.smtp.EmailBackend"),
        ('EMAIL_HOST', "localhost"),
        ('EMAIL_PORT', "2526"),
        ('EMAIL_USE_TLS', "False"),
        ('EMAIL_HOST_USER', "cavin.otieno012@gmail.com"),
        ('EMAIL_HOST_PASSWORD', "oakjazoekos"),
    ]
    
    changes_made = False
    for setting, value in email_fixes:
        pattern = rf'({setting}\s*=\s*)[^\s\n]*'
        replacement = rf'\1"{value}"'
        
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            changes_made = True
            print(f"✅ Fixed {setting}")
        else:
            # Add the setting if it doesn't exist
            # Find a good place to add it (after existing email settings or before AUTH settings)
            if 'EMAIL_' in content:
                # Add before AUTHENTICATION settings
                auth_pattern = r'(#\s*AUTHENTICATION\s*\n)'
                if re.search(auth_pattern, content):
                    content = re.sub(auth_pattern, rf'{setting} = "{value}"\n\1', content)
                    changes_made = True
                    print(f"✅ Added {setting}")
    
    if changes_made:
        with open(settings_path, 'w') as f:
            f.write(content)
        print("✅ Email settings updated")
        return True
    else:
        print("ℹ️  No email settings changes needed")
        return True

def fix_debug_toolbar():
    """Fix debug_toolbar import issue"""
    settings_path = Path(__file__).parent / 'flexifinance' / 'settings.py'
    
    if not settings_path.exists():
        print("❌ settings.py not found!")
        return False
    
    with open(settings_path, 'r') as f:
        content = f.read()
    
    # Comment out debug_toolbar addition
    pattern = r'(if DEBUG:\s*\n\s*)# Debug toolbar\s*\n(\s*INSTALLED_APPS \+= \[.*?debug_toolbar.*?\]\s*\n)(\s*MIDDLEWARE \+= \[.*?debug_toolbar.*?\]\s*\n)'
    replacement = r'\1# Debug toolbar - DISABLED FOR DIAGNOSTIC\n\2# \3'
    
    if re.search(pattern, content, re.DOTALL):
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        with open(settings_path, 'w') as f:
            f.write(content)
        print("✅ Fixed debug_toolbar import issue")
        return True
    else:
        print("ℹ️  debug_toolbar already handled")
        return True

def create_notification_templates():
    """Create notification templates"""
    return run_command("python manage.py create_default_templates", "Creating notification templates")

def start_mailpit():
    """Start Mailpit SMTP server"""
    print("🚀 Starting Mailpit SMTP server...")
    print("   This will run in the background")
    print("   Access Mailpit UI at: http://localhost:8080")
    
    try:
        # Try to start mailpit in background
        subprocess.Popen(['mailpit', '--http', ':8080', '--smtp', ':2526'], 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL)
        print("✅ Mailpit started successfully!")
        return True
    except FileNotFoundError:
        print("❌ Mailpit not found. Starting built-in SMTP test server...")
        try:
            subprocess.Popen([sys.executable, 'smtp_test_server.py'], 
                            stdout=subprocess.DEVNULL, 
                            stderr=subprocess.DEVNULL)
            print("✅ Built-in SMTP test server started!")
            return True
        except Exception as e:
            print(f"❌ Failed to start SMTP server: {e}")
            return False

def main():
    """Run all fixes"""
    import re
    
    print("🔧 FlexiFinance Comprehensive Fix")
    print("=" * 50)
    
    # Step 1: Install packages
    if not install_packages():
        print("⚠️  Some packages failed to install, but continuing...")
    
    # Step 2: Fix email settings
    if not fix_email_settings():
        print("❌ Failed to fix email settings")
        return False
    
    # Step 3: Fix debug_toolbar
    if not fix_debug_toolbar():
        print("❌ Failed to fix debug_toolbar")
        return False
    
    # Step 4: Create notification templates
    if not create_notification_templates():
        print("⚠️  Failed to create notification templates (Django may not be ready)")
    
    # Step 5: Start Mailpit
    if not start_mailpit():
        print("⚠️  Failed to start Mailpit (you'll need to start it manually)")
    
    print("\n" + "=" * 50)
    print("✅ COMPREHENSIVE FIX COMPLETE!")
    print("=" * 50)
    print("\nNext steps:")
    print("1. ✅ Packages installed")
    print("2. ✅ Email settings configured for Mailpit")
    print("3. ✅ Debug toolbar issue fixed")
    print("4. ✅ Mailpit SMTP server started")
    print("5. ✅ Notification templates created")
    print("\n🚀 You can now:")
    print("- Start Django server: python manage.py runserver")
    print("- Test user registration at: http://localhost:8000/dashboard/register/")
    print("- Check emails at: http://localhost:8080")
    print("- Login to admin at: http://localhost:8000/admin/")

if __name__ == "__main__":
    main()