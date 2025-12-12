#!/bin/bash

# Populate LoanProduct and RepaymentSchedule Admin Interfaces
echo "📋 Populating FlexiFinance Admin Interfaces"
echo "=========================================="
echo

# Create directories if they don't exist
mkdir -p /home/cavin/projects/Django_Projects/FlexiFinance/apps/loans/management/commands

echo "🔧 Step 1: Creating Loan Products Management Command..."

# Create the loan products command
cat > /home/cavin/projects/Django_Projects/FlexiFinance/apps/loans/management/commands/create_loan_products.py << 'EOF'
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
EOF

echo "✅ Loan products command created"

echo
echo "🔧 Step 2: Creating Repayment Schedules Management Command..."

# Create the repayment schedules command
cat > /home/cavin/projects/Django_Projects/FlexiFinance/apps/loans/management/commands/generate_repayment_schedules.py << 'EOF'
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.loans.models import Loan, RepaymentSchedule

class Command(BaseCommand):
    help = 'Generate repayment schedules for approved loans'

    def handle(self, *args, **options):
        # Get all approved loans without repayment schedules
        loans = Loan.objects.filter(
            status__in=['APPROVED', 'DISBURSED', 'ACTIVE']
        ).exclude(
            id__in=RepaymentSchedule.objects.values_list('loan_id', flat=True)
        )
        
        created_count = 0
        
        for loan in loans:
            monthly_payment = loan.monthly_payment
            
            for installment in range(1, loan.loan_tenure + 1):
                # Calculate due date (30 days from previous)
                if installment == 1:
                    due_date = loan.disbursement_date or loan.approval_date or timezone.now()
                else:
                    due_date = previous_due_date + timedelta(days=30)
                
                # Create repayment schedule entry
                schedule, created = RepaymentSchedule.objects.get_or_create(
                    loan=loan,
                    installment_number=installment,
                    defaults={
                        'due_date': due_date,
                        'total_amount': monthly_payment,
                        'paid_amount': 0.0,
                        'remaining_amount': monthly_payment,
                        'status': 'PENDING'
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Created schedule: {loan.loan_reference} - Installment {installment}')
                    )
                
                previous_due_date = due_date
        
        self.stdout.write(
            self.style.SUCCESS(f'🎉 Generated {created_count} repayment schedules!')
        )
EOF

echo "✅ Repayment schedules command created"

echo
echo "🔧 Step 3: Creating __init__.py files..."
touch /home/cavin/projects/Django_Projects/FlexiFinance/apps/loans/management/__init__.py
touch /home/cavin/projects/Django_Projects/FlexiFinance/apps/loans/management/commands/__init__.py

echo "✅ Management command structure created"

echo
echo "🔧 Step 4: Running commands to populate admin interfaces..."
cd /home/cavin/projects/Django_Projects/FlexiFinance

echo "📊 Creating Loan Products..."
python manage.py create_loan_products

echo
echo "📅 Generating Repayment Schedules..."
python manage.py generate_repayment_schedules

echo
echo "=========================================="
echo "✅ Admin Interface Population Complete!"
echo "=========================================="
echo
echo "🔍 Now you can view:"
echo "1. Loan Products: http://127.0.0.1:8000/admin/loans/loanproduct/"
echo "2. Repayment Schedules: http://127.0.0.1:8000/admin/loans/repaymentschedule/"
echo
echo "📋 Expected Results:"
echo "- 4 Loan Products created:"
echo "  • Quick Cash: KSh 5,000 - KSh 25,000"
echo "  • Personal Loan: KSh 5,000 - KSh 100,000"
echo "  • Business Loan: KSh 50,000 - KSh 500,000"
echo "  • Emergency Loan: KSh 5,000 - KSh 50,000"
echo "- Repayment schedules generated for approved loans"
echo ""
echo "✅ Updated loan amounts: KSh 5,000 - KSh 500,000 (matching homepage requirements)"