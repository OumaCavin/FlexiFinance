#!/usr/bin/env python
"""
Simple test script to debug form saving issues
"""
import os
import sys
import django

# Setup Django environment
sys.path.append('/workspace/django-microfinance-mpsa')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flexifinance.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import RequestFactory
from apps.users.forms import IdentityForm, ContactForm, EmploymentForm, EmergencyContactForm

def test_form_save():
    """Test form saving with a mock user"""
    User = get_user_model()
    
    # Create or get test user
    try:
        user = User.objects.get(username='testuser_debug')
    except User.DoesNotExist:
        user = User.objects.create_user(
            username='testuser_debug',
            email='debug@example.com',
            password='testpassword123'
        )
        print(f"Created test user: {user.username}")
    
    print(f"\n=== Testing Form Saving ===")
    print(f"User initial data:")
    print(f"  First Name: {user.first_name or 'None'}")
    print(f"  Last Name: {user.last_name or 'None'}")
    print(f"  Phone: {user.phone_number or 'None'}")
    
    # Test 1: Save Identity Form
    print(f"\n1. Testing Identity Form Save...")
    identity_data = {
        'first_name': 'John',
        'last_name': 'Smith',
        'national_id': '12345678'
    }
    
    try:
        form = IdentityForm(data=identity_data, instance=user)
        if form.is_valid():
            saved_user = form.save()
            print(f"✅ Identity form saved successfully!")
            print(f"  Updated first_name: {saved_user.first_name}")
            print(f"  Updated last_name: {saved_user.last_name}")
        else:
            print(f"❌ Identity form validation failed: {form.errors}")
    except Exception as e:
        print(f"❌ Identity form save error: {e}")
    
    # Test 2: Save Contact Form
    print(f"\n2. Testing Contact Form Save...")
    contact_data = {
        'phone_number': '+254712345678',
        'city': 'Nairobi',
        'country': 'Kenya'
    }
    
    try:
        form = ContactForm(data=contact_data, instance=user)
        if form.is_valid():
            saved_user = form.save()
            print(f"✅ Contact form saved successfully!")
            print(f"  Updated phone_number: {saved_user.phone_number}")
            print(f"  Updated city: {saved_user.city}")
        else:
            print(f"❌ Contact form validation failed: {form.errors}")
    except Exception as e:
        print(f"❌ Contact form save error: {e}")
    
    # Test 3: Verify database persistence
    print(f"\n3. Verifying Database Persistence...")
    user.refresh_from_db()
    print(f"Database user data:")
    print(f"  First Name: {user.first_name or 'None'}")
    print(f"  Last Name: {user.last_name or 'None'}")
    print(f"  Phone: {user.phone_number or 'None'}")
    print(f"  City: {user.city or 'None'}")
    
    print(f"\n=== Test Complete ===")

if __name__ == '__main__':
    test_form_save()