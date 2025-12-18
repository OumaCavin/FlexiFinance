#!/usr/bin/env python3
"""
Profile Form Debug Script
This script tests the profile forms directly to identify why saving isn't working.
"""

import os
import sys
import django

# Setup Django
sys.path.append('/workspace/django-microfinance-mpsa')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flexifinance.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.users.forms import IdentityForm, ContactForm, EmploymentForm, EmergencyContactForm
from django.http import HttpRequest
from django.contrib.sessions.middleware import SessionMiddleware

User = get_user_model()

def test_profile_forms():
    """Test profile forms with actual user data"""
    print("🔍 Testing Profile Forms...")
    
    # Create a test user or get existing one
    try:
        user = User.objects.get(username='testuser')
        print(f"✅ Found existing test user: {user.username}")
    except User.DoesNotExist:
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            phone_number='+254700123456',
            national_id='12345678'
        )
        print(f"✅ Created test user: {user.username}")
    
    # Create request object with session
    request = HttpRequest()
    request.user = user
    request.method = 'POST'
    
    # Add session middleware
    middleware = SessionMiddleware(lambda x: x)
    middleware.process_request(request)
    request.session.save()
    
    print(f"📋 Testing forms for user: {user.username}")
    print(f"📧 Email: {user.email}")
    print(f"📱 Phone: {user.phone_number}")
    print(f"🆔 National ID: {user.national_id}")
    
    # Test Identity Form
    print("\n" + "="*50)
    print("🔹 TESTING IDENTITY FORM")
    print("="*50)
    
    identity_data = {
        'form_type': 'identity',
        'first_name': 'John',
        'last_name': 'Doe',
        'date_of_birth': '1990-01-01',
        'gender': 'M',
        'national_id': '12345678',  # Same as existing
        'phone_number': '+254700123456',  # Same as existing
    }
    
    identity_form = IdentityForm(data=identity_data, instance=user)
    print(f"📋 Form valid: {identity_form.is_valid()}")
    
    if not identity_form.is_valid():
        print("❌ Form errors:")
        for field, errors in identity_form.errors.items():
            for error in errors:
                print(f"  - {field}: {error}")
    else:
        print("✅ Form is valid!")
        try:
            identity_form.save()
            print("💾 Form saved successfully!")
        except Exception as e:
            print(f"❌ Save failed: {e}")
    
    # Test Contact Form
    print("\n" + "="*50)
    print("🔹 TESTING CONTACT FORM")
    print("="*50)
    
    contact_data = {
        'form_type': 'contact',
        'address': '123 Test Street',
        'city': 'Nairobi',
        'county': 'Nairobi County',
        'postal_code': '00100',
        'country': 'Kenya',
        'email': 'test@example.com',  # Same as existing
    }
    
    contact_form = ContactForm(data=contact_data, instance=user)
    print(f"📋 Form valid: {contact_form.is_valid()}")
    
    if not contact_form.is_valid():
        print("❌ Form errors:")
        for field, errors in contact_form.errors.items():
            for error in errors:
                print(f"  - {field}: {error}")
    else:
        print("✅ Form is valid!")
        try:
            contact_form.save()
            print("💾 Form saved successfully!")
        except Exception as e:
            print(f"❌ Save failed: {e}")
    
    # Test Employment Form
    print("\n" + "="*50)
    print("🔹 TESTING EMPLOYMENT FORM")
    print("="*50)
    
    employment_data = {
        'form_type': 'employment',
        'employment_status': 'employed',
        'employer_name': 'Test Company',
        'job_title': 'Software Developer',
        'monthly_income': '50000',
        'employment_duration': '24',
    }
    
    employment_form = EmploymentForm(data=employment_data, instance=user)
    print(f"📋 Form valid: {employment_form.is_valid()}")
    
    if not employment_form.is_valid():
        print("❌ Form errors:")
        for field, errors in employment_form.errors.items():
            for error in errors:
                print(f"  - {field}: {error}")
    else:
        print("✅ Form is valid!")
        try:
            employment_form.save()
            print("💾 Form saved successfully!")
        except Exception as e:
            print(f"❌ Save failed: {e}")
    
    # Test Emergency Contact Form
    print("\n" + "="*50)
    print("🔹 TESTING EMERGENCY CONTACT FORM")
    print("="*50)
    
    emergency_data = {
        'form_type': 'emergency',
        'emergency_contact_name': 'Jane Doe',
        'emergency_contact_phone': '+254700654321',
        'emergency_contact_relationship': 'spouse',
    }
    
    emergency_form = EmergencyContactForm(data=emergency_data, instance=user)
    print(f"📋 Form valid: {emergency_form.is_valid()}")
    
    if not emergency_form.is_valid():
        print("❌ Form errors:")
        for field, errors in emergency_form.errors.items():
            for error in errors:
                print(f"  - {field}: {error}")
    else:
        print("✅ Form is valid!")
        try:
            emergency_form.save()
            print("💾 Form saved successfully!")
        except Exception as e:
            print(f"❌ Save failed: {e}")
    
    # Verify database updates
    print("\n" + "="*50)
    print("🔹 VERIFYING DATABASE UPDATES")
    print("="*50)
    
    # Refresh user from database
    user.refresh_from_db()
    
    print(f"📧 Email: {user.email}")
    print(f"📱 Phone: {user.phone_number}")
    print(f"🆔 National ID: {user.national_id}")
    print(f"📍 Address: {user.address}")
    print(f"🏢 Employer: {user.employer_name}")
    print(f"👤 Emergency Contact: {user.emergency_contact_name}")
    
    print("\n🎉 Profile form testing completed!")

if __name__ == "__main__":
    test_profile_forms()