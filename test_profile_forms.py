#!/usr/bin/env python
"""
Test script to verify profile forms are working correctly
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flexifinance.settings')
sys.path.append('/workspace/django-microfinance-mpsa')
django.setup()

from django.contrib.auth import get_user_model
from apps.users.forms import IdentityForm, ContactForm, EmploymentForm, EmergencyContactForm

def test_forms():
    """Test all profile forms with sample data"""
    User = get_user_model()
    
    # Create a test user if doesn't exist
    try:
        user = User.objects.get(username='testuser')
    except User.DoesNotExist:
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        print(f"Created test user: {user.username}")
    
    print("\n=== Testing Profile Forms ===")
    
    # Test Identity Form
    print("\n1. Testing IdentityForm...")
    identity_data = {
        'first_name': 'John',
        'middle_name': 'Michael',
        'last_name': 'Doe',
        'date_of_birth': '1990-01-01',
        'national_id': '12345678'
    }
    
    identity_form = IdentityForm(data=identity_data, instance=user)
    print(f"Identity form valid: {identity_form.is_valid()}")
    if not identity_form.is_valid():
        print(f"Identity form errors: {identity_form.errors}")
    
    # Test Contact Form
    print("\n2. Testing ContactForm...")
    contact_data = {
        'phone_number': '+254712345678',
        'address': '123 Test Street',
        'city': 'Nairobi',
        'county': 'Nairobi',
        'country': 'Kenya'
    }
    
    contact_form = ContactForm(data=contact_data, instance=user)
    print(f"Contact form valid: {contact_form.is_valid()}")
    if not contact_form.is_valid():
        print(f"Contact form errors: {contact_form.errors}")
    
    # Test Employment Form
    print("\n3. Testing EmploymentForm...")
    employment_data = {
        'occupation': 'Software Engineer',
        'employer_name': 'Tech Company',
        'monthly_income': '50000',
        'employment_duration': '24'
    }
    
    employment_form = EmploymentForm(data=employment_data, instance=user)
    print(f"Employment form valid: {employment_form.is_valid()}")
    if not employment_form.is_valid():
        print(f"Employment form errors: {employment_form.errors}")
    
    # Test Emergency Contact Form
    print("\n4. Testing EmergencyContactForm...")
    emergency_data = {
        'emergency_contact_name': 'Jane Doe',
        'emergency_contact_relationship': 'Spouse',
        'emergency_contact_phone': '+254798765432'
    }
    
    emergency_form = EmergencyContactForm(data=emergency_data, instance=user)
    print(f"Emergency form valid: {emergency_form.is_valid()}")
    if not emergency_form.is_valid():
        print(f"Emergency form errors: {emergency_form.errors}")
    
    # Try saving one form to test database persistence
    print("\n5. Testing database persistence...")
    try:
        identity_form.save()
        print("✅ Identity form saved successfully!")
        
        # Verify the data was saved
        user.refresh_from_db()
        print(f"User first_name: {user.first_name}")
        print(f"User last_name: {user.last_name}")
        print(f"User national_id: {user.national_id}")
        
    except Exception as e:
        print(f"❌ Error saving identity form: {e}")
    
    print("\n=== Form Testing Complete ===")

if __name__ == '__main__':
    test_forms()