"""
LangChain tools for the travel planner agent.
Provides tools for fetching city data, points of interest, calculating travel details, and saving itineraries.
"""

from typing import List, Dict, Any
from langchain.tools import tool
from app.services.geo_api import fetch_cities_for_country
from app.services.travel_data_api import fetch_points_of_interest, fetch_distance_between_cities
from app.services.culture_data import fetch_itinerary_list
from app.models.itinerary import Itinerary
from app import db


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
        # Use the OpenTripMap API to fetch real points of interest
        attractions = fetch_points_of_interest(city)
        
        if not attractions:
            # Fallback to generic suggestions if API fails
            return [
                "City Center",
                "Local Museum", 
                "Main Square",
                "Central Park",
                "Historic District"
            ]
        
        return attractions
        
    except Exception as e:
        print(f"Error fetching points of interest for {city}: {str(e)}")
        # Return fallback data
        return [
            "City Center",
            "Local Museum",
            "Main Square", 
            "Central Park",
            "Historic District"
        ]


@tool
def calculate_travel_details(cities: List[str]) -> Dict[str, Any]:
    """
    Calculates the total driving distance and estimated carbon emissions for a trip between a list of cities.
    The cities must be in travel order.
    
    Args:
        cities (List[str]): List of city names in the order of travel
        
    Returns:
        Dict[str, Any]: Dictionary with total_distance_km and carbon_emissions_kg
    """
    try:
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


