#!/usr/bin/env python3
"""
Fix the admin user phone number to resolve UNIQUE constraint issue
"""
import os
import sys
import django

# Setup Django
sys.path.append('/workspace/django-microfinance-mpsa')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flexifinance.settings')
django.setup()

from apps.users.models import User

def fix_admin_phone():
    """Update admin user phone number"""
    try:
        # Get the admin user
        admin_user = User.objects.get(username='admin')
        print(f"Current admin user phone_number: '{admin_user.phone_number}'")
        
        # Update with the provided phone number
        new_phone = "+254715169531"
        admin_user.phone_number = new_phone
        admin_user.save()
        
        print(f"✅ Successfully updated admin user phone number to: {new_phone}")
        
        # Verify the update
        updated_user = User.objects.get(username='admin')
        print(f"Verification - Admin user phone_number: '{updated_user.phone_number}'")
        
        return True
        
    except User.DoesNotExist:
        print("❌ Admin user not found")
        return False
    except Exception as e:
        print(f"❌ Error updating admin user: {e}")
        return False

if __name__ == "__main__":
    print("Fixing admin user phone number...")
    success = fix_admin_phone()
    if success:
        print("\n✅ Admin phone number updated successfully!")
        print("Ready to test user registration with phone number +254715169531")
    else:
        print("\n❌ Failed to update admin phone number")