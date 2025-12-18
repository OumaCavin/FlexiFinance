"""
Django management command to immediately verify existing unverified users
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Command(BaseCommand):
    help = 'Immediately verify existing unverified users (emergency fix)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes',
        )
        parser.add_argument(
            '--limit',
            type=int,
            help='Limit number of users to verify',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        limit = options['limit']
        
        # Find unverified users
        unverified_users = User.objects.filter(is_verified=False)
        
        if limit:
            unverified_users = unverified_users[:limit]
        
        count = unverified_users.count()
        
        if dry_run:
            self.stdout.write(self.style.WARNING(f'DRY RUN: Found {count} unverified users'))
            for user in unverified_users:
                self.stdout.write(f'  - {user.username} ({user.email}) - KYC: {user.kyc_status}')
            return
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('No unverified users found'))
            return
        
        self.stdout.write(f'Verifing {count} existing users...')
        
        verified_count = 0
        
        for user in unverified_users:
            try:
                # Mark user as verified
                user.is_verified = True
                user.verification_date = timezone.now()
                
                # If KYC is still pending, approve it
                if user.kyc_status == 'PENDING':
                    user.kyc_status = 'APPROVED'
                
                user.save(update_fields=['is_verified', 'verification_date', 'kyc_status'])
                
                verified_count += 1
                self.stdout.write(self.style.SUCCESS(f'Verified {user.username} ({user.email})'))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Failed to verify {user.username}: {str(e)}'))
        
        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(f'Summary:')
        self.stdout.write(f'  Users verified: {verified_count}')
        self.stdout.write(f'  Total processed: {count}')
        
        if verified_count > 0:
            self.stdout.write(f'\nAll verified users now have:')
            self.stdout.write(f'  - is_verified = True')
            self.stdout.write(f'  - kyc_status = APPROVED')
            self.stdout.write(f'  - verification_date set')
            self.stdout.write(f'\nThey can now access all features without email verification!')