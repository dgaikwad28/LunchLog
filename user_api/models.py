import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)


class Receipt(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    # TODO: Add a choice field for currency if needed to define the currency
    currency = models.CharField(max_length=10, default='EUR')
    date = models.DateField(help_text='Format: YYYY-MM-DD')
    image = models.ImageField(
        upload_to='lunchlog/',
        default=None,
        blank=True,
        null=True)

    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='receipts')
    restaurant = models.ForeignKey('Restaurant', on_delete=models.CASCADE, related_name='receipts', blank=True,
                                   null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Receipt {self.id} - {self.user.username}'


class Address(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    google_place_id = models.CharField(max_length=255, unique=True, blank=True, null=True)

    street = models.CharField(max_length=255)
    locality = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    region_code = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.postal_code}, {self.region_code}'


class Restaurant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=255)
    food_type = models.JSONField(blank=True, null=True, default=list)
    address = models.OneToOneField('Address', on_delete=models.CASCADE, related_name='restaurant')

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.name}, {self.address}'
