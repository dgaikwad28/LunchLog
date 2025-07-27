import unittest
from unittest.mock import MagicMock

from django.utils import timezone

from user_api.viewsets import ReceiptsViewSet


class TestGetQueryParams(unittest.TestCase):
    def setUp(self):
        self.viewset = ReceiptsViewSet()
        self.viewset.request = MagicMock()

    def test_month_and_year_provided(self):
        self.viewset.request.query_params = {'month': '5', 'year': '2023'}
        filters = self.viewset.get_query_params()
        self.assertEqual(filters, {'date__month': '5', 'date__year': '2023'})

    def test_only_month_provided(self):
        current_year = timezone.now().year
        self.viewset.request.query_params = {'month': '7'}
        filters = self.viewset.get_query_params()
        self.assertEqual(filters, {'date__month': '7', 'date__year': current_year})

    def test_only_year_provided(self):
        self.viewset.request.query_params = {'year': '2022'}
        filters = self.viewset.get_query_params()
        self.assertEqual(filters, {'date__year': '2022'})

    def test_neither_month_nor_year_provided(self):
        current_year = timezone.now().year
        self.viewset.request.query_params = {}
        filters = self.viewset.get_query_params()
        self.assertEqual(filters, {'date__year': current_year})

    def test_month_is_none(self):
        current_year = timezone.now().year
        self.viewset.request.query_params = {'month': None}
        filters = self.viewset.get_query_params()
        self.assertEqual(filters, {'date__year': current_year})
