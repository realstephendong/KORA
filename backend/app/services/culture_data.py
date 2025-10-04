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
import google.generativeai as genai
import json

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
        
        # Generate multiple itinerary options using Gemini AI
        itineraries = _generate_ai_itineraries(poi, num_days, start_date, end_date)
        
        logger.info(f"Generated {len(itineraries)} different itinerary options")
        return itineraries
        
    except Exception as e:
        logger.error(f"Unexpected error generating itineraries: {str(e)}")
        return []


def _generate_ai_itineraries(poi: List[str], num_days: int, start_date: str, end_date: str) -> List[List[str]]:
    """
    Generate multiple travel itineraries using Gemini AI based on points of interest and date range.
    
    Args:
        poi (List[str]): List of points of interest
        num_days (int): Number of days for the trip
        start_date (str): First day of visit
        end_date (str): Last day of visit
        
    Returns:
        List[List[str]]: 2D array containing multiple AI-generated travel itineraries
    """
    try:
        # Configure Gemini API
        api_key = os.environ.get('GOOGLE_API_KEY')
        if not api_key:
            logger.error("GOOGLE_API_KEY environment variable is required")
            return []
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Create prompt for Gemini
        poi_list = ", ".join(poi)
        prompt = f"""
        Create 4 different travel itineraries for a {num_days}-day trip from {start_date} to {end_date}.
        
        Points of Interest: {poi_list}
        
        Please generate 4 distinct itinerary options with different approaches:
        1. Balanced Itinerary: Distribute attractions evenly across all days
        2. Focused Itinerary: Prioritize the most important attractions with more time
        3. Themed Itinerary: Group attractions by themes or proximity
        4. Flexible Itinerary: Create a varied schedule with different pacing
        
        For each itinerary, format the response as:
        Day 1: [attraction1] → [attraction2] → [attraction3]
        Day 2: [attraction4] → [attraction5]
        etc.
        
        Return the response as a JSON array where each element is an array of strings representing each day's plan.
        Example format:
        [
            ["Day 1: Eiffel Tower (10:00-18:00) → Louvre Museum (10:00-18:00) → Notre-Dame (10:00-18:00)", "Day 2: Arc de Triomphe (10:00-18:00) → Champs-Élysées (10:00-18:00)"],
            ["Day 1: Eiffel Tower (full day)", "Day 2: Louvre Museum → Notre-Dame"],
            ["Day 1: Eiffel Tower (10:00-18:00) → Arc de Triomphe (10:00-18:00)", "Day 2: Louvre Museum (10:00-18:00) → Notre-Dame (10:00-18:00)"],
            ["Day 1: Notre-Dame (10:00-18:00) → Eiffel Tower (10:00-18:00)", "Day 2: Arc de Triomphe (10:00-18:00) → Champs-Élysées (10:00-18:00)"]
        ]
        
        Make sure each itinerary uses all the provided points of interest and fits within the {num_days}-day timeframe.
        """
        
        # Generate response from Gemini
        response = model.generate_content(prompt)
        
        if not response.text:
            logger.error("No response received from Gemini API")
            return []
        
        # Parse the JSON response
        try:
            # Clean the response text to extract JSON
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            response_text = response_text.strip()
            
            # Parse JSON
            itineraries = json.loads(response_text)
            
            # Validate the response format
            if not isinstance(itineraries, list):
                logger.error("Invalid response format from Gemini API")
                return []
            
            # Ensure each itinerary is a list of strings
            validated_itineraries = []
            for itinerary in itineraries:
                if isinstance(itinerary, list) and all(isinstance(day, str) for day in itinerary):
                    validated_itineraries.append(itinerary)
                else:
                    logger.warning(f"Invalid itinerary format: {itinerary}")
            
            logger.info(f"Successfully generated {len(validated_itineraries)} AI-powered itineraries")
            return validated_itineraries
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response from Gemini: {str(e)}")
            logger.error(f"Raw response: {response.text}")
            return []
        
    except Exception as e:
        logger.error(f"Error generating AI itineraries: {str(e)}")
        return []


def fetch_cultural_insights(poi: List[str]) -> Dict[str, Any]:
    """
    Get cultural insights and overview using Gemini AI for the points of interest.
    
    Args:
        poi (List[str]): List of points of interest
        
    Returns:
        Dict[str, Any]: AI-generated cultural insights and recommendations
    """
    try:
        # Configure Gemini API
        api_key = os.environ.get('GOOGLE_API_KEY')
        if not api_key:
            logger.error("GOOGLE_API_KEY environment variable is required")
            return {}
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Create prompt for Gemini to generate cultural insights
        poi_list = ", ".join(poi)
        prompt = f"""
        Generate comprehensive cultural insights and travel recommendations for a destination that includes these points of interest: {poi_list}
        
        Please provide a detailed cultural overview including:
        1. Historical and cultural significance of the area
        2. Local customs and etiquette to be aware of
        3. Best times to visit each attraction
        4. Local cuisine recommendations
        5. Transportation tips
        6. Language and communication tips
        7. Safety considerations
        8. Budget-friendly tips
        9. Hidden gems and local secrets
        10. Cultural events and festivals (if applicable)
        
        Return the response as a JSON object with the following structure:
        {{
            "cultural_overview": "Brief overview of the cultural significance",
            "historical_context": "Historical background of the area",
            "local_customs": ["custom1", "custom2", "custom3"],
            "etiquette_tips": ["tip1", "tip2", "tip3"],
            "best_visit_times": {{
                "attraction_name": "best time to visit"
            }},
            "cuisine_recommendations": ["dish1", "dish2", "restaurant1"],
            "transportation_tips": ["tip1", "tip2", "tip3"],
            "language_tips": ["phrase1", "phrase2", "phrase3"],
            "safety_considerations": ["consideration1", "consideration2"],
            "budget_tips": ["tip1", "tip2", "tip3"],
            "hidden_gems": ["gem1", "gem2", "gem3"],
            "cultural_events": ["event1", "event2"],
            "recommended_duration": "suggested time to spend",
            "total_attractions": {len(poi)}
        }}
        
        Make the insights specific to the location and attractions mentioned. Be practical and helpful for travelers.
        """
        
        # Generate response from Gemini
        response = model.generate_content(prompt)
        
        if not response.text:
            logger.error("No response received from Gemini API")
            return {}
        
        # Parse the JSON response
        try:
            # Clean the response text to extract JSON
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            response_text = response_text.strip()
            
            # Parse JSON
            insights = json.loads(response_text)
            
            # Validate the response format
            if not isinstance(insights, dict):
                logger.error("Invalid response format from Gemini API")
                return {}
            
            logger.info(f"Successfully generated AI-powered cultural insights for {len(poi)} points of interest")
            return insights
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response from Gemini: {str(e)}")
            logger.error(f"Raw response: {response.text}")
            return {}
        
    except Exception as e:
        logger.error(f"Error generating cultural insights: {str(e)}")
        return {}
