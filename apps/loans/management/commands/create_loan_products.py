from django.core.management.base import BaseCommand
from apps.loans.models import LoanProduct

class Command(BaseCommand):
    help = 'Create sample loan products for FlexiFinance'

    def handle(self, *args, **options):
        products = [
            {
                'product_code': 'QUICK_CASH_5K_25K',
                'name': 'Quick Cash - Small Amount',
                'description': 'Fast approval loans for small amounts up to KSh 25,000',
                'min_amount': 5000,
                'max_amount': 25000,
                'min_tenure': 1,
                'max_tenure': 6,
                'interest_rate': 15.0,
                'processing_fee': 500.0,
                'late_fee_rate': 2.0,
                'min_income': 30000,
                'min_employment_duration': 3,
                'min_credit_score': 600,
                'is_active': True,
                'requires_documents': False
            },
            {
                'product_code': 'PERSONAL_5K_100K',
                'name': 'Personal Loan - Medium Amount',
                'description': 'Flexible personal loans for various purposes up to KSh 100,000',
                'min_amount': 5000,
                'max_amount': 100000,
                'min_tenure': 3,
                'max_tenure': 24,
                'interest_rate': 12.5,
                'processing_fee': 1000.0,
                'late_fee_rate': 2.0,
                'min_income': 50000,
                'min_employment_duration': 6,
                'min_credit_score': 650,
                'is_active': True,
                'requires_documents': True
            },
            {
                'product_code': 'BUSINESS_50K_500K',
                'name': 'Business Loan',
                'description': 'Business expansion and equipment financing up to KSh 500,000',
                'min_amount': 50000,
                'max_amount': 500000,
                'min_tenure': 6,
                'max_tenure': 36,
                'interest_rate': 10.0,
                'processing_fee': 2500.0,
                'late_fee_rate': 2.0,
                'min_income': 100000,
                'min_employment_duration': 12,
                'min_credit_score': 700,
                'is_active': True,
                'requires_documents': True
            },
            {
                'product_code': 'EMERGENCY_5K_50K',
                'name': 'Emergency Loan',
                'description': 'Urgent loans for medical emergencies and urgent needs up to KSh 50,000',
                'min_amount': 5000,
                'max_amount': 50000,
                'min_tenure': 1,
                'max_tenure': 12,
                'interest_rate': 18.0,
                'processing_fee': 300.0,
                'late_fee_rate': 3.0,
                'min_income': 25000,
                'min_employment_duration': 1,
                'min_credit_score': 550,
                'is_active': True,
                'requires_documents': False
            }
        ]

        created_count = 0
        for product_data in products:
            product, created = LoanProduct.objects.get_or_create(
                product_code=product_data['product_code'],
                defaults=product_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Created: {product.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  Already exists: {product.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'🎉 Created {created_count} new loan products!')
        )
