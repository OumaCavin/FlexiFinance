"""
M-Pesa API Views for FlexiFinance
Handles all M-Pesa API endpoints including callbacks
"""
import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from apps.payments.services.mpesa_service import MpesaService
from apps.payments.models import Payment, MpesaTransaction

logger = logging.getLogger(__name__)


class MpesaCallbackView(APIView):
    """
    M-Pesa STK Push Callback Handler
    This endpoint receives payment confirmations from M-Pesa
    """
    permission_classes = []  # No authentication required for callbacks
    
    def post(self, request):
        """
        Handle M-Pesa STK Push callback
        """
        try:
            # Get callback data
            callback_data = request.data if hasattr(request, 'data') else json.loads(request.body)
            
            logger.info(f"Received M-Pesa STK Push callback: {callback_data}")
            
            # Process callback
            mpesa_service = MpesaService()
            result = mpesa_service.process_callback(callback_data)
            
            if result['success']:
                # Log successful callback processing
                logger.info(f"Successfully processed callback: {result}")
                
                # Return success response for M-Pesa
                return Response({
                    "ResultCode": 0,
                    "ResultDesc": "Accepted"
                }, status=status.HTTP_200_OK)
            else:
                logger.error(f"Failed to process callback: {result}")
                
                # Return error response
                return Response({
                    "ResultCode": 1,
                    "ResultDesc": result['error']
                }, status=status.HTTP_200_OK)
                
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in callback: {e}")
            return Response({
                "ResultCode": 1,
                "ResultDesc": "Invalid JSON format"
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unexpected error processing callback: {e}")
            return Response({
                "ResultCode": 1,
                "ResultDesc": "Internal server error"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MpesaValidationView(APIView):
    """
    M-Pesa Validation Endpoint
    Called by M-Pesa to validate transactions before processing
    """
    permission_classes = []  # No authentication required
    
    def post(self, request):
        """
        Handle M-Pesa validation request
        """
        try:
            validation_data = request.data if hasattr(request, 'data') else json.loads(request.body)
            
            logger.info(f"Received M-Pesa validation request: {validation_data}")
            
            # Extract transaction details
            transaction_id = validation_data.get('TransactionID')
            transaction_amount = validation_data.get('TransactionAmount')
            business_short_code = validation_data.get('BusinessShortCode')
            
            # Perform validation logic here
            # For now, we'll accept all transactions
            is_valid = True
            
            if is_valid:
                logger.info(f"Transaction {transaction_id} validated successfully")
                return Response({
                    "ResultCode": 0,
                    "ResultDesc": "Success. Request accepted"
                }, status=status.HTTP_200_OK)
            else:
                logger.warning(f"Transaction {transaction_id} validation failed")
                return Response({
                    "ResultCode": 1,
                    "ResultDesc": "Failed. Transaction rejected"
                }, status=status.HTTP_200_OK)
                
        except Exception as e:
            logger.error(f"Error in M-Pesa validation: {e}")
            return Response({
                "ResultCode": 1,
                "ResultDesc": "Validation error"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class InitiateSTKPushView(APIView):
    """
    API endpoint to initiate STK Push payment
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Initiate STK Push payment
        """
        try:
            # Get request data
            phone_number = request.data.get('phone_number')
            amount = request.data.get('amount')
            payment_id = request.data.get('payment_id')
            
            # Validate required fields
            if not all([phone_number, amount, payment_id]):
                return Response({
                    'success': False,
                    'error': 'Missing required fields: phone_number, amount, payment_id'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get payment object
            try:
                payment = Payment.objects.get(id=payment_id, user=request.user)
            except Payment.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'Payment not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Check if payment can be processed
            if payment.status not in ['PENDING', 'FAILED']:
                return Response({
                    'success': False,
                    'error': 'Payment cannot be processed in current status'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Initialize M-Pesa service
            mpesa_service = MpesaService()
            
            # Generate reference if not exists
            if not payment.reference_number:
                payment.generate_reference_number()
                payment.save()
            
            # Initiate STK Push
            result = mpesa_service.initiate_stk_push(
                phone_number=phone_number,
                amount=float(amount),
                reference=payment.reference_number,
                description=f"{payment.payment_type} - {payment.description or 'FlexiFinance Payment'}"
            )
            
            if result['success']:
                # Update payment status
                payment.phone_number = phone_number
                payment.status = 'PROCESSING'
                payment.save()
                
                logger.info(f"STK Push initiated successfully for payment {payment.id}")
                
                return Response({
                    'success': True,
                    'message': 'STK Push sent to your phone',
                    'transaction_id': result.get('merchant_request_id'),
                    'checkout_request_id': result.get('checkout_request_id'),
                    'customer_message': result.get('customer_message')
                }, status=status.HTTP_200_OK)
            else:
                # Mark payment as failed
                payment.mark_failed()
                
                logger.error(f"STK Push failed for payment {payment.id}: {result.get('error')}")
                
                return Response({
                    'success': False,
                    'error': result.get('error', 'Failed to initiate STK Push')
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Error initiating STK Push: {e}")
            return Response({
                'success': False,
                'error': 'Internal server error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PaymentStatusView(APIView):
    """
    API endpoint to check payment status
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, payment_id):
        """
        Get payment status
        """
        try:
            # Get payment
            try:
                payment = Payment.objects.get(id=payment_id, user=request.user)
            except Payment.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'Payment not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Prepare response data
            payment_data = {
                'id': str(payment.id),
                'payment_type': payment.payment_type,
                'amount': float(payment.amount),
                'currency': payment.currency,
                'status': payment.status,
                'reference_number': payment.reference_number,
                'phone_number': payment.phone_number,
                'created_at': payment.created_at.isoformat(),
                'updated_at': payment.updated_at.isoformat()
            }
            
            # Add M-Pesa transaction data if exists
            if payment.mpesa_transaction:
                payment_data['mpesa_transaction'] = {
                    'id': str(payment.mpesa_transaction.id),
                    'mpesa_receipt': payment.mpesa_transaction.mpesa_receipt,
                    'result_code': payment.mpesa_transaction.result_code,
                    'result_desc': payment.mpesa_transaction.result_desc,
                    'callback_received': payment.mpesa_transaction.callback_received,
                    'initiated_at': payment.mpesa_transaction.initiated_at.isoformat(),
                    'completed_at': payment.mpesa_transaction.completed_at.isoformat() if payment.mpesa_transaction.completed_at else None
                }
            
            # Add completion info if payment is completed
            if payment.completed_at:
                payment_data['completed_at'] = payment.completed_at.isoformat()
            
            return Response({
                'success': True,
                'data': payment_data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting payment status: {e}")
            return Response({
                'success': False,
                'error': 'Internal server error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PaymentHistoryView(APIView):
    """
    API endpoint to get user's payment history
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Get user's payment history
        """
        try:
            # Get query parameters
            page = int(request.GET.get('page', 1))
            per_page = int(request.GET.get('per_page', 20))
            status_filter = request.GET.get('status')
            payment_type_filter = request.GET.get('payment_type')
            
            # Build queryset
            payments = Payment.objects.filter(user=request.user)
            
            # Apply filters
            if status_filter:
                payments = payments.filter(status=status_filter)
            
            if payment_type_filter:
                payments = payments.filter(payment_type=payment_type_filter)
            
            # Order by creation date
            payments = payments.order_by('-created_at')
            
            # Paginate
            start = (page - 1) * per_page
            end = start + per_page
            payments_page = payments[start:end]
            
            # Prepare response data
            payments_data = []
            for payment in payments_page:
                payment_data = {
                    'id': str(payment.id),
                    'payment_type': payment.payment_type,
                    'amount': float(payment.amount),
                    'currency': payment.currency,
                    'status': payment.status,
                    'reference_number': payment.reference_number,
                    'phone_number': payment.phone_number,
                    'created_at': payment.created_at.isoformat(),
                    'receipt_number': payment.receipt_number,
                    'completed_at': payment.completed_at.isoformat() if payment.completed_at else None
                }
                payments_data.append(payment_data)
            
            # Calculate pagination info
            total_payments = payments.count()
            total_pages = (total_payments + per_page - 1) // per_page
            
            return Response({
                'success': True,
                'data': {
                    'payments': payments_data,
                    'pagination': {
                        'current_page': page,
                        'per_page': per_page,
                        'total_pages': total_pages,
                        'total_items': total_payments
                    }
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting payment history: {e}")
            return Response({
                'success': False,
                'error': 'Internal server error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TestMpesaView(APIView):
    """
    Test endpoint for M-Pesa integration (for development only)
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Test M-Pesa service connection
        """
        try:
            mpesa_service = MpesaService()
            access_token = mpesa_service.get_access_token()
            
            if access_token:
                return Response({
                    'success': True,
                    'message': 'M-Pesa service is working',
                    'environment': mpesa_service.environment,
                    'base_url': mpesa_service.base_url,
                    'has_access_token': True
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'error': 'Failed to get M-Pesa access token'
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
                
        except Exception as e:
            logger.error(f"Error testing M-Pesa service: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Function-based views for backward compatibility
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_stk_push(request):
    """
    Function-based view to initiate STK Push
    """
    view = InitiateSTKPushView.as_view()
    return view(request)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payment_status(request, payment_id):
    """
    Function-based view to get payment status
    """
    view = PaymentStatusView.as_view()
    return view(request, payment_id)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payment_history(request):
    """
    Function-based view to get payment history
    """
    view = PaymentHistoryView.as_view()
    return view(request)


@api_view(['GET'])
def test_mpesa(request):
    """
    Function-based view to test M-Pesa connection
    """
    view = TestMpesaView.as_view()
    return view(request)