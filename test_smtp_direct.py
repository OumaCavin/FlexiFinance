#!/usr/bin/env python3
"""
Direct SMTP server test
"""

import socket
import time

def test_smtp_server():
    """Test SMTP server directly"""
    print("🔧 Testing SMTP Server Directly")
    print("=" * 50)
    
    try:
        # Connect to SMTP server
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect(('localhost', 1026))
        
        # Receive greeting
        greeting = sock.recv(1024).decode('utf-8', errors='ignore')
        print(f"📨 Server greeting: {greeting.strip()}")
        
        # Send EHLO command
        sock.send(b"EHLO localhost\r\n")
        response = sock.recv(1024).decode('utf-8', errors='ignore')
        print(f"📨 EHLO response: {response.strip()}")
        
        # Send MAIL FROM command
        sock.send(b"MAIL FROM:<test@flexifinance.com>\r\n")
        response = sock.recv(1024).decode('utf-8', errors='ignore')
        print(f"📨 MAIL FROM response: {response.strip()}")
        
        # Send RCPT TO command
        sock.send(b"RCPT TO:<recipient@flexifinance.com>\r\n")
        response = sock.recv(1024).decode('utf-8', errors='ignore')
        print(f"📨 RCPT TO response: {response.strip()}")
        
        # Send DATA command
        sock.send(b"DATA\r\n")
        response = sock.recv(1024).decode('utf-8', errors='ignore')
        print(f"📨 DATA response: {response.strip()}")
        
        # Send email content
        email_content = """Subject: Test Email from Direct Connection
From: test@flexifinance.com
To: recipient@flexifinance.com

This is a test email sent directly to the SMTP server.
"""
        sock.send(email_content.encode('utf-8'))
        sock.send(b"\r\n.\r\n")  # End of email
        response = sock.recv(1024).decode('utf-8', errors='ignore')
        print(f"📨 Email content response: {response.strip()}")
        
        # Quit
        sock.send(b"QUIT\r\n")
        response = sock.recv(1024).decode('utf-8', errors='ignore')
        print(f"📨 QUIT response: {response.strip()}")
        
        sock.close()
        print("✅ Direct SMTP test completed successfully!")
        
    except Exception as e:
        print(f"❌ Direct SMTP test failed: {e}")

if __name__ == "__main__":
    test_smtp_server()
    time.sleep(1)  # Give server time to process
    print("\n📄 Checking for log files...")
    import os
    log_files = [f for f in os.listdir('.') if f.endswith('.log')]
    if log_files:
        print(f"📋 Log files found: {log_files}")
    else:
        print("📋 No log files found")