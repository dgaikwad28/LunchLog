import logging
import requests
from celery import shared_task
from django.conf import settings
from django.db import transaction
from user_api.models import Address, Restaurant, Receipt

GOOGLE_PLACES_API_KEY = settings.GOOGLE_API_KEY
GOOGLE_PLACES_API_URL = 'https://places.googleapis.com/v1/places'

logger = logging.getLogger("api")


@shared_task
@transaction.atomic
def fetch_restaurant_details(receipt_id: int, restaurant_dict: dict) -> bool:
    """
    Calls Google Places API to get restaurant details by name and updates/creates Address and Restaurant objects.
    """
    url = f"{GOOGLE_PLACES_API_URL}:searchText"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_PLACES_API_KEY,
        "X-Goog-FieldMask": "places.id,places.displayName,places.types,places.postalAddress,places.internationalPhoneNumber"
    }
    address_dict = restaurant_dict.pop('address')
    query_str = (f"{restaurant_dict.get('name')}, {address_dict.get('street')}, {address_dict.get('locality')}, "
                 f"{address_dict.get('postal_code')}, {address_dict.get('region_code')}")
    data = {
        "textQuery": query_str,
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        response_content = response.json()
    except Exception as e:
        logger.exception(f"Exception during Google Places API call for receipt_id={receipt_id}: {e}", exc_info=True)
        return False

    if response.status_code != 200:
        logger.error(
            f"Google Places API error for receipt_id={receipt_id}: {response_content.get('error', {}).get('message', 'Unknown error')}")
        return False

    if not response_content.get('places'):
        logger.warning(f"No places found for restaurant: {restaurant_dict.get('name')} (receipt_id={receipt_id})")
        return False

    #TODO: Assuming the first place is the most relevant one
    restaurant_place = response_content['places'][0]

    with transaction.atomic():
        address_obj, _ = Address.objects.update_or_create(
            google_place_id=restaurant_place.get('id'),
            defaults={
                'street': restaurant_place.get('postalAddress', {}).get('addressLines', [None])[0],
                'locality': restaurant_place.get('postalAddress', {}).get('locality'),
                'postal_code': restaurant_place.get('postalAddress', {}).get('postalCode'),
                'region_code': restaurant_place.get('postalAddress', {}).get('regionCode'),
                'phone_number': restaurant_place.get('internationalPhoneNumber')
            }
        )
        restaurant_obj, _ = Restaurant.objects.update_or_create(
            address=address_obj,
            defaults={
                'name': restaurant_dict['name'],
                'food_type': restaurant_place.get('types')
            }
        )
        receipt_obj = Receipt.objects.get(id=receipt_id)
        receipt_obj.restaurant = restaurant_obj
        receipt_obj.save()
    return True
