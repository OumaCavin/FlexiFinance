#!/bin/bash
# Quick verification that loan application CSRF fix is working
# ============================================================

echo "🔧 Testing Loan Application Fix"
echo "================================="
echo ""

BASE_URL="http://127.0.0.1:8000"

echo "🧪 Testing Business Loan Application..."
curl -X POST $BASE_URL/loan-application/ \
  -H "Content-Type: application/json" \
  -H "X-Requested-With: XMLHttpRequest" \
  -d '{"first_name":"Test","last_name":"User","email":"test@example.com","phone":"+254700123456","loan_amount":"75000","loan_purpose":"business expansion","loan_tenure":"12","monthly_income":"150000","employer_name":"Test Corp"}'

echo ""
echo ""
echo "Expected: Success response with loan data (no 403 error)"
echo "If you still see 403, restart Django server to load the changes"