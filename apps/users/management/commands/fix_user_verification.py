"""
Django management command to fix user verification status
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Fix user verification status for users who have confirmed email'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        # Find users who are active (means they can log in) but not verified
        users_to_fix = User.objects.filter(is_active=True, is_verified=False)
        
        if users_to_fix.exists():
            self.stdout.write(f'Found {users_to_fix.count()} users who need verification status update:')
            
            for user in users_to_fix:
                self.stdout.write(f'\nUser: {user.username} ({user.email})')
                self.stdout.write(f'  Current KYC status: {user.kyc_status}')
                self.stdout.write(f'  Current is_verified: {user.is_verified}')
                
                if not dry_run:
                    # Mark as verified
                    user.mark_verified()
                    
                    # Set KYC status to approved
                    if user.kyc_status == 'PENDING':
                        user.set_kyc_status('APPROVED')
                        self.stdout.write(f'  Updated KYC status: {user.kyc_status}')
                    
                    self.stdout.write(f'  Updated is_verified: {user.is_verified}')
                    self.stdout.write(f'  Verification date: {user.verification_date}')
                    logger.info(f'Updated user {user.username} verification status')
                else:
                    self.stdout.write(f'  Would update KYC status to: APPROVED')
                    self.stdout.write(f'  Would update is_verified to: True')
        else:
            self.stdout.write(self.style.SUCCESS('No users found that need verification status update.'))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\nRun without --dry-run to apply these changes.'))
        else:
            self.stdout.write(self.style.SUCCESS('\nUser verification status update completed.'))