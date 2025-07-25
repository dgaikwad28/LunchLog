from typing import Dict, Any

from allauth.account import app_settings as allauth_account_settings
from allauth.account.adapter import get_adapter
from allauth.socialaccount.models import EmailAddress
from dj_rest_auth.registration.serializers import RegisterSerializer
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from user_api.models import Receipt

UserModel = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ('pk', 'username', 'email', 'first_name', 'last_name')


class LoginSerializer(TokenObtainPairSerializer):

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, str]:
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data
        return data


class SignUpSerializer(RegisterSerializer):
    _has_phone_field = None
    first_name = serializers.CharField()
    last_name = serializers.CharField()

    def get_cleaned_data(self):
        return {
            'username': self.validated_data.get('username', ''),
            'password1': self.validated_data.get('password1', ''),
            'email': self.validated_data.get('email', ''),
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
        }

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        if allauth_account_settings.UNIQUE_EMAIL:
            if email and EmailAddress.objects.filter(email=email).exists():
                raise serializers.ValidationError(
                    _('A user is already registered with this e-mail address.'),
                )
        return email


class ReceiptsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receipt
        fields = '__all__'


class ReceiptImageUploadSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=True, allow_empty_file=False, allow_null=False)

    class Meta:
        model = Receipt
        fields = ('image',)
        read_only_fields = ('id',)

    def validate_image(self, image):
        if image.size > settings.MEDIA_SIZE:
            raise ValidationError(f'Image file too large')

    def update(self, instance, validated_data):
        if validated_data.get('image'):
            image = validated_data['image']
            image.name = f"{instance.id}_{image.name}"
            instance.image = image
        return super().update(instance, validated_data)
