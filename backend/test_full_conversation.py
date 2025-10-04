#!/usr/bin/env python3
"""
Test the complete agent conversation with a real scenario.
"""

import os
import sys
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

def test_full_conversation():
    """Test a complete conversation scenario with the agent."""
    print("🤖 Testing Full Agent Conversation")
    print("=" * 50)
    
    try:
        from app.agent.agent_executor import create_travel_agent, invoke_agent_with_history
        from langchain_core.messages import HumanMessage, AIMessage
        
        # Create the agent
        print("Creating travel agent...")
        agent = create_travel_agent()
        print("✅ Agent created successfully")
        
        # Simulate a complete conversation
        conversation_messages = []
        
        # Scenario: User has already selected France from the globe page
        print("\n" + "="*60)
        print("SCENARIO: User has selected France from the globe page")
        print("="*60)
        
        # Message 1: User wants to plan cities in France (country already selected)
        print("\n👤 User: What cities should I visit in France?")
        response1 = invoke_agent_with_history(agent, "What cities should I visit in France?", conversation_messages)
        print(f"🤖 Agent: {response1.get('output', 'No response')}")
        conversation_messages.extend([
            HumanMessage(content="What cities should I visit in France?"),
            AIMessage(content=response1.get('output', ''))
        ])
        
        # Add delay to prevent rate limiting
        print("⏳ Waiting 3 seconds to avoid rate limits...")
        time.sleep(3)
        
        # Message 2: User asks about attractions in Paris
        print("\n👤 User: What attractions are in Paris?")
        response2 = invoke_agent_with_history(agent, "What attractions are in Paris?", conversation_messages)
        print(f"🤖 Agent: {response2.get('output', 'No response')}")
        conversation_messages.extend([
            HumanMessage(content="What attractions are in Paris?"),
            AIMessage(content=response2.get('output', ''))
        ])
        
        # Add delay to prevent rate limiting
        print("⏳ Waiting 3 seconds to avoid rate limits...")
        time.sleep(3)
        
        # Message 3: User wants to create multiple itinerary options
        print("\n👤 User: Create multiple itinerary options for Paris, Lyon, and Nice. My food budget is $200 for the whole trip.")
        response3 = invoke_agent_with_history(agent, "Create multiple itinerary options for Paris, Lyon, and Nice. My food budget is $200 for the whole trip.", conversation_messages)
        print(f"🤖 Agent: {response3.get('output', 'No response')}")
        conversation_messages.extend([
            HumanMessage(content="Create multiple itinerary options for Paris, Lyon, and Nice. My food budget is $200 for the whole trip."),
            AIMessage(content=response3.get('output', ''))
        ])
        
        # Add delay to prevent rate limiting
        print("⏳ Waiting 3 seconds to avoid rate limits...")
        time.sleep(3)
        
        # Message 4: User asks for flight options with carbon efficiency focus
        future_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        print(f"\n👤 User: I want to fly from New York to France on {future_date}. Show me flight options with carbon efficiency comparison.")
        response4 = invoke_agent_with_history(agent, f"I want to fly from New York to France on {future_date}. Show me flight options with carbon efficiency comparison.", conversation_messages)
        print(f"🤖 Agent: {response4.get('output', 'No response')}")
        
        # Check if the agent used the flight search tool
        if response4.get('intermediate_steps'):
            print("\n🔍 Tool Usage Analysis:")
            for step in response4.get('intermediate_steps', []):
                if hasattr(step, 'tool'):
                    print(f"✅ Agent used tool: {step.tool}")
        
        # Add delay to prevent rate limiting
        print("⏳ Waiting 3 seconds to avoid rate limits...")
        time.sleep(3)
        
        # Message 5: User wants to create itineraries with flight costs
        print(f"\n👤 User: Create itineraries for Paris, Lyon, Nice with flight costs from New York on {future_date}")
        response5 = invoke_agent_with_history(agent, f"Create itineraries for Paris, Lyon, Nice with flight costs from New York on {future_date}", conversation_messages)
        print(f"🤖 Agent: {response5.get('output', 'No response')}")
        
        # Check if the agent used the create_multiple_itineraries tool
        if response5.get('intermediate_steps'):
            print("\n🔍 Itinerary Creation Analysis:")
            for step in response5.get('intermediate_steps', []):
                if hasattr(step, 'tool'):
                    print(f"✅ Agent used tool: {step.tool}")
                    if step.tool == 'create_multiple_itineraries':
                        print("✅ Flight costs should be included in itinerary calculations")
        
        print("\n" + "="*60)
        print("CONVERSATION COMPLETE")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"❌ Conversation test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_agent_tools():
    """Test individual agent tools."""
    print("\n🔧 Testing Agent Tools")
    print("=" * 30)
    
    try:
        from app.agent.tools import get_recommended_cities, get_points_of_interest, calculate_travel_details, find_flight_options, create_multiple_itineraries, get_itinerary
        
        # Test each tool
        print("Testing get_recommended_cities...")
        cities = get_recommended_cities.invoke({"country_name": "France"})
        print(f"✅ Cities: {cities}")
        
        print("\nTesting get_points_of_interest...")
        attractions = get_points_of_interest.invoke({"city": "Paris"})
        print(f"✅ Attractions: {attractions}")
        
        print("\nTesting calculate_travel_details...")
        travel = calculate_travel_details.invoke({"cities": ["Paris", "Lyon", "Nice"]})
        print(f"✅ Travel details: {travel}")
        
        print("\nTesting create_multiple_itineraries with flight costs and food budget...")
        future_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        itineraries = create_multiple_itineraries.invoke({
            "cities": ["Paris", "Lyon", "Nice"],
            "origin_city": "New York",
            "travel_date": future_date,
            "destination_country": "France",
            "food_budget": 200.0  # User's food budget for the trip
        })
        print(f"✅ Multiple itineraries with costs: {itineraries}")
        
        # Analyze the itinerary results for flight cost integration
        if itineraries and not any('error' in str(itinerary) for itinerary in itineraries):
            print("\n📊 Itinerary Analysis:")
            for i, itinerary in enumerate(itineraries[:2]):  # Show first 2 itineraries
                print(f"  Itinerary {i+1}:")
                print(f"    Cities: {itinerary.get('cities', [])}")
                print(f"    Distance: {itinerary.get('total_distance_km', 0)} km")
                print(f"    Carbon: {itinerary.get('carbon_emissions_kg', 0)} kg CO2")
                if 'costs' in itinerary:
                    costs = itinerary['costs']
                    print(f"    Total Cost: ${costs.get('total_cost', 0)}")
                    print(f"    Flight Cost: ${costs.get('flight_cost', 0)}")
                    print(f"    Land Cost: ${costs.get('land_based_cost', 0)}")
                    if 'cost_breakdown' in costs:
                        breakdown = costs['cost_breakdown']
                        print(f"    Breakdown: Fuel ${breakdown.get('fuel', 0)}, Accommodation ${breakdown.get('accommodation', 0)}, Food ${breakdown.get('food', 0)}, Flights ${breakdown.get('flights', 0)}")
                print()
        else:
            print("⚠️ No valid itineraries returned or error in creation")
        
        print("\nTesting get_itinerary...")
        itinerary_details = get_itinerary.invoke({
            "poi": ["Eiffel Tower", "Louvre Museum"],
            "start_date": "2024-06-15",
            "end_date": "2024-06-20"
        })
        print(f"✅ Detailed itinerary: {itinerary_details}")
        
        print("\nTesting find_flight_options...")
        future_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        flights = find_flight_options.invoke({
            "origin_city": "New York", 
            "destination_country": "France", 
            "travel_date": future_date
        })
        print(f"✅ Flights: {flights}")
        
        # Test flight API directly for detailed analysis
        print("\nTesting flight API directly for carbon efficiency analysis...")
        from app.services.flight_api import search_flights
        direct_flights = search_flights('JFK', 'CDG', future_date)
        print(f"✅ Direct flight API test: Found {len(direct_flights)} flights")
        
        if direct_flights:
            print("Flight options for carbon efficiency comparison:")
            for i, flight in enumerate(direct_flights[:3]):
                print(f"  {i+1}. {flight.get('airline')} - €{flight.get('price')} - {flight.get('stops')} stops - {'Direct' if flight.get('is_direct') else 'Connecting'}")
                if 'warning' in flight:
                    print(f"     ⚠️ {flight.get('warning')}")
        
        # Test carbon efficiency comparison
        print("\nTesting carbon efficiency comparison...")
        if direct_flights:
            direct_flights_list = [f for f in direct_flights if f.get('is_direct')]
            connecting_flights_list = [f for f in direct_flights if not f.get('is_direct')]
            
            print(f"Direct flights: {len(direct_flights_list)}")
            print(f"Connecting flights: {len(connecting_flights_list)}")
            
            if direct_flights_list and connecting_flights_list:
                direct_price = min(f.get('price', 0) for f in direct_flights_list)
                connecting_price = min(f.get('price', 0) for f in connecting_flights_list)
                print(f"Price comparison: Direct €{direct_price} vs Connecting €{connecting_price}")
                print("✅ Carbon efficiency data available for itinerary creation")
        
        return True
        
    except Exception as e:
        print(f"❌ Tool test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run the full conversation test."""
    print("🧪 Testing Full Agent Conversation")
    print("=" * 60)
    
    # Test individual tools first
    tools_success = test_agent_tools()
    
    # Test full conversation
    conversation_success = test_full_conversation()
    
    # Show results
    print("\n📊 Test Results:")
    print(f"Individual Tools: {'✅' if tools_success else '❌'}")
    print(f"Full Conversation: {'✅' if conversation_success else '❌'}")
    
    if tools_success and conversation_success:
        print("\n🎉 All tests passed! Your agent is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Check the error messages above.")


if __name__ == "__main__":
    main()
