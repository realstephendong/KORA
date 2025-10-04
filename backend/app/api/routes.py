"""
API routes for the travel planner application.
Defines public and protected endpoints with Auth0 authentication.
"""

from flask import Blueprint, jsonify, g, request
from app.api.auth import require_auth_decorator, handle_auth_error, AuthError
from app.models.user import User
from app import db
from app.agent.agent_executor import create_travel_agent, parse_chat_history, invoke_agent_with_history
from app.agent.tools import get_recommended_cities, get_points_of_interest, calculate_travel_details, save_itinerary
from functools import partial

# Create API blueprint
api_bp = Blueprint('api', __name__)


def create_travel_agent_with_user(user_id: int):
    """
    Creates a travel planning agent with user-specific tools.
    The save_itinerary tool is pre-configured with the user_id.
    
    Args:
        user_id (int): ID of the current user
        
    Returns:
        AgentExecutor: Configured agent executor with user-specific tools
    """
    from app.agent.agent_executor import create_travel_agent
    from langchain.agents import AgentExecutor, create_react_agent
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain import hub
    import os
    
    # Initialize Google Gemini model (free tier)
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,
        convert_system_message_to_human=True,
        google_api_key=os.environ.get('GOOGLE_API_KEY')
    )
    
    # Create a user-specific version of save_itinerary with user_id pre-filled
    save_itinerary_with_user = partial(save_itinerary, user_id)
    save_itinerary_with_user.__name__ = 'save_itinerary'
    save_itinerary_with_user.__doc__ = save_itinerary.__doc__
    
    # Define available tools with user-specific save_itinerary
    tools = [get_recommended_cities, get_points_of_interest, calculate_travel_details, save_itinerary_with_user]
    
    # Pull the standard ReAct prompt from LangChain Hub
    prompt = hub.pull("hwchase17/react-chat")
    
    # Add custom system message to make agent aware of new capabilities
    system_message = """You are a travel planning assistant with the following capabilities:

1. **get_recommended_cities**: Get top cities for any country
2. **get_points_of_interest**: Find real attractions and landmarks for any city using live OpenTripMap data
3. **calculate_travel_details**: Calculate total driving distance and carbon emissions between cities using OpenRouteService
4. **save_itinerary**: Save completed travel plans to the database (use this as the final step when user confirms they're happy with the plan)

Your workflow should be:
1. Help users discover cities in their desired country
2. Find real attractions for each city using live data
3. Calculate travel logistics (distance, carbon footprint) for the complete route
4. Present the full itinerary with all details
5. Ask if they want to save the itinerary, and use save_itinerary if they confirm

Always aim to provide real, up-to-date information and complete travel plans that users can actually execute."""
    
    # Add the system message to the prompt
    if hasattr(prompt, 'messages'):
        prompt.messages.insert(0, {"role": "system", "content": system_message})
    else:
        # For older prompt templates, add system message differently
        prompt.template = system_message + "\n\n" + prompt.template
    
    # Create the agent using ReAct pattern
    agent = create_react_agent(llm, tools, prompt)
    
    # Create the agent executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        return_intermediate_steps=True,
        handle_parsing_errors=True,
        max_iterations=3
    )
    
    return agent_executor


@api_bp.route('/public', methods=['GET'])
def public_endpoint():
    """
    Public endpoint that doesn't require authentication.
    
    Returns:
        dict: JSON response with public message
    """
    return jsonify({
        'message': 'This is a public endpoint.',
        'status': 'success'
    }), 200


@api_bp.route('/private', methods=['GET'])
@require_auth_decorator
def private_endpoint():
    """
    Protected endpoint that requires authentication.
    
    Returns:
        dict: JSON response with private message and user info
    """
    return jsonify({
        'message': 'Hello from a private endpoint! You need to be authenticated to see this.',
        'user': g.current_user.get('sub', 'Unknown'),
        'status': 'success'
    }), 200


@api_bp.route('/profile', methods=['GET'])
@require_auth_decorator
def get_user_profile():
    """
    Get or create user profile based on Auth0 subject.
    
    Returns:
        dict: JSON response with user profile information
    """
    try:
        # Get Auth0 subject from the JWT payload
        auth0_sub = g.current_user.get('sub')
        
        if not auth0_sub:
            return jsonify({
                'error': 'invalid_token',
                'error_description': 'Token does not contain subject identifier'
            }), 401
        
        # Find or create user
        user = User.find_by_auth0_sub(auth0_sub)
        if not user:
            user = User.create_or_get_user(auth0_sub)
        
        return jsonify({
            'user': user.to_dict(),
            'auth0_info': {
                'sub': g.current_user.get('sub'),
                'email': g.current_user.get('email'),
                'name': g.current_user.get('name')
            },
            'status': 'success'
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'server_error',
            'error_description': str(e)
        }), 500


@api_bp.route('/chat/message', methods=['POST'])
@require_auth_decorator
def chat_message():
    """
    Handle conversational chat with the travel planning agent.
    Accepts a message and chat history, returns agent response.
    
    Expected JSON payload:
    {
        "message": "I want to visit France",
        "chat_history": [
            {"role": "human", "content": "Hi"},
            {"role": "ai", "content": "Hello! How can I help?"}
        ]
    }
    
    Returns:
        dict: JSON response with agent output and intermediate steps
    """
    try:
        # Validate request data
        if not request.is_json:
            return jsonify({
                'error': 'invalid_request',
                'error_description': 'Request must be JSON'
            }), 400
        
        data = request.get_json()
        
        # Validate required fields
        if 'message' not in data:
            return jsonify({
                'error': 'missing_field',
                'error_description': 'Message field is required'
            }), 400
        
        user_message = data.get('message', '').strip()
        if not user_message:
            return jsonify({
                'error': 'invalid_message',
                'error_description': 'Message cannot be empty'
            }), 400
        
        # Get chat history (optional, defaults to empty list)
        chat_history_data = data.get('chat_history', [])
        
        # Validate chat history format
        if not isinstance(chat_history_data, list):
            return jsonify({
                'error': 'invalid_chat_history',
                'error_description': 'Chat history must be a list'
            }), 400
        
        # Parse chat history to LangChain format
        chat_history = parse_chat_history(chat_history_data)
        
        # Get or create user to get user_id
        auth0_sub = g.current_user.get('sub')
        if not auth0_sub:
            return jsonify({
                'error': 'invalid_token',
                'error_description': 'Token does not contain subject identifier'
            }), 401
        
        user = User.find_by_auth0_sub(auth0_sub)
        if not user:
            user = User.create_or_get_user(auth0_sub)
        
        # Create the travel agent with user-specific tools
        agent_executor = create_travel_agent_with_user(user.id)
        
        # Invoke the agent with the user message and history
        result = invoke_agent_with_history(agent_executor, user_message, chat_history)
        
        # Return structured response
        response_data = {
            'response': result['output'],
            'intermediate_steps': result.get('intermediate_steps', []),
            'success': result.get('success', True),
            'timestamp': g.current_user.get('sub', 'unknown')  # Include user context
        }
        
        # Add error information if present
        if 'error' in result:
            response_data['error'] = result['error']
        
        return jsonify(response_data), 200
        
    except Exception as e:
        return jsonify({
            'error': 'server_error',
            'error_description': f'Internal server error: {str(e)}'
        }), 500


@api_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for monitoring.
    
    Returns:
        dict: JSON response with application status
    """
    return jsonify({
        'status': 'healthy',
        'message': 'Travel Planner API is running',
        'version': '1.0.0'
    }), 200


# Register error handlers for the blueprint
@api_bp.errorhandler(AuthError)
def handle_auth_error_blueprint(error):
    """Handle AuthError exceptions within the API blueprint."""
    return handle_auth_error(error)


@api_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'error': 'not_found',
        'error_description': 'The requested resource was not found'
    }), 404


@api_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({
        'error': 'internal_server_error',
        'error_description': 'An internal server error occurred'
    }), 500
