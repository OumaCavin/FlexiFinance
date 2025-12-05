"""
API Views for Users app
REST API endpoints for user management and authentication
"""

import logging
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from rest_framework import status, viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from django_rest_passwordreset.serializers import PasswordResetRequestSerializer
from django_rest_passwordreset.views import (
    PasswordResetRequestView as DRRPasswordResetRequestView,
    PasswordResetConfirmView as DRRPasswordResetConfirmView
)
from dj_rest_auth.views import LoginView as DJRAuthLoginView, LogoutView as DJRAuthLogoutView
from dj_rest_auth.registration.views import RegisterView as DJRAuthRegisterView
from dj_rest_auth.app_settings import serializers as dj_rest_auth_serializers

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


class UserRegistrationView(DJRAuthRegisterView):
    """
    Custom User Registration API View
    Uses dj_rest_auth for registration with additional fields
    """
    permission_classes = [AllowAny]
    
    def get_response_data(self, user):
        return {
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone_number': getattr(user, 'phone_number', None),
            },
            'key': self.token.key if self.token else None,
            'refresh': getattr(self.token, 'refresh_token', None)
        }


class UserLoginView(DJRAuthLoginView):
    """
    Custom User Login API View
    Uses dj_rest_auth for login functionality
    """
    permission_classes = [AllowAny]
    
    def get_response(self):
        data = super().get_response()
        return Response({
            'user': data.data.get('user'),
            'access_token': data.data.get('access_token'),
            'refresh_token': data.data.get('refresh_token')
        })


class UserLogoutView(DJRAuthLogoutView):
    """
    Custom User Logout API View
    Uses dj_rest_auth for logout functionality
    """
    permission_classes = [IsAuthenticated]
    pass


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


class ForgotPasswordView(DRRPasswordResetRequestView):
    """
    API View for requesting password reset
    Uses django-rest-passwordreset package
    """
    permission_classes = [AllowAny]
    serializer_class = PasswordResetRequestSerializer
    
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class ResetPasswordView(DRRPasswordResetConfirmView):
    """
    API View for password reset confirmation
    Uses django-rest-passwordreset package
    """
    permission_classes = [AllowAny]
    pass