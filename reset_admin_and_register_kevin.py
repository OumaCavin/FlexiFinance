#!/usr/bin/env python3
"""
Reset admin phone number and register Kevin Otieno
"""
import os
import sys
import django

# Setup Django
sys.path.append('/workspace/django-microfinance-mpsa')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flexifinance.settings')
django.setup()

from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from apps.users.models import User

User = get_user_model()

def reset_admin_and_register_kevin():
    """Reset admin phone and register Kevin"""
    
    print("🔧 Step 1: Resetting admin user phone number")
    try:
        admin_user = User.objects.get(username='admin')
        admin_user.phone_number = None  # Set to NULL since field is now nullable
        admin_user.save()
        print(f"✅ Admin phone number reset to NULL")
    except Exception as e:
        print(f"❌ Error resetting admin phone: {e}")
        return False
    
    print("\n📝 Step 2: Registering Kevin Otieno")
    user_details = {
        'first_name': 'Kevin',
        'last_name': 'Otieno', 
        'email': 'kevingalacha@gmail.com',
        'password': 'Airtel!23',
        'phone_number': '+254715169531',
        'username': 'kevinotieno'
    }
    
    try:
        # Create user
        user = User.objects.create_user(
            username=user_details['username'],
            email=user_details['email'],
            password=user_details['password'],
            first_name=user_details['first_name'],
            last_name=user_details['last_name'],
            phone_number=user_details['phone_number'],  # Now this should work
            is_active=True
        )
        
        print(f"✅ User created successfully!")
        print(f"   Username: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   Phone: {user.phone_number}")
        
        # Send verification email
        print("\n📧 Step 3: Sending verification email")
        send_mail(
            'Verify your email - FlexiFinance',
            f'''Hello {user.get_full_name()},

Welcome to FlexiFinance! Please verify your email address to complete your registration.

Click the link below to verify your email:
http://localhost:8000/accounts/confirm-email/{user.email_verification_token}/

If you did not create this account, please ignore this email.

Best regards,
FlexiFinance Team''',
            'noreply@flexifinance.com',
            [user.email],
            fail_silently=False,
        )
        
        print(f"✅ Verification email sent to {user.email}")
        return True
        
    except Exception as e:
        print(f"❌ Registration failed: {e}")
        return False

def check_final_status():
    """Check final database status"""
    print("\n📊 Final Database Status")
    print("-" * 40)
    
    total_users = User.objects.count()
    for user in User.objects.all():
        phone_display = user.phone_number if user.phone_number else "NULL"
        print(f"  - {user.username} ({user.email}) - Phone: '{phone_display}' - Active: {user.is_active}")

if __name__ == "__main__":
    print("🚀 Kevin Otieno Registration Test")
    print("=" * 50)
    
    success = reset_admin_and_register_kevin()
    
    check_final_status()
    
    if success:
        print("\n🎉 SUCCESS!")
        print("✅ Kevin Otieno registered successfully")
        print("✅ Phone number constraint issue resolved")
        print("✅ Verification email sent")
        print("\n📋 User can now:")
        print("   1. Check SMTP server for verification email")
        print("   2. Click verification link in email")
        print("   3. Log in with credentials:")
        print("      Username: kevinotieno")
        print("      Password: Airtel!23")
    else:
        print("\n❌ FAILED: Registration could not complete")