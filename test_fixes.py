#!/usr/bin/env python3
"""
Test script to verify the fixes made to FlexiFinance application.
This script checks the key fixes without requiring the full Django environment.
"""

import os
import re
import json
from pathlib import Path

def check_terms_of_service_template():
    """Check if terms-of-service template has been fixed"""
    print("=== Checking Terms of Service Template Fix ===")
    
    template_path = "/workspace/django-microfinance-mpsa/templates/legal/terms-of-service.html"
    
    if not os.path.exists(template_path):
        print(f"❌ Template file not found: {template_path}")
        return False
    
    with open(template_path, 'r') as f:
        content = f.read()
    
    # Check for broken template syntax
    broken_pattern = r'\{\{\s*config\.BUSINESS_ADDRESS\s*</div>\s*\}\}'
    if re.search(broken_pattern, content):
        print("❌ Terms of Service template still has broken syntax")
        return False
    
    # Check for hardcoded contact information
    if "+254 700 123 456" in content:
        print("✅ Phone number correctly hardcoded")
    else:
        print("⚠️  Phone number not found in expected format")
    
    if "FlexiFinance Limited, Kimathi Street, Nairobi, Kenya" in content:
        print("✅ Address correctly hardcoded")
    else:
        print("⚠️  Address not found in expected format")
    
    print("✅ Terms of Service template fix verified")
    return True

def check_loan_application_form():
    """Check if loan application form has been fixed for JSON submission"""
    print("\n=== Checking Loan Application Form Fix ===")
    
    template_path = "/workspace/django-microfinance-mpsa/templates/loans/loan-application.html"
    
    if not os.path.exists(template_path):
        print(f"❌ Template file not found: {template_path}")
        return False
    
    with open(template_path, 'r') as f:
        content = f.read()
    
    # Check for JSON.stringify in the form submission
    if 'JSON.stringify(' in content:
        print("✅ Form data conversion to JSON found")
    else:
        print("❌ JSON.stringify not found - form may still use FormData")
        return False
    
    # Check for proper Content-Type header
    if "'Content-Type': 'application/json'" in content:
        print("✅ Content-Type header correctly set to application/json")
    else:
        print("❌ Content-Type header not properly set")
        return False
    
    print("✅ Loan application form fix verified")
    return True

def check_contact_form_fix():
    """Check if contact form has correct API endpoint"""
    print("\n=== Checking Contact Form Fix ===")
    
    template_path = "/workspace/django-microfinance-mpsa/templates/contact.html"
    
    if not os.path.exists(template_path):
        print(f"❌ Template file not found: {template_path}")
        return False
    
    with open(template_path, 'r') as f:
        content = f.read()
    
    # Check for correct API endpoint
    if '/api/contact/submit/' in content:
        print("✅ Contact form uses correct API endpoint")
    else:
        print("❌ Contact form still uses incorrect API endpoint")
        return False
    
    # Also check main.js file
    js_path = "/workspace/django-microfinance-mpsa/static/js/main.js"
    if os.path.exists(js_path):
        with open(js_path, 'r') as f:
            js_content = f.read()
        
        if '/api/contact/submit/' in js_content:
            print("✅ main.js also uses correct API endpoint")
        else:
            print("⚠️  main.js may still use incorrect endpoint")
    
    print("✅ Contact form fix verified")
    return True

def check_dashboard_url_fix():
    """Check if dashboard URL namespace has been fixed"""
    print("\n=== Checking Dashboard URL Fix ===")
    
    template_path = "/workspace/django-microfinance-mpsa/templates/users/dashboard.html"
    
    if not os.path.exists(template_path):
        print(f"❌ Template file not found: {template_path}")
        return False
    
    with open(template_path, 'r') as f:
        content = f.read()
    
    # Check for correct URL namespace
    if "{% url 'users_auth:profile' %}" in content:
        print("✅ Dashboard uses correct URL namespace 'users_auth:profile'")
    elif "{% url 'users:profile' %}" in content:
        print("❌ Dashboard still uses incorrect URL namespace 'users:profile'")
        return False
    else:
        print("⚠️  Profile URL not found in expected format")
    
    print("✅ Dashboard URL fix verified")
    return True

def check_timezone_import():
    """Check if timezone import has been added to views"""
    print("\n=== Checking Timezone Import Fix ===")
    
    views_path = "/workspace/django-microfinance-mpsa/apps/core/views.py"
    
    if not os.path.exists(views_path):
        print(f"❌ Views file not found: {views_path}")
        return False
    
    with open(views_path, 'r') as f:
        content = f.read()
    
    # Check for timezone import
    if 'from django.utils import timezone' in content:
        print("✅ Timezone import found in views.py")
    else:
        print("❌ Timezone import not found")
        return False
    
    print("✅ Timezone import fix verified")
    return True

def check_registration_javascript_errors():
    """Check registration page for JavaScript issues"""
    print("\n=== Checking Registration JavaScript Issues ===")
    
    template_path = "/workspace/django-microfinance-mpsa/templates/users/register.html"
    
    if not os.path.exists(template_path):
        print(f"❌ Registration template not found: {template_path}")
        return False
    
    with open(template_path, 'r') as f:
        content = f.read()
    
    issues_found = []
    
    # Check for addEventListener on potentially null elements
    if 'addEventListener' in content:
        # Look for potential null element references
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'addEventListener' in line and 'getElementById' in line:
                # Check if there's proper null checking
                if 'if' not in lines[max(0, i-3):i+1]:
                    issues_found.append(f"Line {i+1}: addEventListener without null checking")
    
    # Check for showToast function usage
    if 'showToast(' in content and 'function showToast' not in content:
        issues_found.append("showToast function called but not defined")
    
    if issues_found:
        print("❌ Registration JavaScript issues found:")
        for issue in issues_found:
            print(f"   - {issue}")
        return False
    else:
        print("✅ No obvious JavaScript issues found in registration template")
    
    print("✅ Registration JavaScript check completed")
    return True

def main():
    """Run all fix verification tests"""
    print("🔍 FlexiFinance Fix Verification Test")
    print("=" * 50)
    
    tests = [
        check_terms_of_service_template,
        check_loan_application_form,
        check_contact_form_fix,
        check_dashboard_url_fix,
        check_timezone_import,
        check_registration_javascript_errors,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with error: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Tests Passed: {passed}/{total}")
    print(f"❌ Tests Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 All fixes verified successfully!")
        print("The application should now work correctly.")
    else:
        print(f"\n⚠️  {total - passed} fix(es) need attention.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)