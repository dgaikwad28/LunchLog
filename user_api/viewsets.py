from django.contrib.auth import get_user_model
from rest_framework import viewsets, permissions
from rest_framework_simplejwt.authentication import JWTAuthentication

from . import serializers
from .models import Receipt

UserModel = get_user_model()


class ReceiptsViewSet(viewsets.ModelViewSet):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    queryset = Receipt.objects.all()
    serializer_class = serializers.ReceiptsSerializer
