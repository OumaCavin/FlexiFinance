#!/usr/bin/env python3
"""
Simple SMTP Test Server - Simulates Mailpit functionality
Listens on localhost:1025 and logs all received emails
"""

import smtpd
import asyncore
import email
import email.utils
from datetime import datetime
import json
import os

class CustomSMTPServer(smtpd.SMTPServer):
    def __init__(self, localaddr, remoteaddr):
        super().__init__(localaddr, remoteaddr)
        self.emails = []
        print(f"🚀 SMTP Test Server started on {localaddr}")
        print(f"📧 All emails will be logged to: smtp_emails.log")
        print("=" * 60)
    
    def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
        """Process incoming email messages"""
        try:
            # Parse the email
            msg = email.message_from_string(data.decode('utf-8'))
            
            # Extract email details
            subject = msg.get('Subject', 'No Subject')
            from_addr = msg.get('From', 'Unknown Sender')
            to_addrs = msg.get('To', 'Unknown Recipients')
            date = msg.get('Date', 'No Date')
            
            # Get email body
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        break
            else:
                body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
            
            # Create email record
            email_record = {
                'timestamp': datetime.now().isoformat(),
                'from': from_addr,
                'to': to_addrs,
                'subject': subject,
                'date': date,
                'body': body[:500] + ('...' if len(body) > 500 else ''),  # Truncate long bodies
                'raw_data': data.decode('utf-8', errors='ignore')
            }
            
            self.emails.append(email_record)
            
            # Print to console
            print(f"\n📨 EMAIL RECEIVED at {email_record['timestamp']}")
            print(f"From: {from_addr}")
            print(f"To: {to_addrs}")
            print(f"Subject: {subject}")
            print(f"Date: {date}")
            print(f"Body Preview: {body[:200]}...")
            print("-" * 60)
            
            # Save to log file
            with open('smtp_emails.log', 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*60}\n")
                f.write(f"EMAIL RECEIVED: {email_record['timestamp']}\n")
                f.write(f"From: {from_addr}\n")
                f.write(f"To: {to_addrs}\n")
                f.write(f"Subject: {subject}\n")
                f.write(f"Date: {date}\n")
                f.write(f"\nBody:\n{body}\n")
                f.write(f"{'='*60}\n")
            
            return "250 Message accepted for delivery"
            
        except Exception as e:
            print(f"❌ Error processing email: {e}")
            return "550 Message processing failed"

def main():
    """Start the SMTP test server"""
    print("Starting SMTP Test Server...")
    print("This server simulates Mailpit functionality")
    print("It will listen on localhost:1025 and log all emails")
    
    # Create the SMTP server
    server = CustomSMTPServer(('localhost', 1025), None)
    
    try:
        # Start the asyncore loop
        print("\n✅ SMTP Server is ready to receive emails!")
        print("💡 Django will send emails to this server")
        print("📝 Check smtp_emails.log for all received emails")
        print("\nPress Ctrl+C to stop the server\n")
        asyncore.loop()
    except KeyboardInterrupt:
        print("\n🛑 SMTP Server stopped by user")
        server.close()

if __name__ == "__main__":
    main()