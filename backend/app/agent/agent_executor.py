"""
LangChain agent executor for the travel planner using Google Gemini.
Handles conversational memory and tool integration with ReAct pattern.
"""

import os
from typing import List, Dict, Any
from langchain.agents import AgentExecutor, create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain import hub
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

from app.agent.tools import get_recommended_cities, get_points_of_interest, calculate_travel_details, save_itinerary, find_flight_options


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
    tools = [get_recommended_cities, get_points_of_interest, calculate_travel_details, save_itinerary, find_flight_options]
    
    # Pull the standard ReAct prompt from LangChain Hub
    prompt = hub.pull("hwchase17/react-chat")
    
    # Add custom system message to make agent aware of new capabilities
    system_message = """You are a comprehensive travel planning assistant with the following capabilities:

1. **get_recommended_cities**: Get top cities for any country
2. **get_points_of_interest**: Find real attractions and landmarks for any city using live OpenTripMap data
3. **calculate_travel_details**: Calculate total driving distance and carbon emissions between cities using OpenRouteService
4. **find_flight_options**: Find flight options from origin city to destination country with carbon impact estimates
5. **save_itinerary**: Save completed travel plans to the database (use this as the final step when user confirms they're happy with the plan)

Your complete workflow should be:
1. **First Phase - Land-based Itinerary**: Help users discover cities in their desired country and create a land-based travel plan
2. **Second Phase - Flight Planning**: After the land itinerary is complete, ask the user for their departure city and travel date
3. **Third Phase - Flight Search**: Use find_flight_options to find ways to get to their destination country
4. **Final Phase**: Present the complete travel plan including both land itinerary and flight options, then ask if they want to save it

IMPORTANT: Always follow this sequence:
- Start by helping with the land-based itinerary (cities, attractions, driving routes)
- Only after that's complete, ask for departure city and travel date
- Then search for flights to get there
- Finally present the complete plan and offer to save it

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
        max_iterations=5,
        early_stopping_method="generate"
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
        
        # Invoke the agent
        result = agent_executor.invoke(input_data)
        
        return {
            "output": result.get("output", ""),
            "intermediate_steps": result.get("intermediate_steps", []),
            "success": True
        }
        
    except Exception as e:
        return {
            "output": f"I apologize, but I encountered an error: {str(e)}",
            "intermediate_steps": [],
            "success": False,
            "error": str(e)
        }
