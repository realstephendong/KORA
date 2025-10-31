"""
API routes for the travel planner application.
Defines public and protected endpoints with Auth0 authentication.
"""

from flask import Blueprint, jsonify, g, request
from app.api.auth import require_auth_decorator, handle_auth_error, AuthError
from app.models.user import User
from app.models.itinerary import Itinerary
from app import db
from app.agent.agent_executor import create_travel_agent, parse_chat_history, invoke_agent_with_history
from app.agent.tools import get_recommended_cities, get_points_of_interest, calculate_travel_details, save_itinerary, find_flight_options, create_multiple_itineraries
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
    from langchain.tools import tool
    
    @tool
    def save_itinerary_with_user(itinerary_name: str, cities: list = None, total_distance_km: float = 0.0, carbon_emissions_kg: float = 0.0) -> str:
        """Save completed travel plans to the database for the current user."""
        try:
            # Handle case where agent passes all parameters as a single string
            if isinstance(itinerary_name, str):
                # Check if it's a JSON string containing all parameters
                if itinerary_name.startswith('{') and itinerary_name.endswith('}'):
                    import json
                    try:
                        parsed = json.loads(itinerary_name)
                        itinerary_name = parsed.get('itinerary_name', itinerary_name)
                        cities = parsed.get('cities', cities)
                        total_distance_km = parsed.get('total_distance_km', total_distance_km)
                        carbon_emissions_kg = parsed.get('carbon_emissions_kg', carbon_emissions_kg)
                    except json.JSONDecodeError:
                        pass
                
                # Handle case where agent passes parameters in format "itinerary_name=Name, cities=[...]"
                elif 'itinerary_name=' in itinerary_name and ',' in itinerary_name:
                    import re
                    import ast
                    
                    # Extract itinerary name (everything after "itinerary_name=" and before the first comma)
                    name_match = re.search(r'itinerary_name=([^,]+)', itinerary_name)
                    if name_match:
                        itinerary_name = name_match.group(1).strip()
                    
                    # Extract cities list
                    cities_match = re.search(r"cities=\[([^\]]+)\]", itinerary_name)
                    if cities_match:
                        cities_str = cities_match.group(1)
                        cities = [city.strip().strip("'\"") for city in cities_str.split(',')]
                    
                    # Extract total_distance_km
                    distance_match = re.search(r'total_distance_km=([0-9.]+)', itinerary_name)
                    if distance_match:
                        total_distance_km = float(distance_match.group(1))
                    
                    # Extract carbon_emissions_kg
                    carbon_match = re.search(r'carbon_emissions_kg=([0-9.]+)', itinerary_name)
                    if carbon_match:
                        carbon_emissions_kg = float(carbon_match.group(1))
            
            # Ensure cities is a list
            if cities is None:
                cities = []
            
            # Clean up itinerary name (remove any remaining parameter prefixes)
            if isinstance(itinerary_name, str):
                itinerary_name = itinerary_name.replace('itinerary_name=', '').strip()
            
            print(f"DEBUG: Saving itinerary - Name: '{itinerary_name}', Cities: {cities}, Distance: {total_distance_km}, Carbon: {carbon_emissions_kg}")
            
            return save_itinerary.invoke({
                'user_id': user_id,
                'itinerary_name': itinerary_name,
                'cities': cities,
                'total_distance_km': total_distance_km,
                'carbon_emissions_kg': carbon_emissions_kg
            })
        except Exception as e:
            print(f"DEBUG: Error in save_itinerary_with_user: {str(e)}")
            return f"Error saving itinerary: {str(e)}"
    
    # Define available tools with user-specific save_itinerary
    tools = [get_recommended_cities, get_points_of_interest, calculate_travel_details, save_itinerary_with_user, find_flight_options, create_multiple_itineraries]
    
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

## USER PROFILE INTEGRATION:
- If the user has provided their travel budget, use it to ensure all recommendations stay within budget
- If the user has selected interests (Fashion, Food & treats, Nature & Wildlife, Learning about Culture), tailor recommendations to these preferences
- DO NOT ask about vacation type or travel style if the user has already provided interests
- Use the user's interests to suggest relevant attractions and experiences

## INITIAL WORKFLOW (Country is already selected by user):

**FIRST RESPONSE - Acknowledge Country & Get Basic Info:**
When a user says "I want to visit [COUNTRY]", you should:
1. Acknowledge their choice enthusiastically: "Great choice! [COUNTRY] is an amazing destination!"
2. Ask for their travel dates: "When are you planning to travel? Please provide your departure and return dates."
3. Ask for their origin: "Where will you be traveling from? (city and country)"
4. Ask for duration: "How many days are you planning to stay? (e.g., 3 days, 1 week, etc.)"
5. If user has interests, mention: "I'll make sure to include experiences that match your interests!"

**Layer 1 - City Discovery:**
- Suggest top cities in that country
- If user has interests, prioritize cities that offer relevant experiences
- Let the user choose cities they're interested in (even if just one city)

**Layer 2 - Attraction Discovery:**
- For each selected city, ask: "What places do you want to visit in [CITY]?"
- Suggest real attractions and landmarks that match user interests
- Let the user select their preferred attractions for each city

**Layer 3 - Flight Planning:**
- ALWAYS ask about flights to the destination country
- Get their departure city and travel date
- Use find_flight_options tool to get real flight costs and options
- Present flight options with carbon impact and pricing
- Ensure flight costs fit within the user's budget

**Layer 4 - Itinerary Creation:**
- Use the user's budget to ensure all recommendations stay within their budget
- Generate itinerary options based on their city selections and interests
- For single cities: Create a detailed single-city itinerary with multiple day options
- For multiple cities: Create different city orders/routes with distance and carbon calculations
- Present itinerary options with:
  - Different routes (if multiple cities) or day-by-day plans (if single city)
  - Total distance and carbon emissions (if applicable)
  - Estimated travel time and total costs (ensuring they stay within budget)
  - Cost breakdown (flights, accommodation, food, fuel)
  - Key attractions included (tailored to user interests)

**Final Phase:**
- Present all itinerary options with filters for price and carbon emissions
- Show cost breakdowns and total costs for each option (all within budget)
- Let user select their preferred itinerary
- Offer to save the final selected itinerary

IMPORTANT: Always follow this sequence:
- Start by acknowledging their country choice and asking for dates/origin
- Then get city recommendations (tailored to interests if available)
- Then get attraction preferences for each city (matching interests)
- Then ask about flights to destination country and get flight costs
- Then create itinerary options with calculations (within budget)
- Present options with filters
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
    
    # Create the agent executor
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
    Uses stored user data from SQLite database.
    
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
        
        # Try to get user information from JWT token (if available)
        # Check for custom claims first, then fall back to standard claims
        jwt_email = g.current_user.get('https://kora-travel.com/email') or g.current_user.get('email')
        jwt_name = g.current_user.get('https://kora-travel.com/name') or g.current_user.get('name')
        
        print(f"DEBUG: JWT claims available: {list(g.current_user.keys())}")
        print(f"DEBUG: Full JWT payload: {g.current_user}")
        print(f"DEBUG: Extracted email: {jwt_email}")
        print(f"DEBUG: Extracted name: {jwt_name}")
        
        # Find or create user, updating with any available info from JWT
        user = User.create_or_get_user(
            auth0_sub=auth0_sub,
            name=jwt_name,
            email=jwt_email
        )
        
        # Use stored user data for auth0_info
        auth0_info = {
            'sub': auth0_sub,
            'email': user.email or 'Not available',
            'name': user.name or 'Not available'
        }
        
        return jsonify({
            'user': user.to_dict(),
            'auth0_info': auth0_info,
            'status': 'success'
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'server_error',
            'error_description': str(e)
        }), 500


@api_bp.route('/profile', methods=['PUT'])
@require_auth_decorator
def update_user_profile():
    """
    Update user profile with budget, interests, and profile picture.
    
    Expected JSON payload:
    {
        "budget": "1000-5000",
        "interests": ["Fashion", "Food & treats"],
        "profile_picture": "turtle blue.svg"
    }
    
    Returns:
        dict: JSON response with updated user profile
    """
    try:
        # Get Auth0 subject from the JWT payload
        auth0_sub = g.current_user.get('sub')
        
        if not auth0_sub:
            return jsonify({
                'error': 'invalid_token',
                'error_description': 'Token does not contain subject identifier'
            }), 401
        
        # Validate request data
        if not request.is_json:
            return jsonify({
                'error': 'invalid_request',
                'error_description': 'Request must be JSON'
            }), 400
        
        data = request.get_json()
        
        # Find user
        user = User.find_by_auth0_sub(auth0_sub)
        if not user:
            return jsonify({
                'error': 'user_not_found',
                'error_description': 'User not found'
            }), 404
        
        # Update profile fields
        import json
        updated = False
        
        if 'budget' in data:
            user.budget = data['budget']
            updated = True
        
        if 'interests' in data:
            if isinstance(data['interests'], list):
                user.interests = json.dumps(data['interests'])
                updated = True
        
        if 'profile_picture' in data:
            user.profile_picture = data['profile_picture']
            updated = True
        
        if updated:
            db.session.commit()
            print(f"DEBUG: Updated profile for user {auth0_sub}")
        
        return jsonify({
            'user': user.to_dict(),
            'status': 'success',
            'message': 'Profile updated successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
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
        
        # Get country context (optional)
        country_context = data.get('country_context', None)
        
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
        
        # Add user profile context to the message
        profile_context = ""
        if user.budget:
            profile_context += f" The user's travel budget is ${user.budget}. "
        
        if user.interests:
            import json
            try:
                interests_list = json.loads(user.interests)
                if interests_list:
                    interests_str = ", ".join(interests_list)
                    profile_context += f" The user is interested in: {interests_str}. "
            except (json.JSONDecodeError, TypeError):
                pass
        
        # Add country context to the message if provided
        if country_context:
            country_name = country_context.get('name', 'Unknown')
            user_message = f"I want to visit {country_name}. {user_message}"
        
        # Add profile context to the message
        if profile_context:
            user_message = f"{profile_context}{user_message}"
        
        # Invoke the agent with the user message and history
        result = invoke_agent_with_history(agent_executor, user_message, chat_history)
        
        # Convert intermediate steps to JSON-serializable format
        intermediate_steps = result.get('intermediate_steps', [])
        serializable_steps = []
        for step in intermediate_steps:
            if hasattr(step, '__dict__'):
                # Convert AgentAction objects to dictionaries
                step_dict = {
                    'tool': getattr(step, 'tool', ''),
                    'tool_input': getattr(step, 'tool_input', ''),
                    'log': getattr(step, 'log', '')
                }
                serializable_steps.append(step_dict)
            else:
                # Handle string or other serializable types
                serializable_steps.append(str(step))
        
        # Return structured response
        response_data = {
            'response': result.get('output', ''),
            'intermediate_steps': serializable_steps,
            'success': result.get('success', True),
            'timestamp': g.current_user.get('sub', 'unknown')  # Include user context
        }
        
        # Add error information if present
        if 'error' in result:
            response_data['error'] = result['error']
        
        return jsonify(response_data), 200
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error in chat endpoint: {str(e)}")
        print(f"Traceback: {error_trace}")
        return jsonify({
            'error': 'server_error',
            'error_description': f'Internal server error: {str(e)}',
            'traceback': error_trace
        }), 500


@api_bp.route('/itineraries', methods=['GET'])
@require_auth_decorator
def get_user_itineraries():
    """
    Get all itineraries for the authenticated user from JSON files.
    
    Returns:
        dict: JSON response with user's itineraries
    """
    try:
        import json
        import os
        from datetime import datetime
        
        # Get Auth0 subject from the JWT payload
        auth0_sub = g.current_user.get('sub')
        
        if not auth0_sub:
            return jsonify({
                'error': 'invalid_token',
                'error_description': 'Token does not contain subject identifier'
            }), 401
        
        # Find user
        user = User.find_by_auth0_sub(auth0_sub)
        if not user:
            return jsonify({
                'error': 'user_not_found',
                'error_description': 'User not found'
            }), 404
        
        # Read itineraries from JSON files
        itineraries = []
        
        # Check for main itinerary.json file
        main_itinerary_path = os.path.join(os.path.dirname(__file__), '..', '..', 'itinerary.json')
        agent_itinerary_path = os.path.join(os.path.dirname(__file__), '..', 'agent', 'itinerary.json')
        
        print(f"DEBUG: Looking for JSON files at:")
        print(f"  - Main path: {main_itinerary_path}")
        print(f"  - Agent path: {agent_itinerary_path}")
        print(f"  - Main exists: {os.path.exists(main_itinerary_path)}")
        print(f"  - Agent exists: {os.path.exists(agent_itinerary_path)}")
        
        # Try to read from both possible locations
        for path in [main_itinerary_path, agent_itinerary_path]:
            if os.path.exists(path):
                try:
                    with open(path, 'r') as f:
                        content = f.read().strip()
                        if content:
                            # Parse the JSON content
                            itinerary_data = json.loads(content)
                            
                            print(f"DEBUG: Successfully loaded JSON from {path}")
                            print(f"DEBUG: Data type: {type(itinerary_data)}")
                            print(f"DEBUG: Data content: {json.dumps(itinerary_data, indent=2)}")
                            
                            # Handle both single itinerary and list of itineraries
                            if isinstance(itinerary_data, list):
                                print(f"DEBUG: Processing {len(itinerary_data)} itineraries")
                                # Multiple itineraries
                                for idx, itinerary in enumerate(itinerary_data):
                                    transformed_itinerary = {
                                        'id': idx + 1,
                                        'user_id': user.id,
                                        'name': itinerary.get('itinerary_info', {}).get('name', f'Itinerary {idx + 1}'),
                                        'cities': itinerary.get('travel_details', {}).get('cities', []),
                                        'total_distance_km': itinerary.get('travel_details', {}).get('total_distance_km', 0),
                                        'carbon_emissions_kg': itinerary.get('travel_details', {}).get('carbon_emissions_kg', 0),
                                        'country': None,
                                        'travel_dates': None,
                                        'duration_days': None,
                                        'attractions': None,
                                        'flight_info': None,
                                        'estimated_costs': None,
                                        'created_at': itinerary.get('itinerary_info', {}).get('created_at', datetime.now().isoformat()),
                                        'updated_at': datetime.now().isoformat()
                                    }
                                    itineraries.append(transformed_itinerary)
                                    print(f"DEBUG: Added itinerary {idx + 1}: {transformed_itinerary['name']}")
                            else:
                                print(f"DEBUG: Processing single itinerary")
                                # Single itinerary
                                transformed_itinerary = {
                                    'id': 1,
                                    'user_id': user.id,
                                    'name': itinerary_data.get('itinerary_info', {}).get('name', 'Untitled Itinerary'),
                                    'cities': itinerary_data.get('travel_details', {}).get('cities', []),
                                    'total_distance_km': itinerary_data.get('travel_details', {}).get('total_distance_km', 0),
                                    'carbon_emissions_kg': itinerary_data.get('travel_details', {}).get('carbon_emissions_kg', 0),
                                    'country': None,
                                    'travel_dates': None,
                                    'duration_days': None,
                                    'attractions': None,
                                    'flight_info': None,
                                    'estimated_costs': None,
                                    'created_at': itinerary_data.get('itinerary_info', {}).get('created_at', datetime.now().isoformat()),
                                    'updated_at': datetime.now().isoformat()
                                }
                                itineraries.append(transformed_itinerary)
                                print(f"DEBUG: Added single itinerary: {transformed_itinerary['name']}")
                            
                            break  # Only read from the first found file
                            
                except (json.JSONDecodeError, KeyError) as e:
                    print(f"Error parsing JSON from {path}: {e}")
                    continue
        
        print(f"DEBUG: Final itineraries count: {len(itineraries)}")
        print(f"DEBUG: Final itineraries: {json.dumps([{'id': i['id'], 'name': i['name'], 'cities': i['cities']} for i in itineraries], indent=2)}")
        
        # If no JSON files found, return empty list
        if not itineraries:
            return jsonify({
                'itineraries': [],
                'status': 'success',
                'message': 'No itineraries found in JSON files'
            }), 200
        
        return jsonify({
            'itineraries': itineraries,
            'status': 'success'
        }), 200
        
    except Exception as e:
        print(f"Error in get_user_itineraries: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': 'server_error',
            'error_description': str(e)
        }), 500


@api_bp.route('/itineraries/<int:itinerary_id>', methods=['GET'])
@require_auth_decorator
def get_itinerary_details(itinerary_id):
    """
    Get detailed information about a specific itinerary.
    
    Args:
        itinerary_id (int): ID of the itinerary to retrieve
        
    Returns:
        dict: JSON response with detailed itinerary information
    """
    try:
        # Get Auth0 subject from the JWT payload
        auth0_sub = g.current_user.get('sub')
        
        if not auth0_sub:
            return jsonify({
                'error': 'invalid_token',
                'error_description': 'Token does not contain subject identifier'
            }), 401
        
        # Find user
        user = User.find_by_auth0_sub(auth0_sub)
        if not user:
            return jsonify({
                'error': 'user_not_found',
                'error_description': 'User not found'
            }), 404
        
        # Find the specific itinerary
        itinerary = Itinerary.query.filter_by(id=itinerary_id, user_id=user.id).first()
        if not itinerary:
            return jsonify({
                'error': 'itinerary_not_found',
                'error_description': 'Itinerary not found or access denied'
            }), 404
        
        # Return detailed itinerary information
        return jsonify({
            'itinerary': itinerary.to_dict(),
            'status': 'success'
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'server_error',
            'error_description': str(e)
        }), 500


@api_bp.route('/itineraries/<int:itinerary_id>/export', methods=['GET'])
@require_auth_decorator
def export_itinerary(itinerary_id):
    """
    Export a specific itinerary as structured JSON for frontend consumption.
    Includes carbon emissions data for visualization.
    
    Args:
        itinerary_id (int): ID of the itinerary to export
        
    Returns:
        dict: JSON response with structured itinerary data
    """
    try:
        # Get Auth0 subject from the JWT payload
        auth0_sub = g.current_user.get('sub')
        
        if not auth0_sub:
            return jsonify({
                'error': 'invalid_token',
                'error_description': 'Token does not contain subject identifier'
            }), 401
        
        # Find user
        user = User.find_by_auth0_sub(auth0_sub)
        if not user:
            return jsonify({
                'error': 'user_not_found',
                'error_description': 'User not found'
            }), 404
        
        # Find the specific itinerary
        itinerary = Itinerary.query.filter_by(id=itinerary_id, user_id=user.id).first()
        if not itinerary:
            return jsonify({
                'error': 'itinerary_not_found',
                'error_description': 'Itinerary not found or access denied'
            }), 404
        
        # Create structured export data
        export_data = {
            'id': itinerary.id,
            'name': itinerary.name,
            'cities': itinerary.to_dict()['cities'],
            'carbon_emissions': {
                'total_kg': itinerary.carbon_emissions_kg or 0,
                'breakdown': {
                    'driving': itinerary.carbon_emissions_kg or 0,
                    'flights': 0  # Could be extended to include flight emissions
                }
            },
            'distance': {
                'total_km': itinerary.total_distance_km or 0,
                'breakdown': {
                    'driving': itinerary.total_distance_km or 0,
                    'flights': 0  # Could be extended to include flight distances
                }
            },
            'metadata': {
                'created_at': itinerary.created_at.isoformat() if itinerary.created_at else None,
                'updated_at': itinerary.updated_at.isoformat() if itinerary.updated_at else None,
                'user_id': itinerary.user_id
            },
            'visualization': {
                'carbon_emissions_kg': itinerary.carbon_emissions_kg or 0,
                'distance_km': itinerary.total_distance_km or 0,
                'city_count': len(itinerary.to_dict()['cities']),
                'emissions_per_city': (itinerary.carbon_emissions_kg or 0) / max(len(itinerary.to_dict()['cities']), 1),
                'distance_per_city': (itinerary.total_distance_km or 0) / max(len(itinerary.to_dict()['cities']), 1)
            }
        }
        
        return jsonify({
            'itinerary': export_data,
            'status': 'success'
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'server_error',
            'error_description': str(e)
        }), 500


@api_bp.route('/debug/auth', methods=['GET'])
@require_auth_decorator
def debug_auth():
    """
    Debug endpoint to check authentication status.
    
    Returns:
        dict: JSON response with authentication debug info
    """
    return jsonify({
        'status': 'authenticated',
        'user': g.current_user,
        'message': 'Authentication is working'
    }), 200


@api_bp.route('/latest-itinerary', methods=['GET'])
@require_auth_decorator
def get_latest_itinerary():
    """
    Get the most recently created itinerary for the current user.
    
    Returns:
        dict: JSON response with the latest itinerary data
    """
    try:
        # Get Auth0 subject from the JWT payload
        auth0_sub = g.current_user.get('sub')
        
        if not auth0_sub:
            return jsonify({
                'error': 'invalid_token',
                'error_description': 'Token does not contain subject identifier'
            }), 401
        
        # Find user
        user = User.find_by_auth0_sub(auth0_sub)
        if not user:
            return jsonify({
                'error': 'user_not_found',
                'error_description': 'User not found'
            }), 404
        
        # Get the most recent itinerary for this user
        latest_itinerary = Itinerary.query.filter_by(user_id=user.id)\
            .order_by(Itinerary.created_at.desc())\
            .first()
        
        if not latest_itinerary:
            return jsonify({
                'error': 'no_itineraries',
                'error_description': 'No itineraries found for this user'
            }), 404
        
        return jsonify({
            'itinerary': latest_itinerary.to_dict(),
            'status': 'success'
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'server_error',
            'error_description': str(e)
        }), 500


@api_bp.route('/itineraries/<int:itinerary_id>/json', methods=['GET'])
@require_auth_decorator
def get_itinerary_json(itinerary_id):
    """
    Get the complete JSON data for a specific itinerary.
    
    Args:
        itinerary_id (int): ID of the itinerary to retrieve
        
    Returns:
        dict: JSON response with complete itinerary JSON data
    """
    try:
        # Get Auth0 subject from the JWT payload
        auth0_sub = g.current_user.get('sub')
        
        if not auth0_sub:
            return jsonify({
                'error': 'invalid_token',
                'error_description': 'Token does not contain subject identifier'
            }), 401
        
        # Find user
        user = User.find_by_auth0_sub(auth0_sub)
        if not user:
            return jsonify({
                'error': 'user_not_found',
                'error_description': 'User not found'
            }), 404
        
        # Find the specific itinerary
        itinerary = Itinerary.query.filter_by(id=itinerary_id, user_id=user.id).first()
        if not itinerary:
            return jsonify({
                'error': 'itinerary_not_found',
                'error_description': 'Itinerary not found or access denied'
            }), 404
        
        # Parse the JSON data from attractions field
        import json
        json_data = None
        if itinerary.attractions:
            try:
                json_data = json.loads(itinerary.attractions)
            except json.JSONDecodeError:
                json_data = None
        
        return jsonify({
            'itinerary_id': itinerary.id,
            'itinerary_name': itinerary.name,
            'json_data': json_data,
            'raw_data': {
                'cities': itinerary.to_dict()['cities'],
                'total_distance_km': itinerary.total_distance_km,
                'carbon_emissions_kg': itinerary.carbon_emissions_kg,
                'created_at': itinerary.created_at.isoformat() if itinerary.created_at else None
            },
            'status': 'success'
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'server_error',
            'error_description': str(e)
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
