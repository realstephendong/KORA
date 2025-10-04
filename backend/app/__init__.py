"""
Flask application factory.
Creates and configures the Flask application instance with all necessary extensions.
"""

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from config import config

# Initialize extensions
db = SQLAlchemy()


def create_app(config_name=None):
    """
    Application factory function.
    
    Args:
        config_name (str): Configuration name to use. Defaults to 'default'.
        
    Returns:
        Flask: Configured Flask application instance.
    """
    # Create Flask application instance
    app = Flask(__name__)
    
    # Load configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    app.config.from_object(config[config_name])
    
    # Initialize extensions with app
    db.init_app(app)
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # Import models to ensure they are registered with SQLAlchemy
    from app.models.user import User
    
    # Import and register blueprints
    from app.api.routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app
