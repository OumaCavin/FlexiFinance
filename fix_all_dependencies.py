#!/usr/bin/env python3
"""
Comprehensive fix for dependency issues in settings.py
"""
import re
from pathlib import Path

def fix_settings_dependencies():
    """Fix all problematic dependencies in settings.py"""
    settings_path = Path(__file__).parent / 'flexifinance' / 'settings.py'
    
    if not settings_path.exists():
        print("❌ settings.py not found!")
        return False
    
    with open(settings_path, 'r') as f:
        content = f.read()
    
    # List of problematic apps to comment out temporarily
    problematic_apps = [
        'celery',
        'import_export',
    ]
    
    changes_made = False
    
    for app in problematic_apps:
        # Check if app is already commented out
        if f"# '{app}'," in content:
            print(f"✅ {app} already commented out")
            continue
            
        # Check if app is active and needs to be commented out
        if f"'{app}'," in content:
            pattern = rf"(\s*)'{app}',"
            replacement = rf"\1# '{app}',  # Temporarily disabled for diagnostic"
            content = re.sub(pattern, replacement, content)
            print(f"✅ Temporarily disabled {app} in settings.py")
            changes_made = True
        else:
            print(f"ℹ️  {app} not found in THIRD_PARTY_APPS")
    
    # Write back the modified content
    if changes_made:
        with open(settings_path, 'w') as f:
            f.write(content)
        print("✅ Settings updated successfully")
    else:
        print("ℹ️  No changes needed")
    
    return True

if __name__ == "__main__":
    if fix_settings_dependencies():
        print("\nSettings fixed. You can now run diagnostic scripts.")
        print("After running diagnostics, you may need to:")
        print("1. Install missing dependencies")
        print("2. Re-enable the apps in settings.py")
    else:
        print("Failed to update settings.")