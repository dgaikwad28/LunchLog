from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from . import serializers
from .models import Receipt
from .tasks import fetch_restaurant_details

UserModel = get_user_model()


class ReceiptsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Receipt objects.

    Provides list, create, update, retrieve, and delete operations.
    Supports filtering by month and year via query parameters.
    Uses JWT authentication and requires authenticated users.
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_query_params(self):
        """
        Returns the query parameters for filtering receipts by month and year.

        year is always set to the current year if not provided.

        """
        month = self.request.query_params.get('month')
        year = self.request.query_params.get('year', timezone.now().year)
        filters = {}
        if month is not None:
            filters['date__month'] = month
        filters['date__year'] = year
        return filters

    def get_queryset(self):
        """
        Returns a queryset of Receipt objects, optionally filtered by month and year.

        Query parameters:
            - month: Filter receipts by month of the date field.
            - year: Filter receipts by year of the date field.
        """
        user = self.request.user
        queryset = Receipt.objects.filter(user=user).prefetch_related('user', 'restaurant').select_related(
            'restaurant__address')
        filters = self.get_query_params()
        if filters:
            queryset = queryset.filter(**filters)
        return queryset

    def get_serializer_class(self):
        """
        Returns the appropriate serializer class based on the request method.

        Uses ReceiptsCreateSerializer for POST, PUT, PATCH requests.
        Uses ReceiptsSerializer for other requests.
        """
        if self.request and self.request.method in ('POST', 'PUT', 'PATCH'):
            return serializers.ReceiptsCreateSerializer
        return serializers.ReceiptsSerializer

    def destroy(self, request, *args, **kwargs):
        """
        Deletes a Receipt object and its associated image.
        """
        instance = self.get_object()
        instance.image.delete()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def create(self, request, *args, **kwargs):
        """
        Creates a new Receipt and triggers a background task to fetch restaurant details from Google Places API.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        restaurant_dict = serializer.validated_data.pop('restaurant')
        self.perform_create(serializer)
        receipt_obj = serializer.instance

        fetch_restaurant_details.delay(str(receipt_obj.id), restaurant_dict)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
