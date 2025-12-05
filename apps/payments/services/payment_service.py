"""
Unified Payment Service for FlexiFinance
Handles multiple payment methods: M-PESA and Stripe
"""
import logging
from decimal import Decimal
from .mpesa_service import MpesaService
from .stripe_service import StripeService
from django.conf import settings

logger = logging.getLogger(__name__)


class PaymentService:
    """
    Unified Payment Service
    Orchestrates payments across different payment providers
    """
    
    def __init__(self):
        self.mpesa_service = MpesaService()
        self.stripe_service = StripeService()
        
    def process_payment(self, payment_method, amount, currency='kes', **kwargs):
        """
        Process payment using the specified method
        
        Args:
            payment_method (str): 'mpesa' or 'stripe'
            amount (Decimal): Payment amount
            currency (str): Payment currency
            **kwargs: Additional payment parameters
            
        Returns:
            dict: Payment processing result
        """
        if payment_method.lower() == 'mpesa':
            return self._process_mpesa_payment(amount, currency, **kwargs)
        elif payment_method.lower() == 'stripe':
            return self._process_stripe_payment(amount, currency, **kwargs)
        else:
            return {
                'success': False,
                'error': f'Unsupported payment method: {payment_method}'
            }
    
    def _process_mpesa_payment(self, amount, currency, phone_number, **kwargs):
        """
        Process M-PESA payment
        
        Args:
            amount (Decimal): Payment amount
            currency (str): Payment currency
            phone_number (str): M-PESA phone number
            **kwargs: Additional parameters
            
        Returns:
            dict: M-PESA payment result
        """
        try:
            if currency.lower() != 'kes':
                return {
                    'success': False,
                    'error': 'M-PESA only supports KES currency'
                }
            
            # Initiate STK Push
            result = self.mpesa_service.stk_push(
                phone_number=phone_number,
                amount=float(amount),
                transaction_reference=kwargs.get('reference', 'flexifinance_payment'),
                transaction_description=kwargs.get('description', 'FlexiFinance payment')
            )
            
            if result.get('success'):
                return {
                    'success': True,
                    'payment_method': 'mpesa',
                    'transaction_id': result.get('checkout_request_id'),
                    'merchant_request_id': result.get('merchant_request_id'),
                    'status': 'pending',
                    'message': 'STK push sent to your phone. Please complete the payment.'
                }
            else:
                return {
                    'success': False,
                    'payment_method': 'mpesa',
                    'error': result.get('error', 'M-PESA payment failed')
                }
                
        except Exception as e:
            logger.error(f"M-PESA payment processing error: {e}")
            return {
                'success': False,
                'payment_method': 'mpesa',
                'error': str(e)
            }
    
    def _process_stripe_payment(self, amount, currency, **kwargs):
        """
        Process Stripe payment
        
        Args:
            amount (Decimal): Payment amount
            currency (str): Payment currency
            **kwargs: Additional parameters
            
        Returns:
            dict: Stripe payment result
        """
        try:
            # Create payment intent
            metadata = kwargs.get('metadata', {})
            metadata.update({
                'payment_method': 'stripe',
                'original_currency': currency,
                'description': kwargs.get('description', 'FlexiFinance payment')
            })
            
            result = self.stripe_service.create_payment_intent(
                amount=amount,
                currency=currency.lower(),
                metadata=metadata
            )
            
            if result.get('success'):
                return {
                    'success': True,
                    'payment_method': 'stripe',
                    'client_secret': result.get('client_secret'),
                    'payment_intent_id': result.get('payment_intent_id'),
                    'status': result.get('status'),
                    'message': 'Payment intent created. Please complete the payment.'
                }
            else:
                return {
                    'success': False,
                    'payment_method': 'stripe',
                    'error': result.get('error', 'Stripe payment failed')
                }
                
        except Exception as e:
            logger.error(f"Stripe payment processing error: {e}")
            return {
                'success': False,
                'payment_method': 'stripe',
                'error': str(e)
            }
    
    def get_supported_currencies(self, payment_method):
        """
        Get supported currencies for a payment method
        
        Args:
            payment_method (str): 'mpesa' or 'stripe'
            
        Returns:
            list: Supported currency codes
        """
        if payment_method.lower() == 'mpesa':
            return ['kes']
        elif payment_method.lower() == 'stripe':
            return ['usd', 'eur', 'gbp', 'cad', 'aud']
        else:
            return []
    
    def get_payment_method_display_name(self, payment_method):
        """
        Get human-readable payment method name
        
        Args:
            payment_method (str): 'mpesa' or 'stripe'
            
        Returns:
            str: Display name
        """
        display_names = {
            'mpesa': 'M-PESA Mobile Money',
            'stripe': 'Credit/Debit Card',
            'card': 'Credit/Debit Card',
            'mobile': 'Mobile Money'
        }
        return display_names.get(payment_method.lower(), payment_method.title())
    
    def format_currency(self, amount, currency, payment_method=None):
        """
        Format currency amount for display
        
        Args:
            amount (Decimal): Amount to format
            currency (str): Currency code
            payment_method (str): Payment method for currency symbol
            
        Returns:
            str: Formatted amount
        """
        # Use Stripe service for formatting if available
        try:
            return self.stripe_service.format_amount(amount, currency)
        except:
            # Fallback formatting
            currency_symbols = {
                'usd': '$',
                'eur': '€',
                'gbp': '£',
                'cad': 'C$',
                'aud': 'A$',
                'kes': 'KSh'
            }
            
            symbol = currency_symbols.get(currency.lower(), currency.upper())
            return f"{symbol}{amount:.2f}"
    
    def get_conversion_rate(self, from_currency, to_currency):
        """
        Get exchange rate between currencies
        In production, this would fetch real-time rates from an API
        
        Args:
            from_currency (str): Source currency
            to_currency (str): Target currency
            
        Returns:
            Decimal: Exchange rate (1 unit of from_currency equals X units of to_currency)
        """
        # Simplified exchange rates - in production, use a real API
        rates = {
            ('usd', 'kes'): Decimal('132.50'),
            ('eur', 'kes'): Decimal('142.80'),
            ('gbp', 'kes'): Decimal('165.20'),
            ('kes', 'usd'): Decimal('0.0075'),
            ('kes', 'eur'): Decimal('0.0070'),
            ('kes', 'gbp'): Decimal('0.0060'),
            ('usd', 'eur'): Decimal('1.08'),
            ('eur', 'usd'): Decimal('0.93'),
        }
        
        return rates.get((from_currency.lower(), to_currency.lower()), Decimal('1'))
    
    def convert_amount(self, amount, from_currency, to_currency):
        """
        Convert amount between currencies
        
        Args:
            amount (Decimal): Amount to convert
            from_currency (str): Source currency
            to_currency (str): Target currency
            
        Returns:
            Decimal: Converted amount
        """
        if from_currency.lower() == to_currency.lower():
            return amount
        
        rate = self.get_conversion_rate(from_currency, to_currency)
        return amount * rate
    
    def validate_payment_method(self, payment_method, currency):
        """
        Validate if payment method supports the currency
        
        Args:
            payment_method (str): Payment method
            currency (str): Currency code
            
        Returns:
            bool: True if valid combination
        """
        supported_currencies = self.get_supported_currencies(payment_method)
        return currency.lower() in [c.lower() for c in supported_currencies]
    
    def process_mpesa_callback(self, callback_data):
        """
        Process M-PESA payment callback
        
        Args:
            callback_data (dict): M-PESA callback data
            
        Returns:
            dict: Processing result
        """
        try:
            # Extract transaction details
            transaction_id = callback_data.get('transaction_id', '')
            amount = callback_data.get('amount', 0)
            phone_number = callback_data.get('phone_number', '')
            reference = callback_data.get('reference', '')
            status = callback_data.get('status', '')
            description = callback_data.get('description', '')
            
            # Log the callback
            logger.info(f"Processing M-PESA callback: {transaction_id}")
            
            # Here you would typically:
            # 1. Update payment record in database
            # 2. Update loan/payment status
            # 3. Send notifications
            # 4. Update user balance
            
            # For now, we'll just log and return success
            payment_status = 'completed' if status == '0' else 'failed'
            
            return {
                'success': True,
                'transaction_id': transaction_id,
                'status': payment_status,
                'amount': amount,
                'phone_number': phone_number,
                'message': 'M-PESA callback processed successfully'
            }
            
        except Exception as e:
            logger.error(f"Error processing M-PESA callback: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }