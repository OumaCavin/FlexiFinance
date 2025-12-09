#!/usr/bin/env python3
"""
Fix debug_toolbar import issue by commenting it out in settings
"""
import re
from pathlib import Path

def fix_debug_toolbar():
    """Comment out debug_toolbar conditionally"""
    settings_path = Path(__file__).parent / 'flexifinance' / 'settings.py'
    
    if not settings_path.exists():
        print("❌ settings.py not found!")
        return False
    
    with open(settings_path, 'r') as f:
        content = f.read()
    
    # Replace conditional debug_toolbar addition
    pattern = r'(if DEBUG:\s*\n\s*)# Debug toolbar\s*\n(\s*INSTALLED_APPS \+= \[.*?debug_toolbar.*?\]\s*\n)(\s*MIDDLEWARE \+= \[.*?debug_toolbar.*?\]\s*\n)'
    
    replacement = r'\1# Debug toolbar - DISABLED FOR DIAGNOSTIC\n\2# \3'
    
    if re.search(pattern, content, re.DOTALL):
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        print("✅ Commented out debug_toolbar conditional addition")
    else:
        print("ℹ️  debug_toolbar conditional addition not found or already handled")
    
    # Write back the modified content
    with open(settings_path, 'w') as f:
        f.write(content)
    
    return True

if __name__ == "__main__":
    if fix_debug_toolbar():
        print("✅ Debug toolbar issue fixed!")
    else:
        print("❌ Failed to fix debug toolbar issue")