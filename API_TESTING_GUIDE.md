# FlexiFinance API Testing Commands

Complete curl commands to test all submission areas in your FlexiFinance application.

## 📡 Base URL
```bash
BASE_URL="http://127.0.0.1:8000"
```

---

## 📨 1. Contact Form Submission

**Endpoint**: `/api/contact/submit/`  
**Method**: POST  
**Purpose**: Test contact form with full details

```bash
curl -X POST $BASE_URL/api/contact/submit/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john.doe@example.com", 
    "phone": "+254700123456",
    "subject": "Test Loan Inquiry",
    "message": "I would like to apply for a personal loan of KES 50,000."
  }'
```

**Expected Response**:
```json
{
  "success": true,
  "message": "Thank you for your message. We will get back to you within 24 hours.",
  "data": {
    "submitted_at": "2025-12-12T13:21:44.986566",
    "reference_id": "CF-1765534905"
  }
}
```

---

## 📰 2. Newsletter Subscription

**Endpoint**: `/newsletter/subscribe/`  
**Method**: POST  
**Purpose**: Test newsletter signup

```bash
curl -X POST $BASE_URL/newsletter/subscribe/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "subscriber@example.com"
  }'
```

**Expected Response**:
```json
{
  "success": true,
  "message": "Thank you for subscribing to our newsletter!",
  "data": {
    "subscribed_at": "2025-12-12T13:21:44.986566"
  }
}
```

---

## 💰 3. Loan Application Submission

**Endpoint**: `/loan-application/`  
**Method**: POST  
**Purpose**: Test complete loan application

> **✅ UPDATE**: CSRF protection has been removed from loan applications (2025-12-12). All loan types now work via API.

### 3a. Business Loan Application (✅ NOW WORKING)
```bash
curl -X POST $BASE_URL/loan-application/ \
  -H "Content-Type: application/json" \
  -H "X-Requested-With: XMLHttpRequest" \
  -d '{
    "first_name": "Jane",
    "last_name": "Smith", 
    "email": "jane.smith@example.com",
    "phone": "+254700654321",
    "loan_amount": "75000",
    "loan_purpose": "business expansion",
    "loan_tenure": "12",
    "monthly_income": "150000",
    "employer_name": "ABC Company Ltd",
    "id_number": "12345678"
  }'
```

**Expected Success Response**:
```json
{
  "success": true,
  "message": "Your loan application has been submitted successfully!",
  "data": {
    "loan_reference": "LN-20241212134423",
    "loan_type": "Business",
    "principal_amount": "75000.00",
    "interest_rate": "12.50",
    "loan_tenure": 12,
    "total_amount": "88750.00",
    "monthly_payment": "7395.83",
    "status": "Submitted",
    "application_date": "2025-12-12T13:44:23.531176",
  },
  "redirect_url": "/dashboard/applications/1/"
}
```

### 3b. Emergency Loan Application (✅ NOW WORKING)  
```bash
curl -X POST $BASE_URL/loan-application/ \
  -H "Content-Type: application/json" \
  -H "X-Requested-With: XMLHttpRequest" \
  -d '{
    "first_name": "Mike",
    "last_name": "Johnson",
    "email": "mike.johnson@example.com", 
    "phone": "+254700987654",
    "loan_amount": "25000",
    "loan_purpose": "emergency medical bills",
    "loan_tenure": "6",
    "monthly_income": "80000",
    "employer_name": "XYZ Corp"
  }'
```

**Expected Success Response**: Similar format with `"loan_type": "Emergency"`

### 3c. Quick Cash Loan (Amount ≤ 50,000) (✅ NOW WORKING)
```bash
curl -X POST $BASE_URL/loan-application/ \
  -H "Content-Type: application/json" \
  -H "X-Requested-With: XMLHttpRequest" \
  -d '{
    "first_name": "Sarah",
    "last_name": "Wilson",
    "email": "sarah.wilson@example.com",
    "phone": "+254700555666", 
    "loan_amount": "15000",
    "loan_purpose": "personal expenses",
    "loan_tenure": "3",
    "monthly_income": "60000"
  }'
```

**Expected Success Response**: Similar format with `"loan_type": "Quick Cash"`

---

## 🔍 4. System Health Check

**Endpoint**: `/api/health/`  
**Method**: GET  
**Purpose**: Check system status

```bash
curl -X GET $BASE_URL/api/health/ \
  -H "Accept: application/json"
```

**Expected Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-12T13:21:44.986566",
  "services": {
    "database": "connected",
    "email": "connected"
  },
  "version": "1.0.0",
  "environment": "development"
}
```

---

## ⚙️ 5. Public Configuration

**Endpoint**: `/api/config/`  
**Method**: GET  
**Purpose**: Get public settings

```bash
curl -X GET $BASE_URL/api/config/ \
  -H "Accept: application/json"
```

---

## ❌ 6. Error Testing Commands

### 6a. Invalid Contact Form
```bash
curl -X POST $BASE_URL/api/contact/submit/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "",
    "email": "invalid-email",
    "message": ""
  }'
```

### 6b. Invalid Newsletter Email
```bash
curl -X POST $BASE_URL/newsletter/subscribe/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "invalid-email-format"
  }'
```

### 6c. Invalid Loan Application
```bash
curl -X POST $BASE_URL/loan-application/ \
  -H "Content-Type: application/json" \
  -H "X-Requested-With: XMLHttpRequest" \
  -d '{
    "first_name": "Test",
    "email": "test@example.com"
  }'
```

---

## 🎯 Loan Type Determination Logic

The system automatically determines loan types based on:

| Amount Range | Purpose Keywords | Loan Type |
|--------------|------------------|-----------|
| ≤ KES 50,000 | Any | QUICK_CASH |
| Any | "business" | BUSINESS |
| Any | "emergency" | EMERGENCY |
| > KES 50,000 | Other | PERSONAL |

---

## 🔧 Troubleshooting

### If tests fail, check:

1. **Django Server**: Is it running?

2. **Loan Application 403 Errors**: If you get 403 Forbidden on loan applications, restart Django server:
   ```bash
   # The @csrf_exempt fix requires server restart to take effect
   python manage.py runserver
   ```

3. **Database**: Are migrations applied?
   ```bash
   python manage.py runserver
   ```

2. **Database**: Are migrations applied?
   ```bash
   python manage.py migrate
   ```

3. **Email Service**: Is Resend API configured?

4. **Dependencies**: Are all packages installed?
   ```bash
   pip install -r requirements.txt
   ```

### Common Issues:

- **403 Forbidden**: CSRF protection active (should be fixed with @csrf_exempt)
- **500 Internal Error**: Check Django logs for details
- **Connection Refused**: Django server not running
- **Database Error**: Run migrations

---

## 📊 Expected Results Summary

| Test | Success Response | Error Response |
|------|------------------|----------------|
| Contact Form | `{"success": true, "reference_id": "CF-..."}` | `{"success": false, "error": "..."}` |
| Newsletter | `{"success": true, "subscribed_at": "..."}` | `{"success": false, "error": "..."}` |
| Loan Application | `{"success": true, "data": {...}}` | `{"success": false, "error": "..."}` |
| Health Check | `{"status": "healthy", ...}` | `{"status": "unhealthy", "error": "..."}` |

---

## 🚀 Quick Test All APIs

Run all tests at once:
```bash
chmod +x test_all_apis.sh
./test_all_apis.sh
```

Or copy individual commands above as needed.

---

*Last Updated: 2025-12-12*  
*Author: OumaCavin*