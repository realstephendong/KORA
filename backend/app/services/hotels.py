import os
import requests
from typing import List, Dict, Any, Optional
import logging as logger
from dotenv import load_dotenv

from app.services.travel_data_api import get_city_coordinates

load_dotenv()

def fetch_hotels_in_city(city_name: str) -> List[Dict[str, Any]]:
    """
    Fetch hotels in a given city using Amadeus Hotel List API.
    
    Args:
        city_name (str): Name of the city to search for
        
    Returns:
        List[Dict[str, Any]]: List of hotel information dictionaries
    """
    load_dotenv()
    try:
        # Amadeus API requires both API key and API secret
        api_key = os.environ.get('AMADEUS_API_KEY')
        api_secret = os.environ.get('AMADEUS_SECRET_KEY')
        if not api_key or not api_secret:
            logger.error("AMADEUS_API_KEY and AMADEUS_API_SECRET environment variables are required")
            return []
        
        # First, get an access token from Amadeus
        token_url = "https://api.amadeus.com/v1/security/oauth2/token"
        token_data = {
            'grant_type': 'client_credentials',
            'client_id': api_key,
            'client_secret': api_secret,
            # 'hostname': 'production'
        }
        
        token_response = requests.post(token_url, data=token_data, timeout=10)
        
        if token_response.status_code != 200:
            logger.error(f"Failed to get Amadeus access token: {token_response.status_code} - {token_response.text}")
            return []
        
        access_token = token_response.json().get('access_token')
        if not access_token:
            logger.error("No access token received from Amadeus")
            return []
        
        # Get city coordinates for the hotel search
        coords = get_city_coordinates(city_name)
        if not coords:
            logger.warning(f"Could not get coordinates for {city_name}")
            return []
        
        # Amadeus Hotel List API endpoint - try different endpoint
        url = "https://api.amadeus.com/v1/reference-data/locations/hotels/by-geocode"
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        
        # Try with minimal required parameters first
        params = {
            'latitude': coords['lat'],
            'longitude': coords['lon']
        }
        
        logger.info(f"Making request to Amadeus API with params: {params}")
        response = requests.get(url, headers=headers, params=params, timeout=15)
        logger.info(f"Amadeus API response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            hotels = []
            
            # Parse Amadeus Hotel List response
            if 'data' in data:
                for hotel in data['data'][:5]:  # Limit to 5 hotels
                    hotel_info = {
                        'name': hotel.get('name', 'Unknown Hotel'),
                        'hotel_id': hotel.get('hotelId', ''),
                        'address': hotel.get('address', {}).get('lines', ['Address not available'])[0] if hotel.get('address', {}).get('lines') else 'Address not available',
                        'city': hotel.get('address', {}).get('cityName', city_name),
                        'country': hotel.get('address', {}).get('countryCode', ''),
                        'postal_code': hotel.get('address', {}).get('postalCode', ''),
                        'latitude': hotel.get('geoCode', {}).get('latitude'),
                        'longitude': hotel.get('geoCode', {}).get('longitude'),
                        'amenities': hotel.get('amenities', []),
                        'contact': hotel.get('contact', {}),
                        'description': hotel.get('description', {}).get('text', 'No description available'),
                        'rating': hotel.get('rating', 'Rating not available'),
                        'chain_code': hotel.get('chainCode', ''),
                        'iata_code': hotel.get('iataCode', ''),
                        'dupe_id': hotel.get('dupeId', ''),
                        'hotel_distance': hotel.get('hotelDistance', {}),
                        'self': hotel.get('self', '')
                    }
                    hotels.append(hotel_info)
            
            logger.info(f"Found {len(hotels)} hotels in {city_name}")
            return hotels
            
        elif response.status_code == 400:
            logger.warning(f"Bad request for {city_name}: {response.text}")
            return []
        elif response.status_code == 401:
            logger.error("Invalid Amadeus API credentials")
            return []
        elif response.status_code == 403:
            logger.error("Amadeus API access forbidden")
            return []
        elif response.status_code == 429:
            logger.error("Amadeus API rate limit exceeded")
            return []
        else:
            logger.error(f"Amadeus API error: {response.status_code} - {response.text}")
            return []
        
        url = "https://api.amadeus.com/v1/reference-data/locations/hotels/by-geocode"
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        
        # Try with minimal required parameters first
        params = {
            'latitude': coords['lat'],
            'longitude': coords['lon']
        }
        
        logger.info(f"Making request to Amadeus API with params: {params}")
        response = requests.get(url, headers=headers, params=params, timeout=15)
        logger.info(f"Amadeus API response status: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching hotels for {city_name}: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error fetching hotels for {city_name}: {str(e)}")
        return []


def fetch_hotel_price(hotel_id: str, check_in_date: str, check_out_date: str, adults: int = 1) -> Optional[Dict[str, Any]]:
    """
    Fetch hotel price for a specific hotel using Amadeus Hotel Price API.
    
    Args:
        hotel_id (str): Amadeus hotel ID
        check_in_date (str): Check-in date (format: YYYY-MM-DD)
        check_out_date (str): Check-out date (format: YYYY-MM-DD)
        adults (int): Number of adults (default: 1)
        
    Returns:
        Optional[Dict[str, Any]]: Hotel price information or None on error
    """
    try:
        # Amadeus API requires both API key and API secret
        api_key = os.environ.get('AMADEUS_API_KEY')
        api_secret = os.environ.get('AMADEUS_SECRET_KEY')
        
        if not api_key or not api_secret:
            logger.error("AMADEUS_API_KEY and AMADEUS_API_SECRET environment variables are required")
            return None
        
        # First, get an access token from Amadeus
        token_url = "https://api.amadeus.com/v1/security/oauth2/token"
        token_data = {
            'grant_type': 'client_credentials',
            'client_id': api_key,
            'client_secret': api_secret
        }
        
        token_response = requests.post(token_url, data=token_data, timeout=10)
        
        if token_response.status_code != 200:
            logger.error(f"Failed to get Amadeus access token: {token_response.status_code} - {token_response.text}")
            return None
        
        access_token = token_response.json().get('access_token')
        if not access_token:
            logger.error("No access token received from Amadeus")
            return None
        
        # Amadeus Hotel Price API endpoint
        url = "https://api.amadeus.com/v3/shopping/hotel-offers"
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        
        params = {
            'hotelIds': hotel_id,
            'checkInDate': check_in_date,
            'checkOutDate': check_out_date,
            'adults': adults,
            'currency': 'USD',
            'lang': 'EN'
        }
        
        logger.info(f"Making hotel price request to Amadeus API with params: {params}")
        response = requests.get(url, headers=headers, params=params, timeout=15)
        logger.info(f"Amadeus Hotel Price API response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if 'data' in data and len(data['data']) > 0:
                hotel_data = data['data'][0]
                
                price_info = {
                    'hotel_id': hotel_id,
                    'hotel_name': hotel_data.get('hotel', {}).get('name', 'Unknown Hotel'),
                    'check_in_date': check_in_date,
                    'check_out_date': check_out_date,
                    'adults': adults,
                    'offers': []
                }
                
                # Extract offers and pricing information
                if 'offers' in hotel_data:
                    for offer in hotel_data['offers']:
                        offer_info = {
                            'offer_id': offer.get('id', ''),
                            'room_type': offer.get('room', {}).get('type', 'Standard Room'),
                            'description': offer.get('room', {}).get('description', {}).get('text', 'No description'),
                            'price': offer.get('price', {}).get('total', 'Price not available'),
                            'currency': offer.get('price', {}).get('currency', 'USD'),
                            'base_price': offer.get('price', {}).get('base', 'Base price not available'),
                            'taxes': offer.get('price', {}).get('taxes', []),
                            'cancellation_policy': offer.get('policies', {}).get('cancellation', {}),
                            'payment_policy': offer.get('policies', {}).get('payment', {}),
                            'check_in_time': offer.get('checkInTime', ''),
                            'check_out_time': offer.get('checkOutTime', ''),
                            'guests': offer.get('guests', {}),
                            'self': offer.get('self', '')
                        }
                        price_info['offers'].append(offer_info)
                
                logger.info(f"Found {len(price_info['offers'])} price offers for hotel {hotel_id}")
                return price_info
            else:
                logger.warning(f"No price data available for hotel {hotel_id}")
                return None
                
        elif response.status_code == 400:
            logger.warning(f"Bad request for hotel {hotel_id}: {response.text}")
            return None
        elif response.status_code == 401:
            logger.error("Invalid Amadeus API credentials")
            return None
        elif response.status_code == 403:
            logger.error("Amadeus API access forbidden")
            return None
        elif response.status_code == 429:
            logger.error("Amadeus API rate limit exceeded")
            return None
        else:
            logger.error(f"Amadeus Hotel Price API error: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching hotel price for {hotel_id}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error fetching hotel price for {hotel_id}: {str(e)}")
        return None
