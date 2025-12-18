"""
Management command to populate default document types for FlexiFinance
"""
from django.core.management.base import BaseCommand
from apps.documents.models import DocumentType


class Command(BaseCommand):
    help = 'Populate default document types for FlexiFinance'

    def handle(self, *args, **options):
        # Define default document types
        document_types = [
            {
                'name': 'National ID',
                'description': 'Kenyan National Identity Card or equivalent government-issued photo ID',
                'required_for': 'KYC',
                'is_required': True,
                'max_file_size': 5242880,  # 5MB
                'allowed_extensions': 'pdf,jpg,jpeg,png',
                'verification_required': True,
                'auto_approve': False,
            },
            {
                'name': 'Passport',
                'description': 'Valid passport with photo page showing personal details',
                'required_for': 'KYC',
                'is_required': False,
                'max_file_size': 5242880,  # 5MB
                'allowed_extensions': 'pdf,jpg,jpeg,png',
                'verification_required': True,
                'auto_approve': False,
            },
            {
                'name': 'Driver\'s License',
                'description': 'Valid driver\'s license with photo and personal information',
                'required_for': 'KYC',
                'is_required': False,
                'max_file_size': 5242880,  # 5MB
                'allowed_extensions': 'pdf,jpg,jpeg,png',
                'verification_required': True,
                'auto_approve': False,
            },
            {
                'name': 'Employment Letter',
                'description': 'Official employment verification letter from employer',
                'required_for': 'INCOME_PROOF',
                'is_required': True,
                'max_file_size': 5242880,  # 5MB
                'allowed_extensions': 'pdf,doc,docx',
                'verification_required': True,
                'auto_approve': False,
            },
            {
                'name': 'Salary Slip',
                'description': 'Recent salary slip or pay stub showing income details',
                'required_for': 'INCOME_PROOF',
                'is_required': True,
                'max_file_size': 5242880,  # 5MB
                'allowed_extensions': 'pdf,jpg,jpeg,png',
                'verification_required': True,
                'auto_approve': False,
            },
            {
                'name': 'Bank Statement',
                'description': 'Recent bank statement (last 3-6 months) showing account activity',
                'required_for': 'INCOME_PROOF',
                'is_required': True,
                'max_file_size': 10485760,  # 10MB
                'allowed_extensions': 'pdf',
                'verification_required': True,
                'auto_approve': False,
            },
            {
                'name': 'Utility Bill',
                'description': 'Recent utility bill (electricity, water, or mobile money) showing address',
                'required_for': 'ADDRESS_PROOF',
                'is_required': True,
                'max_file_size': 5242880,  # 5MB
                'allowed_extensions': 'pdf,jpg,jpeg,png',
                'verification_required': True,
                'auto_approve': False,
            },
            {
                'name': 'Business Registration Certificate',
                'description': 'Official business registration certificate or incorporation documents',
                'required_for': 'BUSINESS_DOCS',
                'is_required': True,
                'max_file_size': 10485760,  # 10MB
                'allowed_extensions': 'pdf',
                'verification_required': True,
                'auto_approve': False,
            },
            {
                'name': 'Tax Compliance Certificate',
                'description': 'Current tax compliance certificate from Kenya Revenue Authority',
                'required_for': 'BUSINESS_DOCS',
                'is_required': True,
                'max_file_size': 5242880,  # 5MB
                'allowed_extensions': 'pdf',
                'verification_required': True,
                'auto_approve': False,
            },
            {
                'name': 'Collateral Document',
                'description': 'Property title deed or other collateral documentation',
                'required_for': 'COLLATERAL',
                'is_required': False,
                'max_file_size': 10485760,  # 10MB
                'allowed_extensions': 'pdf',
                'verification_required': True,
                'auto_approve': False,
            },
            {
                'name': 'Loan Application Form',
                'description': 'Completed and signed loan application form',
                'required_for': 'LOAN_APPLICATION',
                'is_required': True,
                'max_file_size': 5242880,  # 5MB
                'allowed_extensions': 'pdf',
                'verification_required': True,
                'auto_approve': False,
            },
            {
                'name': 'Guarantor ID',
                'description': 'National ID of loan guarantor (if required)',
                'required_for': 'LOAN_APPLICATION',
                'is_required': False,
                'max_file_size': 5242880,  # 5MB
                'allowed_extensions': 'pdf,jpg,jpeg,png',
                'verification_required': True,
                'auto_approve': False,
            },
        ]

        created_count = 0
        updated_count = 0

        for doc_type_data in document_types:
            # Check if document type already exists
            doc_type, created = DocumentType.objects.get_or_create(
                name=doc_type_data['name'],
                defaults=doc_type_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created document type: {doc_type.name}')
                )
            else:
                # Update existing document type
                for field, value in doc_type_data.items():
                    setattr(doc_type, field, value)
                doc_type.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Updated document type: {doc_type.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully processed {len(document_types)} document types. '
                f'Created: {created_count}, Updated: {updated_count}'
            )
        )

        # Display summary
        self.stdout.write('\nDocument Types Summary:')
        for doc_type in DocumentType.objects.all():
            self.stdout.write(
                f'  - {doc_type.name} ({doc_type.get_required_for_display}) '
                f'- Required: {doc_type.is_required}, Auto-approve: {doc_type.auto_approve}'
            )