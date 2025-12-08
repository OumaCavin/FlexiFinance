#!/usr/bin/env python3
"""
Direct email test to verify SMTP functionality
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flexifinance.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

def test_email():
    """Test email sending directly"""
    
    print("🧪 Testing email functionality...")
    print(f"📧 Email backend: {settings.EMAIL_BACKEND}")
    print(f"📧 Email host: {settings.EMAIL_HOST}")
    print(f"📧 Email port: {settings.EMAIL_PORT}")
    print(f"📧 Email user: {settings.EMAIL_HOST_USER}")
    print(f"📧 Email TLS: {settings.EMAIL_USE_TLS}")
    
    # Test email content
    subject = "Test Email from FlexiFinance"
    message = """
    Hello Kevin,
    
    This is a test email to verify that the SMTP server is working correctly.
    
    If you receive this email, it means the FlexiFinance email system is functioning properly.
    
    Best regards,
    FlexiFinance Team
    """
    from_email = settings.FROM_EMAIL if hasattr(settings, 'FROM_EMAIL') else 'noreply@flexifinance.com'
    recipient_list = ['kevingalacha@gmail.com']
    
    print(f"📤 Sending email...")
    print(f"   From: {from_email}")
    print(f"   To: {recipient_list[0]}")
    print(f"   Subject: {subject}")
    
    try:
        result = send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            fail_silently=False
        )
        
        print(f"✅ Email sent successfully! Result: {result}")
        return True
        
    except Exception as e:
        print(f"❌ Email sending failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_email()
    if success:
        print("\n🎉 Email test completed successfully!")
        print("📧 Check SMTP server logs for the test email")
    else:
        print("\n❌ Email test failed")