"""
LangChain tools for the travel planner agent.
Provides tools for fetching city data, points of interest, calculating travel details, and saving itineraries.
"""

from typing import List, Dict, Any, Union
import logging
from langchain.tools import tool
from app.services.geo_api import fetch_cities_for_country
from app.services.travel_data_api import fetch_points_of_interest, fetch_distance_between_cities
from app.services.culture_data import fetch_itinerary_list
from app.models.itinerary import Itinerary
from app import db

# Configure logging
logger = logging.getLogger(__name__)


@tool
def get_recommended_cities(country_name: str) -> List[str]:
    """
    Fetches the top 5 most populated cities for a given country.
    Use this to get initial city recommendations when a user mentions a country.
    
    Args:
        country_name (str): The name of the country to get cities for
        
    Returns:
        List[str]: List of the top 5 most populated city names
    """
    try:
        # Handle case where agent passes parameter as dict string
        if isinstance(country_name, dict):
            country_name = country_name.get('country_name', '')
        elif isinstance(country_name, str) and country_name.startswith('{'):
            # Try to extract from JSON-like string
            import json
            try:
                parsed = json.loads(country_name)
                country_name = parsed.get('country_name', '')
            except:
                pass
        
        # Handle case where agent passes parameter as string representation of dict
        if isinstance(country_name, str) and country_name.startswith("{'country_name':"):
            # Extract the country name from the string representation
            import ast
            try:
                parsed = ast.literal_eval(country_name)
                country_name = parsed.get('country_name', '')
            except:
                pass
        
        cities = fetch_cities_for_country(country_name)
        return cities if cities else []
    except Exception as e:
        print(f"Error fetching cities for {country_name}: {str(e)}")
        return []


@tool
def get_points_of_interest(city: str) -> List[str]:
    """
    Finds popular points of interest for a given city using OpenTripMap API.
    Returns real, live data about attractions and landmarks.
    
    Args:
        city (str): The name of the city to find attractions for
        
    Returns:
        List[str]: List of attraction names
    """
    try:
        # Handle case where agent passes parameter as dict string
        if isinstance(city, dict):
            city = city.get('city', '')
        elif isinstance(city, str) and city.startswith('{'):
            # Try to extract from JSON-like string
            import json
            try:
                parsed = json.loads(city)
                city = parsed.get('city', '')
            except:
                pass
        
        # Use the OpenTripMap API to fetch real points of interest
        attractions = fetch_points_of_interest(city)
        
        if not attractions:
            # Return empty list instead of hardcoded fallback
            logger.warning(f"No attractions found for {city} - API may have failed")
            return []
        
        return attractions
        
    except Exception as e:
        logger.error(f"Error fetching points of interest for {city}: {str(e)}")
        # Return empty list instead of hardcoded fallback
        return []


@tool
def calculate_travel_details(cities: Union[List[str], Dict[str, Any], str]) -> Dict[str, Any]:
    """
    Calculates the total driving distance and estimated carbon emissions for a trip between a list of cities.
    The cities must be in travel order.
    
    Args:
        cities (Union[List[str], Dict[str, Any], str]): List of city names in the order of travel, or dict with 'cities' key, or string representation
        
    Returns:
        Dict[str, Any]: Dictionary with total_distance_km and carbon_emissions_kg
    """
    try:
        # Handle case where agent passes parameter as dict string
        if isinstance(cities, dict):
            cities = cities.get('cities', [])
        elif isinstance(cities, str):
            # Handle case where cities is passed as a string representation of dict
            if cities.startswith('{'):
                import json
                try:
                    parsed = json.loads(cities)
                    cities = parsed.get('cities', [])
                except:
                    # Try ast.literal_eval as fallback
                    import ast
                    try:
                        parsed = ast.literal_eval(cities)
                        cities = parsed.get('cities', [])
                    except:
                        cities = []
            else:
                # Handle case where cities is passed as a string like "['Paris', 'Lyon', 'Nice']"
                import ast
                try:
                    cities = ast.literal_eval(cities)
                except:
                    # If that fails, try splitting by comma
                    cities = [city.strip().strip("'\"") for city in cities.split(',')]
        
        # Ensure cities is a list
        if not isinstance(cities, list):
            cities = []
        
        if len(cities) < 2:
            return {
                'total_distance_km': 0,
                'carbon_emissions_kg': 0,
                'error': 'Need at least 2 cities to calculate distance'
            }
        
        # Use OpenRouteService API to calculate distances
        result = fetch_distance_between_cities(cities)
        
        if not result:
            return {
                'total_distance_km': 0,
                'carbon_emissions_kg': 0,
                'error': 'Could not calculate distances between cities'
            }
        
        # Convert distance from meters to kilometers
        total_distance_km = result.get('total_distance_meters', 0) / 1000
        
        # Calculate carbon emissions (0.12 kg CO2 per km for average car)
        carbon_emissions_kg = total_distance_km * 0.12
        
        return {
            'total_distance_km': round(total_distance_km, 2),
            'carbon_emissions_kg': round(carbon_emissions_kg, 2),
            'cities': result.get('cities', cities)
        }
        
    except Exception as e:
        print(f"Error calculating travel details: {str(e)}")
        return {
            'total_distance_km': 0,
            'carbon_emissions_kg': 0,
            'error': f'Error calculating distances: {str(e)}'
        }

@tool
def get_itinerary(poi: List[str], start_date: str, end_date: str) -> List[List[str]]:
    """
    Get a list of itineraries for a given point of interest.
    Args:
        poi (List[str]): List of points of interest
        start_date (str): Start date of the trip
        end_date (str): End date of the trip
        
    Returns:
        List[List[str]]: List of itineraries
    """
    try:
        return fetch_itinerary_list(poi, start_date, end_date)
    except Exception as e:
        print(f"Error getting itinerary: {str(e)}")
        return []


@tool
def save_itinerary(user_id: int, itinerary_name: str, cities: List[str], total_distance_km: float, carbon_emissions_kg: float) -> str:
    """
    Saves the final, complete itinerary to the database.
    Use this ONLY when the user has confirmed they are happy with the plan.
    You must provide all parameters.
    
    Args:
        user_id (int): ID of the user saving the itinerary
        itinerary_name (str): Name for the itinerary
        cities (List[str]): List of cities in the itinerary
        total_distance_km (float): Total distance in kilometers
        carbon_emissions_kg (float): Estimated carbon emissions in kg
        
    Returns:
        str: Confirmation message
    """
    try:
        # Create the itinerary in the database
        itinerary = Itinerary.create_itinerary(
            user_id=user_id,
            name=itinerary_name,
            cities=cities,
            total_distance_km=total_distance_km,
            carbon_emissions_kg=carbon_emissions_kg
        )
        
        return f"Successfully saved itinerary '{itinerary_name}' to the database with ID {itinerary.id}"
        
    except Exception as e:
        print(f"Error saving itinerary: {str(e)}")
        return f"Error saving itinerary: {str(e)}"


@tool
def create_multiple_itineraries(cities: Union[List[str], Dict[str, Any], str]) -> List[Dict[str, Any]]:
    """
    Creates multiple itinerary variations with different city orders and calculates 
    distance and carbon emissions for each option.
    
    Args:
        cities (Union[List[str], Dict[str, Any], str]): List of city names to create itineraries for
        
    Returns:
        List[Dict[str, Any]]: List of itinerary options with different routes and calculations
    """
    try:
        # Handle case where agent passes parameter as dict string
        if isinstance(cities, dict):
            cities = cities.get('cities', [])
        elif isinstance(cities, str):
            # Handle case where cities is passed as a string representation of dict
            if cities.startswith('{'):
                import json
                try:
                    parsed = json.loads(cities)
                    cities = parsed.get('cities', [])
                except:
                    # Try ast.literal_eval as fallback
                    import ast
                    try:
                        parsed = ast.literal_eval(cities)
                        cities = parsed.get('cities', [])
                    except:
                        cities = []
            else:
                # Handle case where cities is passed as a string like "['Paris', 'Lyon', 'Nice']"
                import ast
                try:
                    cities = ast.literal_eval(cities)
                except:
                    # If that fails, try splitting by comma
                    cities = [city.strip().strip("'\"") for city in cities.split(',')]
        
        # Ensure cities is a list
        if not isinstance(cities, list):
            cities = []
        
        if len(cities) < 2:
            return [{
                'error': 'Need at least 2 cities to create itineraries',
                'message': 'Please provide at least 2 cities to create itinerary options'
            }]
        
        # Create different itinerary variations
        import itertools
        
        # Generate different permutations (limit to reasonable number)
        max_permutations = 5
        city_permutations = list(itertools.permutations(cities))
        
        # Limit permutations to avoid too many options
        if len(city_permutations) > max_permutations:
            # Take first few permutations plus some strategic ones
            selected_permutations = city_permutations[:3]  # First 3
            # Add some strategic ones (reverse, middle variations)
            if len(cities) >= 3:
                # Add reverse order
                selected_permutations.append(tuple(reversed(cities)))
                # Add a middle variation if possible
                if len(cities) >= 4:
                    middle_variation = list(cities)
                    # Swap middle elements
                    mid = len(middle_variation) // 2
                    middle_variation[mid-1], middle_variation[mid] = middle_variation[mid], middle_variation[mid-1]
                    selected_permutations.append(tuple(middle_variation))
        else:
            selected_permutations = city_permutations
        
        # Calculate details for each permutation
        itinerary_options = []
        
        for i, city_route in enumerate(selected_permutations[:max_permutations]):
            route_list = list(city_route)
            
            # Calculate travel details for this route
            travel_details = calculate_travel_details.invoke({"cities": route_list})
            
            if 'error' in travel_details:
                continue  # Skip this route if calculation failed
            
            # Create itinerary option
            itinerary_option = {
                'id': i + 1,
                'name': f'Route Option {i + 1}',
                'cities': route_list,
                'total_distance_km': travel_details.get('total_distance_km', 0),
                'carbon_emissions_kg': travel_details.get('carbon_emissions_kg', 0),
                'estimated_drive_time_hours': round(travel_details.get('total_distance_km', 0) / 60, 1),  # Assume 60 km/h average
                'route_description': ' → '.join(route_list)
            }
            
            itinerary_options.append(itinerary_option)
        
        # Sort by carbon emissions (lowest first)
        itinerary_options.sort(key=lambda x: x.get('carbon_emissions_kg', 0))
        
        return itinerary_options
        
    except Exception as e:
        print(f"Error creating multiple itineraries: {str(e)}")
        return [{
            'error': f'Error creating itineraries: {str(e)}',
            'message': 'Could not generate itinerary options'
        }]


@tool
def find_flight_options(origin_city: Union[str, Dict[str, Any]], destination_country: str = None, travel_date: str = None) -> List[Dict[str, Any]]:
    """
    Finds flight options from an origin city to a destination country for a specific date.
    This is a simple tool that the AI can use to search for flights.
    
    Args:
        origin_city (str): The departure city name
        destination_country (str): The destination country name  
        travel_date (str): Travel date in YYYY-MM-DD format
        
    Returns:
        List[Dict[str, Any]]: List of flight options
    """
    try:
        # Handle case where agent passes parameters as dict
        if isinstance(origin_city, dict):
            # Extract all parameters from the dict
            temp_origin = origin_city.get('origin_city', '')
            temp_destination = origin_city.get('destination_country', '')
            temp_date = origin_city.get('travel_date', '')
            origin_city = temp_origin
            destination_country = temp_destination
            travel_date = temp_date
        
        # Handle case where agent passes parameters as string representation of dict
        elif isinstance(origin_city, str) and origin_city.startswith("{'origin_city':"):
            # Extract parameters from the string representation
            import ast
            try:
                parsed = ast.literal_eval(origin_city)
                origin_city = parsed.get('origin_city', '')
                destination_country = parsed.get('destination_country', '')
                travel_date = parsed.get('travel_date', '')
            except:
                pass
        elif isinstance(origin_city, str) and origin_city.startswith('{'):
            # Try to extract from JSON-like string
            import json
            try:
                parsed = json.loads(origin_city)
                origin_city = parsed.get('origin_city', '')
                destination_country = parsed.get('destination_country', '')
                travel_date = parsed.get('travel_date', '')
            except:
                pass
        elif isinstance(origin_city, str) and ',' in origin_city:
            # Handle case where parameters are passed as comma-separated string
            parts = origin_city.split(',')
            if len(parts) >= 3:
                origin_city = parts[0].strip()
                destination_country = parts[1].strip()
                travel_date = parts[2].strip()
        
        # Handle case where parameters are passed as separate arguments
        if destination_country is None:
            destination_country = ''
        if travel_date is None:
            travel_date = ''
        
        # Ensure we have valid parameters
        if not origin_city or not destination_country or not travel_date:
            logger.warning(f"Missing parameters: origin_city={origin_city}, destination_country={destination_country}, travel_date={travel_date}")
            return [{
                'error': 'Missing required parameters',
                'message': 'Please provide origin city, destination country, and travel date'
            }]
        
        # Get IATA codes for the cities
        from app.services.geo_api import get_iata_code
        
        # Get origin airport code
        origin_iata = get_iata_code(origin_city)
        if not origin_iata:
            return [{
                'error': f'Could not find airport code for {origin_city}',
                'message': f'Please specify a valid departure city. {origin_city} not found.'
            }]
        
        # For destination country, we need to find a major airport
        # For now, let's use a simple mapping for major countries
        destination_airports = {
            'france': 'CDG',  # Paris Charles de Gaulle
            'spain': 'MAD',   # Madrid
            'italy': 'FCO',   # Rome Fiumicino
            'germany': 'FRA', # Frankfurt
            'united kingdom': 'LHR', # London Heathrow
            'uk': 'LHR',
            'england': 'LHR',
            'japan': 'NRT',   # Tokyo Narita
            'china': 'PEK',   # Beijing
            'australia': 'SYD', # Sydney
            'canada': 'YYZ',  # Toronto
            'brazil': 'GRU',  # São Paulo
            'india': 'DEL',  # Delhi
            'mexico': 'MEX', # Mexico City
            'south korea': 'ICN', # Seoul Incheon
            'korea': 'ICN',
            'netherlands': 'AMS', # Amsterdam
            'belgium': 'BRU', # Brussels
            'switzerland': 'ZUR', # Zurich
            'austria': 'VIE', # Vienna
            'sweden': 'ARN', # Stockholm
            'norway': 'OSL', # Oslo
            'denmark': 'CPH', # Copenhagen
            'finland': 'HEL', # Helsinki
            'poland': 'WAW', # Warsaw
            'czech republic': 'PRG', # Prague
            'hungary': 'BUD', # Budapest
            'portugal': 'LIS', # Lisbon
            'greece': 'ATH', # Athens
            'turkey': 'IST', # Istanbul
            'russia': 'SVO', # Moscow Sheremetyevo
        }
        
        destination_iata = destination_airports.get(destination_country.lower())
        if not destination_iata:
            return [{
                'error': f'Could not find airport code for {destination_country}',
                'message': f'Please specify a valid destination country. {destination_country} not found in our database.'
            }]
        
        # Search for actual flights using the flight API
        from app.services.flight_api import search_flights
        
        flights = search_flights(origin_iata, destination_iata, travel_date)
        
        if not flights:
            return [{
                'message': f'No flights found from {origin_city} ({origin_iata}) to {destination_country} ({destination_iata}) on {travel_date}',
                'suggestion': 'Try a different date or check with airlines directly',
                'origin_airport': origin_iata,
                'destination_airport': destination_iata
            }]
        
        # Format the flight results - limit to top 10 most relevant flights
        flight_options = []
        
        # Filter and limit flights
        unique_airlines = set()
        for flight in flights[:50]:  # Only process first 50 flights
            airline = flight.get('airline', 'Unknown')
            
            # Skip if we already have this airline (to get variety)
            if airline in unique_airlines and len(flight_options) >= 10:
                continue
                
            # Skip airlines that don't typically do international routes
            if airline in ['Frontier', 'Spirit', 'Allegiant', 'Sun Country']:
                continue
                
            flight_options.append({
                'airline': airline,
                'departure_time': flight.get('departure_time', ''),
                'arrival_time': flight.get('arrival_time', ''),
                'stops': flight.get('number_of_stops', 0),
                'route': flight.get('route', f'{origin_iata} to {destination_iata}')
            })
            
            unique_airlines.add(airline)
            
            # Stop at 10 flights
            if len(flight_options) >= 10:
                break
        
        return flight_options
        
    except Exception as e:
        print(f"Error finding flight options: {str(e)}")
        return [{
            'error': f'Error searching flights: {str(e)}',
            'message': 'Flight search temporarily unavailable'
        }]


