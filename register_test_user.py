#!/usr/bin/env python3
"""
Test user registration for FlexiFinance
This script will register a new user and trigger email sending
"""

import requests
import re
from bs4 import BeautifulSoup

def register_user():
    """Register a test user and monitor email sending"""
    
    base_url = "http://localhost:8000"
    register_url = f"{base_url}/dashboard/register/"
    
    print("🚀 Starting user registration test...")
    
    # Create session to maintain cookies
    session = requests.Session()
    
    # Step 1: Get registration page and extract CSRF token
    print("📄 Loading registration page...")
    response = session.get(register_url)
    
    if response.status_code != 200:
        print(f"❌ Failed to load registration page: {response.status_code}")
        return False
    
    # Extract CSRF token
    soup = BeautifulSoup(response.content, 'html.parser')
    csrf_token = None
    csrf_input = soup.find('input', {'name': 'csrfmiddlewaretoken'})
    if csrf_input:
        csrf_token = csrf_input.get('value')
        print(f"✅ CSRF token extracted: {csrf_token[:10]}...")
    else:
        print("❌ CSRF token not found")
        return False
    
    # Step 2: Prepare registration data
    registration_data = {
        'csrfmiddlewaretoken': csrf_token,
        'first_name': 'Kevin',
        'last_name': 'Otieno', 
        'email': 'kevingalacha@gmail.com',
        'phone': '0712345678',
        'id_number': '12345678',
        'password': 'Airtel!23',
        'confirm_password': 'Airtel!23',
        'terms': 'on',
        'newsletter': 'on'
    }
    
    print("📝 Registration data prepared:")
    for key, value in registration_data.items():
        if key == 'csrfmiddlewaretoken':
            print(f"   {key}: {value[:10]}...")
        elif 'password' in key:
            print(f"   {key}: {'*' * len(value)}")
        else:
            print(f"   {key}: {value}")
    
    # Step 3: Submit registration
    print("🚀 Submitting registration...")
    headers = {
        'Referer': register_url,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    response = session.post(register_url, data=registration_data, headers=headers)
    
    print(f"📡 Response status: {response.status_code}")
    
    # Check response content for success/error messages
    content = response.text.lower()
    
    if 'success' in content or 'account created' in content or response.status_code == 302:
        print("✅ Registration appears successful!")
        
        # Check if redirected to confirmation page
        if response.status_code == 302:
            redirect_url = response.headers.get('Location', '')
            print(f"🔄 Redirected to: {redirect_url}")
        
        return True
        
    elif 'error' in content or 'invalid' in content:
        print("❌ Registration failed with errors:")
        # Extract error messages
        soup = BeautifulSoup(response.content, 'html.parser')
        error_divs = soup.find_all(['div', 'p'], class_=re.compile(r'.*error.*'))
        for error in error_divs[:3]:  # Show first 3 errors
            print(f"   Error: {error.get_text().strip()}")
        return False
        
    else:
        print("⚠️  Unclear response - showing page content preview:")
        print(content[:500] + "..." if len(content) > 500 else content)
        return False

if __name__ == "__main__":
    success = register_user()
    if success:
        print("\n🎉 Registration test completed successfully!")
        print("📧 Check SMTP server logs for email sending confirmation")
    else:
        print("\n❌ Registration test failed")