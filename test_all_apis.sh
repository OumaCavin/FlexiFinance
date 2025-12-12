#!/bin/bash
# FlexiFinance API Testing Commands
# =================================
# Comprehensive curl commands to test all submission areas in your FlexiFinance application
# 
# Usage: source this file or copy individual commands
# Author: OumaCavin
# Date: 2025-12-12

echo "🚀 FlexiFinance API Testing Commands"
echo "=================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Base URL
BASE_URL="http://127.0.0.1:8000"

echo -e "${YELLOW}📡 Base URL: $BASE_URL${NC}"
echo ""

# 1. CONTACT FORM SUBMISSION
echo -e "${GREEN}1. CONTACT FORM SUBMISSION${NC}"
echo "Testing: /api/contact/submit/"
echo "--------------------------------"
curl -X POST $BASE_URL/api/contact/submit/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john.doe@example.com", 
    "phone": "+254700123456",
    "subject": "Test Loan Inquiry",
    "message": "I would like to apply for a personal loan of KES 50,000."
  }'
echo ""
echo ""

# 2. NEWSLETTER SUBSCRIPTION  
echo -e "${GREEN}2. NEWSLETTER SUBSCRIPTION${NC}"
echo "Testing: /newsletter/subscribe/"
echo "--------------------------------"
curl -X POST $BASE_URL/newsletter/subscribe/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "subscriber@example.com"
  }'
echo ""
echo ""

# 3. LOAN APPLICATION SUBMISSION
echo -e "${GREEN}3. LOAN APPLICATION SUBMISSION${NC}"
echo "Testing: /loan-application/ (POST)"
echo "-----------------------------------"
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
echo ""
echo ""

# 4. HEALTH CHECK (GET)
echo -e "${GREEN}4. HEALTH CHECK${NC}"
echo "Testing: /api/health/"
echo "----------------------"
curl -X GET $BASE_URL/api/health/ \
  -H "Accept: application/json"
echo ""
echo ""

# 5. PUBLIC CONFIG (GET)
echo -e "${GREEN}5. PUBLIC CONFIG${NC}"
echo "Testing: /api/config/"
echo "----------------------"
curl -X GET $BASE_URL/api/config/ \
  -H "Accept: application/json"
echo ""
echo ""

# 6. INVALID CONTACT FORM (Error Testing)
echo -e "${GREEN}6. INVALID CONTACT FORM (Error Testing)${NC}"
echo "Testing: /api/contact/submit/ (with invalid data)"
echo "-------------------------------------------------"
curl -X POST $BASE_URL/api/contact/submit/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "",
    "email": "invalid-email",
    "message": ""
  }'
echo ""
echo ""

# 7. INVALID NEWSLETTER (Error Testing)
echo -e "${GREEN}7. INVALID NEWSLETTER (Error Testing)${NC}"
echo "Testing: /newsletter/subscribe/ (with invalid email)"
echo "----------------------------------------------------"
curl -X POST $BASE_URL/newsletter/subscribe/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "invalid-email-format"
  }'
echo ""
echo ""

# 8. LOAN APPLICATION WITH EMERGENCY PURPOSE
echo -e "${GREEN}8. LOAN APPLICATION - EMERGENCY LOAN${NC}"
echo "Testing: /loan-application/ (Emergency purpose)"
echo "-----------------------------------------------"
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
echo ""
echo ""

# 9. LOAN APPLICATION - QUICK CASH (Amount based)
echo -e "${GREEN}9. LOAN APPLICATION - QUICK CASH${NC}"
echo "Testing: /loan-application/ (Small amount = Quick Cash)"
echo "-------------------------------------------------------"
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
echo ""
echo ""

# 10. TESTING INVALID LOAN APPLICATION (Missing fields)
echo -e "${GREEN}10. INVALID LOAN APPLICATION (Error Testing)${NC}"
echo "Testing: /loan-application/ (missing required fields)"
echo "-----------------------------------------------------"
curl -X POST $BASE_URL/loan-application/ \
  -H "Content-Type: application/json" \
  -H "X-Requested-With: XMLHttpRequest" \
  -d '{
    "first_name": "Test",
    "email": "test@example.com"
  }'
echo ""
echo ""

# Summary
echo -e "${YELLOW}📋 TESTING SUMMARY${NC}"
echo "====================="
echo "✅ Contact Form: Tests database storage and email notifications"
echo "✅ Newsletter: Tests subscription functionality"  
echo "✅ Loan Applications: Tests user creation and loan type determination"
echo "✅ Health Check: Tests system status"
echo "✅ Config: Tests public configuration endpoint"
echo "✅ Error Testing: Tests validation and error handling"
echo ""
echo -e "${GREEN}🎯 EXPECTED RESULTS:${NC}"
echo "- Successful submissions return: {\"success\": true, ...}"
echo "- Invalid data returns: {\"success\": false, \"error\": ...}"
echo "- Health check returns system status"
echo "- Loan applications create users and determine loan types automatically"
echo ""
echo -e "${YELLOW}💡 NOTES:${NC}"
echo "- All POST endpoints now work without CSRF tokens (@csrf_exempt applied)"
echo "- Loan types are determined by amount and purpose keywords"
echo "- Contact forms generate unique reference IDs for tracking"
echo "- Newsletter subscriptions validate email format"
echo ""
echo "🔧 If any tests fail, check:"
echo "1. Django server is running: python manage.py runserver"
echo "2. Database is accessible and migrations are applied"
echo "3. Email service configuration is valid"
echo "4. No syntax errors in the curl commands"