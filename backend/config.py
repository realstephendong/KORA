"""
Configuration settings for the Flask application.
Loads environment variables and provides configuration classes.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration class with common settings."""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database settings
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///travel_planner.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Auth0 settings
    AUTH0_DOMAIN = os.environ.get('AUTH0_DOMAIN') or 'your-auth0-domain.auth0.com'
    AUTH0_API_AUDIENCE = os.environ.get('AUTH0_API_AUDIENCE') or 'your-api-identifier'
    
    # Google Gemini settings
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
    
    # RapidAPI settings for GeoDB
    RAPIDAPI_KEY = os.environ.get('RAPIDAPI_KEY')
    RAPIDAPI_HOST = os.environ.get('RAPIDAPI_HOST', 'geodb-cities-graphql.p.rapidapi.com')
    
    # Google Maps settings
    GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY')
    
    # CORS settings
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    FLASK_ENV = 'development'


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    FLASK_ENV = 'production'


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
