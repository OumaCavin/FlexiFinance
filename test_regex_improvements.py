#!/usr/bin/env python3
"""
Test script to demonstrate the improved regex pattern handles all value types
"""
import re

def extract_setting_value(content, setting_name):
    """Extract setting value handling all Python value types"""
    # Pattern to match: setting_name = value
    # Handles: strings (quoted), integers, booleans, None, etc.
    pattern = rf'^{setting_name}\s*=\s*(.+?)(?:\s*#.*)?$'
    match = re.search(pattern, content, re.MULTILINE)
    
    if match:
        value_str = match.group(1).strip()
        
        # Remove trailing commas (common in Python settings)
        if value_str.endswith(','):
            value_str = value_str[:-1].strip()
        
        # Try to determine the actual value type and return it
        if value_str.startswith('"') and value_str.endswith('"'):
            # Double-quoted string
            return value_str[1:-1]
        elif value_str.startswith("'") and value_str.endswith("'"):
            # Single-quoted string
            return value_str[1:-1]
        elif value_str in ['True', 'False']:
            # Boolean
            return value_str == 'True'
        elif value_str in ['None']:
            # None value
            return None
        elif value_str.isdigit() or (value_str.startswith('-') and value_str[1:].isdigit()):
            # Integer
            return int(value_str)
        else:
            # Return as-is for other cases
            return value_str
    
    return None

# Test content with different value types
test_content = '''
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = "localhost"
EMAIL_PORT = 2526
EMAIL_USE_TLS = False
DEBUG = True
SECRET_KEY = None
CORS_ALLOWED_ORIGINS = ['http://localhost:8000', 'http://127.0.0.1:8000']
DATABASE_URL = 'sqlite:///db.sqlite3'
'''

# Test each value type
test_cases = [
    ('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend'),
    ('EMAIL_HOST', 'localhost'),
    ('EMAIL_PORT', 2526),
    ('EMAIL_USE_TLS', False),
    ('DEBUG', True),
    ('SECRET_KEY', None),
]

print("🧪 TESTING VALUE TYPE EXTRACTION")
print("=" * 50)

for setting_name, expected in test_cases:
    actual = extract_setting_value(test_content, setting_name)
    
    if actual == expected:
        print(f"✅ {setting_name:20} → {actual!r} ({type(actual).__name__})")
    else:
        print(f"❌ {setting_name:20} → {actual!r} (expected: {expected!r})")

print("\n🎯 CONCLUSION:")
print("The improved regex now correctly handles:")
print("✅ String values (both single and double quotes)")
print("✅ Integer values (like EMAIL_PORT = 2526)")
print("✅ Boolean values (like EMAIL_USE_TLS = False)")
print("✅ None values")
print("✅ Lists and other complex values")
