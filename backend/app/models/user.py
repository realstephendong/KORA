"""
User model for the travel planner application.
Defines the User database model with Auth0 integration.
"""

from app import db


class User(db.Model):
    """
    User model representing users in the travel planner system.
    
    Attributes:
        id (int): Primary key, auto-incrementing integer
        auth0_sub (str): Unique Auth0 subject identifier, not nullable
        name (str): User's display name
        email (str): User's email address
        created_at (datetime): Timestamp when user was created
        updated_at (datetime): Timestamp when user was last updated
    """
    
    __tablename__ = 'users'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Auth0 subject identifier (unique user identifier from Auth0)
    auth0_sub = db.Column(db.String(255), unique=True, nullable=False, index=True)
    
    # User profile information
    name = db.Column(db.String(255), nullable=True)
    email = db.Column(db.String(255), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), 
                          onupdate=db.func.current_timestamp())
    
    def __repr__(self):
        """String representation of the User model."""
        return f'<User {self.auth0_sub}>'
    
    def to_dict(self):
        """
        Convert User instance to dictionary.
        
        Returns:
            dict: Dictionary representation of the user
        """
        return {
            'id': self.id,
            'auth0_sub': self.auth0_sub,
            'name': self.name,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def find_by_auth0_sub(cls, auth0_sub):
        """
        Find user by Auth0 subject identifier.
        
        Args:
            auth0_sub (str): Auth0 subject identifier
            
        Returns:
            User or None: User instance if found, None otherwise
        """
        return cls.query.filter_by(auth0_sub=auth0_sub).first()
    
    @classmethod
    def create_or_get_user(cls, auth0_sub, name=None, email=None):
        """
        Create a new user or get existing user by Auth0 subject.
        Updates user info if provided.
        
        Args:
            auth0_sub (str): Auth0 subject identifier
            name (str, optional): User's display name from Auth0
            email (str, optional): User's email address from Auth0
            
        Returns:
            User: User instance (newly created or existing)
        """
        user = cls.find_by_auth0_sub(auth0_sub)
        if not user:
            # Create new user with Auth0 data
            user = cls(auth0_sub=auth0_sub, name=name, email=email)
            db.session.add(user)
            db.session.commit()
            print(f"DEBUG: Created new user for Auth0 sub: {auth0_sub}")
        else:
            # Update existing user with new Auth0 data if provided
            updated = False
            if name and user.name != name:
                user.name = name
                updated = True
                print(f"DEBUG: Updated user name to: {name}")
            if email and user.email != email:
                user.email = email
                updated = True
                print(f"DEBUG: Updated user email to: {email}")
            
            if updated:
                db.session.commit()
                print(f"DEBUG: Updated existing user for Auth0 sub: {auth0_sub}")
        
        return user
