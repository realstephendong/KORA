"""
Itinerary model for the travel planner application.
Defines the Itinerary database model for storing travel plans.
"""

from app import db


class Itinerary(db.Model):
    """
    Itinerary model representing saved travel plans.
    
    Attributes:
        id (int): Primary key, auto-incrementing integer
        user_id (int): Foreign key to User model, not nullable
        name (str): Name of the itinerary, not nullable
        cities (str): JSON string of cities list, not nullable
        total_distance_km (float): Total distance in kilometers
        carbon_emissions_kg (float): Estimated carbon emissions in kg
        created_at (datetime): Timestamp when itinerary was created
        updated_at (datetime): Timestamp when itinerary was last updated
    """
    
    __tablename__ = 'itineraries'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign key to User
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Itinerary details
    name = db.Column(db.String(255), nullable=False)
    cities = db.Column(db.Text, nullable=False)  # JSON string of cities list
    total_distance_km = db.Column(db.Float, nullable=True)
    carbon_emissions_kg = db.Column(db.Float, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), 
                          onupdate=db.func.current_timestamp())
    
    # Relationship
    user = db.relationship('User', backref=db.backref('itineraries', lazy=True))
    
    def __repr__(self):
        """String representation of the Itinerary model."""
        return f'<Itinerary {self.name} by User {self.user_id}>'
    
    def to_dict(self):
        """
        Convert Itinerary instance to dictionary.
        
        Returns:
            dict: Dictionary representation of the itinerary
        """
        import json
        
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'cities': json.loads(self.cities) if self.cities else [],
            'total_distance_km': self.total_distance_km,
            'carbon_emissions_kg': self.carbon_emissions_kg,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def create_itinerary(cls, user_id, name, cities, total_distance_km=None, carbon_emissions_kg=None):
        """
        Create a new itinerary.
        
        Args:
            user_id (int): ID of the user creating the itinerary
            name (str): Name of the itinerary
            cities (list): List of city names
            total_distance_km (float, optional): Total distance in kilometers
            carbon_emissions_kg (float, optional): Carbon emissions in kg
            
        Returns:
            Itinerary: Newly created itinerary instance
        """
        import json
        
        itinerary = cls(
            user_id=user_id,
            name=name,
            cities=json.dumps(cities),
            total_distance_km=total_distance_km,
            carbon_emissions_kg=carbon_emissions_kg
        )
        
        db.session.add(itinerary)
        db.session.commit()
        return itinerary
