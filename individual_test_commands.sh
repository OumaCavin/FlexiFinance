#!/bin/bash
# Individual API Test Commands for FlexiFinance
# ==============================================
# Copy and run these commands individually to test specific functionality

echo "🔧 Individual FlexiFinance API Test Commands"
echo "============================================="
echo ""

# Set base URL
BASE_URL="http://127.0.0.1:8000"

echo "📋 Available Test Commands:"
echo ""
echo "1. Contact Form (Full Details):"
echo 'curl -X POST '$BASE_URL'/api/contact/submit/ -H "Content-Type: application/json" -d "{\"name\":\"John Doe\",\"email\":\"john.doe@example.com\",\"phone\":\"+254700123456\",\"subject\":\"Test Loan Inquiry\",\"message\":\"I would like to apply for a personal loan of KES 50,000.\"}"'
echo ""

echo "2. Contact Form (Minimal):"
echo 'curl -X POST '$BASE_URL'/api/contact/submit/ -H "Content-Type: application/json" -d "{\"name\":\"Test User\",\"email\":\"test@example.com\",\"message\":\"Hello from FlexiFinance test\"}"'
echo ""

echo "3. Newsletter Subscription:"
echo 'curl -X POST '$BASE_URL'/newsletter/subscribe/ -H "Content-Type: application/json" -d "{\"email\":\"newsletter@example.com\"}"'
echo ""

echo "4. Business Loan Application:"
echo 'curl -X POST '$BASE_URL'/loan-application/ -H "Content-Type: application/json" -H "X-Requested-With: XMLHttpRequest" -d "{\"first_name\":\"Jane\",\"last_name\":\"Smith\",\"email\":\"jane.smith@example.com\",\"phone\":\"+254700654321\",\"loan_amount\":\"75000\",\"loan_purpose\":\"business expansion\",\"loan_tenure\":\"12\",\"monthly_income\":\"150000\",\"employer_name\":\"ABC Company Ltd\"}"'
echo ""

echo "5. Emergency Loan Application:"
echo 'curl -X POST '$BASE_URL'/loan-application/ -H "Content-Type: application/json" -H "X-Requested-With: XMLHttpRequest" -d "{\"first_name\":\"Mike\",\"last_name\":\"Johnson\",\"email\":\"mike.johnson@example.com\",\"phone\":\"+254700987654\",\"loan_amount\":\"25000\",\"loan_purpose\":\"emergency medical bills\",\"loan_tenure\":\"6\",\"monthly_income\":\"80000\",\"employer_name\":\"XYZ Corp\"}"'
echo ""

echo "6. Quick Cash Loan (≤50,000):"
echo 'curl -X POST '$BASE_URL'/loan-application/ -H "Content-Type: application/json" -H "X-Requested-With: XMLHttpRequest" -d "{\"first_name\":\"Sarah\",\"last_name\":\"Wilson\",\"email\":\"sarah.wilson@example.com\",\"phone\":\"+254700555666\",\"loan_amount\":\"15000\",\"loan_purpose\":\"personal expenses\",\"loan_tenure\":\"3\",\"monthly_income\":\"60000\"}"'
echo ""

echo "7. Health Check:"
echo 'curl -X GET '$BASE_URL'/api/health/ -H "Accept: application/json"'
echo ""

echo "8. Public Config:"
echo 'curl -X GET '$BASE_URL'/api/config/ -H "Accept: application/json"'
echo ""

echo "9. Invalid Contact Form (Error Test):"
echo 'curl -X POST '$BASE_URL'/api/contact/submit/ -H "Content-Type: application/json" -d "{\"name\":\"\",\"email\":\"invalid-email\",\"message\":\"\"}"'
echo ""

echo "10. Invalid Newsletter (Error Test):"
echo 'curl -X POST '$BASE_URL'/newsletter/subscribe/ -H "Content-Type: application/json" -d "{\"email\":\"invalid-email-format\"}"'
echo ""

echo "11. Invalid Loan Application (Error Test):"
echo 'curl -X POST '$BASE_URL'/loan-application/ -H "Content-Type: application/json" -H "X-Requested-With: XMLHttpRequest" -d "{\"first_name\":\"Test\",\"email\":\"test@example.com\"}"'
echo ""

echo "============================================="
echo "💡 Usage Tips:"
echo "- Copy any command above and run in your terminal"
echo "- Replace example.com emails with real test emails"
echo "- All endpoints work without CSRF tokens"
echo "- Expected responses show 'success: true' for valid data"
echo "- Error responses show 'success: false' with error messages"