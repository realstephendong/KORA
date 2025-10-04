"""
Auth0 authentication integration for the Flask application.
Provides JWT token validation and authentication decorators.
"""

import os
import json
from functools import wraps
from flask import request, jsonify, g
from authlib.integrations.flask_oauth2 import ResourceProtector
from authlib.jose import jwt
from authlib.jose.errors import JoseError
import requests


class AuthError(Exception):
    """
    Custom exception for authentication errors.
    
    Attributes:
        error (str): Error code
        error_description (str): Human-readable error description
        status_code (int): HTTP status code
    """
    
    def __init__(self, error, error_description, status_code):
        self.error = error
        self.error_description = error_description
        self.status_code = status_code


# Initialize Auth0 resource protector
require_auth = ResourceProtector()


def get_token_auth_header():
    """
    Extract the bearer token from the Authorization header.
    
    Returns:
        str: The JWT token
        
    Raises:
        AuthError: If the authorization header is missing or malformed
    """
    auth = request.headers.get('Authorization', None)
    
    if not auth:
        raise AuthError('authorization_header_missing', 'Authorization header is expected.', 401)
    
    parts = auth.split()
    
    if parts[0].lower() != 'bearer':
        raise AuthError('invalid_header', 'Authorization header must start with "Bearer".', 401)
    
    elif len(parts) == 1:
        raise AuthError('invalid_header', 'Token not found.', 401)
    
    elif len(parts) > 2:
        raise AuthError('invalid_header', 'Authorization header must be bearer token.', 401)
    
    token = parts[1]
    return token


def verify_decode_jwt(token):
    """
    Verify and decode the JWT token using Auth0's public keys.
    
    Args:
        token (str): JWT token to verify
        
    Returns:
        dict: Decoded JWT payload
        
    Raises:
        AuthError: If token verification fails
    """
    # Get Auth0 domain and audience from config
    auth0_domain = os.environ.get('AUTH0_DOMAIN')
    auth0_audience = os.environ.get('AUTH0_API_AUDIENCE')
    
    if not auth0_domain or not auth0_audience:
        raise AuthError('configuration_error', 'Auth0 configuration is missing.', 500)
    
    # Get the public key from Auth0
    jsonurl = requests.get(f'https://{auth0_domain}/.well-known/jwks.json')
    jwks = jsonurl.json()
    
    try:
        unverified_header = jwt.get_unverified_header(token)
    except JoseError:
        raise AuthError('invalid_header', 'Unable to parse authentication token.', 401)
    
    rsa_key = {}
    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=['RS256'],
                audience=auth0_audience,
                issuer=f'https://{auth0_domain}/'
            )
            return payload
            
        except jwt.ExpiredSignatureError:
            raise AuthError('token_expired', 'Token expired.', 401)
            
        except jwt.JWTClaimsError:
            raise AuthError('invalid_claims', 'Incorrect claims. Please check the audience and issuer.', 401)
            
        except Exception:
            raise AuthError('invalid_header', 'Unable to parse authentication token.', 401)
    
    raise AuthError('invalid_header', 'Unable to find appropriate key.', 401)


def require_auth_decorator(f):
    """
    Decorator to require authentication for protected endpoints.
    
    Args:
        f: Function to decorate
        
    Returns:
        function: Decorated function with authentication check
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            # Get and verify the JWT token
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            
            # Store the payload in Flask's g object for use in the route
            g.current_user = payload
            
        except AuthError as e:
            return jsonify({
                'error': e.error,
                'error_description': e.error_description
            }), e.status_code
        
        return f(*args, **kwargs)
    
    return decorated


def handle_auth_error(error):
    """
    Handle authentication errors and return appropriate JSON responses.
    
    Args:
        error (AuthError): Authentication error
        
    Returns:
        tuple: JSON response and status code
    """
    return jsonify({
        'error': error.error,
        'error_description': error.error_description
    }), error.status_code
