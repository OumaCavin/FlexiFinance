#!/usr/bin/env python3
"""
Test script to verify SMTP email functionality with Django
"""

import os
import sys
import django
import subprocess

# Add the project directory to Python path
sys.path.insert(0, '/workspace/django-microfinance-mpsa')

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flexifinance.settings')

# Configure Django
django.setup()

# Import Django email functionality
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
import time

def test_email_functionality():
    """Test email functionality"""
    print("🔧 Testing SMTP Email Functionality")
    print("=" * 50)
    
    # Print current email configuration
    print(f"📧 Email Backend: {settings.EMAIL_BACKEND}")
    print(f"📡 SMTP Host: {getattr(settings, 'EMAIL_HOST', 'Not configured')}")
    print(f"🔌 SMTP Port: {getattr(settings, 'EMAIL_PORT', 'Not configured')}")
    print(f"🔒 TLS Enabled: {getattr(settings, 'EMAIL_USE_TLS', 'Not configured')}")
    print(f"📤 From Email: {getattr(settings, 'FROM_EMAIL', 'Not configured')}")
    print()
    
    # Test 1: Simple email
    print("📤 Test 1: Sending simple email...")
    try:
        result = send_mail(
            subject='Test Email - FlexiFinance',
            message='This is a test email from FlexiFinance project using SMTP!',
            from_email=settings.FROM_EMAIL,
            recipient_list=['test@flexifinance.com'],
            fail_silently=False,
        )
        print(f"✅ Simple email sent successfully! (Result: {result})")
        time.sleep(2)  # Give server time to process
    except Exception as e:
        print(f"❌ Failed to send simple email: {e}")
    
    print()
    
    # Test 2: Email with HTML content
    print("📤 Test 2: Sending HTML email...")
    try:
        email_msg = EmailMessage(
            subject='Welcome to FlexiFinance',
            body="""
            <html>
            <body>
                <h2>Welcome to FlexiFinance!</h2>
                <p>Thank you for joining our platform.</p>
                <p>This is a test email sent via our SMTP server.</p>
                <br>
                <p>Best regards,<br>FlexiFinance Team</p>
            </body>
            </html>
            """,
            from_email=settings.FROM_EMAIL,
            to=['welcome@flexifinance.com'],
        )
        email_msg.content_subtype = "html"
        email_msg.send()
        print("✅ HTML email sent successfully!")
        time.sleep(2)  # Give server time to process
    except Exception as e:
        print(f"❌ Failed to send HTML email: {e}")
    
    print()
    
    # Test 3: Email with attachments (simulated)
    print("📤 Test 3: Sending email with custom headers...")
    try:
        email_msg = EmailMessage(
            subject='Test Email with Custom Headers',
            body='This email includes custom headers for testing.',
            from_email=settings.FROM_EMAIL,
            to=['custom@flexifinance.com'],
        )
        email_msg.headers['X-Mailer'] = 'FlexiFinance SMTP Test'
        email_msg.headers['X-Priority'] = '3'
        email_msg.send()
        print("✅ Email with custom headers sent successfully!")
        time.sleep(2)  # Give server time to process
    except Exception as e:
        print(f"❌ Failed to send email with custom headers: {e}")
    
    print()
    print("🎉 Email testing completed!")
    print("📋 Check the SMTP server output above to see received emails")
    print("📄 Also check 'smtp_emails.log' file for detailed logs")

if __name__ == "__main__":
    test_email_functionality()