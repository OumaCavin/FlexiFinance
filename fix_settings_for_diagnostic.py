#!/usr/bin/env python3
"""
Quick fix to temporarily remove Celery dependency for diagnostic purposes
"""
import re
from pathlib import Path

def fix_settings():
    """Remove celery from THIRD_PARTY_APPS temporarily"""
    settings_path = Path(__file__).parent / 'flexifinance' / 'settings.py'
    
    if not settings_path.exists():
        print("❌ settings.py not found!")
        return False
    
    with open(settings_path, 'r') as f:
        content = f.read()
    
    # Remove 'celery' from THIRD_PARTY_APPS
    pattern = r"(\s*)'celery',"
    replacement = r"\1# 'celery',  # Temporarily disabled for diagnostic"
    
    if "'celery'," in content:
        content = re.sub(pattern, replacement, content)
        print("✅ Temporarily disabled Celery in settings.py")
    elif "# 'celery'," in content:
        print("✅ Celery already commented out")
    else:
        print("ℹ️  Celery not found in THIRD_PARTY_APPS")
    
    # Write back the modified content
    with open(settings_path, 'w') as f:
        f.write(content)
    
    return True

if __name__ == "__main__":
    if fix_settings():
        print("Settings updated. You can now run diagnostic scripts.")
    else:
        print("Failed to update settings.")