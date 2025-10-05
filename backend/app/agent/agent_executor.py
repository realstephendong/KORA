"""
LangChain agent executor for the travel planner using Google Gemini.
Handles conversational memory and tool integration with ReAct pattern.
"""

import os
import time
from typing import List, Dict, Any
from langchain.agents import AgentExecutor, create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain import hub
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

from app.agent.tools import get_recommended_cities, get_points_of_interest, calculate_travel_details, save_itinerary, find_flight_options, create_multiple_itineraries, get_hotel_options, get_hotel_price, get_cultural_insights

def create_travel_agent() -> AgentExecutor:
    """
    Creates a travel planning agent using Google Gemini with ReAct pattern.
    
    Returns:
        AgentExecutor: Configured agent executor
    """
    # Initialize Google Gemini model (free tier)
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,
        convert_system_message_to_human=True,
        google_api_key=os.environ.get('GOOGLE_API_KEY')
    )
    
    # Define available tools
    tools = [get_recommended_cities, get_points_of_interest, calculate_travel_details, save_itinerary, find_flight_options, create_multiple_itineraries, get_hotel_options, get_hotel_price, get_cultural_insights]
    
    # Pull the standard ReAct prompt from LangChain Hub
    prompt = hub.pull("hwchase17/react-chat")
    
    # Add custom system message to make agent aware of new capabilities
    system_message = """You are a travel planning assistant. Help users plan their trips by providing city recommendations and itinerary options.

## CRITICAL RULES:
- NEVER mention tool names in your responses
- NEVER show "Action:" or "Action Input:" in your responses  
- NEVER mention that you're using tools or APIs
- Keep responses concise and natural
- If you get stuck, ask a simple question to move forward
- Focus on travel recommendations, not technical details

## IMPORTANT: Always follow the ReAct pattern correctly:
- After "Thought:", you MUST include "Action:" and "Action Input:"
- If you don't need to use a tool, end with "Final Answer:"
- Never leave "Thought:" without a follow-up action

## WORKFLOW (Country is already selected by user):

**Layer 1 - City Discovery:**
- The user has already selected a country (this is given context)
- Ask: "What cities do you want to visit in [COUNTRY]?" 
- Suggest top cities in that country
- Let the user choose cities they're interested in (even if just one city)

**Layer 2 - Attraction Discovery:**
- For each selected city, ask: "What places do you want to visit in [CITY]?"
- Suggest real attractions and landmarks
- Let the user select their preferred attractions for each city

**Layer 3 - Itinerary Creation:**
- Ask the user for their food budget for the entire trip
- Generate itinerary options based on their city selections
- For single cities: Create a detailed single-city itinerary with multiple day options
- For multiple cities: Create different city orders/routes with distance and carbon calculations
- Present itinerary options with:
  - Different routes (if multiple cities) or day-by-day plans (if single city)
  - Total distance and carbon emissions (if applicable)
  - Estimated travel time and total costs
  - Cost breakdown (flights, accommodation, food, fuel)
  - Key attractions included

**Layer 4 - Flight Planning (Optional):**
- Only if user wants to fly to the country, ask for their departure city and travel date
- Find flight options and present them with carbon impact

**Final Phase:**
- Present all itinerary options with filters for price and carbon emissions
- Show cost breakdowns and total costs for each option
- Let user select their preferred itinerary
- Offer to save the final selected itinerary

IMPORTANT: Always follow this sequence:
- Start with city recommendations (country is already known)
- Then get attraction preferences for each city
- Create itinerary options with calculations
- Present options with filters
- Only handle flights if user specifically requests them
- Save the final selected itinerary

Always aim to provide real, up-to-date information and complete travel plans that users can actually execute."""
    
    # Add the system message to the prompt
    if hasattr(prompt, 'messages'):
        prompt.messages.insert(0, {"role": "system", "content": system_message})
    else:
        # For older prompt templates, add system message differently
        prompt.template = system_message + "\n\n" + prompt.template
    
    # Create the agent using ReAct pattern
    agent = create_react_agent(llm, tools, prompt)
    
    # Create the agent executor with better error handling
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        return_intermediate_steps=True,
        handle_parsing_errors=True,
        max_iterations=5,  # Allow enough iterations for proper workflow
        max_execution_time=30  # Add time limit
    )
    
    return agent_executor


def parse_chat_history(chat_history_data: List[Dict[str, str]]) -> List[BaseMessage]:
    """
    Parses chat history from API request format to LangChain message format.
    
    Args:
        chat_history_data (List[Dict[str, str]]): Chat history in API format
        
    Returns:
        List[BaseMessage]: Parsed LangChain messages
    """
    messages = []
    
    for message in chat_history_data:
        role = message.get('role', '').lower()
        content = message.get('content', '')
        
        if role == 'human' or role == 'user':
            messages.append(HumanMessage(content=content))
        elif role == 'ai' or role == 'assistant':
            messages.append(AIMessage(content=content))
    
    return messages


def invoke_agent_with_history(
    agent_executor: AgentExecutor,
    user_message: str,
    chat_history: List[BaseMessage]
) -> Dict[str, Any]:
    """
    Invokes the agent with user message and chat history.
    
    Args:
        agent_executor (AgentExecutor): The configured agent
        user_message (str): The user's current message
        chat_history (List[BaseMessage]): Previous conversation messages
        
    Returns:
        Dict[str, Any]: Agent response with intermediate steps
    """
    try:
        # Prepare the input for the agent
        input_data = {
            "input": user_message,
            "chat_history": chat_history
        }
        
        # Invoke the agent with rate limit handling
        result = agent_executor.invoke(input_data)
        
        # Check if the agent got stuck in a loop or hit iteration limit
        output_text = str(result.get("output", ""))
        if ("Agent stopped due to iteration limit" in output_text):
            return {
                "output": "I apologize, but I encountered some technical difficulties. Let me help you with a simpler approach. What specific cities or attractions are you most interested in visiting?",
                "intermediate_steps": [],
                "success": False,
                "error": "Agent iteration limit exceeded"
            }
        
        # Check for parsing errors and provide a helpful response
        if ("Invalid Format: Missing 'Action:'" in output_text and 
            "Thought:" in output_text and 
            "Action:" not in output_text):
            return {
                "output": "I apologize, but I encountered a technical issue. Let me help you with your travel planning. What specific cities in Spain are you most interested in visiting?",
                "intermediate_steps": [],
                "success": False,
                "error": "ReAct parsing error"
            }
        
        return {
            "output": result.get("output", ""),
            "intermediate_steps": result.get("intermediate_steps", []),
            "success": True
        }
        
    except Exception as e:
        error_msg = str(e)
        
        # Handle rate limit errors specifically
        if "429" in error_msg or "quota" in error_msg.lower() or "rate limit" in error_msg.lower():
            return {
                "output": "I'm currently experiencing high demand. Please wait a moment and try again, or consider upgrading to a paid plan for higher rate limits.",
                "intermediate_steps": [],
                "success": False,
                "error": "Rate limit exceeded",
                "rate_limited": True
            }
        
        # Handle iteration limit errors
        if "iteration limit" in error_msg.lower():
            return {
                "output": "I apologize, but I encountered some technical difficulties. Let me help you with a simpler approach. What specific cities or attractions are you most interested in visiting?",
                "intermediate_steps": [],
                "success": False,
                "error": "Agent iteration limit exceeded"
            }
        
        return {
            "output": f"I apologize, but I encountered an error: {error_msg}",
            "intermediate_steps": [],
            "success": False,
            "error": error_msg
        }
