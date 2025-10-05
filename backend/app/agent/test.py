import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

from app.services.travel_data_api import fetch_hotels_in_city

# Test the fetch_hotels_in_city method
print("Testing Hotels in City Fetching...")
print("=" * 50)

# Test parameters
city_name = "Paris"

print(f"City: {city_name}")
print("=" * 50)

# Fetch hotels in the city
hotels = fetch_hotels_in_city(city_name)

if hotels:
    print(f"✅ Successfully Found {len(hotels)} Hotels in {city_name}!")
    print("=" * 50)
    
    # Display hotel information
    for i, hotel in enumerate(hotels, 1):
        print(f"\n🏨 HOTEL {i}:")
        print("-" * 40)
        print(f"  🏷️  Name: {hotel.get('name', 'Unknown Hotel')}")
        print(f"  🆔 Hotel ID: {hotel.get('hotel_id', 'N/A')}")
        print(f"  📍 Address: {hotel.get('address', 'Address not available')}")
        print(f"  🏙️  City: {hotel.get('city', city_name)}")
        print(f"  🌍 Country: {hotel.get('country', 'N/A')}")
        print(f"  📮 Postal Code: {hotel.get('postal_code', 'N/A')}")
        
        # Display coordinates if available
        latitude = hotel.get('latitude')
        longitude = hotel.get('longitude')
        if latitude and longitude:
            print(f"  📍 Coordinates: {latitude}, {longitude}")
        
        # Display rating if available
        rating = hotel.get('rating')
        if rating and rating != 'Rating not available':
            print(f"  ⭐ Rating: {rating}")
        
        # Display amenities if available
        amenities = hotel.get('amenities', [])
        if amenities:
            print(f"  🛎️  Amenities: {', '.join(amenities[:5])}")  # Show first 5 amenities
            if len(amenities) > 5:
                print(f"      ... and {len(amenities) - 5} more")
        
        # Display contact information if available
        contact = hotel.get('contact', {})
        if contact:
            print(f"  📞 Contact: {contact}")
        
        # Display description if available
        description = hotel.get('description')
        if description and description != 'No description available':
            # Truncate long descriptions
            if len(description) > 100:
                description = description[:100] + "..."
            print(f"  📝 Description: {description}")
        
        # Display additional identifiers
        chain_code = hotel.get('chain_code')
        iata_code = hotel.get('iata_code')
        if chain_code:
            print(f"  🏢 Chain Code: {chain_code}")
        if iata_code:
            print(f"  ✈️  IATA Code: {iata_code}")
        
        print("  " + "-" * 30)
    
    # Summary statistics
    print("\n📊 HOTEL SUMMARY:")
    print("-" * 30)
    print(f"  🏨 Total Hotels Found: {len(hotels)}")
    
    # Analyze hotel data
    hotels_with_ratings = [h for h in hotels if h.get('rating') and h.get('rating') != 'Rating not available']
    hotels_with_amenities = [h for h in hotels if h.get('amenities')]
    hotels_with_coordinates = [h for h in hotels if h.get('latitude') and h.get('longitude')]
    
    print(f"  ⭐ Hotels with Ratings: {len(hotels_with_ratings)}")
    print(f"  🛎️  Hotels with Amenities: {len(hotels_with_amenities)}")
    print(f"  📍 Hotels with Coordinates: {len(hotels_with_coordinates)}")
    
    # Chain analysis
    chain_codes = [h.get('chain_code') for h in hotels if h.get('chain_code')]
    if chain_codes:
        unique_chains = list(set(chain_codes))
        print(f"  🏢 Hotel Chains: {len(unique_chains)}")
        for chain in unique_chains[:3]:  # Show top 3 chains
            count = chain_codes.count(chain)
            print(f"    • {chain}: {count} hotel(s)")
    
    # Country analysis
    countries = [h.get('country') for h in hotels if h.get('country')]
    if countries:
        unique_countries = list(set(countries))
        print(f"  🌍 Countries: {', '.join(unique_countries)}")
    
    print("\n" + "=" * 50)
    print("✅ Hotels in city fetching test completed successfully!")
    
else:
    print("❌ No hotels found in the city.")
    print("\nPossible reasons:")
    print("  • City name not recognized by Amadeus API")
    print("  • No hotels available in the city")
    print("  • Amadeus API credentials not configured")
    print("  • API rate limit exceeded")
    print("  • Network connectivity issues")
    print("\nPlease check:")
    print("  • AMADEUS_API_KEY and AMADEUS_SECRET_KEY in your .env file")
    print("  • City name is spelled correctly")
    print("  • City exists in the Amadeus database")
    print("  • Try a major city like 'Paris', 'London', 'New York'")