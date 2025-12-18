"""
API Views for Users app
REST API endpoints for user management and authentication
"""

import logging
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from django.contrib.auth.models import User as DjangoUser
from django.contrib.auth import login, logout
from rest_framework import status, viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView

User = get_user_model()
logger = logging.getLogger(__name__)


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing User model
    """
    queryset = User.objects.all()
    serializer_class = None  # Will be set based on needs
    permission_classes = [permissions.IsAuthenticated]


class UserProfileViewSet(viewsets.ViewSet):
    """
    API endpoint for managing User Profile
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user profile"""
        serializer = None  # Will be set based on needs
        data = {
            'id': request.user.id,
            'email': request.user.email,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'phone_number': getattr(request.user, 'phone_number', None),
        }
        return Response(data)


class UserRegistrationView(APIView):
    """
    Custom User Registration API View
    Simple implementation using Django auth
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Register a new user"""
        email = request.data.get('email')
        password = request.data.get('password')
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')
        phone_number = request.data.get('phone_number', '')
        
        if not email or not password:
            return Response(
                {'error': 'Email and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
            )
            # Set phone_number if the field exists
            if hasattr(user, 'phone_number'):
                user.phone_number = phone_number
                user.save()
            
            return Response({
                'message': 'User registered successfully',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'phone_number': getattr(user, 'phone_number', None),
                }
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class UserLoginView(APIView):
    """
    Custom User Login API View
    Simple implementation using Django auth
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Login user"""
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response(
                {'error': 'Email and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return Response({
                'message': 'Login successful',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'phone_number': getattr(user, 'phone_number', None),
                }
            })
        else:
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_400_BAD_REQUEST
            )


class UserLogoutView(APIView):
    """
    Custom User Logout API View
    Simple implementation using Django auth
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Logout user"""
        logout(request)
        return Response({
            'message': 'Logout successful'
        })


class EmailVerificationView(APIView):
    """
    API View for email verification
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        # Placeholder for email verification logic
        # Will implement based on requirements
        return Response(
            {'message': 'Email verification endpoint ready'},
            status=status.HTTP_200_OK
        )


class ResendVerificationView(APIView):
    """
    API View for resending verification emails
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        # Placeholder for resend verification logic
        # Will implement based on requirements
        return Response(
            {'message': 'Verification email resent successfully'},
            status=status.HTTP_200_OK
        )


class ForgotPasswordView(APIView):
    """
    API View for requesting password reset
    Placeholder implementation - will be enhanced later
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Request password reset"""
        email = request.data.get('email')
        if email:
            # TODO: Implement actual password reset functionality
            return Response(
                {'message': 'Password reset request received. Check your email for instructions.'},
                status=status.HTTP_200_OK
            )
        return Response(
            {'error': 'Email is required'},
            status=status.HTTP_400_BAD_REQUEST
        )


class ResetPasswordView(APIView):
    """
    API View for password reset confirmation
    Placeholder implementation - will be enhanced later
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Confirm password reset"""
        # TODO: Implement actual password reset confirmation
        return Response(
            {'message': 'Password reset confirmed successfully'},
            status=status.HTTP_200_OK
        )