"""
LangChain tools for the travel planner agent.
Provides tools for fetching city data, points of interest, calculating travel details, and saving itineraries.
"""

from typing import List, Dict, Any, Union
import logging
from langchain.tools import tool
from app.services.geo_api import fetch_cities_for_country
from app.services.travel_data_api import fetch_points_of_interest, fetch_distance_between_cities
from app.services.hotels import fetch_hotel_price, fetch_hotels_in_city
from app.services.culture_data import fetch_cultural_insights
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
        
        # Handle case where agent passes "country_name: Spain" format
        if isinstance(country_name, str) and ':' in country_name:
            # Extract the country name after the colon
            parts = country_name.split(':', 1)
            if len(parts) > 1:
                country_name = parts[1].strip()
        
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
def get_hotel_options(city: str) -> List[Dict[str, Any]]:
    """
    Finds hotel options for a given city for a specific date.
    This is a simple tool that the AI can use to search for hotels.
    """
    return fetch_hotels_in_city(city)

@tool
def get_hotel_price(hotel_id: str, check_in_date: str, check_out_date: str, adults: int = 1) -> Dict[str, Any]:
    """
    Finds hotel price for a given hotel for a specific date.
    This is a simple tool that the AI can use to search for hotel prices.
    """
    return fetch_hotel_price(hotel_id, check_in_date, check_out_date, adults)

@tool
def get_cultural_insights(poi: List[str]) -> Dict[str, Any]:
    """
    Finds cultural insights for a given point of interest.
    This is a simple tool that the AI can use to search for cultural insights.
    """
    return fetch_cultural_insights(poi)

@tool
def get_events(itinerary: List[str]) -> Dict[str, Any]:
    """
    Finds cultural insights for a given point of interest.
    This is a simple tool that the AI can use to search for cultural insights.
    """
    return fetch_cultural_insights(itinerary)

@tool
def create_multiple_itineraries(cities: Union[List[str], Dict[str, Any], str], origin_city: str = None, travel_date: str = None, destination_country: str = None, food_budget: float = None) -> List[Dict[str, Any]]:
    """
    Creates multiple itinerary variations with different city orders and calculates 
    distance, carbon emissions, and total costs (including flights) for each option.
    
    Args:
        cities (Union[List[str], Dict[str, Any], str]): List of city names to create itineraries for
        origin_city (str, optional): Origin city for flight calculations
        travel_date (str, optional): Travel date for flight calculations (YYYY-MM-DD format)
        destination_country (str, optional): Destination country for flight calculations
        food_budget (float, optional): User's total food budget for the entire trip
        
    Returns:
        List[Dict[str, Any]]: List of itinerary options with different routes, calculations, and costs
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
        
        if len(cities) < 1:
            return [{
                'error': 'Need at least 1 city to create itineraries',
                'message': 'Please provide at least 1 city to create itinerary options'
            }]
        
        # Get flight costs if flight parameters are provided
        flight_costs = []
        if origin_city and travel_date and destination_country:
            try:
                # Use the flight API to get real flight costs
                from app.services.flight_api import search_flights
                from app.services.geo_api import get_iata_code
                
                # Get origin IATA code
                origin_iata = get_iata_code(origin_city)
                
                # Map destination country to airport code (same as in find_flight_options)
                destination_airports = {
                    'france': 'CDG', 'spain': 'MAD', 'italy': 'FCO', 'germany': 'FRA',
                    'united kingdom': 'LHR', 'uk': 'LHR', 'england': 'LHR',
                    'japan': 'NRT', 'china': 'PEK', 'australia': 'SYD', 'canada': 'YYZ',
                    'brazil': 'GRU', 'india': 'DEL', 'mexico': 'MEX', 'south korea': 'ICN',
                    'korea': 'ICN', 'netherlands': 'AMS', 'belgium': 'BRU', 'switzerland': 'ZUR',
                    'austria': 'VIE', 'sweden': 'ARN', 'norway': 'OSL', 'denmark': 'CPH',
                    'finland': 'HEL', 'poland': 'WAW', 'czech republic': 'PRG', 'hungary': 'BUD',
                    'portugal': 'LIS', 'greece': 'ATH', 'turkey': 'IST', 'russia': 'SVO'
                }
                
                dest_iata = destination_airports.get(destination_country.lower())
                
                if origin_iata and dest_iata:
                    flights = search_flights(origin_iata, dest_iata, travel_date)
                    if flights:
                        # Extract prices from flight results
                        flight_costs = []
                        for flight in flights:
                            price = flight.get('price', 0)
                            if price:
                                # Convert to float if it's a string, then check if > 0
                                try:
                                    price_float = float(price)
                                    if price_float > 0:
                                        flight_costs.append(price_float)
                                except (ValueError, TypeError):
                                    continue
                    
            except Exception as e:
                logger.warning(f"Error getting flight costs: {str(e)}")
        
        # Create different itinerary variations
        import itertools
        
        # Handle single city case
        if len(cities) == 1:
            # For single city, create one itinerary option
            selected_permutations = [tuple(cities)]
        else:
            # Generate different permutations for multiple cities
            city_permutations = list(itertools.permutations(cities))
            
            # Limit permutations to avoid too many options (max 5)
            max_permutations = min(5, len(city_permutations))
            selected_permutations = city_permutations[:max_permutations]
        
        # Calculate details for each permutation
        itinerary_options = []
        
        for i, city_route in enumerate(selected_permutations):
            route_list = list(city_route)
            
            # Handle single city case differently
            if len(route_list) == 1:
                # For single city, no travel distance calculation needed
                travel_details = {
                    'total_distance_km': 0,
                    'carbon_emissions_kg': 0
                }
            else:
                # Calculate travel details for multi-city routes
                travel_details = calculate_travel_details.invoke({"cities": route_list})
                
                if 'error' in travel_details:
                    continue  # Skip this route if calculation failed
            
            # Get flight cost if available
            flight_cost = flight_costs[i] if i < len(flight_costs) else (flight_costs[0] if flight_costs else 0)
            
            # Create itinerary option
            itinerary_option = {
                'id': i + 1,
                'name': f'Route Option {i + 1}',
                'cities': route_list,
                'total_distance_km': travel_details.get('total_distance_km', 0),
                'carbon_emissions_kg': travel_details.get('carbon_emissions_kg', 0),
                'estimated_drive_time_hours': round(travel_details.get('total_distance_km', 0) / 60, 1),
                'route_description': ' → '.join(route_list),
                'costs': {
                    'flight_cost': round(flight_cost, 2) if flight_cost else 0
                }
            }
            
            itinerary_options.append(itinerary_option)
        
        # Sort by carbon emissions (lowest first)
        itinerary_options.sort(key=lambda x: x.get('carbon_emissions_kg', 0))
        
        return itinerary_options
        
    except Exception as e:
        logger.error(f"Error creating multiple itineraries: {str(e)}")
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
                'price': flight.get('price', 0),
                'currency': flight.get('currency', 'USD'),
                'departure_time': flight.get('departure_time', ''),
                'arrival_time': flight.get('arrival_time', ''),
                'stops': flight.get('number_of_stops', 0),
                'route': flight.get('route', f'{origin_iata} to {destination_iata}'),
                'is_direct': flight.get('is_direct', False),
                'source': flight.get('source', 'Unknown')
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


