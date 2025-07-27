import json
import logging

import requests
from celery import shared_task
from django.conf import settings
from django.db import transaction

from user_api.models import Address, Restaurant, Receipt

GOOGLE_PLACES_API_KEY = settings.GOOGLE_API_KEY
GOOGLE_PLACES_API_URL = 'https://places.googleapis.com/v1/places'


@shared_task
def fetch_restaurant_details(receipt_id, restaurant_dict) -> bool:
    """
    Calls Google Places API to get restaurant details by name.
    """
    url = f"{GOOGLE_PLACES_API_URL}:searchText"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_PLACES_API_KEY,  # Replace with your actual API key
        "X-Goog-FieldMask": "places.id,places.displayName,places.types,places.postalAddress,"
                            "places.internationalPhoneNumber"
    }
    address_dict = restaurant_dict.pop('address')
    query_str = (f"{restaurant_dict.get('name')}, {address_dict.get('street')}, {address_dict.get('locality')}, "
                 f"{address_dict.get('postal_code')}, {address_dict.get('region_code')}")
    data = {
        "textQuery": query_str,
    }
    response = requests.post(url, headers=headers, json=data)
    response_content = json.loads(response.text)

    if response.status_code != 200:
        logging.error(f"Google Places API error: {response_content.get('error', {}).get('message', 'Unknown error')}")
        return False

    if not response_content.get('places'):
        logging.warning(f"No places found for restaurant: {restaurant_dict}")
        return False

    # Assuming the first place is the most relevant one

    restaurant_place = response_content['places'][0]

    with transaction.atomic():
        address_obj = update_create_address_obj(google_place_id=restaurant_place.get('id'),
                                                address_dict=restaurant_place.get('postalAddress'),
                                                phone_number=restaurant_place.get('internationalPhoneNumber'))
        restaurant_obj = create_update_restaurant_object(restaurant_dict=restaurant_dict,
                                                        types=restaurant_place.get('types'), address_obj=address_obj)
        receipt_obj = Receipt.objects.get(id=receipt_id)
        receipt_obj.restaurant = restaurant_obj
        receipt_obj.save()
    return True


def update_create_address_obj(address_dict, google_place_id, phone_number):
    """
    Updates or creates an Address object based on the place details.
    """
    with transaction.atomic():
        address_obj, created = Address.objects.update_or_create(
            google_place_id=google_place_id,
            defaults={
                'street': address_dict.get('addressLines')[0],
                'locality': address_dict.get('locality'),
                'postal_code': address_dict.get('postalCode'),
                'region_code': address_dict.get('regionCode'),
                'phone_number': phone_number
            }
        )
    return address_obj


def create_update_restaurant_object(restaurant_dict, types, address_obj):
    with transaction.atomic():
        restaurant_obj, created = Restaurant.objects.update_or_create(
            address=address_obj,
            defaults={
                'name': restaurant_dict['name'],
                'food_type': types
            }
        )
    return restaurant_obj
