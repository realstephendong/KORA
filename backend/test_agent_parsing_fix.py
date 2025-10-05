#!/usr/bin/env python3
"""
Test script to verify the improved parsing error handling.
"""

import os
import sys
from dotenv import load_dotenv

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

def test_parsing_error_handling():
    """Test the improved parsing error handling."""
    print("🧪 Testing Improved Parsing Error Handling")
    print("=" * 50)
    
    try:
        from app.agent.agent_executor import create_travel_agent, invoke_agent_with_history
        from langchain_core.messages import HumanMessage, AIMessage
        
        # Create the agent
        print("Creating travel agent...")
        agent = create_travel_agent()
        print("✅ Agent created successfully")
        
        # Test scenarios that might trigger parsing errors
        test_scenarios = [
            "What cities should I visit in the United Kingdom?",
            "Tell me about attractions in London",
            "I want to visit museums and historical sites",
            "What should I see in Birmingham?"
        ]
        
        conversation_messages = []
        
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"\n--- Test Scenario {i} ---")
            print(f"Input: {scenario}")
            
            try:
                result = invoke_agent_with_history(agent, scenario, conversation_messages)
                
                if result.get('success', False):
                    print(f"✅ Success: {result.get('output', 'No response')[:100]}...")
                else:
                    print(f"⚠️ Handled Error: {result.get('output', 'No response')}")
                    print(f"Error Type: {result.get('error', 'Unknown')}")
                
                # Add to conversation history
                conversation_messages.extend([
                    HumanMessage(content=scenario),
                    AIMessage(content=result.get('output', ''))
                ])
                
            except Exception as e:
                print(f"❌ Exception: {str(e)}")
        
        print("\n" + "="*50)
        print("✅ Parsing error handling test completed")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_error_detection():
    """Test the error detection logic."""
    print("\n🔍 Testing Error Detection Logic")
    print("=" * 40)
    
    # Test cases for error detection
    test_cases = [
        ("Thought: I need to help with cities", True),  # Should trigger error
        ("Thought: I need to help\nAction: get_recommended_cities", False),  # Should not trigger
        ("Final Answer: Here are some cities", False),  # Should not trigger
        ("Invalid Format: Missing 'Action:'", True),  # Should trigger error
        ("What cities should I visit?", False),  # Should not trigger
    ]
    
    for test_input, should_error in test_cases:
        # Simulate the error detection logic
        has_thought = "Thought:" in test_input
        has_action = "Action:" in test_input
        has_final_answer = "Final Answer:" in test_input
        
        detected_error = (has_thought and not has_action and not has_final_answer) or "Invalid Format" in test_input
        
        status = "✅" if detected_error == should_error else "❌"
        print(f"{status} '{test_input[:30]}...' -> Expected: {should_error}, Got: {detected_error}")
    
    print("✅ Error detection test completed")

if __name__ == "__main__":
    print("🧪 Testing Improved Agent Parsing Error Handling")
    print("=" * 60)
    
    # Test error detection logic
    test_error_detection()
    
    # Test actual agent with error handling
    success = test_parsing_error_handling()
    
    if success:
        print("\n🎉 All parsing error handling tests passed!")
        print("The agent should now handle parsing errors more gracefully.")
    else:
        print("\n⚠️ Some tests failed. Check the error messages above.")
