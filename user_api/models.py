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


class Restaurant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    food_type = models.CharField(max_length=100, blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
