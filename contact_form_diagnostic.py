#!/usr/bin/env python3
"""
Contact Form Backend Diagnostic Script
=====================================
Comprehensive testing script for the FlexiFinance contact form backend implementation.

This script verifies:
1. Database connectivity and Contact model
2. API endpoint functionality
3. Admin interface registration
4. Email service integration
5. Form submission workflow

Author: OumaCavin
Date: 2025-12-12
"""

import os
import sys
import json
import django
from datetime import datetime
import requests
from urllib.parse import urljoin

# Add the Django project to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flexifinance.settings')
django.setup()

from django.core.management import execute_from_command_line
from django.db import connection
from django.contrib.auth import get_user_model
from django.test.utils import override_settings
from django.core import mail
from apps.core.models import Contact, Company
from apps.payments.services.resend_email_service import ResendEmailService
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContactFormDiagnostic:
    """Comprehensive diagnostic class for contact form backend"""
    
    def __init__(self, base_url='http://127.0.0.1:8000'):
        self.base_url = base_url
        self.results = {
            'database': {},
            'models': {},
            'api': {},
            'admin': {},
            'email': {},
            'frontend': {}
        }
        self.test_contact_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'phone': '+254700000000',
            'subject': 'Test Message',
            'message': 'This is a test message from the diagnostic script.'
        }

    def print_header(self, title):
        """Print formatted section header"""
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}")

    def print_result(self, test_name, status, details=""):
        """Print formatted test result"""
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {test_name}")
        if details:
            print(f"   {details}")

    def test_database_connection(self):
        """Test database connectivity"""
        self.print_header("DATABASE CONNECTIVITY")
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                self.results['database']['connection'] = True
                self.print_result("Database Connection", True, "Successfully connected to database")
        except Exception as e:
            self.results['database']['connection'] = False
            self.print_result("Database Connection", False, f"Error: {str(e)}")
            return False

        # Test Contact table
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) FROM information_schema.tables 
                    WHERE table_name = 'contact'
                """)
                table_exists = cursor.fetchone()[0] > 0
                
                if table_exists:
                    self.results['database']['contact_table'] = True
                    self.print_result("Contact Table", True, "Contact table exists in database")
                else:
                    self.results['database']['contact_table'] = False
                    self.print_result("Contact Table", False, "Contact table not found")
                    
        except Exception as e:
            self.results['database']['contact_table'] = False
            self.print_result("Contact Table", False, f"Error: {str(e)}")

        return True

    def test_contact_model(self):
        """Test Contact model functionality"""
        self.print_header("CONTACT MODEL")
        
        try:
            # Test model import
            contact = Contact()
            self.results['models']['import'] = True
            self.print_result("Model Import", True, "Contact model imported successfully")
        except Exception as e:
            self.results['models']['import'] = False
            self.print_result("Model Import", False, f"Error: {str(e)}")
            return False

        try:
            # Test model creation
            test_contact = Contact.objects.create(
                name=self.test_contact_data['name'],
                email=self.test_contact_data['email'],
                phone=self.test_contact_data['phone'],
                subject=self.test_contact_data['subject'],
                message=self.test_contact_data['message'],
                source='diagnostic_test',
                ip_address='127.0.0.1',
                user_agent='Diagnostic Script'
            )
            
            self.results['models']['create'] = True
            self.results['models']['test_contact_id'] = test_contact.id
            self.print_result("Model Creation", True, f"Test contact created with ID: {test_contact.id}")
            
            # Test retrieval
            retrieved = Contact.objects.get(id=test_contact.id)
            if retrieved.name == test_contact.name:
                self.results['models']['retrieve'] = True
                self.print_result("Model Retrieval", True, "Contact record retrieved successfully")
            else:
                self.results['models']['retrieve'] = False
                self.print_result("Model Retrieval", False, "Retrieved data doesn't match")
                
        except Exception as e:
            self.results['models']['create'] = False
            self.print_result("Model Creation", False, f"Error: {str(e)}")

        try:
            # Test model fields
            fields = [field.name for field in Contact._meta.fields]
            expected_fields = ['name', 'email', 'phone', 'subject', 'message', 'is_processed', 'created_at']
            missing_fields = [field for field in expected_fields if field not in fields]
            
            if not missing_fields:
                self.results['models']['fields'] = True
                self.print_result("Model Fields", True, "All expected fields present")
            else:
                self.results['models']['fields'] = False
                self.print_result("Model Fields", False, f"Missing fields: {missing_fields}")
                
        except Exception as e:
            self.results['models']['fields'] = False
            self.print_result("Model Fields", False, f"Error: {str(e)}")

        return True

    def test_api_endpoint(self):
        """Test contact form API endpoint"""
        self.print_header("API ENDPOINT")
        
        api_url = urljoin(self.base_url, '/api/contact/submit/')
        
        try:
            # Test GET request (should return 405 Method Not Allowed)
            response = requests.get(api_url, timeout=10)
            if response.status_code == 405:
                self.results['api']['method_check'] = True
                self.print_result("API Method Check", True, "GET correctly returns 405 Method Not Allowed")
            else:
                self.results['api']['method_check'] = False
                self.print_result("API Method Check", False, f"Expected 405, got {response.status_code}")
        except Exception as e:
            self.results['api']['method_check'] = False
            self.print_result("API Method Check", False, f"Error: {str(e)}")

        try:
            # Test POST with valid data
            headers = {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
            
            response = requests.post(api_url, json=self.test_contact_data, headers=headers, timeout=10)
            
            if response.status_code == 200:
                self.results['api']['post_success'] = True
                self.print_result("API POST Request", True, f"Status: {response.status_code}")
                
                try:
                    result = response.json()
                    if result.get('success'):
                        self.results['api']['response_format'] = True
                        self.print_result("API Response Format", True, "Valid JSON response with success field")
                        if 'reference_id' in result:
                            self.results['api']['reference_id'] = True
                            self.print_result("Reference ID", True, f"Reference ID: {result['reference_id']}")
                        else:
                            self.results['api']['reference_id'] = False
                            self.print_result("Reference ID", False, "No reference_id in response")
                    else:
                        self.results['api']['response_format'] = False
                        self.print_result("API Response Format", False, "Success field is False")
                except json.JSONDecodeError:
                    self.results['api']['response_format'] = False
                    self.print_result("API Response Format", False, "Invalid JSON response")
            else:
                self.results['api']['post_success'] = False
                self.print_result("API POST Request", False, f"Status: {response.status_code}")
                if response.text:
                    print(f"   Response: {response.text[:200]}...")
                    
        except requests.exceptions.ConnectionError:
            self.results['api']['post_success'] = False
            self.print_result("API POST Request", False, "Cannot connect to server. Is Django running?")
        except Exception as e:
            self.results['api']['post_success'] = False
            self.print_result("API POST Request", False, f"Error: {str(e)}")

        try:
            # Test POST with invalid data
            invalid_data = {'name': '', 'email': 'invalid', 'message': ''}
            response = requests.post(api_url, json=invalid_data, headers=headers, timeout=10)
            
            if response.status_code == 400:
                self.results['api']['validation'] = True
                self.print_result("API Validation", True, "Invalid data correctly rejected")
            else:
                self.results['api']['validation'] = False
                self.print_result("API Validation", False, f"Expected 400, got {response.status_code}")
                
        except Exception as e:
            self.results['api']['validation'] = False
            self.print_result("API Validation", False, f"Error: {str(e)}")

        return True

    def test_admin_interface(self):
        """Test Django admin interface"""
        self.print_header("ADMIN INTERFACE")
        
        try:
            from django.contrib.admin import site
            from apps.core.admin import ContactAdmin
            
            # Test admin registration
            contact_model = site._registry.get(Contact)
            if contact_model:
                self.results['admin']['registration'] = True
                self.print_result("Admin Registration", True, "Contact model registered in admin")
            else:
                self.results['admin']['registration'] = False
                self.print_result("Admin Registration", False, "Contact model not found in admin")
                
        except Exception as e:
            self.results['admin']['registration'] = False
            self.print_result("Admin Registration", False, f"Error: {str(e)}")

        try:
            # Test admin actions
            admin_instance = ContactAdmin(Contact, site)
            if hasattr(admin_instance, 'mark_as_processed'):
                self.results['admin']['actions'] = True
                self.print_result("Admin Actions", True, "mark_as_processed action available")
            else:
                self.results['admin']['actions'] = False
                self.print_result("Admin Actions", False, "mark_as_processed action missing")
                
        except Exception as e:
            self.results['admin']['actions'] = False
            self.print_result("Admin Actions", False, f"Error: {str(e)}")

        return True

    def test_email_service(self):
        """Test email service integration"""
        self.print_header("EMAIL SERVICE")
        
        try:
            email_service = ResendEmailService()
            self.results['email']['import'] = True
            self.print_result("Email Service Import", True, "ResendEmailService imported successfully")
        except Exception as e:
            self.results['email']['import'] = False
            self.print_result("Email Service Import", False, f"Error: {str(e)}")
            return False

        try:
            # Test email configuration
            if hasattr(email_service, 'api_key') and email_service.api_key:
                self.results['email']['configuration'] = True
                self.print_result("Email Configuration", True, "Email service configured")
            else:
                self.results['email']['configuration'] = False
                self.print_result("Email Configuration", False, "Email service not configured")
                
        except Exception as e:
            self.results['email']['configuration'] = False
            self.print_result("Email Configuration", False, f"Error: {str(e)}")

        return True

    def test_frontend_integration(self):
        """Test frontend integration"""
        self.print_header("FRONTEND INTEGRATION")
        
        try:
            # Check if contact template exists
            contact_template_path = os.path.join(os.path.dirname(__file__), 'templates', 'contact.html')
            if os.path.exists(contact_template_path):
                self.results['frontend']['template'] = True
                self.print_result("Contact Template", True, "contact.html template found")
                
                # Check for JavaScript API call
                with open(contact_template_path, 'r') as f:
                    content = f.read()
                    if '/api/contact/submit/' in content:
                        self.results['frontend']['api_call'] = True
                        self.print_result("API Call in Template", True, "JavaScript makes API call to contact endpoint")
                    else:
                        self.results['frontend']['api_call'] = False
                        self.print_result("API Call in Template", False, "No API call found in template")
            else:
                self.results['frontend']['template'] = False
                self.print_result("Contact Template", False, "contact.html template not found")
                
        except Exception as e:
            self.results['frontend']['template'] = False
            self.print_result("Contact Template", False, f"Error: {str(e)}")

        return True

    def cleanup_test_data(self):
        """Clean up test data"""
        try:
            if 'test_contact_id' in self.results['models']:
                Contact.objects.filter(id=self.results['models']['test_contact_id']).delete()
                print(f"\n🧹 Test contact record {self.results['models']['test_contact_id']} cleaned up")
        except Exception as e:
            print(f"\n⚠️ Failed to cleanup test data: {str(e)}")

    def generate_summary(self):
        """Generate test summary"""
        self.print_header("DIAGNOSTIC SUMMARY")
        
        total_tests = 0
        passed_tests = 0
        
        for category, tests in self.results.items():
            category_passed = 0
            category_total = len(tests)
            
            print(f"\n📋 {category.upper()} TESTS:")
            for test_name, result in tests.items():
                if isinstance(result, bool):
                    total_tests += 1
                    if result:
                        passed_tests += 1
                        category_passed += 1
                        print(f"   ✅ {test_name}")
                    else:
                        print(f"   ❌ {test_name}")
                elif test_name == 'test_contact_id':
                    print(f"   📝 Test ID: {result}")
                elif test_name == 'reference_id':
                    print(f"   📝 Reference ID: {result}")
                else:
                    print(f"   📝 {test_name}: {result}")
            
            if category_total > 0:
                percentage = (category_passed / category_total) * 100
                print(f"   📊 Category Score: {category_passed}/{category_total} ({percentage:.1f}%)")
        
        overall_percentage = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"\n🎯 OVERALL SCORE: {passed_tests}/{total_tests} ({overall_percentage:.1f}%)")
        
        if overall_percentage >= 90:
            print("🏆 EXCELLENT: Contact form backend is fully functional!")
        elif overall_percentage >= 75:
            print("👍 GOOD: Contact form backend is mostly functional with minor issues")
        elif overall_percentage >= 50:
            print("⚠️ FAIR: Contact form backend has some issues that need attention")
        else:
            print("❌ POOR: Contact form backend has significant issues that need immediate attention")

        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'percentage': overall_percentage,
            'results': self.results
        }

    def run_all_tests(self):
        """Run all diagnostic tests"""
        print("🚀 Starting Contact Form Backend Diagnostic...")
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run all test categories
        self.test_database_connection()
        self.test_contact_model()
        self.test_api_endpoint()
        self.test_admin_interface()
        self.test_email_service()
        self.test_frontend_integration()
        
        # Cleanup
        self.cleanup_test_data()
        
        # Generate summary
        summary = self.generate_summary()
        
        print(f"\n⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return summary

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Contact Form Backend Diagnostic')
    parser.add_argument('--url', default='http://127.0.0.1:8000', 
                       help='Base URL of Django application (default: http://127.0.0.1:8000)')
    parser.add_argument('--skip-server', action='store_true', 
                       help='Skip API endpoint tests (for offline testing)')
    
    args = parser.parse_args()
    
    # Create diagnostic instance
    diagnostic = ContactFormDiagnostic(base_url=args.url)
    
    # Run tests
    summary = diagnostic.run_all_tests()
    
    # Exit with appropriate code
    if summary['percentage'] >= 75:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure

if __name__ == '__main__':
    main()