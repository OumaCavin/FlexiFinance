#!/usr/bin/env python3
"""
Registration Endpoint Test Script
Run this in your local FlexiFinance project to test if the 502 Bad Gateway is fixed
"""

import subprocess
import sys
import time
import requests

def start_django_server():
    """Start Django development server"""
    print("🚀 Starting Django development server...")
    try:
        # Start server in background
        process = subprocess.Popen(
            [sys.executable, "manage.py", "runserver", "8000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd="/path/to/your/django-project"  # Update this path
        )
        
        # Wait for server to start
        print("⏳ Waiting for server to start...")
        time.sleep(5)
        
        return process
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return None

def test_registration_endpoint():
    """Test the registration endpoint"""
    print("\n🧪 Testing registration endpoint...")
    
    try:
        # Test the endpoint
        response = requests.get("http://localhost:8000/dashboard/register/", timeout=10)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS: Registration endpoint is working!")
            print(f"✅ Content-Type: {response.headers.get('Content-Type', 'Unknown')}")
            print(f"✅ Content Length: {len(response.content)} bytes")
            
            # Check if it contains registration form
            if "register" in response.text.lower() or "signup" in response.text.lower():
                print("✅ Registration form content detected")
            else:
                print("⚠️  Warning: Registration form content not clearly detected")
                
            return True
            
        elif response.status_code == 502:
            print("❌ FAILED: 502 Bad Gateway error still occurs")
            return False
            
        elif response.status_code == 404:
            print("❌ FAILED: 404 Not Found - Endpoint doesn't exist")
            return False
            
        else:
            print(f"⚠️  Unexpected status code: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ FAILED: Cannot connect to server")
        print("   Make sure Django server is running on port 8000")
        return False
        
    except requests.exceptions.Timeout:
        print("❌ FAILED: Request timeout")
        return False
        
    except Exception as e:
        print(f"❌ FAILED: Error testing endpoint: {e}")
        return False

def test_mailpit():
    """Test if Mailpit is running"""
    print("\n📧 Testing Mailpit SMTP server...")
    
    try:
        response = requests.get("http://localhost:8080", timeout=5)
        if response.status_code == 200:
            print("✅ SUCCESS: Mailpit is running")
            return True
        else:
            print(f"⚠️  Mailpit returned status: {response.status_code}")
            return False
    except:
        print("❌ FAILED: Mailpit is not running")
        print("   Start it with: mailpit --http :8080 --smtp :2526")
        return False

def main():
    """Main test function"""
    print("🔍 FlexiFinance Registration Endpoint Test")
    print("=" * 50)
    
    # Test Mailpit first
    mailpit_ok = test_mailpit()
    
    # Start Django server
    server_process = start_django_server()
    
    if not server_process:
        print("\n❌ Cannot proceed without Django server")
        return False
    
    try:
        # Test registration endpoint
        endpoint_ok = test_registration_endpoint()
        
        # Cleanup
        print("\n🧹 Cleaning up...")
        server_process.terminate()
        server_process.wait()
        
        if endpoint_ok:
            print("\n🎉 SUCCESS: 502 Bad Gateway error is FIXED!")
            print("\n📋 Next steps:")
            print("1. Test user registration in browser: http://localhost:8000/dashboard/register/")
            print("2. Check emails at: http://localhost:8080")
            print("3. Test login functionality")
            return True
        else:
            print("\n❌ FAILURE: 502 Bad Gateway error persists")
            return False
            
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
        server_process.terminate()
        return False

if __name__ == "__main__":
    # Note: Update the Django project path in start_django_server() function
    print("📝 NOTE: Update the project path in this script before running")
    print("   Change: cwd='/path/to/your/django-project'")
    print("   To: cwd='/your/actual/project/path'")
    print("\nOr run this manual test instead:")
    print("1. cd /path/to/your/django-project")
    print("2. python manage.py runserver 8000")
    print("3. In another terminal: curl -I http://localhost:8000/dashboard/register/")
    
    # Uncomment the line below to run the automated test
    # main()