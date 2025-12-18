# FlexiFinance Sequence Diagram

**Author:** Cavin Otieno  
**Date:** December 5, 2025  
**Version:** 1.0.0

## Overview

This document presents the sequence diagram for FlexiFinance, illustrating the chronological interactions between system components during key user workflows including user registration, loan application, approval process, and repayment handling.

![Sequence Diagram](sequence_diagram.png)

## Actors and Components

### 1. Borrower (B)
**Description:** End user seeking loans
**Role:** Initiates all user-facing transactions

### 2. FlexiFinance App (F)
**Description:** Main application backend
**Role:** Orchestrates all system operations and business logic

### 3. Admin Panel (A)
**Description:** Administrative interface
**Role:** Reviews applications, makes decisions, manages system

### 4. M-Pesa System (MP)
**Description:** Mobile money payment platform
**Role:** Handles payment processing and confirmations

### 5. Email Service (E)
**Description:** Notification delivery system
**Role:** Sends email communications to users

### 6. Database (DB)
**Description:** Data persistence layer
**Role:** Stores and retrieves all application data

## Sequence Flow Analysis

### Phase 1: User Registration and KYC

#### Step 1: Account Registration
```
B -> F: Register Account
F -> DB: Save User Data
F -> E: Send Verification Email
E -> B: Email Verification
B -> F: Verify Email
F -> DB: Update User Status
```

**Purpose:** Establish new user account with email verification
**Critical Points:**
- Email validation prevents spam accounts
- Database stores user credentials securely
- Email service must be reliable

**Error Handling:**
- If email fails, retry with backup email service
- If database save fails, rollback and notify user

#### Step 2-6: KYC Process
```
B -> F: Complete KYC
F -> DB: Store KYC Data
B -> F: Upload Documents
F -> DB: Store Documents
F -> A: Notify Admin of New KYC
A -> F: Review KYC
F -> DB: Update KYC Status
A -> F: Approve KYC
F -> E: Notify KYC Approval
E -> B: KYC Approved Email
```

**Purpose:** Verify user identity through document submission
**Critical Points:**
- Document storage must be secure and compliant
- Admin review ensures data quality
- Email notifications keep users informed

**Security Considerations:**
- Document encryption at rest
- Access logging for admin actions
- Data retention policies

### Phase 2: Loan Application and Approval

#### Step 7-11: Loan Application Process
```
B -> F: Apply for Loan
F -> DB: Store Loan Application
F -> DB: Generate Application ID
F -> E: Send Application Confirmation
E -> B: Application Received Email
F -> A: Notify Admin of New Application
A -> F: Review Loan Application
F -> DB: Retrieve User & KYC Data
A -> F: Request Additional Documents
B -> F: Submit Additional Docs
F -> A: Documents Available
A -> F: Make Decision (Approve/Reject)
```

**Purpose:** Process loan application from submission to decision
**Critical Points:**
- Application ID ensures traceability
- Admin workflow manages decision process
- Document requests are tracked

**Business Logic:**
- Interest rate calculation based on user profile
- Loan amount limits based on KYC status
- Risk assessment algorithms

#### Step 12-15: Loan Disbursement
```
F -> DB: Update Loan Status (APPROVED)
F -> MP: Initiate Disbursement
MP -> B: STK Push Notification
B -> MP: Approve Payment
MP -> F: Payment Confirmation
F -> DB: Record Transaction
F -> E: Send Disbursement Confirmation
E -> B: Money Received Email
F -> B: Provide Repayment Portal Access
```

**Purpose:** Execute approved loan disbursement via M-Pesa
**Critical Points:**
- STK Push requires user confirmation
- Payment tracking ensures accountability
- Database transactions maintain consistency

**Error Handling:**
- Payment timeout handling
- Retry mechanism for failed transactions
- Manual intervention for stuck payments

### Phase 3: Loan Repayment

#### Step 16-20: Repayment Processing
```
B -> F: Initiate Repayment
F -> DB: Calculate Outstanding Amount
F -> MP: STK Push for Repayment
MP -> B: Payment Prompt
B -> MP: Confirm Payment
MP -> F: Payment Confirmation
F -> DB: Update Loan Balance
F -> DB: Record Repayment Transaction
F -> E: Send Payment Receipt
E -> B: Payment Successful Email
```

**Purpose:** Process loan repayment through M-Pesa
**Critical Points:**
- Accurate balance calculation
- Real-time payment confirmation
- Receipt generation for audit trail

**Performance Considerations:**
- Database queries optimized for balance calculation
- Caching for frequently accessed data
- Batch processing for email notifications

### Phase 4: Automated Processes

#### Monthly Repayment Reminders
```
F -> E: Reminder Email
E -> B: Payment Reminder
```

**Purpose:** Automated reminder system for due payments
**Features:**
- Configurable reminder timing
- Multiple reminder frequencies
- Escalation for overdue payments

## Exception Scenarios

### Scenario 1: KYC Rejection
```
A -> F: Reject KYC
F -> E: Send KYC Rejection Email
E -> B: Please Resubmit Documents
B -> F: Resubmit KYC Documents
```

**Resolution:** User can resubmit KYC after addressing issues

### Scenario 2: Loan Application Rejection
```
F -> DB: Update Loan Status (REJECTED)
F -> E: Send Rejection Notification
E -> B: Application Rejected with Reason
```

**Resolution:** User receives detailed feedback for improvement

### Scenario 3: Payment Failure
```
MP -> F: Payment Failed
F -> DB: Record Failed Transaction
F -> E: Send Payment Failure Email
E -> B: Payment Failed - Please Retry
B -> F: Retry Payment
```

**Resolution:** User can retry payment with support available

### Scenario 4: System Error During Disbursement
```
F -> MP: Initiate Disbursement
MP -> F: Payment Processed
F -> DB: Record Transaction (FAILS)
F -> A: Alert Admin - Manual Review Required
```

**Resolution:** Manual intervention ensures no lost payments

## Data Flow Analysis

### Database Operations
| Operation | Frequency | Purpose |
|-----------|-----------|---------|
| User Registration | Daily | New user onboarding |
| KYC Storage | Daily | Identity verification |
| Loan Application | Weekly | Core business process |
| Payment Processing | Real-time | Revenue generation |
| Transaction Recording | Real-time | Audit trail |
| Email Notifications | On-demand | User communication |

### Performance Bottlenecks
1. **Document Upload:** Large file sizes
2. **Payment Processing:** Network latency
3. **Balance Calculation:** Complex queries
4. **Email Delivery:** External service dependency

### Scalability Considerations
1. **Database Indexing:** Optimized queries
2. **Caching Strategy:** Redis for frequently accessed data
3. **Load Balancing:** Distribute processing load
4. **Asynchronous Processing:** Background tasks for emails

## Security Flow

### Authentication Flow
```
B -> F: Login Request
F -> DB: Verify Credentials
F -> B: Session Token
B -> F: Authenticated Requests
```

### Authorization Flow
```
B -> F: Request Loan Application
F -> Check: User Permissions
F -> DB: Store Application
F -> B: Application Submitted
```

### Data Encryption
- **Transit:** HTTPS/TLS encryption
- **Storage:** Database encryption at rest
- **API:** JWT token authentication

## Monitoring and Alerting

### Key Metrics
- **Response Time:** API endpoint performance
- **Success Rate:** Payment processing success
- **Error Rate:** System error frequency
- **User Activity:** Registration and loan applications

### Alert Conditions
- Payment processing failures
- System performance degradation
- Unusual user activity patterns
- Database connection issues

## Future Enhancements

### Real-time Notifications
- WebSocket integration for instant updates
- Push notifications for mobile users
- SMS backup for critical alerts

### Advanced Security
- Multi-factor authentication
- Biometric verification
- Fraud detection algorithms

### Automation Improvements
- AI-powered loan decisioning
- Automated credit scoring
- Predictive analytics for repayments

---

**Conclusion:** This sequence diagram provides a detailed view of system interactions, ensuring that all user flows are properly implemented with appropriate error handling, security measures, and performance considerations. The diagram serves as a blueprint for development and testing phases.