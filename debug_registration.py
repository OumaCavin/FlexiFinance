#!/usr/bin/env python3
"""
Debug registration form submission
"""

import requests
import re
from bs4 import BeautifulSoup

def debug_registration():
    """Debug the registration process"""
    
    base_url = "http://localhost:8000"
    register_url = f"{base_url}/dashboard/register/"
    
    print("🔍 Debugging registration process...")
    
    # Create session
    session = requests.Session()
    
    # Get registration page
    print("📄 Getting registration page...")
    response = session.get(register_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract CSRF token
    csrf_token = None
    csrf_input = soup.find('input', {'name': 'csrfmiddlewaretoken'})
    if csrf_input:
        csrf_token = csrf_input.get('value')
        print(f"✅ CSRF token: {csrf_token[:10]}...")
    
    # Check form action
    form = soup.find('form')
    if form:
        action = form.get('action', 'No action found')
        method = form.get('method', 'No method found')
        print(f"📝 Form action: {action}")
        print(f"📝 Form method: {method}")
    
    # Check for error messages
    error_divs = soup.find_all('div', class_=re.compile(r'.*error.*'))
    if error_divs:
        print("❌ Found error messages:")
        for error in error_divs[:3]:
            print(f"   Error: {error.get_text().strip()}")
    
    # Try to access allauth signup directly
    print("\n🔍 Trying allauth signup page...")
    allauth_url = f"{base_url}/accounts/signup/"
    response = session.get(allauth_url)
    
    print(f"📡 Allauth signup response: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Allauth signup page accessible")
        
        # Extract CSRF from allauth page
        soup = BeautifulSoup(response.content, 'html.parser')
        csrf_input = soup.find('input', {'name': 'csrfmiddlewaretoken'})
        if csrf_input:
            csrf_token = csrf_input.get('value')
            print(f"✅ Allauth CSRF token: {csrf_token[:10]}...")
        
        # Try registration through allauth
        registration_data = {
            'csrfmiddlewaretoken': csrf_token,
            'email': 'kevingalacha@gmail.com',
            'email2': 'kevingalacha@gmail.com',
            'password1': 'Airtel!23',
            'password2': 'Airtel!23',
            'terms_accepted': 'on'
        }
        
        print("🚀 Submitting to allauth...")
        headers = {
            'Referer': allauth_url,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = session.post(allauth_url, data=registration_data, headers=headers)
        print(f"📡 Response status: {response.status_code}")
        
        if response.status_code == 302:
            redirect_url = response.headers.get('Location', '')
            print(f"🔄 Redirected to: {redirect_url}")
            return True
        else:
            print("⚠️ No redirect - showing content preview:")
            content = response.text[:500]
            print(content)
            return False
    
    else:
        print("❌ Allauth signup page not accessible")
        return False

if __name__ == "__main__":
    debug_registration()