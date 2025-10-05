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
        model="gemini-2.5-pro",
        temperature=0,
        convert_system_message_to_human=True,
        google_api_key=os.environ.get('GOOGLE_API_KEY')
    )
    
    # Define available tools
    tools = [get_recommended_cities, get_points_of_interest, calculate_travel_details, save_itinerary, find_flight_options, create_multiple_itineraries, get_hotel_options, get_hotel_price, get_cultural_insights]
    
    # Pull the standard ReAct prompt from LangChain Hub
    prompt = hub.pull("hwchase17/react-chat")
    
    # Add custom system message with improved prompt engineering
    system_message = """You are a travel planning assistant. You help users plan trips by gathering information and creating itineraries.

## CRITICAL FORMAT REQUIREMENTS
You MUST follow the ReAct pattern exactly:
- ALWAYS end responses with either "Action:" or "Final Answer:" 
- NEVER end with just "Thought:" - this will cause errors
- If you start with "Thought:", you MUST follow with either "Action:" or "Final Answer:"
- For simple responses: Thought: [reasoning] → Final Answer: [response]
- For tool use: Thought: [reasoning] → Action: [tool] → Action Input: [params] → Observation: [result] → Final Answer: [response]

## CONVERSATION STATE TRACKING
Track what information you have and what you still need:

**REQUIRED INFO:**
- Country: [already provided by user]
- Travel dates: [departure date + duration]
- Origin: [where they're traveling from]
- Cities: [which cities they want to visit]
- Attractions: [what they want to see in each city]
- Flight costs: [flight options and costs to and from the destination country]

**OPTIONAL INFO:**
- Budget: [if provided, use for recommendations]
- Interests: [if provided, tailor recommendations]



## CONVERSATION FLOW
1. **Acknowledge country** and ask for travel dates + origin
2. **Get city preferences** - suggest cities, let them choose
3. **Get attraction preferences** - for each chosen city
4. **Get flight information** - ask about flights to and from destination country and get flight costs
5. **Create itineraries** - use tools to calculate routes, costs, carbon
6. **Present options** - show different itinerary choices
7. **Save final choice** - offer to save their selected itinerary. If the user says yes, use the save_itinerary tool to save the itinerary.

## AVAILABLE TOOLS AND THEIR PURPOSES

**CITY AND LOCATION TOOLS:**
- `get_recommended_cities(country_name)`: Fetches the top 5 most populated cities for a given country. Use this to get initial city recommendations when a user mentions a country.
- `get_points_of_interest(city)`: Finds popular points of interest for a given city using real API data. Returns actual attractions and landmarks.

**TRAVEL PLANNING TOOLS:**
- `calculate_travel_details(cities)`: Calculates total driving distance and estimated carbon emissions for a trip between cities. Cities must be in travel order. Returns distance in km and carbon emissions in kg.
- `create_multiple_itineraries(cities, origin_city, travel_date, destination_country, food_budget)`: Creates multiple itinerary variations with different city orders, calculates distances, carbon emissions, and total costs including flights. Returns list of itinerary options.

**FLIGHT AND ACCOMMODATION TOOLS:**
- `find_flight_options(origin_city, destination_country, travel_date)`: Finds real flight options from an origin city to a destination country for a specific date. Returns flight options with prices, airlines, and routes.
- `get_hotel_options(city)`: Finds hotel options for a given city. Returns available hotels with basic information.
- `get_hotel_price(hotel_id, check_in_date, check_out_date, adults)`: Gets specific pricing for a hotel for given dates and number of guests.

**CULTURAL AND EXPERIENCE TOOLS:**
- `get_cultural_insights(poi)`: Finds cultural insights for given points of interest. Helps provide context about attractions and local culture.

**SAVE AND STORAGE TOOLS:**
- `save_itinerary(user_id, itinerary_name, cities, total_distance_km, carbon_emissions_kg)`: Saves the final, complete itinerary to the database as structured JSON. Use this ONLY when the user has confirmed they are happy with the plan. The JSON includes travel details, sustainability metrics, and metadata.

## TOOL USAGE GUIDELINES
- Use `get_recommended_cities` early in the conversation to suggest cities
- Use `get_points_of_interest` for each city the user is interested in
- Use `calculate_travel_details` when you have a list of cities in travel order
- Use `find_flight_options` when user provides origin city, destination country, and travel date
- Use `create_multiple_itineraries` to generate different route options with costs
- Use `save_itinerary` only when user confirms they want to save their final choice
- Always provide real, up-to-date information from these tools

## KEY RULES
- NEVER ask for country (already selected from globe)
- When user says "3 days", understand this is trip duration, not ask for return date
- Use their budget and interests to tailor recommendations
- Keep responses natural and conversational
- Don't mention tools or technical details in responses"""
    
    # Add the system message to the prompt
    if hasattr(prompt, 'messages'):
        prompt.messages.insert(0, {"role": "system", "content": system_message})
    else:
        # For older prompt templates, add system message differently
        prompt.template = system_message + "\n\n" + prompt.template
    
    # Create the agent using ReAct pattern
    agent = create_react_agent(llm, tools, prompt)
    
    # Create the agent executor with better error handling
    def handle_parsing_error(error):
        """Handle parsing errors by providing a fallback response"""
        return "I need to help you plan your trip. What cities would you like to visit?"
    
    # Enhanced error handling function
    def enhanced_parsing_error_handler(error):
        """Enhanced parsing error handler with better fallback responses"""
        error_str = str(error)
        
        # If it's a ReAct parsing error, provide a helpful response
        if "Missing 'Action:'" in error_str or "Invalid Format" in error_str:
            return "I'm here to help you plan your trip! What would you like to know about your destination?"
        
        # For other parsing errors, provide a general helpful response
        return "I need to help you plan your trip. What cities would you like to visit?"
    
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        return_intermediate_steps=True,
        handle_parsing_errors=True,  # Use custom error handler
        max_iterations=4000,  # Further reduce iterations to prevent loops
        max_execution_time=60000,  # Reduce time limit to prevent hanging
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
        
        # Check for various parsing errors and provide helpful responses
        parsing_errors = [
            "Invalid Format: Missing 'Action:'",
            "Missing 'Action:' after 'Thought:'",
            "Invalid Format: Missing 'Action:' after 'Thought:'",
            "Expected 'Action:' after 'Thought:'"
        ]
        
        # Check if output contains Thought but no Action
        has_thought = "Thought:" in output_text
        has_action = "Action:" in output_text
        has_final_answer = "Final Answer:" in output_text
        
        # Detect incomplete ReAct pattern
        if (has_thought and not has_action and not has_final_answer) or any(error in output_text for error in parsing_errors):
            # Try to extract the thought content to provide a more contextual response
            thought_content = ""
            if "Thought:" in output_text:
                try:
                    thought_start = output_text.find("Thought:") + len("Thought:")
                    thought_end = output_text.find("\n", thought_start)
                    if thought_end == -1:
                        thought_end = len(output_text)
                    thought_content = output_text[thought_start:thought_end].strip()
                except:
                    thought_content = ""
            
            # Provide contextual fallback based on conversation state
            if "city" in thought_content.lower() or "cities" in thought_content.lower():
                fallback_response = "Great! Let me help you explore some amazing cities. What specific cities are you most interested in visiting?"
            elif "flight" in thought_content.lower() or "fly" in thought_content.lower():
                fallback_response = "I'd be happy to help you find flight options! What's your departure city and when are you planning to travel?"
            elif "attraction" in thought_content.lower() or "visit" in thought_content.lower():
                fallback_response = "I'd love to help you find interesting attractions! What places would you like to visit?"
            else:
                fallback_response = "I'm here to help you plan your trip! What would you like to know about your destination?"
            
            return {
                "output": fallback_response,
                "intermediate_steps": [],
                "success": False,
                "error": "ReAct parsing error - incomplete thought/action pattern"
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
