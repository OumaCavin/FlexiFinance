#!/usr/bin/env python
"""
Fix user verification status for users who have confirmed their email
but haven't had their is_verified and kyc_status updated
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flexifinance.settings')
django.setup()

from django.contrib.auth import get_user_model
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

User = get_user_model()

def fix_user_verification():
    """
    Fix verification status for users who have confirmed email but aren't marked as verified
    """
    # Find users who are active (means they can log in) but not verified
    users_to_fix = User.objects.filter(is_active=True, is_verified=False)
    
    if users_to_fix.exists():
        print(f"Found {users_to_fix.count()} users who need verification status update:")
        
        for user in users_to_fix:
            print(f"\nUpdating user: {user.username} ({user.email})")
            print(f"  Current KYC status: {user.kyc_status}")
            print(f"  Current is_verified: {user.is_verified}")
            
            # Mark as verified
            user.mark_verified()
            
            # Set KYC status to approved
            if user.kyc_status == 'PENDING':
                user.set_kyc_status('APPROVED')
            
            print(f"  Updated KYC status: {user.kyc_status}")
            print(f"  Updated is_verified: {user.is_verified}")
            print(f"  Verification date: {user.verification_date}")
            
            logger.info(f"Updated user {user.username} verification status")
    else:
        print("No users found that need verification status update.")

if __name__ == "__main__":
    fix_user_verification()