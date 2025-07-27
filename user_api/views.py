import logging

from dj_rest_auth.registration.views import RegisterView
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenObtainPairView

from . import serializers
from .models import Receipt

logger = logging.getLogger("api")

UserModel = get_user_model()


class LoginView(TokenObtainPairView):
    """
    API view for user login using JWT authentication.
    Accepts username or email in the request data and returns JWT tokens if credentials are valid.
    """
    authentication_classes = ()
    permission_classes = (permissions.AllowAny,)
    serializer_class = serializers.LoginSerializer


class SignUpView(RegisterView):
    authentication_classes = ()
    permission_classes = (permissions.AllowAny,)
    serializer_class = serializers.SignUpSerializer


class ReceiptImageUploadView(generics.UpdateAPIView, generics.DestroyAPIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Receipt.objects.all().prefetch_related('user')
    serializer_class = serializers.ReceiptImageUploadSerializer

    def update(self, request, *args, **kwargs):
        """
        Handle PUT request to update the receipt image.
        """
        try:
            return super().update(request, *args, **kwargs)
        except Exception as e:
            logger.exception(f"Error updating receipt image: {e}")
            return Response({"detail": "Failed to update receipt image"}, status=status.HTTP_400_BAD_REQUEST)
