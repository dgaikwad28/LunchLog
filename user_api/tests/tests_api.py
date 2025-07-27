import json
import os
import uuid
from unittest.mock import patch

from django.conf import settings
from django.core.files import File
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIRequestFactory, APIClient
from rest_framework.test import force_authenticate

from user_api.models import Receipt
from user_api.tests.utils.common import InitModelsUtil
from user_api.views import ReceiptImageUploadView
from user_api.viewsets import ReceiptsViewSet

# set api request factory
api_request_factory = APIRequestFactory()


class UserLoginTestCase(TestCase, InitModelsUtil):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.init_model_user_data()

    def setUp(self) -> None:
        self.init_user_objects()
        self.init_response_keys()
        self.login_dict = {
            "username": self.user_email,
            "password": self.user_password,
        }

        self.login_url = reverse("user_api:login")

    def test_login_with_username_should_success(self):
        response = self.client.post(self.login_url, self.login_dict, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_content = json.loads(response.content)
        self.assertEqual(self.login_response_keys - response_content.keys(), set())
        self.assertEqual(self.user_response_keys - response_content.get('user').keys(), set())

    def test_login_with_wrong_username_should_fail(self):
        self.login_dict["username"] = "wrong_staff_email@example.com"
        response = self.client.post(self.login_url, self.login_dict, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response_content = json.loads(response.content)
        self.assertEqual(response_content.get('detail'), "No active account found with the given credentials")

    def test_login_with_wrong_password_should_fail(self):
        self.login_dict["password"] = "wrong_staff_password"
        response = self.client.post(self.login_url, self.login_dict, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response_content = json.loads(response.content)
        self.assertEqual(response_content.get('detail'), "No active account found with the given credentials")


class SignUpTestCase(TestCase, InitModelsUtil):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.init_model_user_data()

    def setUp(self) -> None:
        self.init_user_objects()
        self.init_response_keys()
        self.signup_dict = {
            "username": 'test_user',
            "email": 'test_user@test.com',
            "password1": 'YXNkZmdoamtsbGtqaGdmZHNh',
            "password2": 'YXNkZmdoamtsbGtqaGdmZHNh',
            "first_name": 'Max',
            "last_name": 'Miller',
        }
        self.signup_url = reverse("user_api:signup")

    def test_signup_should_success(self):
        response = self.client.post(self.signup_url, self.signup_dict, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_content = json.loads(response.content)
        self.assertEqual(self.login_response_keys - response_content.keys(), set())
        self.assertEqual(self.user_response_keys - response_content.get('user').keys(), set())

    def test_signup_with_existing_username_should_fail(self):
        self.signup_dict["username"] = self.user_email
        response = self.client.post(self.signup_url, self.signup_dict, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_content = json.loads(response.content)
        self.assertIn("username", response_content)

    def test_signup_with_existing_email_should_fail(self):
        self.signup_dict["email"] = self.user_email
        self.signup_dict["username"] = self.user_email
        response = self.client.post(self.signup_url, self.signup_dict, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_content = json.loads(response.content)
        self.assertIn("username", response_content)
        self.assertEqual(response_content.get('username'), ["A user with that username already exists."])

    def test_password_mismatch_should_fail(self):
        self.signup_dict["password2"] = "different_password"
        response = self.client.post(self.signup_url, self.signup_dict, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_content = json.loads(response.content)
        self.assertEqual(response_content.get('non_field_errors'), ["The two password fields didn't match."])


class ReceiptImageUploadTestCase(TestCase, InitModelsUtil):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.init_model_user_data()

    def setUp(self):
        self.init_user_objects()
        self.init_model_receipt_data()
        self.client = APIClient()
        self.upload_url = reverse("user_api:receipt-image-upload", kwargs={'pk': str(self.receipt_obj.pk)})
        self.receipt_image_upload_view = ReceiptImageUploadView.as_view()

    @patch("storages.backends.s3boto3.S3Boto3Storage.save", return_value="mocked_url")
    def test_receipt_image_upload_success(self, mock_save):
        image_url = os.path.join(settings.BASE_DIR, 'user_api', 'tests', 'utils', 'test.jpg')
        photo_file = File(open(image_url, 'rb'))

        data = {"image": photo_file}
        request = api_request_factory.put(self.upload_url, data=data)
        force_authenticate(request, user=self.user)
        response = self.receipt_image_upload_view(request, pk=str(self.receipt_obj.pk))
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_202_ACCEPTED])
        mock_save.assert_called()

    @patch("storages.backends.s3boto3.S3Boto3Storage.save", return_value="mocked_url")
    def test_receipt_image_upload_fail(self, mock_save):
        request = api_request_factory.put(self.upload_url, {}, format="multipart")
        force_authenticate(request, user=self.user)
        response = self.receipt_image_upload_view(request, pk=str(self.receipt_obj.id))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ReceiptsViewSetTestCase(TestCase, InitModelsUtil):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.init_model_user_data()

    def setUp(self):
        self.init_user_objects()
        self.init_model_receipt_data()
        self.init_response_keys()

        self.client = APIClient()

        self.list_url = reverse("user_api:receipts-list")
        self.list_view = ReceiptsViewSet.as_view({"get": "list"})

        self.detail_url = reverse("user_api:receipts-detail", kwargs={"pk": str(self.receipt_obj.pk)})
        self.detail_view = ReceiptsViewSet.as_view({"get": "retrieve"})

        self.create_view = ReceiptsViewSet.as_view({"post": "create"})

    def test_list_receipts(self):
        request = api_request_factory.get(self.list_url)
        force_authenticate(request, user=self.user)
        response = self.list_view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        response_content = json.loads(response.rendered_content)
        self.assertEqual(self.receipt_list_keys - response_content[0].keys(), set())
        self.assertEqual(self.address_list_keys - response_content[0].get('restaurant').get('address').keys(), set())

    def test_list_receipts_without_authorization(self):
        response = self.client.get(self.list_url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_receipts_present_year(self):
        self.receipt_obj.date = '2024-01-01'
        self.receipt_obj.save()

        request = api_request_factory.get(self.list_url)
        force_authenticate(request, user=self.user)
        response = self.list_view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_content = json.loads(response.rendered_content)
        self.assertEqual(len(response_content), 0)

    def test_list_receipts_query_param(self):
        self.receipt_obj.date = '2024-01-01'
        self.receipt_obj.save()

        request = api_request_factory.get(self.list_url, {'month': '1', 'year': '2024'})
        force_authenticate(request, user=self.user)
        response = self.list_view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_content = json.loads(response.rendered_content)
        self.assertEqual(len(response_content), 1)

    def test_retrieve_receipt(self):
        request = api_request_factory.get(self.detail_url)
        force_authenticate(request, user=self.user)
        response = self.detail_view(request, pk=str(self.receipt_obj.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIsInstance(response.data, dict)
        response_content = json.loads(response.rendered_content)
        self.assertEqual(response_content.get('id'), str(self.receipt_obj.pk))

    def test_retrieve_receipt_incorrect_id(self):
        incorrect_id = str(uuid.uuid4())
        request = api_request_factory.get(reverse("user_api:receipts-detail", kwargs={"pk": incorrect_id}))
        force_authenticate(request, user=self.user)
        response = self.detail_view(request, pk=incorrect_id)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_receipt(self):
        self.assertEqual(Receipt.objects.filter(user=self.user).count(), 1)
        data = {
            "user": self.user.pk,
            "price": 10.5,
            "date": "2025-07-26",
            "restaurant": {
                "name": "random_restaurant_name",
                "address": {
                    "street": "random_street",
                    "city": "random_city",
                    "state": "random_state",
                    "postal_code": "random_postal_code",
                    "region_code": "random_region_code",
                    "phone_number": "random_phone_number"
                }
            }
        }
        request = api_request_factory.post(self.list_url, data=data, format='json')
        force_authenticate(request, user=self.user)
        response = self.create_view(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response_content = json.loads(response.rendered_content)
        self.assertEqual(Receipt.objects.filter(user=self.user).count(), 2)
        self.assertNotEqual(response_content.get('id'), str(self.receipt_obj.pk))
