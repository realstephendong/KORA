"""
LangChain tools for the travel planner agent.
Provides tools for fetching city data and points of interest.
"""

from typing import List, Dict, Any
from langchain.tools import tool
from app.services.geo_api import fetch_cities_for_country


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
def get_points_of_interest(city: str) -> List[Dict[str, str]]:
    """
    Finds popular points of interest for a given city.
    Returns a list of attractions with their categories.
    
    Args:
        city (str): The name of the city to find attractions for
        
    Returns:
        List[Dict[str, str]]: List of attractions with name and category
    """
    # For now, return hardcoded data based on popular cities
    # In a real implementation, this would call an attractions API
    attractions_data = {
        "paris": [
            {"name": "Louvre Museum", "category": "Museum"},
            {"name": "Eiffel Tower", "category": "Landmark"},
            {"name": "Notre-Dame Cathedral", "category": "Religious Site"},
            {"name": "Arc de Triomphe", "category": "Monument"},
            {"name": "Champs-Élysées", "category": "Shopping Street"}
        ],
        "london": [
            {"name": "Big Ben", "category": "Landmark"},
            {"name": "Tower of London", "category": "Historic Site"},
            {"name": "British Museum", "category": "Museum"},
            {"name": "London Eye", "category": "Attraction"},
            {"name": "Buckingham Palace", "category": "Royal Residence"}
        ],
        "new york": [
            {"name": "Statue of Liberty", "category": "Monument"},
            {"name": "Central Park", "category": "Park"},
            {"name": "Times Square", "category": "Landmark"},
            {"name": "Metropolitan Museum of Art", "category": "Museum"},
            {"name": "Brooklyn Bridge", "category": "Landmark"}
        ],
        "tokyo": [
            {"name": "Tokyo Skytree", "category": "Observation Tower"},
            {"name": "Senso-ji Temple", "category": "Temple"},
            {"name": "Tokyo National Museum", "category": "Museum"},
            {"name": "Shibuya Crossing", "category": "Landmark"},
            {"name": "Meiji Shrine", "category": "Shrine"}
        ],
        "rome": [
            {"name": "Colosseum", "category": "Historic Site"},
            {"name": "Vatican City", "category": "Religious Site"},
            {"name": "Trevi Fountain", "category": "Fountain"},
            {"name": "Pantheon", "category": "Historic Site"},
            {"name": "Roman Forum", "category": "Historic Site"}
        ],
        "barcelona": [
            {"name": "Sagrada Familia", "category": "Church"},
            {"name": "Park Güell", "category": "Park"},
            {"name": "Casa Batlló", "category": "Architecture"},
            {"name": "La Rambla", "category": "Street"},
            {"name": "Gothic Quarter", "category": "Historic District"}
        ],
        "amsterdam": [
            {"name": "Anne Frank House", "category": "Museum"},
            {"name": "Van Gogh Museum", "category": "Museum"},
            {"name": "Rijksmuseum", "category": "Museum"},
            {"name": "Canal Ring", "category": "Historic Site"},
            {"name": "Jordaan District", "category": "Neighborhood"}
        ],
        "berlin": [
            {"name": "Brandenburg Gate", "category": "Monument"},
            {"name": "Berlin Wall Memorial", "category": "Historic Site"},
            {"name": "Museum Island", "category": "Museum Complex"},
            {"name": "Checkpoint Charlie", "category": "Historic Site"},
            {"name": "Pergamon Museum", "category": "Museum"}
        ],
        "madrid": [
            {"name": "Prado Museum", "category": "Museum"},
            {"name": "Royal Palace", "category": "Palace"},
            {"name": "Retiro Park", "category": "Park"},
            {"name": "Puerta del Sol", "category": "Square"},
            {"name": "Plaza Mayor", "category": "Historic Square"}
        ],
        "vienna": [
            {"name": "Schönbrunn Palace", "category": "Palace"},
            {"name": "St. Stephen's Cathedral", "category": "Cathedral"},
            {"name": "Belvedere Palace", "category": "Palace"},
            {"name": "Hofburg Palace", "category": "Palace"},
            {"name": "Prater Park", "category": "Park"}
        ]
    }
    
    # Normalize city name for lookup
    city_key = city.lower().strip()
    
    # Check for exact match first
    if city_key in attractions_data:
        return attractions_data[city_key]
    
    # Check for partial matches
    for key, attractions in attractions_data.items():
        if city_key in key or key in city_key:
            return attractions
    
    # Default attractions for unknown cities
    return [
        {"name": "City Center", "category": "Downtown"},
        {"name": "Local Museum", "category": "Museum"},
        {"name": "Main Square", "category": "Historic Site"},
        {"name": "Central Park", "category": "Park"},
        {"name": "Historic District", "category": "Historic Site"}
    ]


