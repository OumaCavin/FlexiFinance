# FlexiFinance Activity Diagram

**Author:** Cavin Otieno  
**Date:** December 5, 2025  
**Version:** 1.0.0

## Overview

This document presents the activity diagram for FlexiFinance, illustrating the complete workflow from user registration through loan repayment, showing all decision points, parallel activities, and exception handling.

![Activity Diagram](activity_diagram.png)

## Activity Flow Analysis

### Phase 1: User Onboarding

#### 1.1 Account Registration
**Objective:** Create new user account
**Activities:**
- Register account with personal details
- Verify email address
- Activate user account

**Decision Point: Email Verified?**
- **No:** Return to registration (loop)
- **Yes:** Proceed to KYC completion

**Implementation Notes:**
- Email verification prevents spam accounts
- Account activation requires email confirmation
- Failed verifications should be logged for monitoring

#### 1.2 KYC Process
**Objective:** Verify user identity
**Activities:**
- Complete KYC form with personal information
- Upload identity documents (ID, passport photo)
- Submit for admin review

**Decision Point: Admin Review**
- **Reject:** User resubmits documents
- **Approve:** KYC status updated to approved

**Critical Requirements:**
- Document validation (file type, size, readability)
- Secure document storage with encryption
- Admin workflow for document review
- Audit trail for all KYC decisions

### Phase 2: Loan Application

#### 2.1 Loan Application Submission
**Objective:** Submit loan application
**Activities:**
- Apply for loan with requested amount
- Provide loan purpose and details
- Upload supporting documents

**Supporting Documents May Include:**
- Bank statements
- Employment letters
- Business registration certificates
- Income verification documents

#### 2.2 Loan Evaluation Process
**Objective:** Assess loan application
**Activities:**
- Review user profile and KYC status
- Evaluate creditworthiness
- Check supporting documents

**Decision Point: Loan Evaluation**
- **Approve:** Proceed to disbursement
- **Reject:** Notify applicant of rejection
- **Need More Info:** Request additional documents

**Evaluation Criteria:**
- Credit history and score
- Income verification
- Debt-to-income ratio
- Employment stability
- KYC verification status

### Phase 3: Loan Disbursement

#### 3.1 Payment Initiation
**Objective:** Disburse approved loan via M-Pesa
**Activities:**
- Update loan status to approved
- Initiate M-Pesa STK push
- Wait for user confirmation

**Critical Process:**
- STK Push requires user phone confirmation
- Timeout handling for unconfirmed payments
- Retry mechanism for failed attempts

#### 3.2 Payment Confirmation
**Decision Point: Payment Confirmed?**
- **No:** Retry payment process
- **Yes:** Record transaction and disburse loan

**Post-Disbursement Activities:**
- Update loan balance and status
- Send confirmation email to borrower
- Provide access to repayment portal
- Schedule first payment reminder

### Phase 4: Loan Repayment

#### 4.1 Payment Monitoring
**Objective:** Monitor repayment due dates
**Activities:**
- Check payment due dates daily
- Send payment reminders
- Process payments when initiated

**Decision Point: On Due Date?**
- **No:** Send reminder and continue monitoring
- **Yes:** Process payment when initiated

#### 4.2 Payment Processing
**Objective:** Process loan repayment via M-Pesa
**Activities:**
- User initiates repayment
- System calculates outstanding amount
- Initiate M-Pesa STK push
- Process payment confirmation

**Decision Point: Payment Status**
- **Success:** Update payment records
- **Failed:** Retry payment process
- **Partial:** Process partial payment and continue

#### 4.3 Loan Completion
**Decision Point: Balance > 0?**
- **Yes:** Continue with repayment schedule
- **No:** Mark loan as complete

**Completion Activities:**
- Send loan completion confirmation
- Generate final statement
- Offer loan products for future borrowing

## Parallel Activities

### Notification System
**Runs in parallel throughout the process:**
- Email notifications for all major events
- SMS reminders for payment due dates
- In-app notifications for status updates
- Admin alerts for system events

**Notification Triggers:**
- Account registration confirmation
- KYC approval/rejection
- Loan application received
- Loan approval/rejection
- Payment confirmations
- Payment reminders
- Loan completion

### Audit and Logging
**Continuous activities:**
- User action logging
- Transaction recording
- System event logging
- Performance monitoring
- Security event tracking

## Exception Handling

### Document Upload Failures
**Scenario:** User uploads invalid documents
**Response:**
1. System validates file format and size
2. Shows error message to user
3. Requests resubmission
4. Logs attempt for monitoring

### Payment Processing Failures
**Scenario:** M-Pesa payment fails
**Response:**
1. System detects payment failure
2. Records failure in transaction log
3. Notifies user of failure
4. Provides retry mechanism
5. Offers alternative payment methods if needed

### KYC Rejection
**Scenario:** Admin rejects KYC documents
**Response:**
1. Admin provides rejection reason
2. System notifies user of rejection
3. User can resubmit documents
4. New review cycle initiated

### System Errors
**Scenario:** Internal system error
**Response:**
1. Error logging and notification
2. Admin alert for manual intervention
3. User-friendly error messaging
4. Recovery mechanism implementation

## Business Rules Implementation

### Loan Eligibility Rules
```
IF (user_age >= 18 AND user_age <= 65) 
AND (monthly_income >= minimum_income)
AND (kyc_status == 'APPROVED')
AND (credit_score >= minimum_score)
THEN user_eligible = TRUE
```

### Interest Calculation Rules
```
loan_interest = principal_amount * (annual_rate/100) * (loan_tenure/12)
monthly_payment = (principal_amount + loan_interest) / loan_tenure
```

### Payment Priority Rules
```
IF (payment_amount >= total_due)
THEN payment_priority = 'FULL_PAYMENT'
ELSE payment_priority = 'PARTIAL_PAYMENT'
```

## Performance Considerations

### Optimization Points
1. **Document Processing:** Async processing for large files
2. **Payment Processing:** Queue-based processing for high volume
3. **Email Delivery:** Batch email sending
4. **Database Queries:** Optimized indexing for frequent queries

### Scalability Features
1. **Horizontal Scaling:** Stateless application design
2. **Database Scaling:** Read replicas for reporting
3. **Caching:** Redis for session and frequently accessed data
4. **Load Balancing:** Multiple application instances

## Security Activities

### Authentication Flow
- User login verification
- Session management
- Token-based API access
- Password policy enforcement

### Authorization Checks
- Role-based access control
- Resource-level permissions
- API endpoint protection
- Admin action authorization

### Data Protection
- Sensitive data encryption
- Secure document storage
- PCI compliance for payments
- Audit trail maintenance

## Integration Points

### M-Pesa API Integration
- STK push initiation
- Payment confirmation handling
- Webhook processing
- Error handling and retries

### Email Service Integration
- Template-based emails
- Delivery tracking
- Bounce handling
- Unsubscribe management

### Database Integration
- Transaction management
- Data consistency
- Backup procedures
- Recovery mechanisms

## Monitoring and Alerting

### Key Metrics
- Registration completion rate
- KYC approval rate
- Loan approval rate
- Payment success rate
- User satisfaction scores

### Alert Conditions
- High failure rates in payment processing
- Unusual activity patterns
- System performance degradation
- Database connection issues
- Email delivery failures

## Future Enhancements

### Automated Decision Making
- AI-powered loan approval
- Automated document verification
- Fraud detection algorithms
- Credit scoring automation

### Advanced Features
- Multiple loan products
- Loan rescheduling options
- Insurance integration
- Financial advisory services

---

**Conclusion:** This activity diagram provides a comprehensive view of all processes within FlexiFinance, ensuring that every user journey is properly mapped with appropriate decision points, exception handling, and business rule implementation. The diagram serves as a foundation for development, testing, and process optimization.