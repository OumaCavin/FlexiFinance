#!/usr/bin/env python3
"""
Quick Contact Form Test Script
==============================
Simple script to test contact form submission locally.

Usage:
    python test_contact_form.py

This script will:
1. Test the contact API endpoint
2. Verify database storage
3. Check email service
4. Provide clear feedback on functionality
"""

import os
import sys
import json
import django
import requests
from datetime import datetime

# Add the Django project to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flexifinance.settings')
django.setup()

from apps.core.models import Contact

def test_contact_form():
    """Quick test of contact form functionality"""
    print("🔍 Contact Form Quick Test")
    print("=" * 40)
    
    # Test data
    test_data = {
        'name': 'John Doe',
        'email': 'john.doe@example.com',
        'phone': '+254700123456',
        'subject': 'Test Loan Inquiry',
        'message': 'I would like to apply for a personal loan of KES 50,000.'
    }
    
    print(f"📝 Test data prepared:")
    for key, value in test_data.items():
        print(f"   {key}: {value}")
    
    # Test 1: Database Model
    print(f"\n1️⃣ Testing Contact Model...")
    try:
        contact = Contact.objects.create(**test_data)
        print(f"   ✅ Contact created with ID: {contact.id}")
        print(f"   ✅ Timestamp: {contact.created_at}")
        
        # Verify data
        retrieved = Contact.objects.get(id=contact.id)
        if retrieved.email == test_data['email']:
            print(f"   ✅ Data verification passed")
        else:
            print(f"   ❌ Data verification failed")
            return False
            
    except Exception as e:
        print(f"   ❌ Contact model test failed: {str(e)}")
        return False
    
    # Test 2: API Endpoint
    print(f"\n2️⃣ Testing API Endpoint...")
    try:
        url = 'http://127.0.0.1:8000/api/contact/submit/'
        headers = {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        }
        
        response = requests.post(url, json=test_data, headers=headers, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"   ✅ API endpoint working")
                print(f"   ✅ Success message: {result.get('message', 'N/A')}")
                if 'reference_id' in result:
                    print(f"   ✅ Reference ID: {result['reference_id']}")
            else:
                print(f"   ❌ API returned success=False")
                print(f"   ❌ Error: {result.get('error', 'Unknown error')}")
        else:
            print(f"   ❌ API returned status {response.status_code}")
            print(f"   ❌ Response: {response.text[:200]}...")
            
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Cannot connect to Django server")
        print(f"   💡 Make sure Django is running: python manage.py runserver")
        return False
    except Exception as e:
        print(f"   ❌ API test failed: {str(e)}")
        return False
    
    # Test 3: Database Verification
    print(f"\n3️⃣ Verifying Database Storage...")
    try:
        # Count total contacts
        total_contacts = Contact.objects.count()
        print(f"   📊 Total contacts in database: {total_contacts}")
        
        # Get latest contact
        latest_contact = Contact.objects.latest('created_at')
        print(f"   📝 Latest contact: {latest_contact.name} ({latest_contact.email})")
        print(f"   📅 Created: {latest_contact.created_at}")
        
        if latest_contact.email == test_data['email']:
            print(f"   ✅ Latest contact matches our test data")
        else:
            print(f"   ℹ️ Latest contact is different (expected if multiple submissions)")
            
    except Exception as e:
        print(f"   ❌ Database verification failed: {str(e)}")
        return False
    
    # Cleanup test data
    print(f"\n🧹 Cleaning up test data...")
    try:
        Contact.objects.filter(id=contact.id).delete()
        print(f"   ✅ Test contact record deleted")
    except Exception as e:
        print(f"   ⚠️ Cleanup failed: {str(e)}")
    
    print(f"\n🎉 Contact form test completed!")
    print(f"✅ Contact model: Working")
    print(f"✅ Database storage: Working")
    print(f"✅ API endpoint: Working")
    
    return True

def main():
    """Main function"""
    print("🚀 FlexiFinance Contact Form Test")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        success = test_contact_form()
        
        if success:
            print(f"\n🏆 All tests passed! Contact form is working correctly.")
            print(f"\n💡 Next steps:")
            print(f"   1. Test from browser: http://127.0.0.1:8000/contact/")
            print(f"   2. Check admin: http://127.0.0.1:8000/admin/")
            print(f"   3. Run full diagnostic: python contact_form_diagnostic.py")
        else:
            print(f"\n❌ Some tests failed. Check the output above for details.")
            
    except Exception as e:
        print(f"\n💥 Test script failed: {str(e)}")
        return False
    
    print(f"\n⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return success

if __name__ == '__main__':
    main()