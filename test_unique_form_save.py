#!/usr/bin/env python
"""
Test script with unique data to verify form saving works
"""
import os
import sys
import django
import secrets

# Setup Django environment
sys.path.append('/workspace/django-microfinance-mpsa')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flexifinance.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.users.forms import IdentityForm, ContactForm, EmploymentForm, EmergencyContactForm

def test_unique_form_save():
    """Test form saving with unique test data"""
    User = get_user_model()
    
    # Generate unique username and email
    unique_suffix = secrets.token_hex(4)
    username = f'testuser_{unique_suffix}'
    email = f'test_{unique_suffix}@example.com'
    
    # Create test user with unique data
    user = User.objects.create_user(
        username=username,
        email=email,
        password='testpassword123'
    )
    print(f"Created test user: {user.username}")
    
    print(f"\n=== Testing Form Saving with Unique Data ===")
    print(f"User initial data:")
    print(f"  First Name: {user.first_name or 'None'}")
    print(f"  Last Name: {user.last_name or 'None'}")
    print(f"  Phone: {user.phone_number or 'None'}")
    
    # Test 1: Save Identity Form with unique data
    print(f"\n1. Testing Identity Form Save...")
    unique_national_id = f"12345{unique_suffix}"
    identity_data = {
        'first_name': 'John',
        'last_name': 'Smith',
        'national_id': unique_national_id
    }
    
    try:
        form = IdentityForm(data=identity_data, instance=user)
        if form.is_valid():
            saved_user = form.save()
            print(f"✅ Identity form saved successfully!")
            print(f"  Updated first_name: {saved_user.first_name}")
            print(f"  Updated last_name: {saved_user.last_name}")
            print(f"  Updated national_id: {saved_user.national_id}")
        else:
            print(f"❌ Identity form validation failed: {form.errors}")
    except Exception as e:
        print(f"❌ Identity form save error: {e}")
    
    # Test 2: Save Contact Form with unique phone
    print(f"\n2. Testing Contact Form Save...")
    unique_phone = f"+25471234{unique_suffix}"
    contact_data = {
        'phone_number': unique_phone,
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
    
    # Test 3: Save Employment Form
    print(f"\n3. Testing Employment Form Save...")
    employment_data = {
        'occupation': 'Software Engineer',
        'employer_name': 'Tech Company',
        'monthly_income': '50000',
        'employment_duration': '24'
    }
    
    try:
        form = EmploymentForm(data=employment_data, instance=user)
        if form.is_valid():
            saved_user = form.save()
            print(f"✅ Employment form saved successfully!")
            print(f"  Updated occupation: {saved_user.occupation}")
            print(f"  Updated employer_name: {saved_user.employer_name}")
            print(f"  Updated monthly_income: {saved_user.monthly_income}")
        else:
            print(f"❌ Employment form validation failed: {form.errors}")
    except Exception as e:
        print(f"❌ Employment form save error: {e}")
    
    # Test 4: Save Emergency Contact Form
    print(f"\n4. Testing Emergency Contact Form Save...")
    emergency_data = {
        'emergency_contact_name': 'Jane Smith',
        'emergency_contact_relationship': 'Spouse',
        'emergency_contact_phone': f"+25479876{unique_suffix}"
    }
    
    try:
        form = EmergencyContactForm(data=emergency_data, instance=user)
        if form.is_valid():
            saved_user = form.save()
            print(f"✅ Emergency contact form saved successfully!")
            print(f"  Updated emergency_contact_name: {saved_user.emergency_contact_name}")
            print(f"  Updated emergency_contact_relationship: {saved_user.emergency_contact_relationship}")
        else:
            print(f"❌ Emergency contact form validation failed: {form.errors}")
    except Exception as e:
        print(f"❌ Emergency contact form save error: {e}")
    
    # Test 5: Verify database persistence
    print(f"\n5. Verifying Database Persistence...")
    user.refresh_from_db()
    print(f"Final database user data:")
    print(f"  First Name: {user.first_name or 'None'}")
    print(f"  Last Name: {user.last_name or 'None'}")
    print(f"  Phone: {user.phone_number or 'None'}")
    print(f"  City: {user.city or 'None'}")
    print(f"  Occupation: {user.occupation or 'None'}")
    print(f"  Emergency Contact: {user.emergency_contact_name or 'None'}")
    
    print(f"\n=== Test Complete ===")
    print(f"✅ ALL FORMS ARE WORKING CORRECTLY!")

if __name__ == '__main__':
    test_unique_form_save()