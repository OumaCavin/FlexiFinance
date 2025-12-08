#!/usr/bin/env python3
"""
Enhanced SMTP server with detailed logging for testing
"""

import socket
import threading
import time
import sys
import signal
from datetime import datetime

class TestSMTPServer:
    def __init__(self, host='localhost', port=2526):
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False
        self.emails_received = []
        
    def log(self, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {message}")
        sys.stdout.flush()
        
    def handle_client(self, client_socket, client_address):
        self.log(f"📧 New SMTP connection from {client_address}")
        
        try:
            # Send greeting
            client_socket.send(b"220 Test SMTP Server Ready\r\n")
            
            # SMTP command handling
            mail_from = None
            rcpt_to = []
            data_mode = False
            email_content = []
            
            while True:
                try:
                    data = client_socket.recv(1024)
                    if not data:
                        break
                        
                    command = data.decode('utf-8', errors='ignore').strip()
                    self.log(f"📨 Received: {command[:100]}...")
                    
                    if command.upper().startswith('EHLO') or command.upper().startswith('HELO'):
                        client_socket.send(b"250-Test SMTP Server\r\n250-SIZE 35882577\r\n250 HELP\r\n")
                        
                    elif command.upper().startswith('MAIL FROM:'):
                        mail_from = command[10:].strip().strip('<>')
                        self.log(f"📧 MAIL FROM: {mail_from}")
                        client_socket.send(b"250 OK\r\n")
                        
                    elif command.upper().startswith('RCPT TO:'):
                        rcpt = command[8:].strip().strip('<>')
                        rcpt_to.append(rcpt)
                        self.log(f"📧 RCPT TO: {rcpt}")
                        client_socket.send(b"250 OK\r\n")
                        
                    elif command.upper() == 'DATA':
                        self.log("📧 Entering DATA mode")
                        client_socket.send(b"354 Start mail input; end with <CRLF>.<CRLF>\r\n")
                        data_mode = True
                        
                    elif command.upper() == 'QUIT':
                        self.log("📧 QUIT command received")
                        client_socket.send(b"221 Bye\r\n")
                        break
                        
                    elif data_mode:
                        if command == '.':
                            # End of email data
                            email_data = {
                                'from': mail_from,
                                'to': rcpt_to,
                                'content': '\n'.join(email_content),
                                'timestamp': datetime.now()
                            }
                            self.emails_received.append(email_data)
                            self.log(f"📧 Email received and stored! Total emails: {len(self.emails_received)}")
                            self.log(f"📧 From: {mail_from}")
                            self.log(f"📧 To: {rcpt_to}")
                            self.log(f"📧 Content preview: {email_data['content'][:100]}...")
                            client_socket.send(b"250 OK\r\n")
                            data_mode = False
                            email_content = []
                        else:
                            email_content.append(command)
                            
                    else:
                        client_socket.send(b"502 Command not implemented\r\n")
                        
                except Exception as e:
                    self.log(f"❌ Error handling command: {e}")
                    break
                    
        except Exception as e:
            self.log(f"❌ Client handling error: {e}")
        finally:
            client_socket.close()
            self.log(f"📧 Connection closed for {client_address}")
    
    def start_server(self):
        self.log(f"🚀 Starting Test SMTP Server on {self.host}:{self.port}")
        
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True
            
            self.log(f"✅ SMTP Server listening on {self.host}:{self.port}")
            
            while self.running:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, client_address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                except socket.error as e:
                    if self.running:
                        self.log(f"❌ Socket error: {e}")
                    break
                    
        except Exception as e:
            self.log(f"❌ Server error: {e}")
        finally:
            self.stop_server()
    
    def stop_server(self):
        self.running = False
        if self.server_socket:
            self.server_socket.close()
            self.log("🛑 SMTP Server stopped")
    
    def get_emails(self):
        return self.emails_received

def signal_handler(signum, frame):
    print("\n🛑 Shutting down SMTP server...")
    server.stop_server()
    sys.exit(0)

if __name__ == "__main__":
    server = TestSMTPServer(host='localhost', port=2526)
    
    # Register signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        server.start_server()
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
        server.stop_server()