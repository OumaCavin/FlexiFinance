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
