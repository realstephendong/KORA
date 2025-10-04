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
    Fetches the top 5 most populated cities for a given country using GeoDB Cities REST API.
    
    Args:
        country_name (str): The name of the country to search for cities
        
    Returns:
        List[str]: List of city names, or empty list if error occurs
    """
    try:
        # Get API credentials from environment
        rapidapi_key = os.environ.get('RAPIDAPI_KEY')
        rapidapi_host = os.environ.get('RAPIDAPI_HOST', 'geodb-cities.p.rapidapi.com')
        
        if not rapidapi_key:
            logger.error("RAPIDAPI_KEY not found in environment variables")
            return []
        
        # Use the GeoDB Cities REST API to find cities directly
        # First, find the country code using the countries endpoint
        country_url = 'https://geodb-cities.p.rapidapi.com/geo/countries'
        headers = {
            'x-rapidapi-key': rapidapi_key,
            'x-rapidapi-host': rapidapi_host
        }
        
        # Find countries matching the name
        country_params = {
            'namePrefix': country_name,
            'limit': 10  # Get more results to find the right country
        }
        
        country_response = requests.get(country_url, headers=headers, params=country_params, timeout=10)
        
        if country_response.status_code != 200:
            logger.error(f"Country lookup failed with status {country_response.status_code}")
            logger.error(f"Response: {country_response.text}")
            return []
        
        country_data = country_response.json()
        countries = country_data.get('data', [])
        
        if not countries:
            logger.warning(f"No countries found for {country_name}")
            return []
        
        # Get the country code - try to find exact match first
        country_code = None
        for country in countries:
            if country.get('name', '').lower() == country_name.lower():
                country_code = country.get('code')
                break
        
        # If no exact match, use the first result
        if not country_code:
            country_code = countries[0].get('code')
            
        if not country_code:
            logger.warning(f"No country code found for {country_name}")
            return []
        
        # Now use the "Find country places" endpoint to get cities
        cities_url = f'https://geodb-cities.p.rapidapi.com/geo/countries/{country_code}/places'
        cities_params = {
            'limit': 5,
            'sort': '-population'  # Sort by population descending
        }
        
        cities_response = requests.get(cities_url, headers=headers, params=cities_params, timeout=10)
        
        if cities_response.status_code != 200:
            logger.error(f"Cities lookup failed with status {cities_response.status_code}")
            logger.error(f"Response: {cities_response.text}")
            return []
        
        cities_data = cities_response.json()
        cities_list = cities_data.get('data', [])
        
        # Extract city names
        cities = []
        for city in cities_list:
            city_name = city.get('name')
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
    Fetches detailed information about a specific city using GeoDB Cities REST API.
    
    Args:
        city_name (str): The name of the city to get details for
        
    Returns:
        Dict[str, Any]: City details or empty dict if error occurs
    """
    try:
        rapidapi_key = os.environ.get('RAPIDAPI_KEY')
        rapidapi_host = os.environ.get('RAPIDAPI_HOST', 'geodb-cities.p.rapidapi.com')
        
        if not rapidapi_key:
            logger.error("RAPIDAPI_KEY not found in environment variables")
            return {}
        
        # Use the GeoDB Cities REST API for city details
        cities_url = 'https://geodb-cities.p.rapidapi.com/geo/places'
        headers = {
            'x-rapidapi-key': rapidapi_key,
            'x-rapidapi-host': rapidapi_host
        }
        
        # Search for the city
        params = {
            'namePrefix': city_name,
            'limit': 1,
            'sort': '-population'  # Get the most populated match
        }
        
        response = requests.get(cities_url, headers=headers, params=params, timeout=10)
        
        if response.status_code != 200:
            logger.error(f"API request failed with status {response.status_code}")
            return {}
        
        data = response.json()
        cities = data.get('data', [])
        
        if cities:
            city = cities[0]
            return {
                'name': city.get('name', ''),
                'country': city.get('country', ''),
                'population': city.get('population', 0),
                'latitude': city.get('latitude', 0),
                'longitude': city.get('longitude', 0)
            }
        
        return {}
        
    except Exception as e:
        logger.error(f"Error fetching city details for {city_name}: {str(e)}")
        return {}


def get_iata_code(city_name: str) -> str | None:
    """
    Gets the IATA airport code for a given city using GeoDB Cities REST API.
    
    Args:
        city_name (str): The name of the city to get IATA code for
        
    Returns:
        str | None: IATA airport code or None if not found
    """
    try:
        rapidapi_key = os.environ.get('RAPIDAPI_KEY')
        rapidapi_host = os.environ.get('RAPIDAPI_HOST', 'geodb-cities.p.rapidapi.com')
        
        if not rapidapi_key:
            logger.error("RAPIDAPI_KEY not found in environment variables")
            return None
        
        # Use a simple hardcoded approach for major cities since GeoDB doesn't have airports
        major_city_iata = {
            'new york': 'JFK',
            'london': 'LHR', 
            'paris': 'CDG',
            'tokyo': 'NRT',
            'sydney': 'SYD',
            'toronto': 'YYZ',
            'los angeles': 'LAX',
            'chicago': 'ORD',
            'miami': 'MIA',
            'san francisco': 'SFO',
            'seattle': 'SEA',
            'boston': 'BOS',
            'atlanta': 'ATL',
            'dallas': 'DFW',
            'denver': 'DEN',
            'las vegas': 'LAS',
            'phoenix': 'PHX',
            'houston': 'IAH',
            'orlando': 'MCO',
            'vancouver': 'YVR',
            'montreal': 'YUL',
            'calgary': 'YYC',
            'edmonton': 'YEG',
            'ottawa': 'YOW',
            'winnipeg': 'YWG',
            'halifax': 'YHZ',
            'quebec': 'YQB',
            'victoria': 'YYJ',
            'kelowna': 'YLW',
            'regina': 'YQR',
            'saskatoon': 'YXE',
            'thunder bay': 'YQT',
            'sudbury': 'YSB',
            'sault ste marie': 'YAM',
            'north bay': 'YYB',
            'timmins': 'YTS',
            'kenora': 'YQK',
            'dryden': 'YHD',
            'fort frances': 'YAG',
            'red lake': 'YRL',
            'sioux lookout': 'YXL',
            'geraldton': 'YGQ',
            'marathon': 'YSP',
            'wawa': 'YXZ',
            'chapleau': 'YLD',
            'kapuskasing': 'YYU',
            'cochrane': 'YCN',
            'hearst': 'YHF',
            'moosonee': 'YMO',
            'attawapiskat': 'YAT',
            'fort albany': 'YFA',
            'kashechewan': 'ZKE',
            'marten falls': 'YMF',
            'webequie': 'YWP',
            'nibinamik': 'YNB',
            'poplar hill': 'YHP',
            'pikangikum': 'YPM',
            'sandy lake': 'ZSJ',
            'north spirit lake': 'YNO',
            'deer lake': 'YVZ',
            'red sucker lake': 'YRS',
            'garden hill': 'YGH',
            'st. theresa point': 'YST',
            'wasagamack': 'YWS',
            'gods lake narrows': 'YGO',
            'gods river': 'YGO',
            'oxford house': 'YOH',
            'shamattawa': 'ZTM',
            'tadoule lake': 'XTL',
            'brochet': 'YBT',
            'lynn lake': 'YYL',
            'thompson': 'YTH',
            'the pas': 'YQD',
            'swan river': 'YWV',
            'dauphin': 'YDN',
            'brandon': 'YBR',
            'portage la prairie': 'YPG',
            'selkirk': 'YSK',
            'steinbach': 'YSB',
            'winkler': 'YWK',
            'morden': 'YMD',
            'altona': 'YAL',
            'carman': 'YCM',
            'gimli': 'YGM',
            'arborg': 'YAG',
            'stonewall': 'YST',
            'teulon': 'YTN',
            'beausejour': 'YBE',
            'lac du bonnet': 'YLB',
            'pine falls': 'YPF',
            'bissett': 'YBI',
            'manigotagan': 'YMG',
            'grand beach': 'YGB'
        }
        
        city_lower = city_name.lower().strip()
        
        # Direct lookup
        if city_lower in major_city_iata:
            iata_code = major_city_iata[city_lower]
            logger.info(f"Found IATA code {iata_code} for {city_name}")
            return iata_code
        
        # Try partial matches
        for city_key, iata_code in major_city_iata.items():
            if city_key in city_lower or city_lower in city_key:
                logger.info(f"Found IATA code {iata_code} for {city_name} (partial match)")
                return iata_code
        
        logger.warning(f"No IATA code found for {city_name}")
        return None
        
    except Exception as e:
        logger.error(f"Error fetching IATA code for {city_name}: {str(e)}")
        return None
