"""
Travel data API service for the travel planner application.
Provides functions for fetching points of interest and calculating distances using free APIs.
"""

import os
import requests
from typing import List, Dict, Any, Optional
import logging

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
        
        if data and 'lon' in data and 'lat' in data:
            logger.info(f"Found coordinates for {city_name}: {data['lat']}, {data['lon']}")
            return {
                'lon': float(data['lon']),
                'lat': float(data['lat'])
            }
        else:
            logger.warning(f"No coordinates found for {city_name}")
            # Fallback to hardcoded coordinates for major cities
            major_cities_coords = {
                'paris': {'lat': 48.8566, 'lon': 2.3522},
                'lyon': {'lat': 45.7640, 'lon': 4.8357},
                'nice': {'lat': 43.7102, 'lon': 7.2620},
                'london': {'lat': 51.5074, 'lon': -0.1278},
                'rome': {'lat': 41.9028, 'lon': 12.4964},
                'berlin': {'lat': 52.5200, 'lon': 13.4050}
            }
            
            city_key = city_name.lower()
            if city_key in major_cities_coords:
                coords = major_cities_coords[city_key]
                logger.info(f"Using hardcoded coordinates for {city_name}: {coords['lat']}, {coords['lon']}")
                return coords
            
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
