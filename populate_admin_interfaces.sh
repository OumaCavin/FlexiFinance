#!/bin/bash

# Populate Comprehensive Admin Interfaces for FlexiFinance
echo "📋 Populating FlexiFinance Admin Interfaces"
echo "=========================================="
echo

# Create directories if they don't exist
mkdir -p /home/cavin/projects/Django_Projects/FlexiFinance/apps/loans/management/commands
mkdir -p /home/cavin/projects/Django_Projects/FlexiFinance/apps/core/management/commands
mkdir -p /home/cavin/projects/Django_Projects/FlexiFinance/apps/notifications/management/commands

echo "🔧 Step 1: Creating Company Information Management Command..."

# Create the company information command
cat > /home/cavin/projects/Django_Projects/FlexiFinance/apps/core/management/commands/create_company_info.py << 'EOF'
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
EOF

echo "✅ Company information command created"

echo
echo "🔧 Step 2: Creating Notification Templates Management Command..."

# Create the notification templates command
cat > /home/cavin/projects/Django_Projects/FlexiFinance/apps/notifications/management/commands/create_notification_templates.py << 'EOF'
from django.core.management.base import BaseCommand
from apps.notifications.models import NotificationTemplate

class Command(BaseCommand):
    help = 'Create default notification templates for FlexiFinance'

    def handle(self, *args, **options):
        templates = [
            {
                'name': 'loan_approval_email',
                'notification_type': 'LOAN_APPROVAL',
                'channels': ['EMAIL'],
                'subject_template': 'Congratulations! Your FlexiFinance Loan is Approved',
                'message_template': 'Dear {{ user.first_name }}, your loan application for KSh {{ loan.principal_amount }} has been approved. Your loan reference is {{ loan.loan_reference }}. We will disburse the funds within {{ company.disbursement_timeframe_days }} business days.',
                'html_template': '<h2>Congratulations!</h2><p>Your FlexiFinance loan has been approved.</p><p><strong>Loan Amount:</strong> KSh {{ loan.principal_amount }}</p><p><strong>Reference:</strong> {{ loan.loan_reference }}</p><p>Disbursement timeline: {{ company.disbursement_timeframe_days }} business days.</p>',
                'priority': 8,
                'retry_attempts': 3,
                'retry_delay_minutes': 30
            },
            {
                'name': 'loan_rejection_email',
                'notification_type': 'LOAN_REJECTION',
                'channels': ['EMAIL'],
                'subject_template': 'Loan Application Update - FlexiFinance',
                'message_template': 'Dear {{ user.first_name }}, thank you for your loan application. After careful review, we are unable to approve your application at this time. Your loan reference is {{ loan.loan_reference }}. We encourage you to reapply after improving your credit profile.',
                'html_template': '<h2>Application Update</h2><p>Thank you for your loan application with FlexiFinance.</p><p><strong>Reference:</strong> {{ loan.loan_reference }}</p><p>After careful review, we are unable to approve your application at this time. We encourage you to reapply after improving your credit profile.</p>',
                'priority': 7,
                'retry_attempts': 2,
                'retry_delay_minutes': 60
            },
            {
                'name': 'loan_disbursement_email',
                'notification_type': 'LOAN_DISBURSEMENT',
                'channels': ['EMAIL'],
                'subject_template': 'Loan Disbursed - FlexiFinance',
                'message_template': 'Dear {{ user.first_name }}, your FlexiFinance loan has been successfully disbursed. Amount: KSh {{ loan.principal_amount }}. Reference: {{ loan.loan_reference }}. You will receive an SMS confirmation shortly.',
                'html_template': '<h2>Loan Disbursed Successfully!</h2><p><strong>Amount:</strong> KSh {{ loan.principal_amount }}</p><p><strong>Reference:</strong> {{ loan.loan_reference }}</p><p>You will receive an SMS confirmation shortly.</p>',
                'priority': 9,
                'retry_attempts': 3,
                'retry_delay_minutes': 15
            },
            {
                'name': 'payment_confirmation_email',
                'notification_type': 'PAYMENT_CONFIRMATION',
                'channels': ['EMAIL'],
                'subject_template': 'Payment Confirmed - FlexiFinance',
                'message_template': 'Dear {{ user.first_name }}, we have received your payment of KSh {{ payment.amount }}. Reference: {{ payment.reference_number }}. Your outstanding balance is now KSh {{ loan.remaining_balance }}.',
                'html_template': '<h2>Payment Confirmed</h2><p><strong>Amount Paid:</strong> KSh {{ payment.amount }}</p><p><strong>Reference:</strong> {{ payment.reference_number }}</p><p><strong>Remaining Balance:</strong> KSh {{ loan.remaining_balance }}</p>',
                'priority': 8,
                'retry_attempts': 3,
                'retry_delay_minutes': 30
            },
            {
                'name': 'payment_reminder_sms',
                'notification_type': 'PAYMENT_REMINDER',
                'channels': ['SMS'],
                'subject_template': '',
                'message_template': 'Hi {{ user.first_name }}, reminder: Your FlexiFinance loan payment of KSh {{ installment.total_amount }} is due on {{ installment.due_date }}. Reference: {{ loan.loan_reference }}. Pay via M-Pesa to 700 123 456.',
                'html_template': '',
                'priority': 6,
                'retry_attempts': 2,
                'retry_delay_minutes': 120
            },
            {
                'name': 'overdue_notice_email',
                'notification_type': 'OVERDUE_NOTICE',
                'channels': ['EMAIL'],
                'subject_template': 'Overdue Payment Notice - FlexiFinance',
                'message_template': 'Dear {{ user.first_name }}, your FlexiFinance loan payment of KSh {{ installment.total_amount }} was due on {{ installment.due_date }}. Please make immediate payment to avoid late fees. Reference: {{ loan.loan_reference }}.',
                'html_template': '<h2>Overdue Payment Notice</h2><p><strong>Amount Due:</strong> KSh {{ installment.total_amount }}</p><p><strong>Due Date:</strong> {{ installment.due_date }}</p><p><strong>Reference:</strong> {{ loan.loan_reference }}</p><p>Please make immediate payment to avoid late fees.</p>',
                'priority': 9,
                'retry_attempts': 3,
                'retry_delay_minutes': 60
            },
            {
                'name': 'welcome_email',
                'notification_type': 'WELCOME_EMAIL',
                'channels': ['EMAIL'],
                'subject_template': 'Welcome to FlexiFinance - Your Financial Partner',
                'message_template': 'Dear {{ user.first_name }}, welcome to FlexiFinance! We are excited to have you as our customer. You can now apply for loans from KSh 5,000 to KSh 500,000 with competitive interest rates. Visit your dashboard to get started.',
                'html_template': '<h2>Welcome to FlexiFinance!</h2><p>Dear {{ user.first_name }}, welcome to FlexiFinance!</p><p>We are excited to have you as our customer.</p><ul><li>Loan amounts: KSh 5,000 - KSh 500,000</li><li>Competitive interest rates</li><li>Fast approval process</li></ul><p>Visit your dashboard to get started.</p>',
                'priority': 7,
                'retry_attempts': 2,
                'retry_delay_minutes': 60
            },
            {
                'name': 'account_verification_email',
                'notification_type': 'ACCOUNT_VERIFICATION',
                'channels': ['EMAIL'],
                'subject_template': 'Verify Your FlexiFinance Account',
                'message_template': 'Dear {{ user.first_name }}, please verify your FlexiFinance account by clicking the link: {{ verification_url }}. This link will expire in 24 hours. If you did not create this account, please ignore this email.',
                'html_template': '<h2>Account Verification</h2><p>Dear {{ user.first_name }},</p><p>Please verify your FlexiFinance account by clicking the link below:</p><p><a href="{{ verification_url }}">Verify Account</a></p><p><em>This link will expire in 24 hours.</em></p>',
                'priority': 8,
                'retry_attempts': 3,
                'retry_delay_minutes': 30
            },
            {
                'name': 'security_alert_email',
                'notification_type': 'SECURITY_ALERT',
                'channels': ['EMAIL'],
                'subject_template': 'Security Alert - FlexiFinance Account',
                'message_template': 'Dear {{ user.first_name }}, we detected a login to your FlexiFinance account from {{ login_location }} at {{ login_time }}. If this was not you, please change your password immediately and contact our support team.',
                'html_template': '<h2>Security Alert</h2><p>Dear {{ user.first_name }},</p><p>We detected a login to your FlexiFinance account:</p><ul><li><strong>Location:</strong> {{ login_location }}</li><li><strong>Time:</strong> {{ login_time }}</li></ul><p>If this was not you, please change your password immediately.</p>',
                'priority': 9,
                'retry_attempts': 2,
                'retry_delay_minutes': 15
            },
            {
                'name': 'marketing_email',
                'notification_type': 'MARKETING',
                'channels': ['EMAIL'],
                'subject_template': 'Special Loan Offer - FlexiFinance',
                'message_template': 'Dear {{ user.first_name }}, take advantage of our special loan offer! Get 0.5% discount on interest rates for loans above KSh 100,000. Offer valid until {{ offer_expiry }}. Apply now!',
                'html_template': '<h2>Special Loan Offer!</h2><p>Dear {{ user.first_name }},</p><p>Get 0.5% discount on interest rates for loans above KSh 100,000!</p><p><strong>Offer valid until:</strong> {{ offer_expiry }}</p><p><a href="{{ apply_url }}">Apply Now</a></p>',
                'priority': 3,
                'retry_attempts': 1,
                'retry_delay_minutes': 1440
            }
        ]

        created_count = 0
        for template_data in templates:
            template, created = NotificationTemplate.objects.get_or_create(
                name=template_data['name'],
                defaults=template_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Created template: {template.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  Already exists: {template.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'🎉 Created {created_count} new notification templates!')
        )
EOF

echo "✅ Notification templates command created"

echo
echo "🔧 Step 3: Creating Loan Products Management Command..."

# Create the loan products command (keeping existing functionality)
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
            },
            {
                'product_code': 'EDUCATION_25K_300K',
                'name': 'Education Loan',
                'description': 'Student loans for tuition, courses, and educational expenses up to KSh 300,000',
                'min_amount': 25000,
                'max_amount': 300000,
                'min_tenure': 6,
                'max_tenure': 48,
                'interest_rate': 9.0,
                'processing_fee': 1500.0,
                'late_fee_rate': 1.5,
                'min_income': 20000,
                'min_employment_duration': 0,
                'min_credit_score': 500,
                'is_active': True,
                'requires_documents': True
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
echo "🔧 Step 4: Creating Repayment Schedules Management Command..."

# Create the repayment schedules command (keeping existing functionality)
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
            previous_due_date = None
            
            for installment in range(1, loan.loan_tenure + 1):
                # Calculate due date (30 days from previous)
                if installment == 1:
                    due_date = loan.disbursement_date or loan.approval_date or timezone.now()
                else:
                    due_date = previous_due_date + timedelta(days=30)
                
                # Calculate principal and interest amounts
                principal_amount = monthly_payment * (1 - (loan.interest_rate * loan.loan_tenure) / (100 * 12))
                interest_amount = monthly_payment - principal_amount
                
                # Create repayment schedule entry
                schedule, created = RepaymentSchedule.objects.get_or_create(
                    loan=loan,
                    installment_number=installment,
                    defaults={
                        'due_date': due_date.date(),
                        'principal_amount': principal_amount,
                        'interest_amount': interest_amount,
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
echo "🔧 Step 5: Creating __init__.py files..."
touch /home/cavin/projects/Django_Projects/FlexiFinance/apps/core/management/__init__.py
touch /home/cavin/projects/Django_Projects/FlexiFinance/apps/core/management/commands/__init__.py
touch /home/cavin/projects/Django_Projects/FlexiFinance/apps/notifications/management/__init__.py
touch /home/cavin/projects/Django_Projects/FlexiFinance/apps/notifications/management/commands/__init__.py
touch /home/cavin/projects/Django_Projects/FlexiFinance/apps/loans/management/__init__.py
touch /home/cavin/projects/Django_Projects/apps/loans/management/commands/__init__.py

echo "✅ Management command structure created"

echo
echo "🔧 Step 6: Running commands to populate admin interfaces..."
cd /home/cavin/projects/Django_Projects/FlexiFinance

echo "🏢 Creating Company Information..."
python manage.py create_company_info

echo
echo "📧 Creating Notification Templates..."
python manage.py create_notification_templates

echo
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
echo "1. Company Info: http://127.0.0.1:8000/admin/core/company/"
echo "2. Notification Templates: http://127.0.0.1:8000/admin/notifications/notificationtemplate/"
echo "3. Loan Products: http://127.0.0.1:8000/admin/loans/loanproduct/"
echo "4. Repayment Schedules: http://127.0.0.1:8000/admin/loans/repaymentschedule/"
echo
echo "📋 Expected Results:"
echo "- 1 Company record created"
echo "- 10 Notification templates created"
echo "- 5 Loan Products created:"
echo "  • Quick Cash: KSh 5,000 - KSh 25,000"
echo "  • Personal Loan: KSh 5,000 - KSh 100,000"
echo "  • Business Loan: KSh 50,000 - KSh 500,000"
echo "  • Emergency Loan: KSh 5,000 - KSh 50,000"
echo "  • Education Loan: KSh 25,000 - KSh 300,000"
echo "- Repayment schedules generated for approved loans"
echo ""
echo "✅ Complete admin setup: Company + Templates + Products + Schedules"