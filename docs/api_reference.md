# FlexiFinance API Reference

**Author:** Cavin Otieno  
**Date:** December 5, 2025  
**Version:** 1.0.0

## Overview

This document provides comprehensive API documentation for FlexiFinance, a micro-finance platform with M-Pesa integration. The API follows RESTful principles and uses JSON for data exchange.

## Base Information

### API Base URL
```
Production: https://api.flexifinance.com/v1/
Staging: https://api-staging.flexifinance.com/v1/
Development: http://localhost:8000/api/v1/
```

### Authentication
The FlexiFinance API uses JWT (JSON Web Token) authentication for secure access.

**Authentication Flow:**
1. Obtain access token via `/auth/login/`
2. Include token in Authorization header
3. Token expires after 24 hours
4. Refresh token via `/auth/refresh/`

### Common Headers
```http
Content-Type: application/json
Authorization: Bearer <jwt_token>
Accept: application/json
User-Agent: FlexiFinance-API-Client/1.0
```

### Response Format
```json
{
    "success": true,
    "data": {},
    "message": "Operation completed successfully",
    "errors": [],
    "meta": {
        "timestamp": "2025-12-05T14:48:13Z",
        "request_id": "req_123456789",
        "version": "1.0.0"
    }
}
```

## Error Codes

### HTTP Status Codes
- `200 OK` - Successful request
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `409 Conflict` - Resource conflict
- `422 Unprocessable Entity` - Validation errors
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

### Error Response Format
```json
{
    "success": false,
    "data": null,
    "message": "Validation failed",
    "errors": [
        {
            "field": "email",
            "message": "Email is required",
            "code": "required"
        }
    ],
    "meta": {
        "timestamp": "2025-12-05T14:48:13Z",
        "request_id": "req_123456789"
    }
}
```

## Authentication Endpoints

### POST /auth/register/
Register a new user account.

**Request Body:**
```json
{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+254700123456",
    "date_of_birth": "1990-01-01"
}
```

**Response (201 Created):**
```json
{
    "success": true,
    "data": {
        "user_id": "uuid-string",
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "phone_number": "+254700123456",
        "is_verified": false,
        "created_at": "2025-12-05T14:48:13Z"
    },
    "message": "User registered successfully. Please verify your email."
}
```

### POST /auth/login/
Authenticate user and obtain access token.

**Request Body:**
```json
{
    "email": "user@example.com",
    "password": "SecurePass123!"
}
```

**Response (200 OK):**
```json
{
    "success": true,
    "data": {
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "token_type": "Bearer",
        "expires_in": 86400,
        "user": {
            "user_id": "uuid-string",
            "email": "user@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "is_verified": false,
            "kyc_status": "PENDING"
        }
    },
    "message": "Login successful"
}
```

### POST /auth/refresh/
Refresh access token using refresh token.

**Request Body:**
```json
{
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response (200 OK):**
```json
{
    "success": true,
    "data": {
        "access_token": "new_jwt_token_here",
        "token_type": "Bearer",
        "expires_in": 86400
    },
    "message": "Token refreshed successfully"
}
```

### POST /auth/logout/
Invalidate current access token.

**Headers:**
```http
Authorization: Bearer <jwt_token>
```

**Response (200 OK):**
```json
{
    "success": true,
    "data": null,
    "message": "Logout successful"
}
```

### POST /auth/forgot-password/
Request password reset email.

**Request Body:**
```json
{
    "email": "user@example.com"
}
```

**Response (200 OK):**
```json
{
    "success": true,
    "data": null,
    "message": "Password reset email sent if account exists"
}
```

### POST /auth/reset-password/
Reset password using reset token.

**Request Body:**
```json
{
    "token": "reset_token_from_email",
    "new_password": "NewSecurePass123!"
}
```

**Response (200 OK):**
```json
{
    "success": true,
    "data": null,
    "message": "Password reset successfully"
}
```

## User Management Endpoints

### GET /users/profile/
Get current user profile.

**Response (200 OK):**
```json
{
    "success": true,
    "data": {
        "user_id": "uuid-string",
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "phone_number": "+254700123456",
        "date_of_birth": "1990-01-01",
        "is_verified": true,
        "kyc_status": "APPROVED",
        "created_at": "2025-12-05T14:48:13Z",
        "updated_at": "2025-12-05T14:48:13Z"
    }
}
```

### PUT /users/profile/
Update user profile information.

**Request Body:**
```json
{
    "first_name": "Jane",
    "last_name": "Smith",
    "phone_number": "+254700123456",
    "date_of_birth": "1992-05-15"
}
```

**Response (200 OK):**
```json
{
    "success": true,
    "data": {
        "user_id": "uuid-string",
        "email": "user@example.com",
        "first_name": "Jane",
        "last_name": "Smith",
        "phone_number": "+254700123456",
        "date_of_birth": "1992-05-15",
        "updated_at": "2025-12-05T14:48:13Z"
    },
    "message": "Profile updated successfully"
}
```

### GET /users/kyc/status/
Get KYC verification status.

**Response (200 OK):**
```json
{
    "success": true,
    "data": {
        "kyc_status": "APPROVED",
        "verification_level": "STANDARD",
        "submitted_at": "2025-12-01T10:00:00Z",
        "reviewed_at": "2025-12-02T14:30:00Z",
        "reviewed_by": "admin_user_id",
        "review_notes": "All documents verified",
        "documents_uploaded": true,
        "next_review_date": null
    }
}
```

### POST /users/kyc/documents/
Upload KYC documents.

**Request (multipart/form-data):**
```
national_id_front: file.jpg
national_id_back: file.jpg
passport_photo: file.jpg
```

**Response (201 Created):**
```json
{
    "success": true,
    "data": {
        "document_id": "doc_uuid",
        "document_type": "KYC_DOCUMENTS",
        "upload_date": "2025-12-05T14:48:13Z",
        "verification_status": "PENDING",
        "file_count": 3
    },
    "message": "Documents uploaded successfully and pending review"
}
```

## Loan Management Endpoints

### GET /loans/products/
Get available loan products.

**Response (200 OK):**
```json
{
    "success": true,
    "data": [
        {
            "product_id": "quick_cash",
            "product_name": "Quick Cash Loan",
            "min_amount": 1000,
            "max_amount": 20000,
            "min_tenure": 1,
            "max_tenure": 6,
            "interest_rate": 15.0,
            "processing_fee": 500,
            "penalty_rate": 2.0,
            "eligibility_criteria": {
                "min_income": 10000,
                "employment_duration": 3,
                "credit_score_min": 600
            },
            "is_active": true
        }
    ]
}
```

### POST /loans/apply/
Submit loan application.

**Request Body:**
```json
{
    "product_id": "quick_cash",
    "requested_amount": 10000,
    "requested_tenure": 3,
    "purpose": "Business expansion",
    "employment_info": {
        "occupation": "Business Owner",
        "employer_name": "Self Employed",
        "monthly_income": 50000,
        "employment_duration": 24
    }
}
```

**Response (201 Created):**
```json
{
    "success": true,
    "data": {
        "application_id": "app_uuid",
        "loan_reference": "LF202500001",
        "status": "SUBMITTED",
        "requested_amount": 10000,
        "requested_tenure": 3,
        "estimated_interest": 375,
        "total_amount": 10375,
        "monthly_payment": 3458,
        "submitted_at": "2025-12-05T14:48:13Z",
        "processing_time": "24-48 hours"
    },
    "message": "Loan application submitted successfully"
}
```

### GET /loans/
Get user's loan applications and loans.

**Query Parameters:**
- `status` - Filter by status (DRAFT, SUBMITTED, UNDER_REVIEW, APPROVED, REJECTED, ACTIVE, COMPLETED)
- `page` - Page number (default: 1)
- `per_page` - Items per page (default: 20)

**Response (200 OK):**
```json
{
    "success": true,
    "data": {
        "loans": [
            {
                "loan_id": "loan_uuid",
                "loan_reference": "LF202500001",
                "product_name": "Quick Cash Loan",
                "principal_amount": 10000,
                "interest_rate": 15.0,
                "loan_tenure": 3,
                "total_amount": 10375,
                "remaining_balance": 6875,
                "status": "ACTIVE",
                "application_date": "2025-12-01T10:00:00Z",
                "disbursement_date": "2025-12-02T15:30:00Z",
                "next_payment_date": "2025-12-15T00:00:00Z",
                "next_payment_amount": 3458
            }
        ],
        "pagination": {
            "current_page": 1,
            "per_page": 20,
            "total_pages": 1,
            "total_items": 1
        }
    }
}
```

### GET /loans/{loan_id}/
Get specific loan details.

**Response (200 OK):**
```json
{
    "success": true,
    "data": {
        "loan_id": "loan_uuid",
        "loan_reference": "LF202500001",
        "product_name": "Quick Cash Loan",
        "principal_amount": 10000,
        "interest_rate": 15.0,
        "loan_tenure": 3,
        "total_amount": 10375,
        "remaining_balance": 6875,
        "status": "ACTIVE",
        "purpose": "Business expansion",
        "application_date": "2025-12-01T10:00:00Z",
        "disbursement_date": "2025-12-02T15:30:00Z",
        "repayment_schedule": [
            {
                "installment_number": 1,
                "due_date": "2025-12-15T00:00:00Z",
                "principal_amount": 3233,
                "interest_amount": 125,
                "total_amount": 3358,
                "paid_amount": 3358,
                "remaining_amount": 0,
                "status": "PAID"
            },
            {
                "installment_number": 2,
                "due_date": "2025-01-15T00:00:00Z",
                "principal_amount": 3233,
                "interest_amount": 94,
                "total_amount": 3327,
                "paid_amount": 0,
                "remaining_amount": 3327,
                "status": "DUE"
            }
        ]
    }
}
```

### GET /loans/{loan_id}/payments/
Get payment history for specific loan.

**Response (200 OK):**
```json
{
    "success": true,
    "data": {
        "payments": [
            {
                "payment_id": "pay_uuid",
                "payment_type": "REPAYMENT",
                "amount": 3358,
                "status": "COMPLETED",
                "initiated_at": "2025-12-15T09:30:00Z",
                "completed_at": "2025-12-15T09:35:00Z",
                "phone_number": "+254700123456",
                "mpesa_reference": "ODK123456789",
                "receipt_number": "RCP123456"
            }
        ]
    }
}
```

## Payment Endpoints

### POST /payments/stk-push/
Initiate M-Pesa STK push for payment.

**Request Body:**
```json
{
    "loan_id": "loan_uuid",
    "amount": 3358,
    "phone_number": "+254700123456",
    "payment_type": "REPAYMENT",
    "description": "Loan repayment for LF202500001"
}
```

**Response (200 OK):**
```json
{
    "success": true,
    "data": {
        "payment_id": "pay_uuid",
        "mpesa_request": {
            "checkout_request_id": "chk_uuid",
            "merchant_request_id": "mrc_uuid"
        },
        "status": "PENDING",
        "message": "STK push sent to your phone"
    },
    "message": "Payment initiated successfully"
}
```

### GET /payments/transactions/
Get payment transaction history.

**Query Parameters:**
- `loan_id` - Filter by specific loan
- `payment_type` - Filter by payment type (DISBURSEMENT, REPAYMENT, FEE)
- `status` - Filter by status (PENDING, COMPLETED, FAILED)
- `start_date` - Filter from date (YYYY-MM-DD)
- `end_date` - Filter to date (YYYY-MM-DD)
- `page` - Page number
- `per_page` - Items per page

**Response (200 OK):**
```json
{
    "success": true,
    "data": {
        "transactions": [
            {
                "payment_id": "pay_uuid",
                "loan_reference": "LF202500001",
                "payment_type": "REPAYMENT",
                "amount": 3358,
                "status": "COMPLETED",
                "phone_number": "+254700123456",
                "mpesa_reference": "ODK123456789",
                "receipt_number": "RCP123456",
                "initiated_at": "2025-12-15T09:30:00Z",
                "completed_at": "2025-12-15T09:35:00Z"
            }
        ],
        "summary": {
            "total_payments": 1,
            "total_amount": 3358,
            "successful_payments": 1,
            "failed_payments": 0
        },
        "pagination": {
            "current_page": 1,
            "per_page": 20,
            "total_pages": 1,
            "total_items": 1
        }
    }
}
```

### GET /payments/{payment_id}/
Get specific payment details.

**Response (200 OK):**
```json
{
    "success": true,
    "data": {
        "payment_id": "pay_uuid",
        "loan_id": "loan_uuid",
        "loan_reference": "LF202500001",
        "payment_type": "REPAYMENT",
        "amount": 3358,
        "status": "COMPLETED",
        "phone_number": "+254700123456",
        "payment_method": "MPESA",
        "mpesa_reference": "ODK123456789",
        "receipt_number": "RCP123456",
        "initiated_at": "2025-12-15T09:30:00Z",
        "completed_at": "2025-12-15T09:35:00Z",
        "mpesa_transaction": {
            "mpesa_receipt": "ODK123456789",
            "transaction_date": "20251215113500",
            "phone_number": "+254700123456",
            "amount": 3358,
            "result_code": "0",
            "result_desc": "Success. Request accepted for processing"
        }
    }
}
```

## Webhook Endpoints

### POST /webhooks/mpesa/
M-Pesa webhook endpoint for payment confirmations.

**Request Headers:**
```http
Content-Type: application/json
X-MPESA-SIGNATURE: <webhook_signature>
```

**Request Body:**
```json
{
    "Body": {
        "stkCallback": {
            "merchantRequestID": "mrc_uuid",
            "checkoutRequestID": "chk_uuid",
            "resultCode": 0,
            "resultDesc": "The service request is processed successfully.",
            "callbackMetadata": {
                "item": [
                    {
                        "name": "Amount",
                        "value": 3358
                    },
                    {
                        "name": "MpesaReceiptNumber",
                        "value": "ODK123456789"
                    },
                    {
                        "name": "PhoneNumber",
                        "value": "254700123456"
                    },
                    {
                        "name": "TransactionDate",
                        "value": 20251215113500
                    }
                ]
            }
        }
    }
}
```

**Response (200 OK):**
```json
{
    "ResultCode": 0,
    "ResultDesc": "Accepted"
}
```

### POST /webhooks/loan-status/
Webhook for loan status updates.

**Request Body:**
```json
{
    "loan_id": "loan_uuid",
    "old_status": "APPROVED",
    "new_status": "DISBURSED",
    "timestamp": "2025-12-05T14:48:13Z",
    "metadata": {
        "disbursed_amount": 10000,
        "transaction_reference": "ODK123456789"
    }
}
```

## Notification Endpoints

### GET /notifications/
Get user notifications.

**Query Parameters:**
- `is_read` - Filter by read status
- `notification_type` - Filter by type (EMAIL, SMS, IN_APP)
- `page` - Page number
- `per_page` - Items per page

**Response (200 OK):**
```json
{
    "success": true,
    "data": {
        "notifications": [
            {
                "notification_id": "notif_uuid",
                "notification_type": "EMAIL",
                "title": "Loan Application Approved",
                "message": "Your loan application has been approved",
                "is_read": false,
                "created_at": "2025-12-05T14:48:13Z",
                "read_at": null,
                "data": {
                    "loan_reference": "LF202500001",
                    "amount": 10000
                }
            }
        ],
        "unread_count": 5,
        "pagination": {
            "current_page": 1,
            "per_page": 20,
            "total_pages": 1,
            "total_items": 1
        }
    }
}
```

### PUT /notifications/{notification_id}/read/
Mark notification as read.

**Response (200 OK):**
```json
{
    "success": true,
    "data": {
        "notification_id": "notif_uuid",
        "is_read": true,
        "read_at": "2025-12-05T14:48:13Z"
    },
    "message": "Notification marked as read"
}
```

### PUT /notifications/mark-all-read/
Mark all notifications as read.

**Response (200 OK):**
```json
{
    "success": true,
    "data": {
        "marked_count": 5
    },
    "message": "All notifications marked as read"
}
```

## Document Management Endpoints

### POST /documents/upload/
Upload document files.

**Request (multipart/form-data):**
```
document_type: BANK_STATEMENT
file: file.pdf
loan_id: loan_uuid (optional)
description: Latest bank statement
```

**Response (201 Created):**
```json
{
    "success": true,
    "data": {
        "document_id": "doc_uuid",
        "document_type": "BANK_STATEMENT",
        "file_name": "bank_statement.pdf",
        "file_size": 2048576,
        "upload_date": "2025-12-05T14:48:13Z",
        "verification_status": "PENDING",
        "download_url": "/api/v1/documents/doc_uuid/download/"
    },
    "message": "Document uploaded successfully"
}
```

### GET /documents/
Get user's documents.

**Query Parameters:**
- `document_type` - Filter by document type
- `verification_status` - Filter by verification status
- `loan_id` - Filter by loan

**Response (200 OK):**
```json
{
    "success": true,
    "data": {
        "documents": [
            {
                "document_id": "doc_uuid",
                "document_type": "BANK_STATEMENT",
                "file_name": "bank_statement.pdf",
                "file_size": 2048576,
                "upload_date": "2025-12-05T14:48:13Z",
                "verification_status": "VERIFIED",
                "verified_at": "2025-12-05T16:30:00Z",
                "verified_by": "admin_user_id",
                "download_url": "/api/v1/documents/doc_uuid/download/"
            }
        ]
    }
}
```

### GET /documents/{document_id}/download/
Download document file.

**Response (200 OK):**
- File stream with appropriate Content-Type header

## Admin Endpoints (Restricted)

### GET /admin/loans/pending/
Get pending loan applications (Admin only).

**Response (200 OK):**
```json
{
    "success": true,
    "data": {
        "applications": [
            {
                "application_id": "app_uuid",
                "loan_reference": "LF202500002",
                "user": {
                    "user_id": "user_uuid",
                    "first_name": "Jane",
                    "last_name": "Doe",
                    "email": "jane@example.com",
                    "phone_number": "+254700123456"
                },
                "requested_amount": 15000,
                "requested_tenure": 4,
                "product_name": "Business Loan",
                "submitted_at": "2025-12-05T10:00:00Z",
                "kyc_status": "APPROVED",
                "risk_score": 750
            }
        ]
    }
}
```

### PUT /admin/loans/{application_id}/approve/
Approve loan application (Admin only).

**Request Body:**
```json
{
    "approved_amount": 15000,
    "approved_tenure": 4,
    "interest_rate": 14.0,
    "admin_notes": "Approved based on strong credit score and stable income"
}
```

**Response (200 OK):**
```json
{
    "success": true,
    "data": {
        "application_id": "app_uuid",
        "loan_id": "loan_uuid",
        "loan_reference": "LF202500002",
        "status": "APPROVED",
        "approved_amount": 15000,
        "approved_tenure": 4,
        "interest_rate": 14.0,
        "total_amount": 16800,
        "monthly_payment": 4200,
        "approved_at": "2025-12-05T14:48:13Z",
        "approved_by": "admin_user_id"
    },
    "message": "Loan application approved successfully"
}
```

### PUT /admin/loans/{application_id}/reject/
Reject loan application (Admin only).

**Request Body:**
```json
{
    "rejection_reason": "Insufficient income documentation",
    "admin_notes": "Need additional bank statements showing consistent income"
}
```

## Rate Limiting

### Rate Limits
- **Authentication endpoints:** 5 requests per minute
- **General API endpoints:** 100 requests per minute
- **Payment endpoints:** 10 requests per minute
- **Document upload:** 20 requests per hour

### Rate Limit Headers
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

### Rate Limit Exceeded Response (429 Too Many Requests)
```json
{
    "success": false,
    "data": null,
    "message": "Rate limit exceeded",
    "errors": [
        {
            "field": "rate_limit",
            "message": "Too many requests. Please try again later.",
            "code": "rate_limit_exceeded"
        }
    ],
    "meta": {
        "retry_after": 60,
        "limit": 100,
        "remaining": 0
    }
}
```

## SDKs and Code Examples

### Python SDK Example
```python
from flexifinance import FlexiFinanceAPI

# Initialize client
client = FlexiFinanceAPI(
    base_url='https://api.flexifinance.com/v1/',
    access_token='your_access_token'
)

# Register user
user_data = {
    'email': 'user@example.com',
    'password': 'SecurePass123!',
    'first_name': 'John',
    'last_name': 'Doe',
    'phone_number': '+254700123456'
}
user = client.users.register(user_data)

# Apply for loan
loan_data = {
    'product_id': 'quick_cash',
    'requested_amount': 10000,
    'requested_tenure': 3,
    'purpose': 'Business expansion'
}
loan = client.loans.apply(loan_data)

# Make payment
payment_data = {
    'loan_id': loan.loan_id,
    'amount': 3358,
    'phone_number': '+254700123456'
}
payment = client.payments.stk_push(payment_data)
```

### JavaScript SDK Example
```javascript
import { FlexiFinanceAPI } from '@flexifinance/sdk';

// Initialize client
const client = new FlexiFinanceAPI({
    baseURL: 'https://api.flexifinance.com/v1/',
    accessToken: 'your_access_token'
});

// Register user
const userData = {
    email: 'user@example.com',
    password: 'SecurePass123!',
    first_name: 'John',
    last_name: 'Doe',
    phone_number: '+254700123456'
};

const user = await client.users.register(userData);

// Apply for loan
const loanData = {
    product_id: 'quick_cash',
    requested_amount: 10000,
    requested_tenure: 3,
    purpose: 'Business expansion'
};

const loan = await client.loans.apply(loanData);
```

### cURL Examples

#### User Registration
```bash
curl -X POST https://api.flexifinance.com/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+254700123456"
  }'
```

#### User Login
```bash
curl -X POST https://api.flexifinance.com/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'
```

#### Get User Profile
```bash
curl -X GET https://api.flexifinance.com/v1/users/profile/ \
  -H "Authorization: Bearer <jwt_token>" \
  -H "Accept: application/json"
```

#### Apply for Loan
```bash
curl -X POST https://api.flexifinance.com/v1/loans/apply/ \
  -H "Authorization: Bearer <jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "quick_cash",
    "requested_amount": 10000,
    "requested_tenure": 3,
    "purpose": "Business expansion"
  }'
```

#### Initiate STK Push
```bash
curl -X POST https://api.flexifinance.com/v1/payments/stk-push/ \
  -H "Authorization: Bearer <jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "loan_id": "loan_uuid",
    "amount": 3358,
    "phone_number": "+254700123456",
    "payment_type": "REPAYMENT"
  }'
```

## Testing

### Sandbox Environment
Use the sandbox environment for testing:
- **Base URL:** https://api-staging.flexifinance.com/v1/
- **Test Data:** Use provided test accounts
- **M-Pesa Integration:** Sandbox M-Pesa API

### Test Accounts
```
Test User Account:
Email: test@flexifinance.com
Password: TestPass123!
Phone: +254700123456

Admin Account:
Email: admin@flexifinance.com
Password: AdminPass123!
Role: Loan Officer
```

### Testing Webhooks
Use webhook testing services like:
- ngrok for local development
- webhook.site for testing webhooks
- Postman for API testing

## Support and Contact

### API Support
- **Email:** api-support@flexifinance.com
- **Documentation:** https://docs.flexifinance.com
- **Status Page:** https://status.flexifinance.com

### SDK Support
- **GitHub:** https://github.com/flexifinance/sdks
- **Issues:** Report bugs and feature requests
- **Discussions:** Community support forum

---

**Version History:**
- v1.0.0 - Initial API release (December 5, 2025)
- All endpoints are currently in stable version
- Backward compatibility guaranteed for minor versions

**API Versioning:**
- Major version in URL path (v1)
- Minor version changes in response format
- Deprecation notices provided 6 months in advance