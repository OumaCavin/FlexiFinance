"""
Management command to create default notification templates
"""
from django.core.management.base import BaseCommand
from apps.notifications.services.notification_service import notification_service


class Command(BaseCommand):
    help = 'Create default notification templates for FlexiFinance'

    def handle(self, *args, **options):
        """Create default templates"""
        try:
            created = notification_service.create_default_templates()
            if created > 0:
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created {created} default notification templates')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('All default notification templates already exist')
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating templates: {str(e)}')
            )