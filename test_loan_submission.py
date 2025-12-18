#!/usr/bin/env python3
"""
Test script to debug loan form submission
"""

import os
import sys
import django

# Add the Django project to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flexifinance.settings')
django.setup()

def test_loan_submission():
    """Test loan submission with proper field mapping"""
    
    # Simulate the data that would come from the form
    test_data = {
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john.doe.test@example.com',
        'phone': '+254700123456',  # Form field name
        'id_number': '12345678',   # Form field name
        'date_of_birth': '1990-01-01',
        'loan_amount': '50000',
        'loan_purpose': 'business',
        'loan_tenure': '12',
        'monthly_income': '50000',
        'employment_status': 'employed',
        'employer_name': 'Test Company',
        'work_experience': '2-5',
        'ref1_name': 'Jane Doe',
        'ref1_phone': '+254700987654',
        'ref1_relationship': 'spouse',
        'terms_consent': True,
        'credit_check': True,
        'marketing_consent': False
    }
    
    print("🧪 Testing Loan Submission Data")
    print("=" * 50)
    
    try:
        from apps.core.views import LoanApplicationView
        from django.test import RequestFactory
        from django.http import JsonResponse
        import json
        
        # Create a mock request
        factory = RequestFactory()
        request = factory.post('/loan-application/', 
                             data=json.dumps(test_data),
                             content_type='application/json')
        
        # Create view instance and call post method
        view = LoanApplicationView()
        response = view.post(request)
        
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.content.decode()}")
        
        if response.status_code == 200:
            print("✅ Loan submission test successful!")
            return True
        else:
            print("❌ Loan submission test failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error testing loan submission: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_user_creation():
    """Test user creation with form data"""
    from apps.users.models import User
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    
    print("\n🔍 Testing User Creation")
    print("=" * 50)
    
    try:
        # Test data matching form fields
        test_email = 'test.user@example.com'
        
        # Check if user exists and delete for clean test
        try:
            existing_user = User.objects.get(email=test_email)
            existing_user.delete()
            print(f"Deleted existing test user: {test_email}")
        except User.DoesNotExist:
            pass
        
        # Create user with form field mapping
        user = User.objects.create_user(
            username=test_email,
            email=test_email,
            password='testpassword123',
            first_name='Test',
            last_name='User',
            phone_number='+254700123456',  # Maps from form 'phone' field
            national_id='12345678',        # Maps from form 'id_number' field
        )
        
        print(f"✅ Created test user: {user.email}")
        print(f"   Phone: {user.phone_number}")
        print(f"   National ID: {user.national_id}")
        
        # Clean up
        user.delete()
        print("✅ Cleaned up test user")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing user creation: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🚀 Django Loan Form Debug Testing")
    print("=" * 50)
    
    # Test user creation
    user_test = test_user_creation()
    
    # Test loan submission
    loan_test = test_loan_submission()
    
    print("\n📊 Test Results")
    print("=" * 50)
    print(f"User Creation Test: {'✅ PASS' if user_test else '❌ FAIL'}")
    print(f"Loan Submission Test: {'✅ PASS' if loan_test else '❌ FAIL'}")
    
    if user_test and loan_test:
        print("\n🎉 All tests passed! The form submission should work.")
        return True
    else:
        print("\n💥 Some tests failed. Check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)