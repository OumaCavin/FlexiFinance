#!/usr/bin/env python3
"""
Simple Profile Debug Script
This script analyzes the profile forms and identifies potential issues.
"""

import os
import sys

def analyze_profile_forms():
    """Analyze profile forms and identify issues"""
    
    print("🔍 PROFILE FORM ANALYSIS")
    print("=" * 60)
    
    # Read the forms file
    forms_path = '/workspace/django-microfinance-mpsa/apps/users/forms.py'
    
    try:
        with open(forms_path, 'r') as f:
            forms_content = f.read()
        
        print("✅ Successfully read forms.py")
        
        # Check for validation methods
        print("\n🔹 CHECKING VALIDATION METHODS:")
        
        if 'clean_phone_number' in forms_content:
            print("✅ clean_phone_number method found")
            
            # Extract the method
            start = forms_content.find('def clean_phone_number')
            if start != -1:
                end = forms_content.find('\n    def ', start + 1)
                if end == -1:
                    end = forms_content.find('\nclass ', start + 1)
                if end == -1:
                    end = len(forms_content)
                
                method_content = forms_content[start:end]
                print("📋 Method content:")
                print("-" * 40)
                print(method_content)
                print("-" * 40)
                
                if 'exclude(id=self.instance.id)' in method_content:
                    print("✅ Method correctly excludes current user")
                else:
                    print("❌ Method does NOT exclude current user - this could be the issue!")
        else:
            print("❌ clean_phone_number method NOT found")
        
        if 'clean_national_id' in forms_content:
            print("✅ clean_national_id method found")
            
            # Extract the method
            start = forms_content.find('def clean_national_id')
            if start != -1:
                end = forms_content.find('\n    def ', start + 1)
                if end == -1:
                    end = forms_content.find('\nclass ', start + 1)
                if end == -1:
                    end = len(forms_content)
                
                method_content = forms_content[start:end]
                print("📋 Method content:")
                print("-" * 40)
                print(method_content)
                print("-" * 40)
                
                if 'exclude(id=self.instance.id)' in method_content:
                    print("✅ Method correctly excludes current user")
                else:
                    print("❌ Method does NOT exclude current user - this could be the issue!")
        else:
            print("❌ clean_national_id method NOT found")
        
        # Check form definitions
        print("\n🔹 CHECKING FORM CLASSES:")
        
        forms_to_check = ['IdentityForm', 'ContactForm', 'EmploymentForm', 'EmergencyContactForm']
        
        for form_name in forms_to_check:
            if f'class {form_name}' in forms_content:
                print(f"✅ {form_name} found")
            else:
                print(f"❌ {form_name} NOT found")
        
        # Check for form_type field
        print("\n🔹 CHECKING FORM_TYPE FIELD:")
        
        if 'form_type' in forms_content:
            print("✅ form_type field reference found")
        else:
            print("❌ form_type field NOT found in forms")
        
    except FileNotFoundError:
        print(f"❌ Forms file not found at: {forms_path}")
    except Exception as e:
        print(f"❌ Error reading forms file: {e}")
    
    # Read the views file
    views_path = '/workspace/django-microfinance-mpsa/apps/users/views.py'
    
    try:
        with open(views_path, 'r') as f:
            views_content = f.read()
        
        print(f"\n✅ Successfully read views.py")
        
        # Check profile view
        print("\n🔹 CHECKING PROFILE VIEW:")
        
        if 'def profile' in views_content:
            print("✅ profile view found")
            
            # Extract the view
            start = views_content.find('def profile')
            end = views_content.find('\ndef ', start + 1)
            if end == -1:
                end = len(views_content)
            
            view_content = views_content[start:end]
            
            # Check for form_type handling
            if 'form_type' in view_content:
                print("✅ form_type handling found in profile view")
            else:
                print("❌ form_type handling NOT found in profile view")
            
            # Check for form instantiation
            if 'IdentityForm' in view_content:
                print("✅ IdentityForm instantiation found")
            else:
                print("❌ IdentityForm instantiation NOT found")
            
            if 'ContactForm' in view_content:
                print("✅ ContactForm instantiation found")
            else:
                print("❌ ContactForm instantiation NOT found")
            
            if 'EmploymentForm' in view_content:
                print("✅ EmploymentForm instantiation found")
            else:
                print("❌ EmploymentForm instantiation NOT found")
            
            if 'EmergencyContactForm' in view_content:
                print("✅ EmergencyContactForm instantiation found")
            else:
                print("❌ EmergencyContactForm instantiation NOT found")
            
        else:
            print("❌ profile view NOT found")
    
    except FileNotFoundError:
        print(f"❌ Views file not found at: {views_path}")
    except Exception as e:
        print(f"❌ Error reading views file: {e}")
    
    # Check template
    template_path = '/workspace/django-microfinance-mpsa/templates/users/profile.html'
    
    try:
        with open(template_path, 'r') as f:
            template_content = f.read()
        
        print(f"\n✅ Successfully read profile.html")
        
        print("\n🔹 CHECKING TEMPLATE STRUCTURE:")
        
        # Check for form tags
        form_count = template_content.count('<form')
        print(f"📋 Found {form_count} <form> tags")
        
        # Check for form_type hidden inputs
        form_type_count = template_content.count('form_type')
        print(f"📋 Found {form_type_count} form_type references")
        
        # Check for specific form names
        if 'IdentityForm' in template_content:
            print("✅ IdentityForm found in template")
        else:
            print("❌ IdentityForm NOT found in template")
        
        if 'ContactForm' in template_content:
            print("✅ ContactForm found in template")
        else:
            print("❌ ContactForm NOT found in template")
        
        if 'EmploymentForm' in template_content:
            print("✅ EmploymentForm found in template")
        else:
            print("❌ EmploymentForm NOT found in template")
        
        if 'EmergencyContactForm' in template_content:
            print("✅ EmergencyContactForm found in template")
        else:
            print("❌ EmergencyContactForm NOT found in template")
        
        # Check for Save buttons
        save_button_count = template_content.lower().count('save')
        print(f"📋 Found {save_button_count} 'save' references (buttons/links)")
    
    except FileNotFoundError:
        print(f"❌ Template file not found at: {template_path}")
    except Exception as e:
        print(f"❌ Error reading template file: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 ANALYSIS COMPLETE")
    print("=" * 60)
    
    # Provide diagnostic summary
    print("\n🔍 LIKELY ISSUES TO CHECK:")
    print("1. Validation methods missing .exclude(id=self.instance.id)")
    print("2. View not properly routing form_type parameter")
    print("3. Template not sending correct form_type with each form")
    print("4. Database connection or transaction issues")
    print("5. CSRF token issues")

if __name__ == "__main__":
    analyze_profile_forms()