from django.contrib.auth import get_user_model
from django.utils import timezone

from user_api.models import Receipt, Restaurant, Address

User = get_user_model()


class InitModelsUtil:
    def __init__(self):
        self.address_list_keys = None
        self.address_obj = None
        self.restaurant_obj = None
        self.receipt_list_keys = None
        self.receipt_obj = None
        self.user_response_keys = None
        self.login_response_keys = None
        self.user_password = None
        self.user_email = None
        self.user = None

    @classmethod
    def init_model_user_data(cls):
        user_password = "pass123"
        user_email = "user@example.com"
        User.objects.create_user(
            username=user_email,
            email=user_email,
            password=user_password,
            first_name='first_name',
            last_name='last_name'
        )

    def init_model_receipt_data(self):
        self.address_obj = Address.objects.create(street='123 Main St',
                                                  locality='Cityville',
                                                  postal_code='12345',
                                                  region_code='Country',
                                                  phone_number='1234567890')
        self.restaurant_obj = Restaurant.objects.create(name='restaurant_name',
                                                        food_type='food_type',
                                                        address=self.address_obj,)
        self.receipt_obj = Receipt.objects.create(price=10,
                                                  date=str(timezone.now().date()),
                                                  user=self.user,
                                                  restaurant=self.restaurant_obj,)

    def init_user_objects(self):
        self.user_password = "pass123"
        self.user_email = "user@example.com"

        self.user = User.objects.get(username=self.user_email)

    def init_response_keys(self):
        self.login_response_keys = ["refresh", "access", "user"]
        self.user_response_keys = ["pk", "username", "email", "first_name", "last_name"]

        self.receipt_list_keys = ['id', 'restaurant', 'user', 'price', 'currency', 'date', 'image', 'created',
                                  'updated']
        self.address_list_keys = ['id', 'street', 'locality', 'postal_code', 'region_code', 'phone_number', 'created',
                                  'updated']
