#!/usr/bin/env python3
"""
Test the complete agent conversation with a real scenario.
"""

import os
import sys
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
        
        # Scenario: User wants to plan a trip to France
        print("\n" + "="*60)
        print("SCENARIO: User wants to plan a trip to France")
        print("="*60)
        
        # Message 1: User wants to plan a trip to France
        print("\n👤 User: I want to plan a trip to France. What cities should I visit?")
        response1 = invoke_agent_with_history(agent, "I want to plan a trip to France. What cities should I visit?", conversation_messages)
        print(f"🤖 Agent: {response1.get('output', 'No response')}")
        conversation_messages.extend([
            HumanMessage(content="I want to plan a trip to France. What cities should I visit?"),
            AIMessage(content=response1.get('output', ''))
        ])
        
        # Message 2: User asks about attractions in Paris
        print("\n👤 User: What attractions are in Paris?")
        response2 = invoke_agent_with_history(agent, "What attractions are in Paris?", conversation_messages)
        print(f"🤖 Agent: {response2.get('output', 'No response')}")
        conversation_messages.extend([
            HumanMessage(content="What attractions are in Paris?"),
            AIMessage(content=response2.get('output', ''))
        ])
        
        # Message 3: User wants to calculate travel between cities
        print("\n👤 User: Calculate the travel distance between Paris, Lyon, and Nice")
        response3 = invoke_agent_with_history(agent, "Calculate the travel distance between Paris, Lyon, and Nice", conversation_messages)
        print(f"🤖 Agent: {response3.get('output', 'No response')}")
        conversation_messages.extend([
            HumanMessage(content="Calculate the travel distance between Paris, Lyon, and Nice"),
            AIMessage(content=response3.get('output', ''))
        ])
        
        # Message 4: User asks for flight options
        future_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        print(f"\n👤 User: I want to fly from New York to France on {future_date}. What are my flight options?")
        response4 = invoke_agent_with_history(agent, f"I want to fly from New York to France on {future_date}. What are my flight options?", conversation_messages)
        print(f"🤖 Agent: {response4.get('output', 'No response')}")
        
        # Check if the agent used the flight search tool
        if response4.get('intermediate_steps'):
            print("\n🔍 Tool Usage Analysis:")
            for step in response4.get('intermediate_steps', []):
                if hasattr(step, 'tool'):
                    print(f"✅ Agent used tool: {step.tool}")
        
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
        from app.agent.tools import get_recommended_cities, get_points_of_interest, calculate_travel_details, find_flight_options
        
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
        
        print("\nTesting find_flight_options...")
        future_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        flights = find_flight_options.invoke({
            "origin_city": "New York", 
            "destination_country": "France", 
            "travel_date": future_date
        })
        print(f"✅ Flights: {flights}")
        
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
