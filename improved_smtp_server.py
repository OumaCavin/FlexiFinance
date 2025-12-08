#!/usr/bin/env python3
"""
Improved Simple SMTP Test Server - Simulates Mailpit functionality
Uses socket programming to create a basic SMTP server on localhost:1025
"""

import socket
import threading
import email
import email.utils
from datetime import datetime
import re
import sys

class ImprovedSMTPServer:
    def __init__(self, host='localhost', port=2525):
        self.host = host
        self.port = port
        self.emails = []
        self.running = False
        self.server_socket = None
        
    def log_email(self, from_addr, to_addrs, subject, body):
        """Log email to console and file"""
        email_record = {
            'timestamp': datetime.now().isoformat(),
            'from': from_addr,
            'to': ', '.join(to_addrs),
            'subject': subject,
            'body': body
        }
        
        self.emails.append(email_record)
        
        # Print to console
        print(f"\n📨 EMAIL RECEIVED at {email_record['timestamp']}")
        print(f"From: {from_addr}")
        print(f"To: {', '.join(to_addrs)}")
        print(f"Subject: {subject}")
        print(f"Body Preview: {body[:200]}...")
        print("-" * 60)
        
        # Save to log file
        try:
            with open('smtp_emails.log', 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*60}\n")
                f.write(f"EMAIL RECEIVED: {email_record['timestamp']}\n")
                f.write(f"From: {from_addr}\n")
                f.write(f"To: {', '.join(to_addrs)}\n")
                f.write(f"Subject: {subject}\n")
                f.write(f"\nBody:\n{body}\n")
                f.write(f"{'='*60}\n")
        except Exception as e:
            print(f"Error logging email: {e}")
    
    def handle_client(self, client_socket, address):
        """Handle individual client connection"""
        try:
            print(f"🔗 New connection from {address}")
            
            # Send greeting
            client_socket.send(b"220 Simple SMTP Server Ready\r\n")
            
            # Initialize variables for email collection
            from_addr = ""
            to_addrs = []
            subject = ""
            body_lines = []
            in_data_mode = False
            
            while True:
                # Receive data
                data = client_socket.recv(1024).decode('utf-8', errors='ignore')
                if not data:
                    break
                
                print(f"📨 Received: {data.strip()}")
                
                # Parse SMTP commands
                if data.startswith("EHLO") or data.startswith("HELO"):
                    client_socket.send(b"250-Hello\r\n250 AUTH PLAIN\r\n")
                    
                elif data.startswith("MAIL FROM:"):
                    from_match = re.search(r'<([^>]+)>', data)
                    if from_match:
                        from_addr = from_match.group(1)
                    client_socket.send(b"250 OK\r\n")
                    
                elif data.startswith("RCPT TO:"):
                    to_match = re.search(r'<([^>]+)>', data)
                    if to_match:
                        to_addrs.append(to_match.group(1))
                    client_socket.send(b"250 OK\r\n")
                    
                elif data.startswith("DATA"):
                    client_socket.send(b"354 Start mail input; end with <CRLF>.<CRLF>\r\n")
                    in_data_mode = True
                    
                elif in_data_mode and data.strip() == ".":
                    # End of email data
                    in_data_mode = False
                    body = "\n".join(body_lines)
                    
                    # Parse subject from headers
                    if body:
                        try:
                            msg = email.message_from_string(body)
                            subject = msg.get('Subject', 'No Subject')
                        except:
                            subject = 'No Subject'
                    
                    # Log the email
                    if from_addr and to_addrs:
                        self.log_email(from_addr, to_addrs, subject, body)
                    
                    client_socket.send(b"250 Message accepted\r\n")
                    
                elif in_data_mode:
                    # Collect email body
                    body_lines.append(data.rstrip())
                    
                elif data.startswith("QUIT"):
                    client_socket.send(b"221 Bye\r\n")
                    break
                    
                else:
                    client_socket.send(b"250 OK\r\n")
                    
        except Exception as e:
            print(f"❌ Error handling client: {e}")
            try:
                client_socket.send(b"500 Error\r\n")
            except:
                pass
        finally:
            client_socket.close()
            print(f"🔗 Connection closed from {address}")
    
    def start(self):
        """Start the SMTP server"""
        try:
            # Create socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            
            self.running = True
            print(f"🚀 Improved SMTP Server started on {self.host}:{self.port}")
            print(f"📧 All emails will be logged to: smtp_emails.log")
            print("=" * 60)
            
            while self.running:
                try:
                    # Accept client connection
                    client_socket, address = self.server_socket.accept()
                    
                    # Handle client in separate thread
                    client_thread = threading.Thread(
                        target=self.handle_client, 
                        args=(client_socket, address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                except socket.error as e:
                    if self.running:
                        print(f"Socket error: {e}")
                    break
                    
        except Exception as e:
            print(f"❌ Error starting SMTP server: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if self.server_socket:
                self.server_socket.close()
    
    def stop(self):
        """Stop the SMTP server"""
        self.running = False
        print("🛑 SMTP Server stopped")

def main():
    """Main function to start the server"""
    print("Starting Improved SMTP Test Server...")
    print("This server simulates Mailpit functionality")
    print("It will listen on localhost:1025 and log all emails")
    
    server = ImprovedSMTPServer()
    
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n🛑 Stopping SMTP Server...")
        server.stop()

if __name__ == "__main__":
    main()