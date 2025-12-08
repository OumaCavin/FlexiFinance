#!/usr/bin/env python3
"""
Test script to verify environment variables are loaded correctly
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.insert(0, '/workspace/django-microfinance-mpsa')

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flexifinance.settings')

# Configure Django
django.setup()

# Import Django email functionality
from django.conf import settings

def test_env_variables():
    """Test environment variables"""
    print("🔧 Testing Environment Variables")
    print("=" * 50)
    
    # Print current email configuration
    print(f"📧 Email Backend: {settings.EMAIL_BACKEND}")
    print(f"📡 SMTP Host: {getattr(settings, 'EMAIL_HOST', 'Not configured')}")
    print(f"🔌 SMTP Port: {getattr(settings, 'EMAIL_PORT', 'Not configured')}")
    print(f"🔒 TLS Enabled: {getattr(settings, 'EMAIL_USE_TLS', 'Not configured')}")
    print(f"📤 From Email: {getattr(settings, 'FROM_EMAIL', 'Not configured')}")
    
    # Print environment variable values
    from decouple import config
    print("\n📋 Environment Variables:")
    print(f"EMAIL_BACKEND: {config('EMAIL_BACKEND', default='not set')}")
    print(f"EMAIL_HOST: {config('EMAIL_HOST', default='not set')}")
    print(f"EMAIL_PORT: {config('EMAIL_PORT', default='not set')}")
    print(f"EMAIL_USE_TLS: {config('EMAIL_USE_TLS', default='not set')}")
    print(f"FROM_EMAIL: {config('FROM_EMAIL', default='not set')}")
    
    # Check if .env file exists and its content
    print(f"\n📄 .env file exists: {os.path.exists('/workspace/django-microfinance-mpsa/.env')}")
    
    if os.path.exists('/workspace/django-microfinance-mpsa/.env'):
        print("📋 First few lines of .env file:")
        with open('/workspace/django-microfinance-mpsa/.env', 'r') as f:
            lines = f.readlines()[:10]
            for i, line in enumerate(lines, 1):
                print(f"  {i}: {line.strip()}")

if __name__ == "__main__":
    test_env_variables()