#!/usr/bin/env python3
"""
Detailed debug registration with error analysis
"""

import requests
import re
from bs4 import BeautifulSoup

def detailed_debug_registration():
    """Detailed debugging of registration process"""
    
    base_url = "http://localhost:8000"
    
    print("🔍 Detailed registration debugging...")
    
    # Test allauth signup directly
    allauth_url = f"{base_url}/accounts/signup/"
    session = requests.Session()
    
    # Get allauth signup page
    response = session.get(allauth_url)
    print(f"📄 Allauth page status: {response.status_code}")
    
    if response.status_code != 200:
        print("❌ Cannot access allauth signup page")
        return False
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract CSRF token
    csrf_input = soup.find('input', {'name': 'csrfmiddlewaretoken'})
    if not csrf_input:
        print("❌ CSRF token not found")
        return False
    
    csrf_token = csrf_input.get('value')
    print(f"✅ CSRF token: {csrf_token[:10]}...")
    
    # Find all form fields
    form_fields = {}
    for input_tag in soup.find_all(['input', 'select', 'textarea']):
        name = input_tag.get('name')
        if name and name != 'csrfmiddlewaretoken':
            field_type = input_tag.get('type', 'text')
            if field_type in ['text', 'email', 'password']:
                form_fields[name] = field_type
    
    print(f"📝 Found form fields: {list(form_fields.keys())}")
    
    # Prepare registration data
    registration_data = {
        'csrfmiddlewaretoken': csrf_token,
        'email': 'kevingalacha@gmail.com',
        'password1': 'Airtel!23',
        'password2': 'Airtel!23'
    }
    
    # Add required fields based on form
    if 'email2' in form_fields:
        registration_data['email2'] = 'kevingalacha@gmail.com'
    
    if 'terms_accepted' in form_fields:
        registration_data['terms_accepted'] = 'on'
    
    print("📤 Submitting registration data...")
    print(f"   Data: {registration_data}")
    
    # Submit registration
    headers = {
        'Referer': allauth_url,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    response = session.post(allauth_url, data=registration_data, headers=headers)
    print(f"📡 Response status: {response.status_code}")
    
    # Analyze response
    if response.status_code == 302:
        redirect_url = response.headers.get('Location', '')
        print(f"✅ Registration successful! Redirected to: {redirect_url}")
        return True
    
    elif response.status_code == 200:
        print("⚠️ Registration form returned with errors")
        
        # Check for error messages
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for common error patterns
        error_selectors = [
            'div[class*="error"]',
            'ul[class*="errorlist"]',
            'span[class*="error"]',
            'p[class*="error"]',
            '.errorlist',
            '.alert-error'
        ]
        
        errors_found = []
        for selector in error_selectors:
            error_elements = soup.select(selector)
            for elem in error_elements:
                error_text = elem.get_text().strip()
                if error_text and error_text not in ['', ' ']:
                    errors_found.append(error_text)
        
        if errors_found:
            print("❌ Validation errors found:")
            for i, error in enumerate(errors_found[:5], 1):
                print(f"   {i}. {error}")
        else:
            print("ℹ️ No specific error messages found")
        
        # Check if user was created anyway
        if 'already registered' in response.text.lower() or 'email already exists' in response.text.lower():
            print("ℹ️ User might already exist")
            return True
        
        return False
    
    else:
        print(f"❌ Unexpected response status: {response.status_code}")
        return False

def test_login_after_registration():
    """Test if user can login after registration"""
    
    print("\n🔐 Testing login capability...")
    
    login_url = "http://localhost:8000/accounts/login/"
    session = requests.Session()
    
    # Get login page
    response = session.get(login_url)
    if response.status_code != 200:
        print("❌ Cannot access login page")
        return False
    
    soup = BeautifulSoup(response.content, 'html.parser')
    csrf_input = soup.find('input', {'name': 'csrfmiddlewaretoken'})
    if not csrf_input:
        print("❌ CSRF token not found on login page")
        return False
    
    csrf_token = csrf_input.get('value')
    
    # Try to login
    login_data = {
        'csrfmiddlewaretoken': csrf_token,
        'login': 'kevingalacha@gmail.com',
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
        return False

if __name__ == "__main__":
    registration_success = detailed_debug_registration()
    
    if registration_success:
        print("\n🎉 Registration completed successfully!")
        login_success = test_login_after_registration()
        if login_success:
            print("✅ User can login successfully!")
        else:
            print("⚠️ User registered but cannot login")
    else:
        print("\n❌ Registration failed")