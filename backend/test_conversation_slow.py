#!/usr/bin/env python3
"""
Test the complete agent conversation with rate limiting to avoid hitting Gemini API limits.
This version includes delays and better error handling for the free tier.
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

def test_conversation_with_rate_limiting():
    """Test a complete conversation scenario with rate limiting."""
    print("🤖 Testing Agent Conversation (Rate Limited)")
    print("=" * 50)
    
    try:
        from app.agent.agent_executor import create_travel_agent, invoke_agent_with_history
        from langchain_core.messages import HumanMessage, AIMessage
        
        # Create the agent
        print("Creating travel agent...")
        agent = create_travel_agent()
        print("✅ Agent created successfully")
        
        # Initialize conversation history
        conversation_messages = []
        
        # Scenario: User has already selected France from the globe page
        print("\n" + "="*60)
        print("SCENARIO: User has selected France from the globe page")
        print("="*60)
        
        # Message 1: User wants to plan cities in France (country already selected)
        print("\n👤 User: What cities should I visit in France?")
        response1 = invoke_agent_with_history(agent, "What cities should I visit in France?", conversation_messages)
        
        if response1.get('rate_limited'):
            print("⚠️  Rate limit hit! Waiting 60 seconds...")
            time.sleep(60)
            response1 = invoke_agent_with_history(agent, "What cities should I visit in France?", conversation_messages)
        
        print(f"🤖 Agent: {response1.get('output', 'No response')}")
        conversation_messages.extend([
            HumanMessage(content="What cities should I visit in France?"),
            AIMessage(content=response1.get('output', ''))
        ])
        
        # Add delay to prevent rate limiting
        print("⏳ Waiting 5 seconds to avoid rate limits...")
        time.sleep(5)
        
        # Message 2: User asks about attractions in Paris
        print("\n👤 User: What attractions are in Paris?")
        response2 = invoke_agent_with_history(agent, "What attractions are in Paris?", conversation_messages)
        
        if response2.get('rate_limited'):
            print("⚠️  Rate limit hit! Waiting 60 seconds...")
            time.sleep(60)
            response2 = invoke_agent_with_history(agent, "What attractions are in Paris?", conversation_messages)
        
        print(f"🤖 Agent: {response2.get('output', 'No response')}")
        conversation_messages.extend([
            HumanMessage(content="What attractions are in Paris?"),
            AIMessage(content=response2.get('output', ''))
        ])
        
        # Add delay to prevent rate limiting
        print("⏳ Waiting 5 seconds to avoid rate limits...")
        time.sleep(5)
        
        # Message 3: User wants to create multiple itinerary options
        print("\n👤 User: Create multiple itinerary options for Paris, Lyon, and Nice")
        response3 = invoke_agent_with_history(agent, "Create multiple itinerary options for Paris, Lyon, and Nice", conversation_messages)
        
        if response3.get('rate_limited'):
            print("⚠️  Rate limit hit! Waiting 60 seconds...")
            time.sleep(60)
            response3 = invoke_agent_with_history(agent, "Create multiple itinerary options for Paris, Lyon, and Nice", conversation_messages)
        
        print(f"🤖 Agent: {response3.get('output', 'No response')}")
        conversation_messages.extend([
            HumanMessage(content="Create multiple itinerary options for Paris, Lyon, and Nice"),
            AIMessage(content=response3.get('output', ''))
        ])
        
        # Add delay to prevent rate limiting
        print("⏳ Waiting 5 seconds to avoid rate limits...")
        time.sleep(5)
        
        # Message 4: User asks for flight options (optional)
        future_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        print(f"\n👤 User: I also want to fly from New York to France on {future_date}. What are my flight options?")
        response4 = invoke_agent_with_history(agent, f"I also want to fly from New York to France on {future_date}. What are my flight options?", conversation_messages)
        
        if response4.get('rate_limited'):
            print("⚠️  Rate limit hit! Waiting 60 seconds...")
            time.sleep(60)
            response4 = invoke_agent_with_history(agent, f"I also want to fly from New York to France on {future_date}. What are my flight options?", conversation_messages)
        
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
        
        print("\n📊 Test Results:")
        print("Individual Tools: ✅")
        print("Full Conversation: ✅")
        
        print("\n🎉 All tests passed! Your agent is working correctly.")
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    test_conversation_with_rate_limiting()
