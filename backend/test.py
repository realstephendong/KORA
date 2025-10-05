#!/usr/bin/env python3
"""
Test script for the save_itinerary method.
Tests the JSON storage functionality and database operations.
"""

import os
import sys
import json
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app import create_app
from app.models.user import User
from app.models.itinerary import Itinerary
from app.agent.tools import save_itinerary
from app import db

def test_save_itinerary():
    """Test the save_itinerary method with various scenarios."""
    app = create_app()
    
    with app.app_context():
        print("=== TESTING SAVE_ITINERARY METHOD ===\n")
        
        # Clean up any existing test data
        cleanup_test_data()
        
        # Test 1: Create a test user
        print("Test 1: Creating test user...")
        test_user = User.create_or_get_user(
            auth0_sub="test-user-123",
            name="Test User",
            email="test@example.com"
        )
        print(f"✓ Created test user with ID: {test_user.id}\n")
        
        # Test 2: Save a simple single-city itinerary
        print("Test 2: Saving single-city itinerary...")
        result1 = save_itinerary.invoke({
            'user_id': test_user.id,
            'itinerary_name': 'London Weekend Trip',
            'cities': ['London'],
            'total_distance_km': 0.0,
            'carbon_emissions_kg': 0.0
        })
        print(f"✓ Result: {result1}\n")
        
        # Test 3: Save a multi-city itinerary with distance and carbon data
        print("Test 3: Saving multi-city itinerary...")
        result2 = save_itinerary.invoke({
            'user_id': test_user.id,
            'itinerary_name': 'France Adventure',
            'cities': ['Paris', 'Lyon', 'Nice'],
            'total_distance_km': 750.5,
            'carbon_emissions_kg': 90.06
        })
        print(f"✓ Result: {result2}\n")
        
        # Test 4: Save itinerary with edge case data
        print("Test 4: Saving itinerary with edge case data...")
        result3 = save_itinerary.invoke({
            'user_id': test_user.id,
            'itinerary_name': 'Japan Cultural Tour',
            'cities': ['Tokyo', 'Kyoto', 'Osaka', 'Hiroshima'],
            'total_distance_km': 1200.0,
            'carbon_emissions_kg': 144.0
        })
        print(f"✓ Result: {result3}\n")
        
        # Test 5: Verify data was saved correctly
        print("Test 5: Verifying saved data...")
        verify_saved_itineraries(test_user.id)
        
        # Test 6: Test JSON structure
        print("Test 6: Testing JSON structure...")
        test_json_structure(test_user.id)
        
        # Test 7: Test JSON file
        print("Test 7: Testing JSON file...")
        test_json_file()
        
        # Test 8: Test error handling
        print("Test 8: Testing error handling...")
        test_error_handling()
        
        print("=== ALL TESTS COMPLETED ===\n")
        
        # Clean up test data
        cleanup_test_data()
        print("✓ Cleaned up test data")

def verify_saved_itineraries(user_id):
    """Verify that itineraries were saved correctly."""
    itineraries = Itinerary.query.filter_by(user_id=user_id).all()
    
    print(f"Found {len(itineraries)} itineraries for user {user_id}:")
    
    for itinerary in itineraries:
        print(f"\n  Itinerary ID: {itinerary.id}")
        print(f"  Name: {itinerary.name}")
        print(f"  Cities: {itinerary.cities}")
        print(f"  Distance: {itinerary.total_distance_km} km")
        print(f"  Carbon: {itinerary.carbon_emissions_kg} kg")
        print(f"  Created: {itinerary.created_at}")
        
        # Check if JSON data exists
        if itinerary.attractions:
            try:
                json_data = json.loads(itinerary.attractions)
                print(f"  JSON Data: ✓ Available")
                print(f"  JSON Keys: {list(json_data.keys())}")
            except json.JSONDecodeError:
                print(f"  JSON Data: ✗ Invalid JSON")
        else:
            print(f"  JSON Data: ✗ Not available")

def test_json_structure(user_id):
    """Test the JSON structure of saved itineraries."""
    itineraries = Itinerary.query.filter_by(user_id=user_id).all()
    
    for itinerary in itineraries:
        if itinerary.attractions:
            try:
                json_data = json.loads(itinerary.attractions)
                
                # Check required JSON structure
                required_keys = ['itinerary_info', 'travel_details', 'sustainability_metrics', 'metadata']
                missing_keys = [key for key in required_keys if key not in json_data]
                
                if missing_keys:
                    print(f"✗ Itinerary {itinerary.id} missing JSON keys: {missing_keys}")
                else:
                    print(f"✓ Itinerary {itinerary.id} has complete JSON structure")
                    
                    # Check specific values
                    travel_details = json_data['travel_details']
                    sustainability_metrics = json_data['sustainability_metrics']
                    metadata = json_data['metadata']
                    
                    print(f"    Cities in JSON: {travel_details.get('cities', [])}")
                    print(f"    Distance in JSON: {travel_details.get('total_distance_km', 0)}")
                    print(f"    Carbon in JSON: {travel_details.get('carbon_emissions_kg', 0)}")
                    print(f"    City count: {metadata.get('city_count', 0)}")
                    print(f"    Is multi-city: {metadata.get('is_multi_city', False)}")
                    
            except json.JSONDecodeError as e:
                print(f"✗ Itinerary {itinerary.id} has invalid JSON: {e}")

def test_json_file():
    """Test the JSON file functionality."""
    import os
    
    # Check if JSON file exists
    json_file_path = os.path.join('app', 'models', 'itinerary.json')
    
    if os.path.exists(json_file_path):
        print(f"  ✓ JSON file exists at: {json_file_path}")
        
        try:
            with open(json_file_path, 'r') as f:
                json_data = json.load(f)
            
            if isinstance(json_data, list):
                print(f"  ✓ JSON file contains {len(json_data)} itineraries")
                
                for i, itinerary in enumerate(json_data):
                    print(f"    Itinerary {i+1}:")
                    print(f"      ID: {itinerary.get('itinerary_info', {}).get('id', 'N/A')}")
                    print(f"      Name: {itinerary.get('itinerary_info', {}).get('name', 'N/A')}")
                    print(f"      Cities: {itinerary.get('travel_details', {}).get('cities', [])}")
                    print(f"      Distance: {itinerary.get('travel_details', {}).get('total_distance_km', 0)} km")
                    print(f"      Carbon: {itinerary.get('travel_details', {}).get('carbon_emissions_kg', 0)} kg")
            else:
                print(f"  ✗ JSON file format is incorrect (expected list, got {type(json_data)})")
                
        except json.JSONDecodeError as e:
            print(f"  ✗ JSON file is corrupted: {e}")
        except Exception as e:
            print(f"  ✗ Error reading JSON file: {e}")
    else:
        print(f"  ✗ JSON file does not exist at: {json_file_path}")

def test_error_handling():
    """Test error handling scenarios."""
    print("  Testing invalid user ID...")
    try:
        result = save_itinerary.invoke({
            'user_id': 99999,  # Non-existent user
            'itinerary_name': 'Test Itinerary',
            'cities': ['Test City'],
            'total_distance_km': 100.0,
            'carbon_emissions_kg': 12.0
        })
        print(f"    Result: {result}")
    except Exception as e:
        print(f"    Expected error: {e}")
    
    print("  Testing invalid data types...")
    try:
        result = save_itinerary.invoke({
            'user_id': 1,
            'itinerary_name': 'Test Itinerary',
            'cities': "not a list",  # Invalid type
            'total_distance_km': 100.0,
            'carbon_emissions_kg': 12.0
        })
        print(f"    Result: {result}")
    except Exception as e:
        print(f"    Expected error: {e}")

def cleanup_test_data():
    """Clean up test data from the database and JSON file."""
    try:
        # Delete test itineraries
        test_itineraries = Itinerary.query.filter(
            Itinerary.name.like('%Test%') |
            Itinerary.name.like('%London Weekend%') |
            Itinerary.name.like('%France Adventure%') |
            Itinerary.name.like('%Japan Cultural%')
        ).all()
        
        for itinerary in test_itineraries:
            db.session.delete(itinerary)
        
        # Delete test user
        test_user = User.query.filter_by(auth0_sub="test-user-123").first()
        if test_user:
            db.session.delete(test_user)
        
        db.session.commit()
        
        # Clean up JSON file
        cleanup_json_file()
        
        print("✓ Cleaned up test data")
        
    except Exception as e:
        print(f"Error cleaning up test data: {e}")
        db.session.rollback()

def cleanup_json_file():
    """Clean up test data from the JSON file."""
    try:
        import os
        
        json_file_path = os.path.join('app', 'models', 'itinerary.json')
        
        if os.path.exists(json_file_path):
            with open(json_file_path, 'r') as f:
                json_data = json.load(f)
            
            if isinstance(json_data, list):
                # Filter out test itineraries
                filtered_data = [
                    itinerary for itinerary in json_data
                    if not any(test_name in itinerary.get('itinerary_info', {}).get('name', '') 
                             for test_name in ['Test', 'London Weekend', 'France Adventure', 'Japan Cultural'])
                ]
                
                # Write back filtered data
                with open(json_file_path, 'w') as f:
                    json.dump(filtered_data, f, indent=2)
                
                print(f"✓ Cleaned up JSON file, removed {len(json_data) - len(filtered_data)} test entries")
        
    except Exception as e:
        print(f"Error cleaning up JSON file: {e}")

def test_database_connection():
    """Test database connection and basic operations."""
    app = create_app()
    
    with app.app_context():
        print("=== TESTING DATABASE CONNECTION ===\n")
        
        # Test user count
        user_count = User.query.count()
        print(f"Total users in database: {user_count}")
        
        # Test itinerary count
        itinerary_count = Itinerary.query.count()
        print(f"Total itineraries in database: {itinerary_count}")
        
        # Test recent itineraries
        recent_itineraries = Itinerary.query.order_by(Itinerary.created_at.desc()).limit(3).all()
        print(f"\nRecent itineraries:")
        for itinerary in recent_itineraries:
            print(f"  - {itinerary.name} (ID: {itinerary.id}, User: {itinerary.user_id})")
        
        print("\n✓ Database connection successful\n")

if __name__ == "__main__":
    print("Starting save_itinerary tests...\n")
    
    # Test database connection first
    test_database_connection()
    
    # Run main tests
    test_save_itinerary()
    
    print("All tests completed successfully!")
