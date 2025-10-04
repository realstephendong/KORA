#!/usr/bin/env python3
"""
Simple test script for KORA geo API and agent functionality.
Tests the core functionality without complex authentication.
"""

import os
import sys
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_geo_api_simple():
    """Test geo API with simplified queries."""
    print("=== Testing Geo API (Simplified) ===")
    
    try:
        from app.services.geo_api import fetch_cities_for_country, fetch_city_details
        
        # Test with a simple approach - let's try different countries
        test_countries = ["France", "Italy", "Spain", "Germany"]
        
        for country in test_countries:
            print(f"\n--- Testing {country} ---")
            cities = fetch_cities_for_country(country)
            if cities:
                print(f"✅ {country}: {cities}")
            else:
                print(f"❌ {country}: No cities returned")
        
        # Test city details
        print(f"\n--- Testing City Details ---")
        test_cities = ["Paris", "Rome", "Madrid", "Berlin"]
        
        for city in test_cities:
            details = fetch_city_details(city)
            if details:
                print(f"✅ {city}: {details}")
            else:
                print(f"❌ {city}: No details returned")
                
    except Exception as e:
        print(f"❌ Geo API error: {e}")


def test_agent_tools_simple():
    """Test agent tools with hardcoded data."""
    print("\n=== Testing Agent Tools ===")
    
    try:
        from app.agent.tools import get_recommended_cities, get_points_of_interest
        
        # Test get_points_of_interest (this should work with hardcoded data)
        print("\n--- Testing Points of Interest ---")
        test_cities = ["Paris", "London", "New York", "Tokyo", "Rome"]
        
        for city in test_cities:
            attractions = get_points_of_interest(city)
            if attractions:
                print(f"✅ {city}: {len(attractions)} attractions")
                for attraction in attractions[:2]:  # Show first 2
                    print(f"   - {attraction['name']} ({attraction['category']})")
            else:
                print(f"❌ {city}: No attractions")
        
        # Test get_recommended_cities (this might fail due to geo API issues)
        print("\n--- Testing Recommended Cities ---")
        test_countries = ["France", "Italy"]
        
        for country in test_countries:
            cities = get_recommended_cities(country)
            if cities:
                print(f"✅ {country}: {cities}")
            else:
                print(f"❌ {country}: No cities (likely due to geo API issues)")
                
    except Exception as e:
        print(f"❌ Agent tools error: {e}")


def test_agent_executor_simple():
    """Test agent executor with simple queries."""
    print("\n=== Testing Agent Executor ===")
    
    # Check if Google API key is available
    google_key = os.environ.get('GOOGLE_API_KEY')
    if not google_key:
        print("❌ GOOGLE_API_KEY not found")
        return
    
    print(f"✅ Google API key found: {google_key[:10]}...")
    
    try:
        from app.agent.agent_executor import create_travel_agent, invoke_agent_with_history
        
        # Create the agent
        print("\n--- Creating travel agent ---")
        agent = create_travel_agent()
        print("✅ Travel agent created successfully")
        
        # Test agent with simple messages
        test_messages = [
            "What attractions are in Paris?",
            "Tell me about London",
            "I want to visit Italy"
        ]
        
        for message in test_messages:
            print(f"\n--- Testing: '{message}' ---")
            try:
                result = invoke_agent_with_history(agent, message, [])
                
                if result.get('success'):
                    print(f"✅ Response: {result.get('output', 'No output')[:100]}...")
                    if result.get('intermediate_steps'):
                        print(f"✅ Used {len(result['intermediate_steps'])} tools")
                else:
                    print(f"❌ Failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                print(f"❌ Agent error: {e}")
                
    except Exception as e:
        print(f"❌ Agent executor error: {e}")


def test_curl_commands():
    """Test the API endpoints with curl commands."""
    print("\n=== Testing API Endpoints with curl ===")
    
    base_url = "http://localhost:8000"
    
    # Test health endpoint
    print("\n--- Health Endpoint ---")
    import subprocess
    try:
        result = subprocess.run(['curl', '-s', f'{base_url}/api/health'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Health: {result.stdout.strip()}")
        else:
            print(f"❌ Health failed: {result.stderr}")
    except Exception as e:
        print(f"❌ Health error: {e}")
    
    # Test public endpoint
    print("\n--- Public Endpoint ---")
    try:
        result = subprocess.run(['curl', '-s', f'{base_url}/api/public'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Public: {result.stdout.strip()}")
        else:
            print(f"❌ Public failed: {result.stderr}")
    except Exception as e:
        print(f"❌ Public error: {e}")


if __name__ == "__main__":
    print("🧪 Simple KORA Testing")
    print("=" * 50)
    
    # Test curl endpoints
    test_curl_commands()
    
    # Test geo API
    test_geo_api_simple()
    
    # Test agent tools
    test_agent_tools_simple()
    
    # Test agent executor
    test_agent_executor_simple()
    
    print("\n" + "=" * 50)
    print("🎉 Simple testing completed!")
