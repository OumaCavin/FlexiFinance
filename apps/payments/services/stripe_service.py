"""
Stripe Payment Service for FlexiFinance
Handles international card payments and Stripe API interactions
"""
# import stripe  # Commented out for development - stripe not installed
import logging
from django.conf import settings
from decimal import Decimal
import json

logger = logging.getLogger(__name__)


class StripeService:
    """
    Stripe Payment Integration Service
    Provides methods for card payments, payment intents, and webhooks
    """
    
    def __init__(self):
        # Configure Stripe API
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
    def create_payment_intent(self, amount, currency='usd', metadata=None):
        """
        Create a Stripe payment intent for card payments
        
        Args:
            amount (Decimal): Payment amount
            currency (str): Currency code (usd, eur)
            metadata (dict): Additional payment metadata
            
        Returns:
            dict: Payment intent data
        """
        try:
            # Convert amount to cents (Stripe expects integer amounts)
            amount_cents = int(amount * 100)
            
            payment_intent_data = {
                'amount': amount_cents,
                'currency': currency,
                'automatic_payment_methods': {
                    'enabled': True,
                },
                'metadata': metadata or {}
            }
            
            # Add description if metadata exists
            if metadata:
                payment_intent_data['description'] = f"Payment for {metadata.get('description', 'FlexiFinance service')}"
            
            payment_intent = stripe.PaymentIntent.create(**payment_intent_data)
            
            logger.info(f"Stripe payment intent created: {payment_intent.id}")
            return {
                'success': True,
                'client_secret': payment_intent.client_secret,
                'payment_intent_id': payment_intent.id,
                'status': payment_intent.status
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe payment intent creation failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_setup_intent(self, customer_id=None, metadata=None):
        """
        Create a setup intent for saving payment methods
        
        Args:
            customer_id (str): Stripe customer ID
            metadata (dict): Additional metadata
            
        Returns:
            dict: Setup intent data
        """
        try:
            setup_intent_data = {
                'automatic_payment_methods': {
                    'enabled': True,
                },
                'metadata': metadata or {}
            }
            
            if customer_id:
                setup_intent_data['customer'] = customer_id
                
            setup_intent = stripe.SetupIntent.create(**setup_intent_data)
            
            logger.info(f"Stripe setup intent created: {setup_intent.id}")
            return {
                'success': True,
                'client_secret': setup_intent.client_secret,
                'setup_intent_id': setup_intent.id
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe setup intent creation failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def confirm_payment(self, payment_intent_id):
        """
        Confirm a payment intent
        
        Args:
            payment_intent_id (str): Stripe payment intent ID
            
        Returns:
            dict: Payment confirmation data
        """
        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            logger.info(f"Stripe payment intent status: {payment_intent.status}")
            return {
                'success': True,
                'status': payment_intent.status,
                'amount_received': payment_intent.amount_received,
                'currency': payment_intent.currency
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe payment confirmation failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def handle_webhook(self, payload, signature):
        """
        Handle Stripe webhook events
        
        Args:
            payload (str): Webhook payload
            signature (str): Webhook signature
            
        Returns:
            dict: Webhook processing result
        """
        try:
            # Verify webhook signature
            event = stripe.Webhook.construct_event(
                payload, signature, settings.STRIPE_WEBHOOK_SECRET
            )
            
            logger.info(f"Stripe webhook received: {event.type}")
            
            # Handle different event types
            if event.type == 'payment_intent.succeeded':
                payment_intent = event.data.object
                logger.info(f"Payment succeeded: {payment_intent.id}")
                # Here you would update your database with payment success
                
            elif event.type == 'payment_intent.payment_failed':
                payment_intent = event.data.object
                logger.warning(f"Payment failed: {payment_intent.id}")
                # Here you would update your database with payment failure
                
            elif event.type == 'payment_method.attached':
                payment_method = event.data.object
                logger.info(f"Payment method attached: {payment_method.id}")
                # Here you would save the payment method to user account
                
            return {
                'success': True,
                'event_type': event.type,
                'event_id': event.id
            }
            
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Stripe webhook signature verification failed: {e}")
            return {
                'success': False,
                'error': 'Invalid signature'
            }
        except stripe.error.StripeError as e:
            logger.error(f"Stripe webhook processing failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_customer(self, email, name=None, phone=None, metadata=None):
        """
        Create a Stripe customer
        
        Args:
            email (str): Customer email
            name (str): Customer name
            phone (str): Customer phone
            metadata (dict): Additional metadata
            
        Returns:
            dict: Customer creation result
        """
        try:
            customer_data = {
                'email': email,
                'metadata': metadata or {}
            }
            
            if name:
                customer_data['name'] = name
                
            if phone:
                customer_data['phone'] = phone
                
            customer = stripe.Customer.create(**customer_data)
            
            logger.info(f"Stripe customer created: {customer.id}")
            return {
                'success': True,
                'customer_id': customer.id,
                'email': customer.email
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe customer creation failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_customer_payment_methods(self, customer_id):
        """
        Get customer's saved payment methods
        
        Args:
            customer_id (str): Stripe customer ID
            
        Returns:
            dict: Payment methods data
        """
        try:
            payment_methods = stripe.PaymentMethod.list(
                customer=customer_id,
                type='card'
            )
            
            return {
                'success': True,
                'payment_methods': [
                    {
                        'id': pm.id,
                        'type': pm.type,
                        'card': {
                            'brand': pm.card.brand,
                            'last4': pm.card.last4,
                            'exp_month': pm.card.exp_month,
                            'exp_year': pm.card.exp_year
                        }
                    } for pm in payment_methods.auto_paging_iter()
                ]
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to get customer payment methods: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def format_amount(self, amount, currency='usd'):
        """
        Format amount for display
        
        Args:
            amount (Decimal): Amount to format
            currency (str): Currency code
            
        Returns:
            str: Formatted amount with currency symbol
        """
        currency_symbols = {
            'usd': '$',
            'eur': '€',
            'kes': 'KSh'
        }
        
        symbol = currency_symbols.get(currency, currency.upper())
        return f"{symbol}{amount:.2f}"
    
    def verify_webhook(self, payload, signature):
        """
        Verify Stripe webhook signature
        
        Args:
            payload (str): Raw webhook payload
            signature (str): Webhook signature header
            
        Returns:
            dict or None: Verified event data or None if verification failed
        """
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, settings.STRIPE_WEBHOOK_SECRET
            )
            return event
        except stripe.error.SignatureVerificationError:
            logger.error("Stripe webhook signature verification failed")
            return None
    
    def handle_payment_success(self, payment_intent):
        """
        Handle successful payment webhook
        
        Args:
            payment_intent (dict): Payment intent data
            
        Returns:
            dict: Processing result
        """
        try:
            logger.info(f"Processing successful payment: {payment_intent.id}")
            
            # Here you would typically:
            # 1. Update payment status in database
            # 2. Update loan/payment records
            # 3. Send confirmation emails
            # 4. Update user balance
            
            # For now, just log the success
            return {
                'success': True,
                'payment_intent_id': payment_intent.id,
                'amount': payment_intent.amount,
                'currency': payment_intent.currency,
                'status': payment_intent.status,
                'message': 'Payment success processed'
            }
            
        except Exception as e:
            logger.error(f"Error processing payment success: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def handle_payment_failure(self, payment_intent):
        """
        Handle failed payment webhook
        
        Args:
            payment_intent (dict): Payment intent data
            
        Returns:
            dict: Processing result
        """
        try:
            logger.warning(f"Processing failed payment: {payment_intent.id}")
            
            # Here you would typically:
            # 1. Update payment status in database
            # 2. Update loan/payment records
            # 3. Send failure notification emails
            # 4. Log the failure reason
            
            return {
                'success': True,
                'payment_intent_id': payment_intent.id,
                'amount': payment_intent.amount,
                'currency': payment_intent.currency,
                'status': payment_intent.status,
                'last_payment_error': payment_intent.get('last_payment_error', {}),
                'message': 'Payment failure processed'
            }
            
        except Exception as e:
            logger.error(f"Error processing payment failure: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def handle_payment_canceled(self, payment_intent):
        """
        Handle canceled payment webhook
        
        Args:
            payment_intent (dict): Payment intent data
            
        Returns:
            dict: Processing result
        """
        try:
            logger.info(f"Processing canceled payment: {payment_intent.id}")
            
            # Here you would typically:
            # 1. Update payment status in database
            # 2. Update loan/payment records
            # 3. Send cancellation notification
            
            return {
                'success': True,
                'payment_intent_id': payment_intent.id,
                'amount': payment_intent.amount,
                'currency': payment_intent.currency,
                'status': payment_intent.status,
                'message': 'Payment cancellation processed'
            }
            
        except Exception as e:
            logger.error(f"Error processing payment cancellation: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def check_payment_status(self, payment_intent_id):
        """
        Check the status of a payment intent
        
        Args:
            payment_intent_id (str): Stripe payment intent ID
            
        Returns:
            dict: Payment status data
        """
        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            return {
                'success': True,
                'data': {
                    'id': payment_intent.id,
                    'status': payment_intent.status,
                    'amount': payment_intent.amount,
                    'currency': payment_intent.currency,
                    'created': payment_intent.created,
                    'description': payment_intent.description
                }
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to check payment status: {e}")
            return {
                'success': False,
                'error': str(e)
            }