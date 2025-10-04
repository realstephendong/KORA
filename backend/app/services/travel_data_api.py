"""
Travel data API service for the travel planner application.
Provides functions for fetching points of interest and calculating distances using free APIs.
"""

import os
import requests
from typing import List, Dict, Any, Optional
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



def get_city_coordinates(city_name: str) -> Optional[Dict[str, float]]:
    """
    Get coordinates for a city using OpenTripMap geoname API.
    
    Args:
        city_name (str): Name of the city to find coordinates for
        
    Returns:
        Optional[Dict[str, float]]: Dictionary with 'lon' and 'lat' keys, or None on failure
    """
    try:
        api_key = os.environ.get('OPENTRIPMAP_API_KEY')
        if not api_key:
            logger.error("OPENTRIPMAP_API_KEY environment variable is required")
            return None
        
        # Handle specific city disambiguation with country codes
        search_name = city_name
        if city_name.lower() == 'paris':
            search_name = 'Paris, France'  # More specific for France with comma
        elif city_name.lower() == 'london':
            search_name = 'London, England'  # More specific for UK
        elif city_name.lower() == 'rome':
            search_name = 'Rome, Italy'  # More specific for Italy
        elif city_name.lower() == 'berlin':
            search_name = 'Berlin, Germany'  # More specific for Germany
        elif city_name.lower() == 'lyon':
            search_name = 'Lyon, France'  # More specific for France
        elif city_name.lower() == 'nice':
            search_name = 'Nice, France'  # More specific for France
        
        # OpenTripMap geoname endpoint
        url = "https://api.opentripmap.com/0.1/en/places/geoname"
        params = {
            'name': search_name,
            'apikey': api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Fallback to hardcoded coordinates for major cities first
        major_cities_coords = {
            'paris': {'lat': 48.8566, 'lon': 2.3522},
            'lyon': {'lat': 45.7640, 'lon': 4.8357},
            'nice': {'lat': 43.7102, 'lon': 7.2620},
            'london': {'lat': 51.5074, 'lon': -0.1278},
            'rome': {'lat': 41.9028, 'lon': 12.4964},
            'berlin': {'lat': 52.5200, 'lon': 13.4050},
            'cdg': {'lat': 49.0097, 'lon': 2.5479},  # Charles de Gaulle Airport
            'charles de gaulle': {'lat': 49.0097, 'lon': 2.5479}
        }
        
        city_key = city_name.lower().strip()
        if city_key in major_cities_coords:
            coords = major_cities_coords[city_key]
            logger.info(f"Using hardcoded coordinates for {city_name}: {coords['lat']}, {coords['lon']}")
            return coords
        
        # If API data is available, validate it before using
        if data and 'lon' in data and 'lat' in data:
            lat = float(data['lat'])
            lon = float(data['lon'])
            
            # Validate coordinates are reasonable (not obviously wrong)
            if -90 <= lat <= 90 and -180 <= lon <= 180:
                logger.info(f"Found coordinates for {city_name}: {lat}, {lon}")
                return {
                    'lon': lon,
                    'lat': lat
                }
            else:
                logger.warning(f"Invalid coordinates from API for {city_name}: {lat}, {lon}")
        
        logger.warning(f"No valid coordinates found for {city_name}")
        return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching coordinates for {city_name}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error fetching coordinates for {city_name}: {str(e)}")
        return None


def fetch_points_of_interest(city_name: str) -> List[str]:
    """
    Fetch points of interest for a given city using OpenTripMap API.
    
    Args:
        city_name (str): Name of the city to search for
        
    Returns:
        List[str]: List of attraction names
    """
    try:
        # First get city coordinates
        coords = get_city_coordinates(city_name)
        if not coords:
            logger.warning(f"Could not get coordinates for {city_name}")
            return []
        
        api_key = os.environ.get('OPENTRIPMAP_API_KEY')
        if not api_key:
            logger.error("OPENTRIPMAP_API_KEY environment variable is required")
            return []
        
        # OpenTripMap radius endpoint to find attractions within 5km
        url = "https://api.opentripmap.com/0.1/en/places/radius"
        params = {
            'radius': 5000,  # 5km radius
            'lon': coords['lon'],
            'lat': coords['lat'],
            'apikey': api_key,
            'limit': 10,
            'format': 'json'
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code != 200:
            logger.error(f"OpenTripMap API error: {response.status_code} - {response.text}")
            return []
        
        data = response.json()
        
        
        attractions = []
        if isinstance(data, list):
            # OpenTripMap returns a list directly
            for item in data[:10]:  # Limit to 10 attractions
                if 'name' in item and item['name']:  # Only include items with names
                    attractions.append(item['name'])
        elif isinstance(data, dict) and 'features' in data:
            # GeoJSON format
            for feature in data['features'][:10]:  # Limit to 10 attractions
                if 'properties' in feature and 'name' in feature['properties']:
                    attractions.append(feature['properties']['name'])
        
        logger.info(f"Found {len(attractions)} points of interest for {city_name}")
        return attractions
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching points of interest for {city_name}: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error fetching points of interest for {city_name}: {str(e)}")
        return []

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


def fetch_distance_between_cities(cities: List[str]) -> Optional[Dict[str, Any]]:
    """
    Calculate distance between cities using OpenRouteService API.
    
    Args:
        cities (List[str]): List of city names in travel order
        
    Returns:
        Optional[Dict[str, Any]]: Dictionary with distance and duration, or None on error
    """
    try:
        if len(cities) < 2:
            logger.warning("Need at least 2 cities for distance calculation")
            return None
        
        # Get coordinates for all cities
        coordinates = []
        for city in cities:
            coords = get_city_coordinates(city)
            if not coords:
                logger.error(f"Could not get coordinates for {city}")
                return None
            coordinates.append([coords['lon'], coords['lat']])
        
        api_key = os.environ.get('OPENROUTESERVICE_API_KEY')
        if not api_key:
            logger.error("OPENROUTESERVICE_API_KEY environment variable is required")
            return None
        
        # OpenRouteService directions API
        url = "https://api.openrouteservice.org/v2/directions/driving-car"
        headers = {
            'Authorization': api_key,
            'Content-Type': 'application/json'
        }
        
        # Calculate total distance by summing distances between consecutive cities
        total_distance = 0
        total_duration = 0
        
        for i in range(len(coordinates) - 1):
            origin = coordinates[i]
            destination = coordinates[i + 1]
            
            payload = {
                'coordinates': [origin, destination]
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            
            if response.status_code != 200:
                logger.error(f"OpenRouteService API error: {response.status_code} - {response.text}")
                # If it's a distance limit error, try to calculate a rough estimate
                if response.status_code == 400 and "distance must not be greater than" in response.text:
                    # Calculate straight-line distance as fallback
                    import math
                    lat1, lon1 = origin[1], origin[0]
                    lat2, lon2 = destination[1], destination[0]
                    
                    # Haversine formula for straight-line distance
                    R = 6371000  # Earth's radius in meters
                    dlat = math.radians(lat2 - lat1)
                    dlon = math.radians(lon2 - lon1)
                    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
                    c = 2 * math.asin(math.sqrt(a))
                    distance = R * c
                    
                    # Estimate driving distance as 1.3x straight-line distance
                    driving_distance = distance * 1.3
                    duration = driving_distance / 13.89  # Assume 50 km/h average speed
                    
                    total_distance += driving_distance
                    total_duration += duration
                    
                    logger.info(f"Using straight-line distance estimate from {cities[i]} to {cities[i+1]}: {driving_distance}m")
                continue
            
            data = response.json()
            
            if 'routes' in data and len(data['routes']) > 0:
                route = data['routes'][0]
                if 'summary' in route:
                    summary = route['summary']
                    distance = summary.get('distance', 0)
                    duration = summary.get('duration', 0)
                    
                    total_distance += distance
                    total_duration += duration
                    
                    logger.info(f"Distance from {cities[i]} to {cities[i+1]}: {distance}m, {duration}s")
                else:
                    logger.warning(f"No summary in response for {cities[i]} to {cities[i+1]}")
            elif 'features' in data and len(data['features']) > 0:
                # Fallback for GeoJSON format
                feature = data['features'][0]
                if 'properties' in feature and 'summary' in feature['properties']:
                    summary = feature['properties']['summary']
                    distance = summary.get('distance', 0)
                    duration = summary.get('duration', 0)
                    
                    total_distance += distance
                    total_duration += duration
                    
                    logger.info(f"Distance from {cities[i]} to {cities[i+1]}: {distance}m, {duration}s")
                else:
                    logger.warning(f"No summary in response for {cities[i]} to {cities[i+1]}")
            else:
                logger.warning(f"Could not calculate distance from {cities[i]} to {cities[i+1]}")
        
        return {
            'total_distance_meters': total_distance,
            'total_duration_seconds': total_duration,
            'cities': cities
        }
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error calculating distance between cities {cities}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error calculating distance between cities {cities}: {str(e)}")
        return None
