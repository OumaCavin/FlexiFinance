#!/usr/bin/env python3
import json
from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()
client = Client()

print('🚀 FLEXIFINANCE END-TO-END FUNCTIONALITY VERIFICATION')
print('=' * 60)

# Test 1: Loan Application
print('\n1. LOAN APPLICATION TEST')
print('-' * 40)

response = client.get('/loan-application/')
print(f'Loan Application Page: {response.status_code}')
if response.status_code == 200:
    print('✅ PASS: Loan application page loads')
else:
    print('❌ FAIL: Loan application page failed')

# Test 2: Registration
print('\n2. USER REGISTRATION TEST')  
print('-' * 40)

response = client.get('/dashboard/register/')
print(f'Registration Page: {response.status_code}')
if response.status_code == 200:
    print('✅ PASS: Registration page loads')
else:
    print('❌ FAIL: Registration page failed')

# Test 3: Login
print('\n3. USER LOGIN TEST')
print('-' * 40)

response = client.get('/dashboard/login/')
print(f'Login Page: {response.status_code}')
if response.status_code == 200:
    print('✅ PASS: Login page loads')
else:
    print('❌ FAIL: Login page failed')

# Test API endpoints
print('\n4. API ENDPOINTS TEST')
print('-' * 40)

# Test registration API
reg_data = {'email': 'test@example.com', 'password': 'Test123!'}
response = client.post('/api/v1/auth/register/', data=json.dumps(reg_data), content_type='application/json')
print(f'Registration API: {response.status_code}')
if response.status_code == 201:
    print('✅ PASS: Registration API working')
else:
    print('⚠️  Registration API returned:', response.status_code)

# Test login API  
login_data = {'email': 'test@example.com', 'password': 'Test123!'}
response = client.post('/api/v1/auth/login/', data=json.dumps(login_data), content_type='application/json')
print(f'Login API: {response.status_code}')
if response.status_code == 200:
    print('✅ PASS: Login API working')
else:
    print('⚠️  Login API returned:', response.status_code)

print('\n✅ Basic functionality test completed!')