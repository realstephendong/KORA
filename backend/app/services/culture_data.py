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

def fetch_events(itinerary: List[str]) -> Dict[str, Any]:
    """
    Get events for a given itinerary.
    """
    return fetch_events(itinerary)

def fetch_images(places: List[str]) -> Dict[str, Any]:
    """
    Get images and place information using Google Places API.
    
    Args:
        places (List[str]): List of places to search for
        
    Returns:
        Dict[str, Any]: Place information with images and details
    """
    try:
        api_key = os.environ.get('GOOGLE_API_KEY')
        if not api_key:
            logger.error("GOOGLE_API_KEY environment variable is required")
            return {}
        
        url = "https://places.googleapis.com/v1/places:searchText"
        headers = {
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': api_key,
            'X-Goog-FieldMask': 'places.displayName,places.formattedAddress,places.priceLevel,places.photos,places.rating,places.userRatingCount,places.types'
        }
        
        results = {}
        
        for place in places:
            # Create search query for the place
            search_query = f"{place} tourist attraction"
            
            payload = {
                "textQuery": search_query
            }
            
            logger.info(f"Searching for images and info for: {place}")
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'places' in data and len(data['places']) > 0:
                    place_data = data['places'][0]  # Get the first result
                    
                    # Extract place information
                    place_info = {
                        'name': place_data.get('displayName', {}).get('text', place),
                        'address': place_data.get('formattedAddress', 'Address not available'),
                        'price_level': place_data.get('priceLevel', 'Price level not available'),
                        'rating': place_data.get('rating', 'Rating not available'),
                        'user_rating_count': place_data.get('userRatingCount', 0),
                        'types': place_data.get('types', []),
                        'photos': []
                    }
                    
                    # Process photos if available
                    if 'photos' in place_data:
                        for photo in place_data['photos'][:3]:  # Limit to 3 photos
                            photo_info = {
                                'name': photo.get('name', ''),
                                'width_px': photo.get('widthPx', 0),
                                'height_px': photo.get('heightPx', 0),
                                'author_attributions': photo.get('authorAttributions', [])
                            }
                            place_info['photos'].append(photo_info)
                    
                    results[place] = place_info
                    logger.info(f"Found {len(place_info['photos'])} photos for {place}")
                else:
                    logger.warning(f"No places found for: {place}")
                    results[place] = {'error': 'No places found'}
            else:
                logger.error(f"Google Places API error for {place}: {response.status_code} - {response.text}")
                results[place] = {'error': f'API error: {response.status_code}'}
        
        return {
            'places': results,
            'total_places_searched': len(places),
            'successful_searches': len([r for r in results.values() if 'error' not in r])
        }
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching images from Google Places API: {str(e)}")
        return {'error': f'Request error: {str(e)}'}
    except Exception as e:
        logger.error(f"Unexpected error fetching images: {str(e)}")
        return {'error': f'Unexpected error: {str(e)}'}

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
