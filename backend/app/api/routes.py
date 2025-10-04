"""
API routes for the travel planner application.
Defines public and protected endpoints with Auth0 authentication.
"""

from flask import Blueprint, jsonify, g, request
from app.api.auth import require_auth_decorator, handle_auth_error, AuthError
from app.models.user import User
from app import db
from app.agent.agent_executor import create_travel_agent, parse_chat_history, invoke_agent_with_history

# Create API blueprint
api_bp = Blueprint('api', __name__)


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
        
        # Create the travel agent (stateless)
        agent_executor = create_travel_agent()
        
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
