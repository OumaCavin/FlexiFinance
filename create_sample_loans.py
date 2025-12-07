#!/usr/bin/env python3
"""
Create sample loan data for FlexiFinance
"""

import os
import sys
import django
from pathlib import Path
from decimal import Decimal
from datetime import date, timedelta

# Add the project directory to Python path
project_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(project_dir))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flexifinance.settings')
django.setup()

# Import our models
from apps.loans.models import Loan, LoanProduct, RepaymentSchedule
from apps.users.models import User

def create_sample_data():
    """Create sample loan data"""
    print("🏦 Creating Sample Loan Data for FlexiFinance")
    print("=" * 50)
    
    # Get or create admin user
    try:
        admin_user = User.objects.get(username='admin')
        print(f"✅ Using existing admin user: {admin_user.get_full_name()}")
    except User.DoesNotExist:
        print("❌ Admin user not found")
        return
    
    # Create loan products
    products_data = [
        {
            'product_code': 'QC001',
            'name': 'Quick Cash Loan',
            'description': 'Fast approval loans for immediate needs',
            'min_amount': Decimal('1000'),
            'max_amount': Decimal('50000'),
            'min_tenure': 1,
            'max_tenure': 12,
            'interest_rate': Decimal('12.5'),
            'processing_fee': Decimal('500'),
            'late_fee_rate': Decimal('2.0'),
            'min_income': Decimal('15000'),
            'min_employment_duration': 3,
            'min_credit_score': 600
        },
        {
            'product_code': 'BL001',
            'name': 'Business Loan',
            'description': 'Loans for business expansion and working capital',
            'min_amount': Decimal('50000'),
            'max_amount': Decimal('500000'),
            'min_tenure': 6,
            'max_tenure': 60,
            'interest_rate': Decimal('15.0'),
            'processing_fee': Decimal('2000'),
            'late_fee_rate': Decimal('1.5'),
            'min_income': Decimal('50000'),
            'min_employment_duration': 12,
            'min_credit_score': 650
        },
        {
            'product_code': 'EL001',
            'name': 'Emergency Loan',
            'description': 'Quick emergency funds for urgent situations',
            'min_amount': Decimal('500'),
            'max_amount': Decimal('25000'),
            'min_tenure': 1,
            'max_tenure': 6,
            'interest_rate': Decimal('10.0'),
            'processing_fee': Decimal('300'),
            'late_fee_rate': Decimal('2.5'),
            'min_income': Decimal('10000'),
            'min_employment_duration': 1,
            'min_credit_score': 550
        }
    ]
    
    products_created = 0
    for product_data in products_data:
        product, created = LoanProduct.objects.get_or_create(
            product_code=product_data['product_code'],
            defaults=product_data
        )
        if created:
            products_created += 1
            print(f"✅ Created loan product: {product.name}")
        else:
            print(f"ℹ️  Loan product already exists: {product.name}")
    
    print(f"📊 Total loan products: {LoanProduct.objects.count()}")
    
    # Create sample loans
    loans_data = [
        {
            'user': admin_user,
            'loan_type': 'QUICK_CASH',
            'principal_amount': Decimal('25000'),
            'interest_rate': Decimal('12.5'),
            'loan_tenure': 6,
            'purpose': 'Emergency home repairs',
            'description': 'Need to fix roof and plumbing issues',
            'status': 'ACTIVE'
        },
        {
            'user': admin_user,
            'loan_type': 'BUSINESS',
            'principal_amount': Decimal('150000'),
            'interest_rate': Decimal('15.0'),
            'loan_tenure': 24,
            'purpose': 'Business expansion',
            'description': 'Expand retail store inventory',
            'status': 'UNDER_REVIEW'
        },
        {
            'user': admin_user,
            'loan_type': 'EMERGENCY',
            'principal_amount': Decimal('8000'),
            'interest_rate': Decimal('10.0'),
            'loan_tenure': 3,
            'purpose': 'Medical emergency',
            'description': 'Unexpected medical expenses',
            'status': 'APPROVED'
        }
    ]
    
    loans_created = 0
    for loan_data in loans_data:
        # Check if loan already exists
        existing_loan = Loan.objects.filter(
            user=loan_data['user'],
            principal_amount=loan_data['principal_amount'],
            loan_type=loan_data['loan_type']
        ).first()
        
        if not existing_loan:
            loan = Loan.objects.create(**loan_data)
            loans_created += 1
            print(f"✅ Created loan: {loan.loan_reference} - KES {loan.principal_amount}")
            
            # Create repayment schedule for active loans
            if loan.status in ['ACTIVE', 'APPROVED']:
                create_repayment_schedule(loan)
        else:
            print(f"ℹ️  Loan already exists: {existing_loan.loan_reference}")
    
    print(f"📊 Total loans: {Loan.objects.count()}")
    print(f"📊 Total repayment schedules: {RepaymentSchedule.objects.count()}")
    
    print("\n🎉 Sample data creation completed!")

def create_repayment_schedule(loan):
    """Create repayment schedule for a loan"""
    monthly_payment = loan.monthly_payment
    remaining_principal = loan.principal_amount
    
    for installment in range(1, loan.loan_tenure + 1):
        # Calculate interest for this installment
        monthly_interest_rate = loan.interest_rate / (100 * 12)
        interest_amount = remaining_principal * monthly_interest_rate
        principal_amount = monthly_payment - interest_amount
        
        # Due date calculation
        due_date = date.today() + timedelta(days=30 * installment)
        
        # Create repayment schedule entry
        RepaymentSchedule.objects.get_or_create(
            loan=loan,
            installment_number=installment,
            defaults={
                'due_date': due_date,
                'principal_amount': principal_amount,
                'interest_amount': interest_amount,
                'total_amount': monthly_payment,
                'remaining_amount': monthly_payment
            }
        )
        
        # Update remaining principal
        remaining_principal -= principal_amount

if __name__ == "__main__":
    create_sample_data()