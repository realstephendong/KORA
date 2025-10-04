"""
Culture data service for the travel planner application.
Provides functions for generating travel itineraries based on points of interest and dates.
"""

import os
import requests
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timedelta
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fetch_itinerary_list(poi: List[str], start_date: str, end_date: str) -> List[List[str]]:
    """
    Generate multiple different travel itineraries based on points of interest and date range.
    
    Args:
        poi (List[str]): List of points of interest
        start_date (str): First day of visit (format: YYYY-MM-DD)
        end_date (str): Last day of visit (format: YYYY-MM-DD)
        
    Returns:
        List[List[str]]: 2D array containing possible travel itineraries
    """
    try:
        # Validate input parameters
        if not poi or len(poi) == 0:
            logger.warning("No points of interest provided")
            return []
        
        if not start_date or not end_date:
            logger.warning("Start date and end date are required")
            return []
        
        # Parse dates
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError as e:
            logger.error(f"Invalid date format: {str(e)}")
            return []
        
        # Calculate number of days
        num_days = (end_dt - start_dt).days + 1
        if num_days <= 0:
            logger.warning("End date must be after start date")
            return []
        
        logger.info(f"Generating itineraries for {num_days} days with {len(poi)} points of interest")
        
        # Generate multiple itinerary options
        itineraries = []
        
        # Option 1: Balanced distribution across all days
        itinerary_1 = _generate_balanced_itinerary(poi, num_days)
        if itinerary_1:
            itineraries.append(itinerary_1)
        
        # Option 2: Focus on top attractions with more time
        itinerary_2 = _generate_focused_itinerary(poi, num_days)
        if itinerary_2:
            itineraries.append(itinerary_2)
        
        # Option 3: Random distribution for variety
        itinerary_3 = _generate_random_itinerary(poi, num_days)
        if itinerary_3:
            itineraries.append(itinerary_3)
        
        # Option 4: Grouped by proximity (if we have location data)
        itinerary_4 = _generate_grouped_itinerary(poi, num_days)
        if itinerary_4:
            itineraries.append(itinerary_4)
        
        logger.info(f"Generated {len(itineraries)} different itinerary options")
        return itineraries
        
    except Exception as e:
        logger.error(f"Unexpected error generating itineraries: {str(e)}")
        return []


def _generate_balanced_itinerary(poi: List[str], num_days: int) -> List[str]:
    """
    Generate a balanced itinerary distributing POIs evenly across days.
    
    Args:
        poi (List[str]): List of points of interest
        num_days (int): Number of days for the trip
        
    Returns:
        List[str]: Daily itinerary plan
    """
    try:
        itinerary = []
        poi_per_day = max(1, len(poi) // num_days)
        remaining_poi = poi.copy()
        
        for day in range(num_days):
            day_poi = []
            # Distribute POIs evenly
            for _ in range(min(poi_per_day, len(remaining_poi))):
                if remaining_poi:
                    day_poi.append(remaining_poi.pop(0))
            
            # Add any remaining POIs to the last day
            if day == num_days - 1 and remaining_poi:
                day_poi.extend(remaining_poi)
            
            if day_poi:
                day_plan = f"Day {day + 1}: " + " → ".join(day_poi)
                itinerary.append(day_plan)
        
        return itinerary
        
    except Exception as e:
        logger.error(f"Error generating balanced itinerary: {str(e)}")
        return []


def _generate_focused_itinerary(poi: List[str], num_days: int) -> List[str]:
    """
    Generate a focused itinerary prioritizing top attractions.
    
    Args:
        poi (List[str]): List of points of interest
        num_days (int): Number of days for the trip
        
    Returns:
        List[str]: Daily itinerary plan
    """
    try:
        itinerary = []
        # Prioritize first few POIs (assuming they are most important)
        priority_poi = poi[:min(3, len(poi))]
        other_poi = poi[3:] if len(poi) > 3 else []
        
        for day in range(num_days):
            day_poi = []
            
            if day < len(priority_poi):
                # Focus on priority attractions
                day_poi.append(priority_poi[day])
                
                # Add supporting attractions if available
                if other_poi and day < len(other_poi):
                    day_poi.append(other_poi[day])
            elif other_poi:
                # Fill remaining days with other attractions
                remaining_index = day - len(priority_poi)
                if remaining_index < len(other_poi):
                    day_poi.append(other_poi[remaining_index])
            
            if day_poi:
                day_plan = f"Day {day + 1}: " + " → ".join(day_poi)
                itinerary.append(day_plan)
        
        return itinerary
        
    except Exception as e:
        logger.error(f"Error generating focused itinerary: {str(e)}")
        return []


def _generate_random_itinerary(poi: List[str], num_days: int) -> List[str]:
    """
    Generate a random itinerary for variety.
    
    Args:
        poi (List[str]): List of points of interest
        num_days (int): Number of days for the trip
        
    Returns:
        List[str]: Daily itinerary plan
    """
    try:
        itinerary = []
        shuffled_poi = poi.copy()
        random.shuffle(shuffled_poi)
        
        poi_per_day = max(1, len(shuffled_poi) // num_days)
        remaining_poi = shuffled_poi.copy()
        
        for day in range(num_days):
            day_poi = []
            for _ in range(min(poi_per_day, len(remaining_poi))):
                if remaining_poi:
                    day_poi.append(remaining_poi.pop(0))
            
            # Add any remaining POIs to the last day
            if day == num_days - 1 and remaining_poi:
                day_poi.extend(remaining_poi)
            
            if day_poi:
                day_plan = f"Day {day + 1}: " + " → ".join(day_poi)
                itinerary.append(day_plan)
        
        return itinerary
        
    except Exception as e:
        logger.error(f"Error generating random itinerary: {str(e)}")
        return []


def _generate_grouped_itinerary(poi: List[str], num_days: int) -> List[str]:
    """
    Generate an itinerary grouping POIs by themes or proximity.
    
    Args:
        poi (List[str]): List of points of interest
        num_days (int): Number of days for the trip
        
    Returns:
        List[str]: Daily itinerary plan
    """
    try:
        itinerary = []
        
        # Simple grouping: divide POIs into chunks
        chunk_size = max(1, len(poi) // num_days)
        poi_chunks = [poi[i:i + chunk_size] for i in range(0, len(poi), chunk_size)]
        
        for day in range(num_days):
            if day < len(poi_chunks):
                day_poi = poi_chunks[day]
                if day_poi:
                    day_plan = f"Day {day + 1}: " + " → ".join(day_poi)
                    itinerary.append(day_plan)
        
        return itinerary
        
    except Exception as e:
        logger.error(f"Error generating grouped itinerary: {str(e)}")
        return []


def get_cultural_insights(poi: List[str]) -> Dict[str, Any]:
    """
    Get additional cultural insights for points of interest.
    
    Args:
        poi (List[str]): List of points of interest
        
    Returns:
        Dict[str, Any]: Cultural insights and recommendations
    """
    try:
        insights = {
            'total_attractions': len(poi),
            'recommended_duration': f"{len(poi) * 2} hours minimum",
            'tips': [
                "Plan to spend 2-3 hours at each major attraction",
                "Consider booking tickets in advance for popular sites",
                "Check opening hours and any special events",
                "Allow time for travel between locations"
            ],
            'cultural_notes': [
                "Research local customs and etiquette",
                "Learn basic phrases in the local language",
                "Check for cultural festivals or events during your visit"
            ]
        }
        
        logger.info(f"Generated cultural insights for {len(poi)} points of interest")
        return insights
        
    except Exception as e:
        logger.error(f"Error generating cultural insights: {str(e)}")
        return {}
