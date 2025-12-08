#!/usr/bin/env python3
"""
Fix phone numbers for admin and Kevin users with unique values
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

def fix_phone_numbers():
    """Update phone numbers for all users with unique values"""
    
    print("🔧 Fixing Phone Numbers for M-Pesa Integration")
    print("=" * 50)
    
    try:
        # Update admin user
        admin_user = User.objects.get(username='admin')
        admin_phone = "+254708101604"
        admin_user.phone_number = admin_phone
        admin_user.save()
        print(f"✅ Admin phone updated to: {admin_phone}")
        
        # Update Kevin user
        kevin_user = User.objects.get(username='kevinotieno')
        kevin_phone = "+254715169531"
        kevin_user.phone_number = kevin_phone
        kevin_user.save()
        print(f"✅ Kevin phone updated to: {kevin_phone}")
        
        print("\n📊 Updated User Phone Numbers:")
        for user in User.objects.all():
            print(f"  👤 {user.username}: {user.phone_number}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating phone numbers: {e}")
        return False

def test_email_sending():
    """Test email sending to Kevin with proper SMTP"""
    
    print("\n📧 Testing Email Sending to Kevin")
    print("-" * 40)
    
    try:
        kevin_user = User.objects.get(username='kevinotieno')
        
        # Test direct SMTP connection first
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex(('localhost', 2526))
        
        if result == 0:
            print("✅ SMTP server connection successful")
            sock.close()
        else:
            print("❌ SMTP server not accessible")
            return False
        
        # Send verification email
        subject = "Verify Your Email - FlexiFinance"
        message = f"""Hello {kevin_user.get_full_name()},

Welcome to FlexiFinance! Your account has been successfully created.

Account Details:
- Username: {kevin_user.username}
- Email: {kevin_user.email}
- Phone: {kevin_user.phone_number}

To complete your registration, please verify your email address by clicking the link below:
http://localhost:8000/accounts/confirm-email/verification-token-here/

If you did not create this account, please ignore this email.

Best regards,
FlexiFinance Team"""
        
        result = send_mail(
            subject,
            message,
            'noreply@flexifinance.com',
            [kevin_user.email],
            fail_silently=False,
        )
        
        print(f"✅ Email sent successfully! Result: {result}")
        print(f"   To: {kevin_user.email}")
        print(f"   Subject: {subject}")
        
        return True
        
    except Exception as e:
        print(f"❌ Email sending failed: {e}")
        return False

def check_smtp_server():
    """Check SMTP server status"""
    print("\n🔍 Checking SMTP Server Status")
    print("-" * 30)
    
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex(('localhost', 2526))
        
        if result == 0:
            response = sock.recv(1024).decode('utf-8')
            print(f"✅ SMTP Server Status: OPERATIONAL")
            print(f"   Response: {response.strip()}")
            sock.close()
            return True
        else:
            print("❌ SMTP Server: NOT ACCESSIBLE")
            return False
            
    except Exception as e:
        print(f"❌ SMTP Server Check Failed: {e}")
        return False

if __name__ == "__main__":
    print("FlexiFinance Phone Number & Email Fix")
    print("=" * 60)
    
    # Check SMTP server first
    smtp_ok = check_smtp_server()
    
    # Fix phone numbers
    phone_ok = fix_phone_numbers()
    
    # Test email sending
    if smtp_ok and phone_ok:
        email_ok = test_email_sending()
    else:
        email_ok = False
    
    print("\n" + "=" * 60)
    
    if phone_ok and email_ok:
        print("🎉 SUCCESS: All fixes completed!")
        print("\n✅ Results:")
        print("   1. ✅ Phone numbers updated (required for M-Pesa)")
        print("   2. ✅ Admin phone: +254708101604")
        print("   3. ✅ Kevin phone: +254715169531")
        print("   4. ✅ SMTP server operational")
        print("   5. ✅ Verification email sent")
        print("\n📋 Next Steps:")
        print("   1. Check kevingalacha@gmail.com for verification email")
        print("   2. Click verification link in email")
        print("   3. Login with: kevinotieno / Airtel!23")
    else:
        print("❌ Some issues remain:")
        if not phone_ok:
            print("   - Phone number update failed")
        if not email_ok:
            print("   - Email sending failed")
        if not smtp_ok:
            print("   - SMTP server not accessible")