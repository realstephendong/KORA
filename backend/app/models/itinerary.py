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
        
        # Enhanced fields for comprehensive travel data
        country (str): Destination country name
        travel_dates (str): JSON string with departure and return dates
        duration_days (int): Trip duration in days
        attractions (str): JSON string of attractions/POIs for each city
        flight_info (str): JSON string with flight details and costs
        estimated_costs (str): JSON string with cost breakdown
    """
    
    __tablename__ = 'itineraries'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign key to User
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Basic itinerary details
    name = db.Column(db.String(255), nullable=False)
    cities = db.Column(db.Text, nullable=False)  # JSON string of cities list
    total_distance_km = db.Column(db.Float, nullable=True)
    carbon_emissions_kg = db.Column(db.Float, nullable=True)
    
    # Enhanced travel information
    country = db.Column(db.String(100), nullable=True)
    travel_dates = db.Column(db.Text, nullable=True)  # JSON: {"departure": "2024-01-15", "return": "2024-01-22"}
    duration_days = db.Column(db.Integer, nullable=True)
    attractions = db.Column(db.Text, nullable=True)  # JSON: {"Paris": ["Eiffel Tower", "Louvre"], "Lyon": ["Basilica"]}
    flight_info = db.Column(db.Text, nullable=True)  # JSON: {"departure_flight": {...}, "return_flight": {...}}
    estimated_costs = db.Column(db.Text, nullable=True)  # JSON: {"flights": 500, "hotels": 300, "food": 200, "total": 1000}
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), 
                          onupdate=db.func.current_timestamp())
    
    # Relationship
    user = db.relationship('User', backref=db.backref('itineraries', lazy=True), foreign_keys=[user_id])
    
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
            'country': self.country,
            'travel_dates': json.loads(self.travel_dates) if self.travel_dates else None,
            'duration_days': self.duration_days,
            'attractions': json.loads(self.attractions) if self.attractions else None,
            'flight_info': json.loads(self.flight_info) if self.flight_info else None,
            'estimated_costs': json.loads(self.estimated_costs) if self.estimated_costs else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def create_itinerary(cls, user_id, name, cities, total_distance_km=None, carbon_emissions_kg=None, 
                        country=None, travel_dates=None, duration_days=None,
                        attractions=None, flight_info=None, estimated_costs=None):
        """
        Create a new itinerary with enhanced travel information.
        
        Args:
            user_id (int): ID of the user creating the itinerary
            name (str): Name of the itinerary
            cities (list): List of city names
            total_distance_km (float, optional): Total distance in kilometers
            carbon_emissions_kg (float, optional): Carbon emissions in kg
            country (str, optional): Destination country name
            travel_dates (dict, optional): Travel dates with departure and return
            duration_days (int, optional): Trip duration in days
            attractions (dict, optional): Attractions/POIs for each city
            flight_info (dict, optional): Flight details and costs
            estimated_costs (dict, optional): Cost breakdown
            
        Returns:
            Itinerary: Newly created itinerary instance
        """
        import json
        
        itinerary = cls(
            user_id=user_id,
            name=name,
            cities=json.dumps(cities),
            total_distance_km=total_distance_km,
            carbon_emissions_kg=carbon_emissions_kg,
            country=country,
            travel_dates=json.dumps(travel_dates) if travel_dates else None,
            duration_days=duration_days,
            attractions=json.dumps(attractions) if attractions else None,
            flight_info=json.dumps(flight_info) if flight_info else None,
            estimated_costs=json.dumps(estimated_costs) if estimated_costs else None
        )
        
        db.session.add(itinerary)
        db.session.commit()
        return itinerary
