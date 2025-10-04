#!/usr/bin/env python3
"""
Test script for KORA API with authentication.
Tests the geo API and agent functionality with proper Auth0 authentication.
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_auth0_token():
    """
    Get an access token from Auth0 for testing.
    This is a simplified version - in production, you'd use the proper OAuth flow.
    """
    auth0_domain = os.environ.get('AUTH0_DOMAIN')
    client_id = os.environ.get('AUTH0_CLIENT_ID')
    client_secret = os.environ.get('AUTH0_CLIENT_SECRET')
    
    if not all([auth0_domain, client_id, client_secret]):
        print("❌ Auth0 client credentials not found in .env file")
        print("Please add AUTH0_CLIENT_ID and AUTH0_CLIENT_SECRET to your .env file")
        return None
    
    print(f"✅ Found Auth0 credentials:")
    print(f"   Domain: {auth0_domain}")
    print(f"   Client ID: {client_id[:10]}...")
    print(f"   Client Secret: {client_secret[:10]}...")
    
    # Auth0 Machine-to-Machine token request
    url = f"https://{auth0_domain}/oauth/token"
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "audience": os.environ.get('AUTH0_API_AUDIENCE'),
        "grant_type": "client_credentials"
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            token_data = response.json()
            return token_data.get('access_token')
        else:
            print(f"❌ Failed to get Auth0 token: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error getting Auth0 token: {e}")
        return None


def test_endpoints_without_auth():
    """Test endpoints that don't require authentication."""
    print("=== Testing Public Endpoints ===")
    
    base_url = "http://localhost:8000"
    
    # Test health endpoint
    print("\n--- Testing Health Endpoint ---")
    try:
        response = requests.get(f"{base_url}/api/health")
        if response.status_code == 200:
            print(f"✅ Health endpoint: {response.json()}")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
    
    # Test public endpoint
    print("\n--- Testing Public Endpoint ---")
    try:
        response = requests.get(f"{base_url}/api/public")
        if response.status_code == 200:
            print(f"✅ Public endpoint: {response.json()}")
        else:
            print(f"❌ Public endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Public endpoint error: {e}")


def test_chat_endpoint_with_auth():
    """Test the chat endpoint with authentication."""
    print("\n=== Testing Chat Endpoint with Authentication ===")
    
    base_url = "http://localhost:8000"
    
    # Get Auth0 token
    token = get_auth0_token()
    if not token:
        print("❌ Cannot test chat endpoint without Auth0 token")
        return
    
    print(f"✅ Got Auth0 token: {token[:20]}...")
    
    # Test chat endpoint
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    test_messages = [
        "I want to visit France",
        "What are the top cities in Italy?",
        "Tell me about attractions in Paris"
    ]
    
    for message in test_messages:
        print(f"\n--- Testing message: '{message}' ---")
        try:
            payload = {
                "message": message,
                "chat_history": []
            }
            
            response = requests.post(
                f"{base_url}/api/chat/message",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Response: {result.get('response', 'No response')}")
                if result.get('intermediate_steps'):
                    print(f"✅ Agent used {len(result['intermediate_steps'])} tools")
            else:
                print(f"❌ Chat failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Chat endpoint error: {e}")


def test_geo_api_directly():
    """Test the geo API functions directly without authentication."""
    print("\n=== Testing Geo API Directly ===")
    
    # Add the backend directory to Python path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    try:
        from app.services.geo_api import fetch_cities_for_country, fetch_city_details
        
        # Test fetch_cities_for_country
        print("\n--- Testing fetch_cities_for_country ---")
        cities = fetch_cities_for_country("France")
        if cities:
            print(f"✅ Cities for France: {cities}")
        else:
            print("❌ No cities returned for France")
        
        # Test fetch_city_details
        print("\n--- Testing fetch_city_details ---")
        city_details = fetch_city_details("Paris")
        if city_details:
            print(f"✅ Paris details: {city_details}")
        else:
            print("❌ No details returned for Paris")
            
    except Exception as e:
        print(f"❌ Geo API error: {e}")


def test_agent_tools_directly():
    """Test the agent tools directly."""
    print("\n=== Testing Agent Tools Directly ===")
    
    try:
        from app.agent.tools import get_recommended_cities, get_points_of_interest
        
        # Test get_recommended_cities
        print("\n--- Testing get_recommended_cities ---")
        cities = get_recommended_cities("France")
        if cities:
            print(f"✅ Agent tool cities: {cities}")
        else:
            print("❌ Agent tool returned no cities")
        
        # Test get_points_of_interest
        print("\n--- Testing get_points_of_interest ---")
        attractions = get_points_of_interest("Paris")
        if attractions:
            print(f"✅ Paris attractions: {attractions}")
        else:
            print("❌ No attractions returned")
            
    except Exception as e:
        print(f"❌ Agent tools error: {e}")


if __name__ == "__main__":
    print("🧪 Testing KORA API with Authentication")
    print("=" * 50)
    
    # Test public endpoints
    test_endpoints_without_auth()
    
    # Test geo API directly
    test_geo_api_directly()
    
    # Test agent tools directly
    test_agent_tools_directly()
    
    # Test chat endpoint with auth (if Auth0 is configured)
    test_chat_endpoint_with_auth()
    
    print("\n" + "=" * 50)
    print("🎉 Testing completed!")
