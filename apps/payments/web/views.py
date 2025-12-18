"""
Payment webhook views for FlexiFinance
Handles M-PESA callbacks and Stripe webhooks
"""

from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
import logging
import json
from datetime import datetime

# Import payment services
from apps.payments.services.mpesa_service import MpesaService
from apps.payments.services.stripe_service import StripeService
from apps.payments.services.payment_service import PaymentService

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["POST"])
def mpesa_callback(request):
    """Handle M-PESA payment callbacks"""
    try:
        # Log the callback data for debugging
        callback_data = json.loads(request.body)
        logger.info(f"M-PESA Callback received: {callback_data}")
        
        # Extract transaction details
        transaction_id = callback_data.get('TransID', '')
        transaction_time = callback_data.get('TransTime', '')
        amount = float(callback_data.get('TransAmount', 0))
        phone_number = callback_data.get('MSISDN', '')
        reference = callback_data.get('Reference', '')
        
        # Validate callback data
        if not all([transaction_id, amount, phone_number]):
            logger.error(f"Invalid M-PESA callback data: {callback_data}")
            return JsonResponse({
                'ResultCode': 1,
                'ResultDesc': 'Invalid callback data'
            })
        
        # Process the payment
        payment_service = PaymentService()
        result = payment_service.process_mpesa_callback({
            'transaction_id': transaction_id,
            'transaction_time': transaction_time,
            'amount': amount,
            'phone_number': phone_number,
            'reference': reference,
            'status': callback_data.get('ResultCode', 0),
            'description': callback_data.get('ResultDesc', ''),
        })
        
        if result['success']:
            logger.info(f"M-PESA payment processed successfully: {transaction_id}")
            return JsonResponse({
                'ResultCode': 0,
                'ResultDesc': 'Payment processed successfully'
            })
        else:
            logger.error(f"Failed to process M-PESA payment: {result.get('error', 'Unknown error')}")
            return JsonResponse({
                'ResultCode': 1,
                'ResultDesc': f"Payment processing failed: {result.get('error', 'Unknown error')}"
            })
            
    except json.JSONDecodeError:
        logger.error("Invalid JSON in M-PESA callback")
        return JsonResponse({
            'ResultCode': 1,
            'ResultDesc': 'Invalid JSON data'
        })
    except Exception as e:
        logger.error(f"Error processing M-PESA callback: {str(e)}")
        return JsonResponse({
            'ResultCode': 1,
            'ResultDesc': f'Server error: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["POST"])
def mpesa_validation(request):
    """Handle M-PESA payment validation (optional for transactions above KES 1,000)"""
    try:
        validation_data = json.loads(request.body)
        logger.info(f"M-PESA Validation received: {validation_data}")
        
        # Validate the transaction
        amount = float(validation_data.get('TransAmount', 0))
        
        # Always accept the transaction for demonstration
        # In production, you would validate:
        # 1. User has sufficient loan balance
        # 2. Transaction amount is within limits
        # 3. User is authorized to make this payment
        
        return JsonResponse({
            'ResultCode': 0,
            'ResultDesc': 'Accepted'
        })
        
    except Exception as e:
        logger.error(f"Error in M-PESA validation: {str(e)}")
        return JsonResponse({
            'ResultCode': 1,
            'ResultDesc': 'Validation failed'
        })

@csrf_exempt
@require_http_methods(["POST"])
def stripe_webhook(request):
    """Handle Stripe webhooks for payment status updates"""
    try:
        # Get the raw payload and signature
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')
        
        # Verify webhook signature
        stripe_service = StripeService()
        event = stripe_service.verify_webhook(payload, sig_header)
        
        if not event:
            logger.error("Invalid Stripe webhook signature")
            return HttpResponse(status=400)
        
        # Log the event
        logger.info(f"Stripe webhook received: {event['type']}")
        
        # Handle different event types
        event_type = event['type']
        
        if event_type == 'payment_intent.succeeded':
            # Payment succeeded
            payment_intent = event['data']['object']
            result = stripe_service.handle_payment_success(payment_intent)
            
            if result['success']:
                logger.info(f"Stripe payment succeeded: {payment_intent['id']}")
            else:
                logger.error(f"Failed to process Stripe payment success: {result.get('error')}")
        
        elif event_type == 'payment_intent.payment_failed':
            # Payment failed
            payment_intent = event['data']['object']
            result = stripe_service.handle_payment_failure(payment_intent)
            
            if result['success']:
                logger.info(f"Stripe payment failed processed: {payment_intent['id']}")
            else:
                logger.error(f"Failed to process Stripe payment failure: {result.get('error')}")
        
        elif event_type == 'payment_intent.canceled':
            # Payment canceled
            payment_intent = event['data']['object']
            result = stripe_service.handle_payment_canceled(payment_intent)
            
            if result['success']:
                logger.info(f"Stripe payment canceled processed: {payment_intent['id']}")
            else:
                logger.error(f"Failed to process Stripe payment cancellation: {result.get('error')}")
        
        else:
            logger.info(f"Unhandled Stripe event type: {event_type}")
        
        return HttpResponse(status=200)
        
    except stripe_service.stripe.error.SignatureVerificationError:
        logger.error("Stripe webhook signature verification failed")
        return HttpResponse(status=400)
    except Exception as e:
        logger.error(f"Error processing Stripe webhook: {str(e)}")
        return HttpResponse(status=500)

@csrf_exempt
@require_http_methods(["POST"])
def payment_status_check(request, provider, transaction_id):
    """Check payment status for a transaction"""
    try:
        if provider == 'mpesa':
            # Check M-PESA transaction status
            mpesa_service = MpesaService()
            result = mpesa_service.check_transaction_status(transaction_id)
            
            if result['success']:
                return JsonResponse({
                    'success': True,
                    'status': result['data']['status'],
                    'transaction_id': transaction_id,
                    'provider': 'mpesa'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': result.get('error', 'Transaction not found'),
                    'status': 'not_found'
                }, status=404)
        
        elif provider == 'stripe':
            # Check Stripe payment status
            stripe_service = StripeService()
            result = stripe_service.check_payment_status(transaction_id)
            
            if result['success']:
                return JsonResponse({
                    'success': True,
                    'status': result['data']['status'],
                    'transaction_id': transaction_id,
                    'provider': 'stripe'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': result.get('error', 'Payment not found'),
                    'status': 'not_found'
                }, status=404)
        
        else:
            return JsonResponse({
                'success': False,
                'error': 'Unsupported payment provider'
            }, status=400)
            
    except Exception as e:
        logger.error(f"Error checking payment status: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Internal server error'
        }, status=500)