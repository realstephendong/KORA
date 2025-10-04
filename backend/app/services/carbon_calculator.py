"""
Carbon emissions calculator for flights.
Calculates CO2 emissions based on flight distance and fuel consumption rates.
"""

import logging
from typing import Dict, Any, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Single fuel consumption rate for all aircraft (liters per kilometer)
FUEL_CONSUMPTION_RATE = 4.0  # liters/km - flat rate for all aircraft

# CO2 emissions per liter of jet fuel (kg CO2 per liter)
CO2_PER_LITER_JET_FUEL = 2.5



def calculate_flight_distance(origin_city: str, destination_city: str) -> float:
    """
    Calculate the great circle distance between two cities in kilometers.
    Uses approximate distances for common routes to avoid API calls.
    
    Args:
        origin_city (str): Origin city name
        destination_city (str): Destination city name
        
    Returns:
        float: Distance in kilometers
    """
    try:
        # Use approximate distances for common routes to avoid API rate limits
        distance_km = _get_approximate_distance(origin_city, destination_city)
        
        if distance_km == 0:
            logger.warning(f"Could not get distance for {origin_city} to {destination_city}")
            return 0.0
        
        logger.info(f"Distance from {origin_city} to {destination_city}: {distance_km:.1f} km")
        return distance_km
        
    except Exception as e:
        logger.error(f"Error calculating distance: {str(e)}")
        return 0.0


def _get_approximate_distance(origin_city: str, destination_city: str) -> float:
    """
    Get approximate distance between cities using common route distances.
    
    Args:
        origin_city (str): Origin city name
        destination_city (str): Destination city name
        
    Returns:
        float: Distance in kilometers
    """
    # Common route distances (km) - these are real-world flight distances
    route_distances = {
        ('New York', 'Paris'): 5834,
        ('New York', 'London'): 5585,
        ('New York', 'Frankfurt'): 6200,
        ('New York', 'Madrid'): 5769,
        ('New York', 'Rome'): 6900,
        ('Los Angeles', 'Paris'): 9100,
        ('Los Angeles', 'London'): 8750,
        ('San Francisco', 'Paris'): 8960,
        ('San Francisco', 'London'): 8600,
        ('Chicago', 'Paris'): 6600,
        ('Chicago', 'London'): 6400,
        ('Miami', 'Paris'): 7500,
        ('Miami', 'London'): 7200,
        ('Boston', 'Paris'): 5500,
        ('Boston', 'London'): 5200,
        ('Seattle', 'Paris'): 8200,
        ('Seattle', 'London'): 7800,
        ('Atlanta', 'Paris'): 7200,
        ('Atlanta', 'London'): 6900,
        ('Dallas', 'Paris'): 8000,
        ('Dallas', 'London'): 7700,
        ('Denver', 'Paris'): 8500,
        ('Denver', 'London'): 8200,
        ('Houston', 'Paris'): 8200,
        ('Houston', 'London'): 7900,
        ('Phoenix', 'Paris'): 9000,
        ('Phoenix', 'London'): 8700,
        ('Las Vegas', 'Paris'): 9200,
        ('Las Vegas', 'London'): 8900,
        ('Orlando', 'Paris'): 7600,
        ('Orlando', 'London'): 7300,
    }
    
    # Check both directions
    distance = route_distances.get((origin_city, destination_city), 0)
    if distance == 0:
        distance = route_distances.get((destination_city, origin_city), 0)
    
    return distance


def calculate_carbon_emissions(aircraft_model: str, origin_city: str, destination_city: str, stops: int = 0) -> Dict[str, Any]:
    """
    Calculate carbon emissions for a flight based on aircraft type, distance, and stops.
    
    Args:
        aircraft_model (str): Aircraft model (e.g., "Boeing 737-800")
        origin_city (str): Origin city name
        destination_city (str): Destination city name
        stops (int): Number of stops (0 for direct flight)
        
    Returns:
        Dict[str, Any]: Dictionary with emissions data
    """
    try:
        # Calculate flight distance
        distance_km = calculate_flight_distance(origin_city, destination_city)
        
        if distance_km == 0:
            return {
                'error': 'Could not calculate distance',
                'carbon_emissions_kg': 0,
                'fuel_used_liters': 0,
                'distance_km': 0
            }
        
        # Use flat fuel consumption rate for all aircraft
        fuel_rate = FUEL_CONSUMPTION_RATE
        
        # Calculate total distance (including stops)
        # Each stop adds approximately 20% more distance due to routing
        total_distance = distance_km * (1 + stops * 0.2)
        
        # Calculate fuel consumption
        fuel_used_liters = total_distance * fuel_rate
        
        # Calculate CO2 emissions
        carbon_emissions_kg = fuel_used_liters * CO2_PER_LITER_JET_FUEL
        
        return {
            'carbon_emissions_kg': round(carbon_emissions_kg, 1),
            'fuel_used_liters': round(fuel_used_liters, 1),
            'distance_km': round(distance_km, 1),
            'total_distance_km': round(total_distance, 1),
            'fuel_rate_liters_per_km': fuel_rate,
            'stops': stops,
            'aircraft_model': aircraft_model
        }
        
    except Exception as e:
        logger.error(f"Error calculating carbon emissions: {str(e)}")
        return {
            'error': f'Calculation error: {str(e)}',
            'carbon_emissions_kg': 0,
            'fuel_used_liters': 0,
            'distance_km': 0
        }




def _haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points on Earth.
    
    Args:
        lat1, lon1: Latitude and longitude of first point
        lat2, lon2: Latitude and longitude of second point
        
    Returns:
        float: Distance in kilometers
    """
    import math
    
    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of Earth in kilometers
    r = 6371
    
    return c * r


def get_emissions_comparison(flights_data: list) -> list:
    """
    Compare carbon emissions across multiple flights and rank them.
    
    Args:
        flights_data (list): List of flight dictionaries with aircraft, origin, destination, stops
        
    Returns:
        list: Flights sorted by carbon emissions (lowest first)
    """
    try:
        emissions_data = []
        
        for flight in flights_data:
            aircraft = flight.get('aircraft', 'Unknown')
            origin = flight.get('origin_city', '')
            destination = flight.get('destination_city', '')
            stops = flight.get('stops', 0)
            
            emissions = calculate_carbon_emissions(aircraft, origin, destination, stops)
            
            if 'error' not in emissions:
                flight_with_emissions = flight.copy()
                flight_with_emissions.update(emissions)
                emissions_data.append(flight_with_emissions)
        
        # Sort by carbon emissions (lowest first)
        emissions_data.sort(key=lambda x: x.get('carbon_emissions_kg', float('inf')))
        
        return emissions_data
        
    except Exception as e:
        logger.error(f"Error in emissions comparison: {str(e)}")
        return []
