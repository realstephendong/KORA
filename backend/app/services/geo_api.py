"""
GeoDB Cities API service wrapper.
Provides functions to interact with the GeoDB Cities GraphQL API via RapidAPI.
"""

import os
import requests
import logging
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fetch_cities_for_country(country_name: str) -> List[str]:
    """
    Fetches the top 5 most populated cities for a given country using GeoDB Cities API.
    
    Args:
        country_name (str): The name of the country to search for cities
        
    Returns:
        List[str]: List of city names, or empty list if error occurs
    """
    try:
        # Get API credentials from environment
        rapidapi_key = os.environ.get('RAPIDAPI_KEY')
        rapidapi_host = os.environ.get('RAPIDAPI_HOST', 'geodb-cities-graphql.p.rapidapi.com')
        
        if not rapidapi_key:
            logger.error("RAPIDAPI_KEY not found in environment variables")
            return []
        
        # Prepare the GraphQL query
        query = f"""
        query {{
            countries(namePrefix: "{country_name}") {{
                edges {{
                    node {{
                        name
                        populatedPlaces(first: 5) {{
                            edges {{
                                node {{
                                    name
                                    population
                                }}
                            }}
                        }}
                    }}
                }}
            }}
        }}
        """
        
        # Prepare headers
        headers = {
            'x-rapidapi-key': rapidapi_key,
            'x-rapidapi-host': rapidapi_host,
            'Content-Type': 'application/json'
        }
        
        # Prepare request payload
        payload = {
            'query': query
        }
        
        # Make the API request
        url = 'https://geodb-cities-graphql.p.rapidapi.com/'
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        # Check for successful response
        if response.status_code != 200:
            logger.error(f"API request failed with status {response.status_code}: {response.text}")
            return []
        
        # Parse the response
        data = response.json()
        
        # Handle GraphQL errors
        if 'errors' in data:
            logger.error(f"GraphQL errors: {data['errors']}")
            return []
        
        # Extract city names from the response
        cities = []
        countries_data = data.get('data', {}).get('countries', {})
        edges = countries_data.get('edges', [])
        
        if edges:
            # Get the first matching country
            country_node = edges[0].get('node', {})
            populated_places = country_node.get('populatedPlaces', {})
            place_edges = populated_places.get('edges', [])
            
            for edge in place_edges:
                node = edge.get('node', {})
                city_name = node.get('name')
                if city_name:
                    cities.append(city_name)
        
        logger.info(f"Successfully fetched {len(cities)} cities for {country_name}")
        return cities
        
    except requests.exceptions.Timeout:
        logger.error("API request timed out")
        return []
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error fetching cities: {str(e)}")
        return []


def fetch_city_details(city_name: str) -> Dict[str, Any]:
    """
    Fetches detailed information about a specific city.
    
    Args:
        city_name (str): The name of the city to get details for
        
    Returns:
        Dict[str, Any]: City details or empty dict if error occurs
    """
    try:
        rapidapi_key = os.environ.get('RAPIDAPI_KEY')
        rapidapi_host = os.environ.get('RAPIDAPI_HOST', 'geodb-cities-graphql.p.rapidapi.com')
        
        if not rapidapi_key:
            logger.error("RAPIDAPI_KEY not found in environment variables")
            return {}
        
        # Prepare the GraphQL query for city details
        query = f"""
        query {{
            populatedPlaces(namePrefix: "{city_name}", first: 1) {{
                edges {{
                    node {{
                        name
                        country {{
                            name
                        }}
                        population
                        latitude
                        longitude
                    }}
                }}
            }}
        }}
        """
        
        headers = {
            'x-rapidapi-key': rapidapi_key,
            'x-rapidapi-host': rapidapi_host,
            'Content-Type': 'application/json'
        }
        
        payload = {'query': query}
        url = 'https://geodb-cities-graphql.p.rapidapi.com/'
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code != 200:
            logger.error(f"API request failed with status {response.status_code}")
            return {}
        
        data = response.json()
        
        if 'errors' in data:
            logger.error(f"GraphQL errors: {data['errors']}")
            return {}
        
        # Extract city details
        populated_places_data = data.get('data', {}).get('populatedPlaces', {})
        edges = populated_places_data.get('edges', [])
        
        if edges:
            # Return the first matching city
            city_node = edges[0].get('node', {})
            country_info = city_node.get('country', {})
            country_name = country_info.get('name', '') if isinstance(country_info, dict) else str(country_info)
            
            return {
                'name': city_node.get('name', ''),
                'country': country_name,
                'population': city_node.get('population', 0),
                'latitude': city_node.get('latitude', 0),
                'longitude': city_node.get('longitude', 0)
            }
        
        return {}
        
    except Exception as e:
        logger.error(f"Error fetching city details for {city_name}: {str(e)}")
        return {}
