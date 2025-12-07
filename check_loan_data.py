#!/usr/bin/env python3
"""
Check loan data in the FlexiFinance database
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(project_dir))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flexifinance.settings')
django.setup()

# Import our models
from apps.loans.models import Loan, LoanProduct, RepaymentSchedule
from apps.users.models import User

def check_loan_data():
    """Check loan data in database"""
    print("📊 FlexiFinance Loan Data Overview")
    print("=" * 50)
    
    # Check total counts
    total_loans = Loan.objects.count()
    total_products = LoanProduct.objects.count()
    total_schedules = RepaymentSchedule.objects.count()
    total_users = User.objects.count()
    
    print(f"👥 Total Users: {total_users}")
    print(f"🏦 Total Loan Products: {total_products}")
    print(f"📋 Total Loans: {total_loans}")
    print(f"📅 Total Repayment Schedules: {total_schedules}")
    
    # Check loan status distribution
    if total_loans > 0:
        print("\n📈 Loan Status Distribution:")
        status_counts = Loan.objects.values('status').annotate(count=models.Count('status'))
        for status in status_counts:
            print(f"   • {status['status']}: {status['count']} loans")
    
    # Check loan type distribution
    if total_loans > 0:
        print("\n💰 Loan Type Distribution:")
        type_counts = Loan.objects.values('loan_type').annotate(count=models.Count('loan_type'))
        for loan_type in type_counts:
            print(f"   • {loan_type['loan_type']}: {loan_type['count']} loans")
    
    # Check loan products
    if total_products > 0:
        print("\n🏦 Available Loan Products:")
        for product in LoanProduct.objects.all():
            print(f"   • {product.name} (Code: {product.product_code})")
            print(f"     - Amount Range: KES {product.min_amount} - KES {product.max_amount}")
            print(f"     - Tenure: {product.min_tenure}-{product.max_tenure} months")
            print(f"     - Interest Rate: {product.interest_rate}%")
    
    # Check recent loans
    if total_loans > 0:
        print("\n📝 Recent Loans:")
        recent_loans = Loan.objects.order_by('-application_date')[:5]
        for loan in recent_loans:
            print(f"   • {loan.loan_reference} - KES {loan.principal_amount} - {loan.status}")
            print(f"     User: {loan.user.get_full_name()} | Applied: {loan.application_date.strftime('%Y-%m-%d')}")

if __name__ == "__main__":
    from django.db import models
    check_loan_data()