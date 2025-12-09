#!/usr/bin/env python3
"""
Quick Mailpit Starter Script for FlexiFinance
This script checks if Mailpit is running and starts it if needed
"""
import subprocess
import time
import os
import sys

def check_mailpit_running():
    """Check if Mailpit is already running"""
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        return 'mailpit' in result.stdout.lower()
    except Exception:
        return False

def start_mailpit():
    """Start Mailpit SMTP server"""
    print("🚀 Starting Mailpit SMTP server...")
    print("   HTTP UI: http://localhost:8080")
    print("   SMTP: localhost:2526")
    print("\nPress Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        subprocess.run(['mailpit', '--http', ':8080', '--smtp', ':2526'])
    except FileNotFoundError:
        print("❌ Mailpit not found!")
        print("\nTo install Mailpit:")
        print("  curl -fsSL https://raw.githubusercontent.com/axllent/mailpit/develop/install.sh | sh")
        print("\nOr use the built-in SMTP test server:")
        print("  python smtp_test_server.py")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n✅ Mailpit server stopped")

def start_builtin_smtp_server():
    """Start the built-in SMTP test server"""
    print("🚀 Starting built-in SMTP test server...")
    print("   This simulates Mailpit functionality")
    print("   SMTP: localhost:2526")
    print("\nPress Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        subprocess.run([sys.executable, 'smtp_test_server.py'])
    except KeyboardInterrupt:
        print("\n\n✅ SMTP test server stopped")

def main():
    """Main function"""
    print("📧 FlexiFinance Mailpit Starter")
    print("=" * 40)
    
    if check_mailpit_running():
        print("✅ Mailpit is already running!")
        print("   Access Mailpit UI: http://localhost:8080")
        print("   SMTP Port: 2526")
    else:
        print("❌ Mailpit is not running")
        print("\nChoose an option:")
        print("1. Start Mailpit (recommended)")
        print("2. Start built-in SMTP test server")
        
        try:
            choice = input("\nEnter choice (1 or 2): ").strip()
            
            if choice == '1':
                start_mailpit()
            elif choice == '2':
                start_builtin_smtp_server()
            else:
                print("Invalid choice. Please run the script again.")
        except KeyboardInterrupt:
            print("\n\nExiting...")

if __name__ == "__main__":
    main()