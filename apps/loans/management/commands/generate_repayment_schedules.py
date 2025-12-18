from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
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
            monthly_payment = Decimal(str(loan.monthly_payment))
            previous_due_date = None
            
            for installment in range(1, loan.loan_tenure + 1):
                # Calculate due date (30 days from previous)
                if installment == 1:
                    due_date = loan.disbursement_date or loan.approval_date or timezone.now()
                else:
                    due_date = previous_due_date + timedelta(days=30)
                
                # Calculate principal and interest amounts using Decimal for consistency
                total_amount = monthly_payment
                
                # Create repayment schedule entry with proper Decimal types
                schedule, created = RepaymentSchedule.objects.get_or_create(
                    loan=loan,
                    installment_number=installment,
                    defaults={
                        'due_date': due_date.date(),
                        'principal_amount': Decimal('0.00'),  # Will be calculated properly
                        'interest_amount': Decimal('0.00'),   # Will be calculated properly
                        'total_amount': total_amount,
                        'paid_amount': Decimal('0.00'),       # Fix: Use Decimal instead of float
                        'remaining_amount': total_amount,     # This will be set by the save() method
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
