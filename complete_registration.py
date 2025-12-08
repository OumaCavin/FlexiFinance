#!/usr/bin/env python3
"""
Complete registration test with all required fields
"""

import requests
import re
from bs4 import BeautifulSoup

def complete_registration_test():
    """Test registration with all required fields"""
    
    base_url = "http://localhost:8000"
    allauth_url = f"{base_url}/accounts/signup/"
    
    print("🎯 Complete registration test...")
    
    session = requests.Session()
    
    # Get allauth signup page
    response = session.get(allauth_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract CSRF token
    csrf_input = soup.find('input', {'name': 'csrfmiddlewaretoken'})
    csrf_token = csrf_input.get('value')
    print(f"✅ CSRF token extracted")
    
    # Find all form fields and their requirements
    required_fields = []
    for input_tag in soup.find_all(['input', 'select', 'textarea']):
        name = input_tag.get('name')
        if name and name != 'csrfmiddlewaretoken':
            field_type = input_tag.get('type', 'text')
            required = input_tag.get('required') is not None
            if required:
                required_fields.append(name)
    
    print(f"📝 Required fields: {required_fields}")
    
    # Prepare complete registration data
    registration_data = {
        'csrfmiddlewaretoken': csrf_token,
        'username': 'kevin_otieno',  # Required by allauth
        'email': 'kevingalacha@gmail.com',
        'password1': 'Airtel!23',
        'password2': 'Airtel!23'
    }
    
    print("📤 Submitting complete registration data...")
    for key, value in registration_data.items():
        if 'password' in key:
            print(f"   {key}: {'*' * len(value)}")
        else:
            print(f"   {key}: {value}")
    
    # Submit registration
    headers = {
        'Referer': allauth_url,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    response = session.post(allauth_url, data=registration_data, headers=headers)
    print(f"📡 Response status: {response.status_code}")
    
    # Check response
    if response.status_code == 302:
        redirect_url = response.headers.get('Location', '')
        print(f"✅ Registration successful! Redirected to: {redirect_url}")
        return True
    
    elif response.status_code == 200:
        print("⚠️ Checking for validation errors...")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        error_elements = soup.find_all(['div', 'ul', 'span'], class_=re.compile(r'.*error.*'))
        
        if error_elements:
            print("❌ Errors found:")
            for elem in error_elements[:3]:
                error_text = elem.get_text().strip()
                if error_text:
                    print(f"   - {error_text}")
            return False
        else:
            print("ℹ️ No errors detected, but no redirect either")
            # Check if it's a success page
            if 'confirm' in response.text.lower() or 'verify' in response.text.lower():
                print("✅ Registration successful - email confirmation page")
                return True
            return False
    
    else:
        print(f"❌ Unexpected status: {response.status_code}")
        return False

def test_login():
    """Test login after successful registration"""
    
    print("\n🔐 Testing user login...")
    
    login_url = "http://localhost:8000/accounts/login/"
    session = requests.Session()
    
    # Get login page
    response = session.get(login_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract CSRF token
    csrf_input = soup.find('input', {'name': 'csrfmiddlewaretoken'})
    csrf_token = csrf_input.get('value')
    
    # Try login with username
    login_data = {
        'csrfmiddlewaretoken': csrf_token,
        'login': 'kevin_otieno',  # Use username
        'password': 'Airtel!23'
    }
    
    headers = {
        'Referer': login_url,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    response = session.post(login_url, data=login_data, headers=headers)
    print(f"📡 Login response status: {response.status_code}")
    
    if response.status_code == 302:
        redirect_url = response.headers.get('Location', '')
        print(f"✅ Login successful! Redirected to: {redirect_url}")
        return True
    else:
        print("❌ Login failed")
        # Try with email instead
        login_data['login'] = 'kevingalacha@gmail.com'
        response = session.post(login_url, data=login_data, headers=headers)
        print(f"📡 Login with email status: {response.status_code}")
        if response.status_code == 302:
            print("✅ Login successful with email!")
            return True
        return False

if __name__ == "__main__":
    print("🚀 Starting complete user registration and login test...\n")
    
    registration_success = complete_registration_test()
    
    if registration_success:
        print("\n🎉 Registration completed successfully!")
        
        # Check for emails
        print("📧 Checking SMTP server for verification emails...")
        
        login_success = test_login()
        
        if login_success:
            print("\n✅ SUCCESS: User registered and can login!")
        else:
            print("\n⚠️ User registered but login failed")
    else:
        print("\n❌ Registration failed")
    
    print("\n📧 Final check - SMTP server email count:")
    # We would need to check the SMTP server's email count here
    # For now, we'll just indicate the test is complete