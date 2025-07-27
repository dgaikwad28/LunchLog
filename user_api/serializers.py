import logging
from typing import Dict, Any

from allauth.account import app_settings as allauth_account_settings
from allauth.account.adapter import get_adapter
from allauth.socialaccount.models import EmailAddress
from botocore.exceptions import SSLError
from dj_rest_auth.registration.serializers import RegisterSerializer
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import TemporaryUploadedFile
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from user_api.models import Receipt, Address, Restaurant

logger = logging.getLogger("api")

UserModel = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the user model, exposing primary key, username, email, first name, and last name.
    """

    class Meta:
        model = UserModel
        fields = ('pk', 'username', 'email', 'first_name', 'last_name')


class LoginSerializer(TokenObtainPairSerializer):
    """
    Serializer for user login, returns JWT tokens and serialized user data.
    """

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, str]:
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data
        return data


class SignUpSerializer(RegisterSerializer):
    """
    Serializer for user registration. Handles first name, last name, and email validation.
    """
    _has_phone_field = None
    first_name = serializers.CharField()
    last_name = serializers.CharField()

    def get_cleaned_data(self) -> Dict[str, str]:
        """
        Returns a dictionary of cleaned user registration data including username, password, email, first name,
        and last name.
        """
        return {
            'username': self.validated_data.get('username', ''),
            'password1': self.validated_data.get('password1', ''),
            'email': self.validated_data.get('email', ''),
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
        }

    def validate_email(self, email: str) -> str:
        """
        Validates the email address for uniqueness and proper formatting.
        Raises a ValidationError if the email is already registered.
        """
        email = get_adapter().clean_email(email)
        if allauth_account_settings.UNIQUE_EMAIL:
            if email and EmailAddress.objects.filter(email=email).exists():
                logger.debug(f"Email already registered: {email}")
                raise serializers.ValidationError('A user is already registered with this e-mail address.')
        return email


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'


class RestaurantSerializer(serializers.ModelSerializer):
    """
    Serializer for the Restaurant model, exposing primary key and name.
    """
    address = AddressSerializer(required=True)

    class Meta:
        model = Restaurant
        fields = '__all__'


class ReceiptsCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating Receipt instances. Uses all fields from the Receipt model.
    """

    restaurant = RestaurantSerializer(required=False, write_only=True)

    class Meta:
        model = Receipt
        fields = '__all__'


class ReceiptsSerializer(ReceiptsCreateSerializer):
    """
    Serializer for displaying Receipt instances, including nested user data.
    """
    user = UserSerializer(read_only=True)
    restaurant = RestaurantSerializer(read_only=True)

    class Meta:
        model = Receipt
        fields = '__all__'


class ReceiptImageUploadSerializer(serializers.ModelSerializer):
    """
    Serializer for uploading and validating receipt images. Ensures image size and handles S3 upload errors.
    """
    image = serializers.ImageField(required=True, allow_empty_file=False, allow_null=False, )

    class Meta:
        model = Receipt
        fields = ('image',)
        read_only_fields = ('id',)

    def validate_image(self, image: TemporaryUploadedFile) -> TemporaryUploadedFile:
        """
        Validates the uploaded image for size constraints.
        """
        if image.size > settings.MEDIA_SIZE:
            logger.info("Image file too large")
            raise ValidationError('Image file too large')
        return image

    def update(self, instance: Receipt, validated_data: dict) -> Receipt:
        """
        Updates the Receipt instance with a new image, renames the image, and handles S3 upload errors.
        """
        if instance.image:
            instance.image.delete()
        if validated_data.get('image'):
            image = validated_data['image']
            image.name = f"{str(instance.user.pk)}_{instance.date}"
            instance.image = image
            try:
                return super().update(instance, validated_data)
            except SSLError:
                logger.warning("Error uploading image to S3")
                pass
            except Exception as e:
                logger.exception(f"Unexpected error uploading image: {e}")
                pass
        raise ValidationError("There was an error uploading the image. Please try again.")
