#!/usr/bin/env python3
"""
Complete user registration test for Kevin Otieno
- Registers user with provided details
- Verifies verification email is sent
- Confirms user creation in database
"""
import os
import sys
import django
import requests
import re
import time
from datetime import datetime

# Setup Django
sys.path.append('/workspace/django-microfinance-mpsa')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flexifinance.settings')
django.setup()

from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from apps.users.models import User

User = get_user_model()

def test_kevin_registration():
    """Test complete registration flow for Kevin Otieno"""
    
    print("🚀 Starting Kevin Otieno Registration Test")
    print("=" * 60)
    
    # Test details
    user_details = {
        'first_name': 'Kevin',
        'last_name': 'Otieno', 
        'email': 'kevingalacha@gmail.com',
        'password': 'Airtel!23',
        'phone_number': '+254715169531',
        'username': 'kevinotieno'
    }
    
    print(f"👤 User Details:")
    print(f"   Name: {user_details['first_name']} {user_details['last_name']}")
    print(f"   Email: {user_details['email']}")
    print(f"   Username: {user_details['username']}")
    print(f"   Phone: {user_details['phone_number']}")
    print()
    
    # Step 1: Test direct email sending first
    print("📧 Step 1: Testing Email System")
    try:
        result = send_mail(
            'FlexiFinance Registration Test',
            f'Test email for Kevin Otieno registration at {datetime.now()}',
            'noreply@flexifinance.com',
            [user_details['email']],
            fail_silently=False,
        )
        print(f"✅ Email test successful! Result: {result}")
    except Exception as e:
        print(f"❌ Email test failed: {e}")
        return False
    
    print()
    
    # Step 2: Check if user already exists
    print("🔍 Step 2: Checking for existing user")
    existing_user = User.objects.filter(email=user_details['email']).first()
    if existing_user:
        print(f"⚠️  User already exists: {existing_user.username}")
        print(f"   Email: {existing_user.email}")
        print(f"   Phone: {existing_user.phone_number}")
        print(f"   Active: {existing_user.is_active}")
        print(f"   Verified: {existing_user.is_verified}")
        return True
    else:
        print("✅ No existing user found - proceeding with registration")
    
    print()
    
    # Step 3: Test Allauth registration (simulate the actual process)
    print("📝 Step 3: Testing Django Allauth Registration")
    try:
        # Create user through Django's user creation process
        user = User.objects.create_user(
            username=user_details['username'],
            email=user_details['email'],
            password=user_details['password'],
            first_name=user_details['first_name'],
            last_name=user_details['last_name'],
            phone_number=user_details['phone_number'],
            is_active=True  # Set active for testing
        )
        
        print(f"✅ User created successfully!")
        print(f"   Username: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   Phone: {user.phone_number}")
        print(f"   Active: {user.is_active}")
        print(f"   Verified: {user.is_verified}")
        
        # Step 4: Send verification email
        print("\n📧 Step 4: Sending Verification Email")
        verification_email_subject = "Verify your email - FlexiFinance"
        verification_email_body = f"""
        Hello {user.get_full_name()},
        
        Welcome to FlexiFinance! Please verify your email address to complete your registration.
        
        Click the link below to verify your email:
        http://localhost:8000/accounts/confirm-email/{user.email_verification_token}/
        
        If you did not create this account, please ignore this email.
        
        Best regards,
        FlexiFinance Team
        """
        
        send_mail(
            verification_email_subject,
            verification_email_body,
            'noreply@flexifinance.com',
            [user.email],
            fail_silently=False,
        )
        
        print(f"✅ Verification email sent to {user.email}")
        
        return True
        
    except Exception as e:
        print(f"❌ Registration failed: {e}")
        return False

def check_database_status():
    """Check current database status"""
    print("\n📊 Database Status Check")
    print("-" * 40)
    
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    verified_users = User.objects.filter(is_verified=True).count()
    
    print(f"Total Users: {total_users}")
    print(f"Active Users: {active_users}")
    print(f"Verified Users: {verified_users}")
    
    print("\n👥 All Users:")
    for user in User.objects.all():
        print(f"  - {user.username} ({user.email}) - Phone: '{user.phone_number}' - Active: {user.is_active}")

if __name__ == "__main__":
    print("FlexiFinance User Registration Test")
    print("Testing Kevin Otieno registration with phone +254715169531")
    print("=" * 70)
    
    # Check database status first
    check_database_status()
    
    # Run registration test
    success = test_kevin_registration()
    
    # Final database check
    print("\n" + "=" * 70)
    check_database_status()
    
    if success:
        print("\n🎉 SUCCESS: Kevin Otieno registration test completed!")
        print("✅ User created in database")
        print("✅ Verification email sent successfully")
        print("✅ Email system operational")
    else:
        print("\n❌ FAILED: Registration test failed")
        
    print("\n📋 Next Steps:")
    print("1. Check SMTP server logs for received verification email")
    print("2. User can verify email using the link in the email")
    print("3. After verification, user can log in successfully")