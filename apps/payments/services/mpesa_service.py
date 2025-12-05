"""
M-Pesa Service for FlexiFinance
Handles all M-Pesa API interactions including STK Push and callbacks
"""
import requests
import base64
import json
import logging
from datetime import datetime
from django.conf import settings
from django.urls import reverse
from urllib.parse import urlencode
import time

logger = logging.getLogger(__name__)


class MpesaService:
    """
    M-Pesa Integration Service
    Provides methods for STK Push, B2C, and callback handling
    """
    
    def __init__(self):
        self.consumer_key = settings.MPESA_CONFIG.get('CONSUMER_KEY')
        self.consumer_secret = settings.MPESA_CONFIG.get('CONSUMER_SECRET')
        self.passkey = settings.MPESA_CONFIG.get('PASSKEY')
        self.shortcode = settings.MPESA_CONFIG.get('SHORTCODE')
        self.environment = settings.MPESA_CONFIG.get('ENVIRONMENT', 'sandbox')
        
        if self.environment == 'production':
            self.base_url = 'https://api.safaricom.co.ke'
            self.oauth_url = 'https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
        else:
            self.base_url = 'https://sandbox.safaricom.co.ke'
            self.oauth_url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    
    def get_access_token(self):
        """
        Generate M-Pesa access token
        """
        try:
            # Create credentials string
            credentials = f"{self.consumer_key}:{self.consumer_secret}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode('utf-8')
            
            headers = {
                'Authorization': f'Basic {encoded_credentials}'
            }
            
            response = requests.get(self.oauth_url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            return data['access_token']
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get M-Pesa access token: {e}")
            return None
        except KeyError as e:
            logger.error(f"Invalid token response: {e}")
            return None
    
    def initiate_stk_push(self, phone_number, amount, reference, description, callback_url=None):
        """
        Initiate STK Push for payment
        """
        try:
            # Clean phone number
            clean_phone = self._clean_phone_number(phone_number)
            
            # Get access token
            access_token = self.get_access_token()
            if not access_token:
                return {'success': False, 'error': 'Failed to get access token'}
            
            # Generate timestamp
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            
            # Generate password
            password_string = f"{self.shortcode}{self.passkey}{timestamp}"
            password = base64.b64encode(password_string.encode()).decode('utf-8')
            
            # Prepare callback URL
            if not callback_url:
                callback_url = self._get_callback_url('stk_push')
            
            # Prepare request data
            data = {
                "BusinessShortCode": self.shortcode,
                "Password": password,
                "Timestamp": timestamp,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": int(amount),
                "PartyA": clean_phone,
                "PartyB": self.shortcode,
                "PhoneNumber": clean_phone,
                "CallBackURL": callback_url,
                "AccountReference": reference,
                "TransactionDesc": description
            }
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # Make request to M-Pesa
            stk_push_url = f"{self.base_url}/mpesa/stkpush/v1/processrequest"
            response = requests.post(stk_push_url, json=data, headers=headers)
            
            logger.info(f"STK Push request sent: {data}")
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('ResponseCode') == '0':
                    return {
                        'success': True,
                        'merchant_request_id': result.get('MerchantRequestID'),
                        'checkout_request_id': result.get('CheckoutRequestID'),
                        'customer_message': result.get('CustomerMessage'),
                        'response_description': result.get('ResponseDescription')
                    }
                else:
                    logger.error(f"STK Push failed: {result}")
                    return {
                        'success': False,
                        'error': result.get('ResponseDescription', 'Unknown error')
                    }
            else:
                logger.error(f"STK Push request failed with status {response.status_code}: {response.text}")
                return {
                    'success': False,
                    'error': f"Request failed with status {response.status_code}"
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"STK Push request error: {e}")
            return {'success': False, 'error': str(e)}
        except Exception as e:
            logger.error(f"STK Push unexpected error: {e}")
            return {'success': False, 'error': 'Unexpected error occurred'}
    
    def process_callback(self, callback_data):
        """
        Process M-Pesa callback data
        This is called when M-Pesa sends payment confirmation
        """
        try:
            logger.info(f"Processing M-Pesa callback: {callback_data}")
            
            if 'Body' not in callback_data or 'stkCallback' not in callback_data['Body']:
                logger.error("Invalid callback data format")
                return {'success': False, 'error': 'Invalid callback format'}
            
            stk_callback = callback_data['Body']['stkCallback']
            
            # Extract transaction details
            checkout_request_id = stk_callback.get('CheckoutRequestID')
            merchant_request_id = stk_callback.get('MerchantRequestID')
            result_code = stk_callback.get('ResultCode')
            result_desc = stk_callback.get('ResultDesc')
            
            # Find the transaction
            from apps.payments.models import MpesaTransaction
            
            transaction = MpesaTransaction.objects.filter(
                checkout_request_id=checkout_request_id
            ).first()
            
            if not transaction:
                logger.error(f"Transaction not found for checkout_request_id: {checkout_request_id}")
                return {'success': False, 'error': 'Transaction not found'}
            
            # Process callback
            transaction.process_callback(callback_data)
            
            # Extract payment details from callback
            amount = None
            receipt_number = None
            transaction_date = None
            
            if 'CallbackMetadata' in stk_callback:
                metadata = stk_callback['CallbackMetadata']
                for item in metadata.get('Item', []):
                    item_name = item.get('Name', '')
                    item_value = item.get('Value', '')
                    
                    if item_name == 'Amount':
                        amount = item_value
                    elif item_name == 'MpesaReceiptNumber':
                        receipt_number = item_value
                    elif item_name == 'TransactionDate':
                        transaction_date = item_value
            
            # Update transaction with extracted data
            if amount:
                try:
                    transaction.amount = float(amount)
                except (ValueError, TypeError):
                    pass
            
            transaction.save()
            
            logger.info(f"Processed callback for transaction {transaction.id}: {result_desc}")
            
            # Trigger any post-payment processing
            self._post_payment_processing(transaction)
            
            return {
                'success': True,
                'transaction_id': str(transaction.id),
                'result_code': result_code,
                'result_desc': result_desc,
                'receipt_number': receipt_number,
                'amount': amount
            }
            
        except Exception as e:
            logger.error(f"Error processing M-Pesa callback: {e}")
            return {'success': False, 'error': str(e)}
    
    def _clean_phone_number(self, phone_number):
        """
        Clean and format phone number for M-Pesa
        """
        # Remove all non-digit characters
        cleaned = ''.join(filter(str.isdigit, phone_number))
        
        # Remove leading zero if present
        if cleaned.startswith('0'):
            cleaned = cleaned[1:]
        
        # Add country code if not present
        if not cleaned.startswith('254'):
            cleaned = f'254{cleaned}'
        
        return cleaned
    
    def _get_callback_url(self, callback_type='stk_push'):
        """
        Get the appropriate callback URL
        """
        # Get the base URL from settings or request
        from django.contrib.sites.models import Site
        try:
            current_site = Site.objects.get_current()
            base_url = f"https://{current_site.domain}"
        except:
            # Fallback for development
            base_url = "http://localhost:8000"
        
        if callback_type == 'stk_push':
            return f"{base_url}/api/v1/payments/mpesa/callback/"
        elif callback_type == 'b2c':
            return f"{base_url}/api/v1/payments/mpesa/b2c-callback/"
        elif callback_type == 'validation':
            return f"{base_url}/api/v1/payments/mpesa/validate/"
        else:
            return f"{base_url}/api/v1/payments/mpesa/callback/"
    
    def _post_payment_processing(self, transaction):
        """
        Handle post-payment processing
        This can be extended to trigger additional actions
        """
        try:
            # Update payment status if linked to a payment
            if hasattr(transaction, 'payment') and transaction.payment:
                payment = transaction.payment
                
                if transaction.status == 'COMPLETED':
                    payment.mark_completed(transaction.mpesa_receipt)
                    
                    # Trigger any business logic
                    self._handle_successful_payment(payment)
                elif transaction.status == 'FAILED':
                    payment.mark_failed()
            
            # Log the transaction
            logger.info(f"Processed payment transaction {transaction.id} with status {transaction.status}")
            
        except Exception as e:
            logger.error(f"Error in post-payment processing: {e}")
    
    def _handle_successful_payment(self, payment):
        """
        Handle successful payment completion
        """
        try:
            # This can be extended based on payment type
            if payment.payment_type == 'REPAYMENT':
                self._handle_loan_repayment(payment)
            elif payment.payment_type == 'DISBURSEMENT':
                self._handle_loan_disbursement(payment)
            
            # Send confirmation notifications
            self._send_payment_notifications(payment)
            
        except Exception as e:
            logger.error(f"Error handling successful payment: {e}")
    
    def _handle_loan_repayment(self, payment):
        """
        Handle loan repayment processing
        """
        # This would integrate with loan models
        # Update loan balance, mark payments as received, etc.
        logger.info(f"Processing loan repayment for payment {payment.id}")
    
    def _handle_loan_disbursement(self, payment):
        """
        Handle loan disbursement processing
        """
        # This would integrate with loan models
        # Update loan status, etc.
        logger.info(f"Processing loan disbursement for payment {payment.id}")
    
    def _send_payment_notifications(self, payment):
        """
        Send payment notifications
        """
        try:
            # Send email notification
            # send_payment_confirmation_email.delay(payment.id)
            
            # Send SMS notification
            # send_payment_confirmation_sms.delay(payment.id)
            
            logger.info(f"Sent payment notifications for payment {payment.id}")
            
        except Exception as e:
            logger.error(f"Error sending payment notifications: {e}")
    
    def query_transaction_status(self, checkout_request_id):
        """
        Query the status of a transaction
        """
        try:
            access_token = self.get_access_token()
            if not access_token:
                return {'success': False, 'error': 'Failed to get access token'}
            
            # Generate timestamp and password
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            password_string = f"{self.shortcode}{self.passkey}{timestamp}"
            password = base64.b64encode(password_string.encode()).decode('utf-8')
            
            data = {
                "BusinessShortCode": self.shortcode,
                "Password": password,
                "Timestamp": timestamp,
                "CheckoutRequestID": checkout_request_id
            }
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # Make status query request
            status_url = f"{self.base_url}/mpesa/stkpushquery/v1/query"
            response = requests.post(status_url, json=data, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                
                return {
                    'success': True,
                    'status': result.get('ResultCode'),
                    'description': result.get('ResultDesc'),
                    'checkout_request_id': result.get('CheckoutRequestID')
                }
            else:
                return {
                    'success': False,
                    'error': f"Query failed with status {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Error querying transaction status: {e}")
            return {'success': False, 'error': str(e)}
    
    def b2c_payment(self, phone_number, amount, remarks, occasion=None):
        """
        Send B2C payment (for loan disbursements)
        """
        try:
            access_token = self.get_access_token()
            if not access_token:
                return {'success': False, 'error': 'Failed to get access token'}
            
            # Clean phone number
            clean_phone = self._clean_phone_number(phone_number)
            
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            password_string = f"{self.shortcode}{self.passkey}{timestamp}"
            password = base64.b64encode(password_string.encode()).decode('utf-8')
            
            callback_url = self._get_callback_url('b2c')
            
            data = {
                "InitiatorName": settings.MPESA_CONFIG.get('INITIATOR_NAME', 'FlexiFinance'),
                "SecurityCredential": password,  # This should be properly encrypted in production
                "CommandID": "BusinessPayment",
                "Amount": int(amount),
                "PartyA": self.shortcode,
                "PartyB": clean_phone,
                "Remarks": remarks,
                "QueueTimeOutURL": callback_url,
                "ResultURL": callback_url,
                "Occasion": occasion or remarks
            }
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            b2c_url = f"{self.base_url}/mpesa/b2c/v1/paymentrequest"
            response = requests.post(b2c_url, json=data, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('ResponseCode') == '0':
                    return {
                        'success': True,
                        'conversation_id': result.get('ConversationID'),
                        'reference_id': result.get('ReferenceData', {}).get('ReferenceItem', [{}])[0].get('Reference'),
                        'response_description': result.get('ResponseDescription')
                    }
                else:
                    return {
                        'success': False,
                        'error': result.get('ResponseDescription', 'Unknown error')
                    }
            else:
                return {
                    'success': False,
                    'error': f"B2C request failed with status {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"B2C payment error: {e}")
            return {'success': False, 'error': str(e)}