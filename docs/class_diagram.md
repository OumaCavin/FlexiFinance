# FlexiFinance Class Diagram

**Author:** Cavin Otieno  
**Date:** December 5, 2025  
**Version:** 1.0.0

## Overview

This document presents the class diagram for FlexiFinance, illustrating the data structure, relationships, and methods for all major entities in the micro-finance platform.

![Class Diagram](class_diagram.png)

## Class Hierarchy Overview

### Core Domain Layers

1. **User Management Layer**
   - User, UserProfile, KYCStatus, AdminUser

2. **Loan Management Layer**
   - Loan, LoanProduct, RepaymentSchedule

3. **Payment Processing Layer**
   - Payment, MpesaTransaction

4. **Notification Layer**
   - Notification, EmailTemplate

5. **Document Management Layer**
   - Document

6. **Configuration Layer**
   - SystemConfig

## Class Descriptions

### User Management Classes

#### User Class
**Purpose:** Core user entity for authentication and basic profile information

**Key Attributes:**
- `id`: UUID primary key for unique identification
- `email`: User's email address for communication
- `phone_number`: Mobile number for M-Pesa integration
- `first_name`, `last_name`: User's legal names
- `date_of_birth`: Required for age verification and eligibility
- `is_verified`: Email verification status
- `last_login`: Security tracking

**Key Methods:**
- `register()`: Creates new user account
- `verify_email()`: Handles email verification process
- `login()`, `logout()`: Authentication methods
- `update_profile()`: Profile information updates

**Relationships:**
- One-to-one with UserProfile
- One-to-one with KYCStatus
- One-to-many with Loan applications
- One-to-many with Payment transactions

#### UserProfile Class
**Purpose:** Extended user information and financial details

**Key Attributes:**
- `national_id`: Primary identification document
- `passport_photo`: Profile picture for verification
- `monthly_income`: Income used for loan eligibility
- `employer_name`, `employment_duration`: Employment verification
- `emergency_contact_name`, `emergency_contact_phone`: Safety contact

**Key Methods:**
- `save_profile()`: Persists profile data
- `update_employment_info()`: Employment status updates

**Business Rules:**
- Monthly income must meet minimum loan amount
- Employment duration affects creditworthiness

#### KYCStatus Class
**Purpose:** Know Your Customer verification tracking

**Key Attributes:**
- `status`: PENDING, APPROVED, REJECTED
- `verification_level`: Basic, Standard, Enhanced
- `reviewed_by`: Admin user who performed review
- `review_notes`: Comments on approval/rejection

**Key Methods:**
- `submit_documents()`: Uploads KYC documents
- `approve_kyc()`, `reject_kyc()`: Admin actions
- `get_status()`: Current verification status

**Workflow:**
1. User submits documents
2. Status becomes PENDING
3. Admin reviews and updates status
4. Approved users can apply for loans

### Loan Management Classes

#### Loan Class
**Purpose:** Core loan entity with all loan-related data

**Key Attributes:**
- `loan_reference`: Unique identifier for tracking
- `principal_amount`: Original loan amount
- `interest_rate`: Annual interest rate
- `loan_tenure`: Repayment period in months
- `total_amount`: Principal + interest
- `remaining_balance`: Outstanding amount
- `credit_score`: Risk assessment score
- `risk_category`: LOW, MEDIUM, HIGH

**Key Methods:**
- `apply_loan()`: Creates new loan application
- `calculate_interest()`: Computes interest amount
- `approve_loan()`: Admin approval process
- `disburse_loan()`: Initiates payment to user
- `get_outstanding_amount()`: Current balance

**State Transitions:**
```
DRAFT -> PENDING_REVIEW -> APPROVED -> DISBURSED -> ACTIVE
                    -> REJECTED
```

#### LoanProduct Class
**Purpose:** Configurable loan products with different terms

**Key Attributes:**
- `product_name`: Consumer-friendly product name
- `min_amount`, `max_amount`: Loan amount range
- `min_tenure`, `max_tenure`: Repayment period range
- `interest_rate`: Applicable interest rate
- `processing_fee`: One-time processing charge
- `penalty_rate`: Late payment penalty
- `eligibility_criteria`: JSON configuration for rules

**Key Methods:**
- `check_eligibility()`: Validates user against criteria
- `calculate_total_amount()`: Computes total repayment

**Example Products:**
- Quick Cash: KES 1,000-10,000, 1-3 months, 15% p.a.
- Business Loan: KES 10,000-100,000, 3-12 months, 12% p.a.

#### RepaymentSchedule Class
**Purpose:** Structured repayment plan for each loan

**Key Attributes:**
- `installment_number`: Sequential payment number
- `due_date`: Payment due date
- `principal_amount`, `interest_amount`: Payment breakdown
- `total_amount`: Total payment due
- `paid_amount`: Amount already paid
- `remaining_amount`: Outstanding for this installment

**Key Methods:**
- `record_payment()`: Updates payment status
- `get_outstanding()`: Calculates remaining amount
- `mark_as_paid()`: Finalizes payment

### Payment Processing Classes

#### Payment Class
**Purpose:** General payment entity for all transactions

**Key Attributes:**
- `mpesa_reference`: M-Pesa transaction reference
- `transaction_id`: Internal transaction ID
- `payment_type`: DISBURSEMENT, REPAYMENT, FEE
- `status`: PENDING, COMPLETED, FAILED
- `phone_number`: M-Pesa phone number
- `receipt_number`: Payment confirmation number

**Key Methods:**
- `initiate_stk_push()`: Sends payment request
- `process_payment()`: Handles payment logic
- `confirm_payment()`: Confirms successful payment
- `generate_receipt()`: Creates payment receipt

**Payment Types:**
- DISBURSEMENT: Loan money to borrower
- REPAYMENT: Borrower paying back loan
- FEE: Processing or service fees

#### MpesaTransaction Class
**Purpose:** Detailed M-Pesa integration and callbacks

**Key Attributes:**
- `mpesa_receipt`: Official M-Pesa receipt number
- `checkout_request_id`: STK push request ID
- `merchant_request_id`: Internal request tracking
- `customer_phone`: Phone number used
- `transaction_amount`: Amount transacted
- `result_code`, `result_desc`: M-Pesa response status

**Key Methods:**
- `process_callback()`: Handles M-Pesa webhook
- `validate_transaction()`: Validates M-Pesa response
- `get_transaction_status()`: Current transaction state

**Callback Process:**
1. User approves STK push
2. M-Pesa sends callback to webhook
3. System validates callback
4. Updates payment status

### Notification System

#### Notification Class
**Purpose:** In-app and push notifications

**Key Attributes:**
- `notification_type`: EMAIL, SMS, IN_APP
- `is_read`: Read status tracking
- `read_at`: Timestamp when read
- `title`, `message`: Notification content

**Key Methods:**
- `send_notification()`: Delivers notification
- `mark_as_read()`: Updates read status
- `delete_notification()`: Removes notification

**Notification Types:**
- Loan application received
- KYC approval/rejection
- Loan approval/disbursement
- Payment reminders
- Payment confirmations

#### EmailTemplate Class
**Purpose:** Reusable email templates

**Key Attributes:**
- `template_name`: Identifier for template
- `subject`: Email subject line
- `content`: HTML email content
- `template_type`: LOAN_APPROVAL, PAYMENT_CONFIRMATION, etc.

### Document Management

#### Document Class
**Purpose:** File upload and document management

**Key Attributes:**
- `document_type`: KYC, BANK_STATEMENT, EMPLOYMENT_LETTER
- `file_path`: Storage location
- `file_size`: File size in bytes
- `verification_status`: PENDING, VERIFIED, REJECTED
- `verified_by`: Admin who verified

**Key Methods:**
- `upload_file()`: Handles file upload
- `verify_document()`: Admin verification
- `download_file()`: Secure file access

### Administration

#### AdminUser Class
**Purpose:** Administrative user management

**Key Attributes:**
- `role`: SUPER_ADMIN, LOAN_OFFICER, SUPPORT_AGENT
- `permissions`: JSON array of permissions

**Key Methods:**
- `has_permission()`: Permission checking
- Login/logout methods for admin access

#### SystemConfig Class
**Purpose:** System-wide configuration

**Key Attributes:**
- `config_key`: Configuration identifier
- `config_value`: Configuration value
- `config_type`: STRING, INTEGER, BOOLEAN, JSON
- `description`: Configuration description

**Example Configurations:**
- `MIN_LOAN_AMOUNT`: 1000
- `MAX_LOAN_AMOUNT`: 500000
- `DEFAULT_INTEREST_RATE`: 15.0
- `PAYMENT_GRACE_DAYS`: 3

## Relationships and Cardinality

### Primary Relationships

1. **User - UserProfile** (1:1)
   - Each user has exactly one profile
   - Profile contains extended user information

2. **User - KYCStatus** (1:1)
   - Each user has one KYC status
   - Tracks verification progress

3. **User - Loan** (1:M)
   - One user can have multiple loans
   - Historical loan tracking

4. **Loan - Payment** (1:M)
   - One loan has multiple payments
   - Disbursement + repayments

5. **Loan - RepaymentSchedule** (1:M)
   - One loan has multiple installments
   - Structured repayment plan

### Data Integrity Constraints

**Foreign Key Constraints:**
- All user-related classes reference User.id
- Loan payments reference User.id and Loan.id
- Documents reference either User.id or Loan.id

**Validation Rules:**
- Email must be unique across users
- Phone number format validation
- Loan amount must be within product limits
- Payment amounts cannot exceed loan balance

**Indexing Strategy:**
- Primary keys: UUID for security
- User email: Unique index for authentication
- Loan reference: Unique index for tracking
- Payment status: Index for querying

## Business Logic Implementation

### Loan Approval Logic
```python
def approve_loan(self):
    if self.credit_score >= 650 and self.risk_category == 'LOW':
        self.status = 'APPROVED'
        self.approval_date = timezone.now()
    else:
        raise ValidationError("Credit score too low for approval")
```

### Interest Calculation
```python
def calculate_interest(self):
    monthly_rate = self.interest_rate / 100 / 12
    total_interest = self.principal_amount * monthly_rate * self.loan_tenure
    self.total_amount = self.principal_amount + total_interest
    return total_interest
```

### Payment Processing
```python
def process_payment(self, amount):
    if amount >= self.remaining_balance:
        self.status = 'COMPLETED'
        self.remaining_balance = 0
    else:
        self.remaining_balance -= amount
    self.save()
```

## Security Considerations

### Data Encryption
- Password hashing using PBKDF2
- Sensitive fields encrypted at database level
- File storage with encryption

### Access Control
- Role-based permissions
- Object-level permissions for loans
- Admin-only access to sensitive data

### Audit Trail
- All model changes logged
- User actions tracked
- Payment transactions audited

## Future Enhancements

### Machine Learning Integration
- Credit scoring models
- Fraud detection algorithms
- Risk assessment automation

### Microservices Architecture
- User service separation
- Payment service independence
- Notification service scaling

### Advanced Features
- Multi-loan products
- Loan restructuring
- Insurance integration
- Investment products

---

**Conclusion:** This class diagram provides a comprehensive data model for FlexiFinance, ensuring proper separation of concerns, data integrity, and extensibility. The design supports all current requirements while allowing for future enhancements and scalability.