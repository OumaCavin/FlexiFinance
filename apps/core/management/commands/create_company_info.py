from django.core.management.base import BaseCommand
from apps.core.models import Company

class Command(BaseCommand):
    help = 'Create default company information for FlexiFinance'

    def handle(self, *args, **options):
        # Check if company already exists
        existing_company = Company.objects.filter(is_active=True).first()
        if existing_company:
            self.stdout.write(
                self.style.WARNING(f'⚠️  Company already exists: {existing_company.company_name}')
            )
            return

        # Create default company
        company_data = {
            'registration_number': 'CPR/2018/234567',
            'license_number': 'P05123456789',
            'cbk_registration': 'CBK/RG/234567',
            'bank_account_number': '1234567890',
            'physical_address': 'Westlands Business Park, House No. 24, Ring Road',
            'postal_address': 'P.O. Box 12345-00100, Nairobi',
            'phone': '+254 700 123 456',
            'email': 'info@flexifinance.co.ke',
            'website': 'https://www.flexifinance.co.ke'
        }
        
        company = Company.objects.create(**company_data)
        self.stdout.write(
            self.style.SUCCESS(f'✅ Created company: {company.company_name}')
        )
        self.stdout.write(
            self.style.SUCCESS(f'📋 Registration: {company.registration_number}')
        )
        self.stdout.write(
            self.style.SUCCESS(f'🏦 Bank Account: {company.bank_account_number}')
        )
