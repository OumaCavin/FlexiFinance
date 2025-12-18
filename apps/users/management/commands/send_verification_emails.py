"""
Django management command to send verification emails to existing unverified users
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
import secrets

User = get_user_model()

class Command(BaseCommand):
    help = 'Send verification emails to existing unverified users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without actually sending emails',
        )
        parser.add_argument(
            '--limit',
            type=int,
            help='Limit number of emails to send',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        limit = options['limit']
        
        # Find unverified users who haven't received verification emails
        unverified_users = User.objects.filter(
            is_verified=False,
            email_verification_token=''
        )
        
        if limit:
            unverified_users = unverified_users[:limit]
        
        count = unverified_users.count()
        
        if dry_run:
            self.stdout.write(self.style.WARNING(f'DRY RUN: Found {count} unverified users'))
            for user in unverified_users:
                self.stdout.write(f'  - {user.username} ({user.email})')
            return
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('No unverified users found'))
            return
        
        self.stdout.write(f'Sending verification emails to {count} users...')
        
        sent_count = 0
        error_count = 0
        
        for user in unverified_users:
            try:
                # Generate verification token
                user.email_verification_token = secrets.token_urlsafe(32)
                user.email_verification_sent_at = timezone.now()
                user.save(update_fields=['email_verification_token', 'email_verification_sent_at'])
                
                # Import and send verification email
                from apps.users.signals import send_verification_email
                send_verification_email(user)
                
                sent_count += 1
                self.stdout.write(self.style.SUCCESS(f'Sent to {user.username} ({user.email})'))
                
            except Exception as e:
                error_count += 1
                self.stdout.write(self.style.ERROR(f'Failed to send to {user.username}: {str(e)}'))
        
        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(f'Summary:')
        self.stdout.write(f'  Emails sent: {sent_count}')
        self.stdout.write(f'  Errors: {error_count}')
        self.stdout.write(f'  Total processed: {count}')
        
        if sent_count > 0:
            self.stdout.write(f'\nCheck Mailpit at http://localhost:8025/ to view emails')