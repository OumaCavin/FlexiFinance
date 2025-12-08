#!/usr/bin/env python3
"""
Check database users and phone numbers
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flexifinance.settings')
django.setup()

from apps.users.models import User

def check_users():
    """Check existing users"""
    users = User.objects.all()
    print(f"Total users: {users.count()}")
    print("\nUsers with phone numbers:")
    for user in users[:10]:
        print(f"  {user.username}: phone='{user.phone_number}', email='{user.email}'")
    
    # Check for empty phone numbers
    empty_phones = User.objects.filter(phone_number='').count()
    print(f"\nUsers with empty phone numbers: {empty_phones}")

if __name__ == "__main__":
    check_users()