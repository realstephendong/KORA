"""
Amadeus Flight API service wrapper.
Provides functions to search for flights using the Amadeus API (free tier: 2000 calls/month).
"""

import os
import requests
import logging
from typing import List, Dict, Any
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def search_flights(from_iata: str, to_iata: str, date: str) -> List[Dict[str, Any]]:
    """
    Searches for flights between two airports using Amadeus API production environment.
    
    Uses real-time flight data and pricing from the production Amadeus API.
    Returns actual market prices and flight availability.
    
    Args:
        from_iata (str): IATA code of departure airport
        to_iata (str): IATA code of arrival airport
        date (str): Flight date in YYYY-MM-DD format
        
    Returns:
        List[Dict[str, Any]]: List of flight options with real pricing and details
    """
    try:
        # Get Amadeus API credentials
        amadeus_api_key = os.environ.get('AMADEUS_API_KEY')
        amadeus_api_secret = os.environ.get('AMADEUS_API_SECRET')
        
        if not amadeus_api_key or not amadeus_api_secret:
            logger.warning("AMADEUS_API_KEY and AMADEUS_API_SECRET not found in environment variables")
            logger.warning("Returning mock flight data for testing purposes")
            return _get_mock_flight_data(from_iata, to_iata, date)
        
        # Validate date format
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            logger.error(f"Invalid date format: {date}. Expected YYYY-MM-DD")
            return []
        
        # Amadeus API endpoints - using production environment for real pricing
        base_url = "https://api.amadeus.com"
        
        # First, get access token
        token_url = f"{base_url}/v1/security/oauth2/token"
        token_data = {
            'grant_type': 'client_credentials',
            'client_id': amadeus_api_key,
            'client_secret': amadeus_api_secret
        }
        
        token_response = requests.post(token_url, data=token_data, timeout=10)
        
        if token_response.status_code != 200:
            logger.error(f"Amadeus token request failed: {token_response.status_code}")
            logger.warning("Amadeus API credentials are invalid, returning mock data")
            return _get_mock_flight_data(from_iata, to_iata, date)
        
        access_token = token_response.json().get('access_token')
        if not access_token:
            logger.error("No access token received from Amadeus")
            return []
        
        # Search for flights
        headers = {'Authorization': f'Bearer {access_token}'}
        search_url = f"{base_url}/v2/shopping/flight-offers"
        
        params = {
            'originLocationCode': from_iata,
            'destinationLocationCode': to_iata,
            'departureDate': date,
            'adults': 1,
            'max': 5  # Limit to 5 results
        }
        
        search_response = requests.get(search_url, headers=headers, params=params, timeout=15)
        
        if search_response.status_code != 200:
            logger.error(f"Amadeus flight search failed: {search_response.status_code}")
            logger.warning("Flight search failed, returning mock data")
            return _get_mock_flight_data(from_iata, to_iata, date)
        
        flight_data = search_response.json()
        
        if 'data' not in flight_data or not flight_data['data']:
            logger.warning("No flight data returned from Amadeus")
            return []
        
        # Extract flight information from Amadeus response
        flights = []
        flight_options = flight_data['data']
        
        for flight in flight_options:
            try:
                # Extract pricing information
                price_info = flight.get('price', {})
                total_price = price_info.get('total', 0)
                currency = price_info.get('currency', 'USD')
                
                # Extract itinerary information
                itineraries = flight.get('itineraries', [])
                if not itineraries:
                    continue
                
                first_itinerary = itineraries[0]
                segments = first_itinerary.get('segments', [])
                if not segments:
                    continue
                
                # Get flight details - use first segment for departure, last for arrival
                first_segment = segments[0]
                last_segment = segments[-1]
                
                # For connecting flights, show the operating airline of the first segment
                airline_code = first_segment.get('carrierCode', 'Unknown')
                departure_time = first_segment.get('departure', {}).get('at', '')
                arrival_time = last_segment.get('arrival', {}).get('at', '')
                
                # Count stops
                stops = len(segments) - 1
                
                # Create flight option dictionary with real pricing data
                flight_option = {
                    'airline': airline_code,
                    'price': total_price,
                    'currency': currency,
                    'departure_time': departure_time,
                    'arrival_time': arrival_time,
                    'stops': stops,
                    'route': f"{from_iata} to {to_iata}",
                    'is_direct': stops == 0,
                    'source': 'Amadeus API (Production - Real-time)'
                }
                
                flights.append(flight_option)
                
            except Exception as e:
                logger.warning(f"Error processing flight data: {str(e)}")
                continue
        
        logger.info(f"Found {len(flights)} flights from {from_iata} to {to_iata} with pricing")
        return flights
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching flights from Amadeus: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error fetching flights: {str(e)}")
        return []


def _get_mock_flight_data(from_iata: str, to_iata: str, date: str) -> List[Dict[str, Any]]:
    """
    Returns mock flight data for testing when Amadeus API is not available.
    Uses realistic pricing ranges for the route.
    
    NOTE: To get real-time flight data, set up valid Amadeus API credentials
    in your .env file with AMADEUS_API_KEY and AMADEUS_API_SECRET.
    """
    # Realistic price ranges for JFK to CDG (New York to Paris)
    base_prices = [450, 520, 680, 750, 890]
    airlines = ['AF', 'DL', 'AA', 'UA', 'VS']
    
    mock_flights = []
    for i, (price, airline) in enumerate(zip(base_prices, airlines)):
        flight = {
            'airline': airline,
            'price': price,
            'currency': 'USD',
            'departure_time': f'{date}T{10 + i*2:02d}:00:00',
            'arrival_time': f'{date}T{18 + i*2:02d}:00:00',
            'stops': 0 if i < 3 else 1,
            'route': f"{from_iata} to {to_iata}",
            'is_direct': i < 3,
            'source': 'Mock Data (Amadeus API Unavailable)',
            'warning': 'These are estimated prices for demonstration purposes only. Set up valid Amadeus API credentials for real-time pricing.'
        }
        mock_flights.append(flight)
    
    logger.info(f"Returning {len(mock_flights)} mock flights for {from_iata} to {to_iata}")
    return mock_flights


def _get_city_name_from_iata(iata_code: str) -> str:
    """
    Map IATA airport codes to city names for carbon calculations.
    
    Args:
        iata_code (str): IATA airport code
        
    Returns:
        str: City name
    """
    # Common IATA to city mappings
    iata_to_city = {
        'JFK': 'New York',
        'LGA': 'New York', 
        'EWR': 'New York',
        'CDG': 'Paris',
        'LHR': 'London',
        'FRA': 'Frankfurt',
        'MAD': 'Madrid',
        'FCO': 'Rome',
        'LAX': 'Los Angeles',
        'SFO': 'San Francisco',
        'ORD': 'Chicago',
        'ATL': 'Atlanta',
        'MIA': 'Miami',
        'SEA': 'Seattle',
        'BOS': 'Boston',
        'DFW': 'Dallas',
        'DEN': 'Denver',
        'LAS': 'Las Vegas',
        'PHX': 'Phoenix',
        'IAH': 'Houston',
        'MCO': 'Orlando',
        'YVR': 'Vancouver',
        'YYZ': 'Toronto',
        'YUL': 'Montreal',
        'NRT': 'Tokyo',
        'ICN': 'Seoul',
        'PEK': 'Beijing',
        'SYD': 'Sydney',
        'MEL': 'Melbourne',
        'GRU': 'São Paulo',
        'DEL': 'Delhi',
        'MEX': 'Mexico City',
        'AMS': 'Amsterdam',
        'BRU': 'Brussels',
        'ZUR': 'Zurich',
        'VIE': 'Vienna',
        'ARN': 'Stockholm',
        'OSL': 'Oslo',
        'CPH': 'Copenhagen',
        'HEL': 'Helsinki',
        'WAW': 'Warsaw',
        'PRG': 'Prague',
        'BUD': 'Budapest',
        'LIS': 'Lisbon',
        'ATH': 'Athens',
        'IST': 'Istanbul',
        'SVO': 'Moscow'
    }
    
    return iata_to_city.get(iata_code, '')


def _calculate_duration(departure_time: str, arrival_time: str) -> int:
    """
    Calculates flight duration in minutes from departure and arrival times.
    
    Args:
        departure_time (str): Departure time string
        arrival_time (str): Arrival time string
        
    Returns:
        int: Duration in minutes, or 0 if calculation fails
    """
    try:
        if not departure_time or not arrival_time:
            return 0
        
        # Parse times (assuming ISO format or similar)
        # This is a simplified calculation - in production you'd want more robust parsing
        dep_time = datetime.fromisoformat(departure_time.replace('Z', '+00:00'))
        arr_time = datetime.fromisoformat(arrival_time.replace('Z', '+00:00'))
        
        # Calculate difference in minutes
        duration = (arr_time - dep_time).total_seconds() / 60
        return max(0, int(duration))
        
    except Exception as e:
        logger.warning(f"Error calculating duration: {str(e)}")
        return 0
