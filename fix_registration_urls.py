#!/usr/bin/env python3
"""
FlexiFinance Registration URL Fixer
This script checks and fixes the registration URL configuration
"""
import os
import sys
from pathlib import Path

# Add the project to Python path
project_path = Path(__file__).parent
sys.path.insert(0, str(project_path))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flexifinance.settings')
import django
django.setup()

def check_registration_url_config():
    """Check and fix registration URL configuration"""
    print("🔍 Checking registration URL configuration...")
    
    web_urls_path = project_path / 'apps' / 'users' / 'web_urls.py'
    
    if not web_urls_path.exists():
        print("❌ web_urls.py not found!")
        return False
    
    with open(web_urls_path, 'r') as f:
        content = f.read()
    
    # Check if it's importing from the correct view file
    if 'from . import views' in content:
        print("✅ Correct import found: from . import views")
        print("   This uses the view with actual registration logic")
        return True
    elif 'from .web import views' in content:
        print("❌ Wrong import found: from .web import views")
        print("   This uses the placeholder view without registration logic")
        print("\n🔧 Fixing the import...")
        
        # Fix the import
        content = content.replace('from .web import views', 'from . import views')
        
        with open(web_urls_path, 'w') as f:
            f.write(content)
        
        print("✅ Fixed! Now importing from the correct view file")
        return True
    else:
        print("⚠️  Could not determine import structure")
        print("   Please check web_urls.py manually")
        return False

def verify_user_registration_logic():
    """Verify the user registration view has proper logic"""
    print("\n🔍 Checking user registration logic...")
    
    views_path = project_path / 'apps' / 'users' / 'views.py'
    
    if not views_path.exists():
        print("❌ views.py not found!")
        return False
    
    with open(views_path, 'r') as f:
        content = f.read()
    
    # Check for key registration logic
    checks = [
        ('POST method handling', 'if request.method == \'POST\''),
        ('User creation', 'User.objects.create_user'),
        ('Password validation', 'password1'),
        ('Field validation', 'messages.error'),
    ]
    
    all_good = True
    for check_name, check_string in checks:
        if check_string in content:
            print(f"✅ {check_name}: Found")
        else:
            print(f"❌ {check_name}: Missing")
            all_good = False
    
    return all_good

def main():
    """Main function"""
    print("🔧 FlexiFinance Registration URL Fixer")
    print("=" * 50)
    
    # Check URL configuration
    url_ok = check_registration_url_config()
    
    # Check registration logic
    logic_ok = verify_user_registration_logic()
    
    print("\n" + "=" * 50)
    print("SUMMARY:")
    print(f"URL Configuration: {'✅ OK' if url_ok else '❌ Needs Fix'}")
    print(f"Registration Logic: {'✅ OK' if logic_ok else '❌ Needs Fix'}")
    
    if url_ok and logic_ok:
        print("\n✅ Registration system looks good!")
        print("   You can now test user registration at:")
        print("   http://localhost:8000/dashboard/register/")
    else:
        print("\n❌ Issues found. Please review the output above.")
        print("\nNext steps:")
        print("1. Review the web_urls.py file")
        print("2. Ensure the correct view is imported")
        print("3. Test registration after fixes")

if __name__ == "__main__":
    main()