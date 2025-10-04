"""
AeroDataBox Flight API service wrapper.
Provides functions to search for flights using the AeroDataBox API via RapidAPI.
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
    Searches for flights between two airports using AeroDataBox API.
    
    Args:
        from_iata (str): IATA code of departure airport
        to_iata (str): IATA code of arrival airport
        date (str): Flight date in YYYY-MM-DD format
        
    Returns:
        List[Dict[str, Any]]: List of flight options with details
    """
    try:
        # Get API credentials from environment
        api_key = os.environ.get('AERODATABOX_API_KEY')
        api_host = os.environ.get('AERODATABOX_API_HOST', 'aerodatabox.p.rapidapi.com')
        
        if not api_key:
            logger.error("AERODATABOX_API_KEY not found in environment variables")
            return []
        
        # Validate date format
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            logger.error(f"Invalid date format: {date}. Expected YYYY-MM-DD")
            return []
        
        # Prepare headers
        headers = {
            'x-rapidapi-key': api_key,
            'x-rapidapi-host': api_host
        }
        
        # Use a shorter time range to comply with API limits (12 hours max)
        # Format: /flights/airports/{codeType}/{code}/{fromLocal}/{toLocal}
        url = f'https://aerodatabox.p.rapidapi.com/flights/airports/iata/{from_iata}/{date}T06:00/{date}T18:00'
        response = requests.get(url, headers=headers, timeout=15)
        
        # Check for successful response
        if response.status_code != 200:
            logger.error(f"API request failed with status {response.status_code}: {response.text}")
            return []
        
        # Parse the response
        data = response.json()
        
        # Handle API errors
        if 'error' in data:
            logger.error(f"API error: {data['error']}")
            return []
        
        # Extract flight information from AeroDataBox response
        flights = []
        departures = data.get('departures', [])
        
        for flight in departures:
            try:
                # Extract basic flight information
                airline = flight.get('airline', {}).get('name', 'Unknown')
                number_of_stops = flight.get('stops', 0)
                
                # Calculate duration in minutes
                departure_time = flight.get('departure', {}).get('scheduledTimeLocal', '')
                arrival_time = flight.get('arrival', {}).get('scheduledTimeLocal', '')
                duration_minutes = _calculate_duration(departure_time, arrival_time)
                
                # Create flight option dictionary
                flight_option = {
                    'airline': airline,
                    'number_of_stops': number_of_stops,
                    'duration_minutes': duration_minutes,
                    'departure_time': departure_time,
                    'arrival_time': arrival_time,
                    'route': f"{from_iata} to {to_iata}"
                }
                
                flights.append(flight_option)
                
            except Exception as e:
                logger.warning(f"Error processing flight data: {str(e)}")
                continue
        
        logger.info(f"Found {len(flights)} flights from {from_iata} to {to_iata}")
        return flights
        
    except requests.exceptions.Timeout:
        logger.error("API request timed out")
        return []
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error searching flights: {str(e)}")
        return []


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
