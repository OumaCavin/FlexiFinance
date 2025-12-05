"""
Resend Email Service for FlexiFinance
Handles automated email notifications and communications
"""
import logging
import requests
import json
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


class ResendEmailService:
    """
    Resend Email Service
    Provides email functionality for user notifications and communications
    """
    
    def __init__(self):
        self.api_key = settings.RESEND_API_KEY
        self.from_email = settings.FROM_EMAIL
        self.from_name = settings.FROM_NAME
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        self.base_url = 'https://api.resend.com/emails'
    
    def send_email(self, to_email, subject, html_content, text_content=None, from_email=None, from_name=None):
        """
        Send email using Resend API
        
        Args:
            to_email (str): Recipient email
            subject (str): Email subject
            html_content (str): HTML email content
            text_content (str): Plain text content (optional)
            from_email (str): Sender email (optional)
            from_name (str): Sender name (optional)
            
        Returns:
            dict: Email sending result
        """
        try:
            email_data = {
                'from': f"{from_name or self.from_name} <{from_email or self.from_email}>",
                'to': [to_email],
                'subject': subject,
                'html': html_content
            }
            
            if text_content:
                email_data['text'] = text_content
            
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=email_data
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Email sent successfully: {result['id']}")
                return {
                    'success': True,
                    'email_id': result['id'],
                    'message': 'Email sent successfully'
                }
            else:
                logger.error(f"Email sending failed: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': f'Failed to send email: {response.status_code}'
                }
                
        except Exception as e:
            logger.error(f"Email sending error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_welcome_email(self, user_email, user_name):
        """
        Send welcome email to new users
        
        Args:
            user_email (str): User email
            user_name (str): User name
            
        Returns:
            dict: Email sending result
        """
        try:
            subject = "Welcome to FlexiFinance - Your Financial Journey Begins!"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Welcome to FlexiFinance</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }}
                    .content {{ padding: 30px; background: #f9f9f9; }}
                    .button {{ display: inline-block; padding: 15px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                    .footer {{ padding: 20px; text-align: center; color: #666; font-size: 14px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Welcome to FlexiFinance!</h1>
                        <p>Your trusted financial partner</p>
                    </div>
                    <div class="content">
                        <h2>Hello {user_name},</h2>
                        <p>Thank you for joining FlexiFinance! We're excited to have you as part of our community.</p>
                        <p>With FlexiFinance, you can:</p>
                        <ul>
                            <li>Apply for quick and easy loans</li>
                            <li>Manage your financial profile</li>
                            <li>Make secure payments via M-PESA or cards</li>
                            <li>Track your loan applications and repayments</li>
                            <li>Access 24/7 customer support</li>
                        </ul>
                        <p>Start your financial journey with us today!</p>
                        <a href="#" class="button">Get Started</a>
                    </div>
                    <div class="footer">
                        <p>FlexiFinance - Empowering Financial Freedom</p>
                        <p>Need help? Contact us at support@flexifinance.com</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            text_content = f"""Welcome to FlexiFinance!

Hello {user_name},

Thank you for joining FlexiFinance! We're excited to have you as part of our community.

With FlexiFinance, you can:
- Apply for quick and easy loans
- Manage your financial profile
- Make secure payments via M-PESA or cards
- Track your loan applications and repayments
- Access 24/7 customer support

Start your financial journey with us today!

Best regards,
The FlexiFinance Team

Need help? Contact us at support@flexifinance.com
"""
            
            return self.send_email(user_email, subject, html_content, text_content)
            
        except Exception as e:
            logger.error(f"Welcome email error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_loan_approval_email(self, user_email, user_name, loan_amount, loan_id):
        """
        Send loan approval notification
        
        Args:
            user_email (str): User email
            user_name (str): User name
            loan_amount (str): Approved loan amount
            loan_id (str): Loan ID
            
        Returns:
            dict: Email sending result
        """
        try:
            subject = f"Congratulations! Your FlexiFinance loan #{loan_id} has been approved"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Loan Approved - FlexiFinance</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #28a745 0%, #20c997 100%); color: white; padding: 30px; text-align: center; }}
                    .content {{ padding: 30px; background: #f9f9f9; }}
                    .loan-details {{ background: white; padding: 20px; border-left: 4px solid #28a745; margin: 20px 0; }}
                    .button {{ display: inline-block; padding: 15px 30px; background: #28a745; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                    .footer {{ padding: 20px; text-align: center; color: #666; font-size: 14px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🎉 Loan Approved!</h1>
                        <p>Congratulations on your approved FlexiFinance loan</p>
                    </div>
                    <div class="content">
                        <h2>Hello {user_name},</h2>
                        <p>Great news! Your loan application has been approved.</p>
                        
                        <div class="loan-details">
                            <h3>Loan Details</h3>
                            <p><strong>Loan ID:</strong> #{loan_id}</p>
                            <p><strong>Approved Amount:</strong> KSh {loan_amount}</p>
                            <p><strong>Status:</strong> Approved</p>
                        </div>
                        
                        <p>Your funds will be disbursed to your registered account within 24 hours.</p>
                        <p>Thank you for choosing FlexiFinance for your financial needs!</p>
                        
                        <a href="#" class="button">View Loan Details</a>
                    </div>
                    <div class="footer">
                        <p>FlexiFinance - Your Financial Success Partner</p>
                        <p>Questions? Contact us at support@flexifinance.com</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            return self.send_email(user_email, subject, html_content)
            
        except Exception as e:
            logger.error(f"Loan approval email error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_payment_confirmation_email(self, user_email, user_name, amount, payment_method, transaction_id):
        """
        Send payment confirmation email
        
        Args:
            user_email (str): User email
            user_name (str): User name
            amount (str): Payment amount
            payment_method (str): Payment method used
            transaction_id (str): Transaction ID
            
        Returns:
            dict: Email sending result
        """
        try:
            subject = f"Payment Confirmation - FlexiFinance Transaction #{transaction_id}"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Payment Confirmation - FlexiFinance</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #007bff 0%, #6610f2 100%); color: white; padding: 30px; text-align: center; }}
                    .content {{ padding: 30px; background: #f9f9f9; }}
                    .payment-details {{ background: white; padding: 20px; border-left: 4px solid #007bff; margin: 20px 0; }}
                    .footer {{ padding: 20px; text-align: center; color: #666; font-size: 14px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>💳 Payment Confirmed</h1>
                        <p>Your FlexiFinance payment has been processed</p>
                    </div>
                    <div class="content">
                        <h2>Hello {user_name},</h2>
                        <p>Your payment has been successfully processed.</p>
                        
                        <div class="payment-details">
                            <h3>Payment Details</h3>
                            <p><strong>Transaction ID:</strong> #{transaction_id}</p>
                            <p><strong>Amount:</strong> KSh {amount}</p>
                            <p><strong>Payment Method:</strong> {payment_method}</p>
                            <p><strong>Status:</strong> Completed</p>
                        </div>
                        
                        <p>Thank you for your payment. If you have any questions, please contact our support team.</p>
                    </div>
                    <div class="footer">
                        <p>FlexiFinance - Secure & Reliable Payments</p>
                        <p>Need assistance? Contact us at support@flexifinance.com</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            return self.send_email(user_email, subject, html_content)
            
        except Exception as e:
            logger.error(f"Payment confirmation email error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_contact_form_reply(self, user_email, user_name, subject, message):
        """
        Send reply to contact form submission
        
        Args:
            user_email (str): User email
            user_name (str): User name
            subject (str): Original subject
            message (str): Original message
            
        Returns:
            dict: Email sending result
        """
        try:
            reply_subject = f"Re: {subject}"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Contact Form Reply - FlexiFinance</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #6f42c1 0%, #e83e8c 100%); color: white; padding: 30px; text-align: center; }}
                    .content {{ padding: 30px; background: #f9f9f9; }}
                    .original-message {{ background: white; padding: 20px; border-left: 4px solid #6f42c1; margin: 20px 0; }}
                    .footer {{ padding: 20px; text-align: center; color: #666; font-size: 14px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>📧 We've Received Your Message</h1>
                        <p>Thank you for contacting FlexiFinance</p>
                    </div>
                    <div class="content">
                        <h2>Hello {user_name},</h2>
                        <p>Thank you for reaching out to us. We have received your message and will get back to you shortly.</p>
                        
                        <div class="original-message">
                            <h3>Your Original Message</h3>
                            <p><strong>Subject:</strong> {subject}</p>
                            <p><strong>Message:</strong> {message}</p>
                        </div>
                        
                        <p>Our support team will review your inquiry and respond within 24 hours.</p>
                        <p>For urgent matters, please call our 24/7 hotline at +254 708 101 604.</p>
                    </div>
                    <div class="footer">
                        <p>FlexiFinance - We're Here to Help</p>
                        <p>24/7 Customer Support: support@flexifinance.com | +254 708 101 604</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            return self.send_email(user_email, reply_subject, html_content)
            
        except Exception as e:
            logger.error(f"Contact form reply email error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_password_reset_email(self, user_email, user_name, reset_token):
        """
        Send password reset email
        
        Args:
            user_email (str): User email
            user_name (str): User name
            reset_token (str): Password reset token
            
        Returns:
            dict: Email sending result
        """
        try:
            subject = "Reset Your FlexiFinance Password"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Password Reset - FlexiFinance</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #fd7e14 0%, #dc3545 100%); color: white; padding: 30px; text-align: center; }}
                    .content {{ padding: 30px; background: #f9f9f9; }}
                    .reset-link {{ background: white; padding: 20px; border-left: 4px solid #fd7e14; margin: 20px 0; text-align: center; }}
                    .button {{ display: inline-block; padding: 15px 30px; background: #fd7e14; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                    .footer {{ padding: 20px; text-align: center; color: #666; font-size: 14px; }}
                    .warning {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🔐 Password Reset</h1>
                        <p>Secure your FlexiFinance account</p>
                    </div>
                    <div class="content">
                        <h2>Hello {user_name},</h2>
                        <p>We received a request to reset your FlexiFinance password.</p>
                        
                        <div class="reset-link">
                            <p>Click the button below to reset your password:</p>
                            <a href="#" class="button">Reset Password</a>
                            <p style="font-size: 14px; color: #666; margin-top: 20px;">Or copy this link: https://flexifinance.com/reset-password/{reset_token}</p>
                        </div>
                        
                        <div class="warning">
                            <p><strong>Security Notice:</strong></p>
                            <ul>
                                <li>This link expires in 24 hours</li>
                                <li>If you didn't request this reset, please ignore this email</li>
                                <li>Never share this link with anyone</li>
                            </ul>
                        </div>
                    </div>
                    <div class="footer">
                        <p>FlexiFinance - Your Account Security Matters</p>
                        <p>Questions? Contact us at support@flexifinance.com</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            return self.send_email(user_email, subject, html_content)
            
        except Exception as e:
            logger.error(f"Password reset email error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def health_check(self):
        """
        Check Resend service health
        
        Returns:
            bool: True if service is healthy
        """
        try:
            # Try to send a test email to verify service connectivity
            # In a real implementation, you might ping the API or send a test email
            response = requests.get(
                'https://api.resend.com/domains',
                headers=self.headers
            )
            return response.status_code in [200, 401]  # 401 is okay (invalid API key but service reachable)
        except Exception as e:
            logger.error(f"Resend health check failed: {e}")
            return False
    
    def send_contact_notification(self, contact_data):
        """
        Send notification email to support team about new contact form submission
        
        Args:
            contact_data (dict): Contact form data
            
        Returns:
            dict: Email sending result
        """
        try:
            subject = f"New Contact Form Submission - {contact_data.get('subject', 'General Inquiry')}"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>New Contact Form Submission</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #e83e8c 0%, #fd7e14 100%); color: white; padding: 30px; text-align: center; }}
                    .content {{ padding: 30px; background: #f9f9f9; }}
                    .contact-details {{ background: white; padding: 20px; border-left: 4px solid #e83e8c; margin: 20px 0; }}
                    .footer {{ padding: 20px; text-align: center; color: #666; font-size: 14px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>📧 New Contact Form Submission</h1>
                        <p>FlexiFinance Website</p>
                    </div>
                    <div class="content">
                        <h2>Contact Details</h2>
                        
                        <div class="contact-details">
                            <p><strong>Name:</strong> {contact_data.get('name', 'N/A')}</p>
                            <p><strong>Email:</strong> {contact_data.get('email', 'N/A')}</p>
                            <p><strong>Phone:</strong> {contact_data.get('phone', 'N/A')}</p>
                            <p><strong>Subject:</strong> {contact_data.get('subject', 'N/A')}</p>
                            <p><strong>Source:</strong> {contact_data.get('source', 'website')}</p>
                            <p><strong>Submitted:</strong> {contact_data.get('created_at', 'N/A')}</p>
                            <p><strong>IP Address:</strong> {contact_data.get('ip_address', 'N/A')}</p>
                        </div>
                        
                        <h3>Message:</h3>
                        <div style="background: white; padding: 20px; border-radius: 5px; margin: 20px 0;">
                            <p>{contact_data.get('message', 'No message provided').replace('\\n', '<br>')}</p>
                        </div>
                        
                        <p>Please respond to this inquiry within 24 hours.</p>
                    </div>
                    <div class="footer">
                        <p>FlexiFinance - Customer Support Notification</p>
                        <p>View all submissions in the admin panel</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Send to support team
            support_email = getattr(settings, 'SUPPORT_EMAIL', 'support@flexifinance.com')
            return self.send_email(support_email, subject, html_content)
            
        except Exception as e:
            logger.error(f"Contact notification email error: {e}")
            return {
                'success': False,
                'error': str(e)
            }