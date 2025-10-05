import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

from app.services.culture_data import fetch_place_information

# Test the fetch_place_information method
print("Testing Place Information Fetching...")
print("=" * 60)

# Test parameters - list of places to search for
test_places = [
    "Eiffel Tower",
    "Sydney Opera House", 
    "Colosseum Rome",
    "Golden Gate Bridge",
    "Machu Picchu"
]

print(f"Places to search: {', '.join(test_places)}")
print("=" * 60)

# Fetch place information
place_data = fetch_place_information(test_places)

if place_data and 'places' in place_data:
    successful_searches = place_data.get('successful_searches', 0)
    total_searches = place_data.get('total_places_searched', 0)
    
    print(f"✅ Successfully Found Information for {successful_searches}/{total_searches} Places!")
    print("=" * 60)
    
    # Display place information
    for place_name, place_info in place_data['places'].items():
        print(f"\n🏛️  PLACE: {place_name}")
        print("-" * 50)
        
        if 'error' in place_info:
            print(f"  ❌ Error: {place_info['error']}")
            continue
        
        # Display basic information
        print(f"  🏷️  Name: {place_info.get('name', 'Unknown Place')}")
        print(f"  📍 Address: {place_info.get('address', 'Address not available')}")
        
        # Display rating information
        rating = place_info.get('rating')
        user_rating_count = place_info.get('user_rating_count', 0)
        if rating and rating != 'Rating not available':
            print(f"  ⭐ Rating: {rating} ({user_rating_count} reviews)")
        
        # Display price level
        price_level = place_info.get('price_level')
        if price_level and price_level != 'Price level not available':
            price_symbols = {1: '$', 2: '$$', 3: '$$$', 4: '$$$$'}
            price_display = price_symbols.get(price_level, f'Level {price_level}')
            print(f"  💰 Price Level: {price_display}")
        
        # Display place types
        types = place_info.get('types', [])
        if types:
            print(f"  🏷️  Categories: {', '.join(types[:5])}")
            if len(types) > 5:
                print(f"      ... and {len(types) - 5} more")
        
        # Display location coordinates
        location = place_info.get('location', {})
        if location:
            lat = location.get('latitude')
            lng = location.get('longitude')
            if lat and lng:
                print(f"  📍 Coordinates: {lat}, {lng}")
        
        # Display contact information
        website = place_info.get('website')
        phone = place_info.get('phone')
        if website and website != 'Website not available':
            print(f"  🌐 Website: {website}")
        if phone and phone != 'Phone not available':
            print(f"  📞 Phone: {phone}")
        
        print("  " + "-" * 40)
    
    # Summary statistics
    print("\n📊 PLACE INFORMATION SUMMARY:")
    print("-" * 40)
    print(f"  🏛️  Total Places Searched: {total_searches}")
    print(f"  ✅ Successful Searches: {successful_searches}")
    print(f"  ❌ Failed Searches: {total_searches - successful_searches}")
    
    # Analyze place data
    places_with_ratings = [p for p in place_data['places'].values() 
                          if 'error' not in p and p.get('rating') and p.get('rating') != 'Rating not available']
    places_with_coordinates = [p for p in place_data['places'].values() 
                              if 'error' not in p and p.get('location', {}).get('latitude')]
    places_with_websites = [p for p in place_data['places'].values() 
                           if 'error' not in p and p.get('website') and p.get('website') != 'Website not available']
    places_with_phone = [p for p in place_data['places'].values() 
                        if 'error' not in p and p.get('phone') and p.get('phone') != 'Phone not available']
    
    print(f"  ⭐ Places with Ratings: {len(places_with_ratings)}")
    print(f"  📍 Places with Coordinates: {len(places_with_coordinates)}")
    print(f"  🌐 Places with Websites: {len(places_with_websites)}")
    print(f"  📞 Places with Phone: {len(places_with_phone)}")
    
    # Category analysis
    all_types = []
    for place_info in place_data['places'].values():
        if 'error' not in place_info:
            all_types.extend(place_info.get('types', []))
    
    if all_types:
        from collections import Counter
        type_counts = Counter(all_types)
        print(f"  🏷️  Most Common Categories:")
        for category, count in type_counts.most_common(5):
            print(f"    • {category}: {count} place(s)")
    
    # Rating analysis
    if places_with_ratings:
        ratings = [float(p.get('rating', 0)) for p in places_with_ratings if p.get('rating')]
        if ratings:
            avg_rating = sum(ratings) / len(ratings)
            print(f"  📊 Average Rating: {avg_rating:.1f}/5.0")
            print(f"  📈 Highest Rating: {max(ratings)}/5.0")
            print(f"  📉 Lowest Rating: {min(ratings)}/5.0")
    
    print("\n" + "=" * 60)
    print("✅ Place information fetching test completed successfully!")
    
else:
    print("❌ No place information found.")
    print("\nPossible reasons:")
    print("  • Google Places API key not configured")
    print("  • API rate limit exceeded")
    print("  • Network connectivity issues")
    print("  • Invalid place names")
    print("\nPlease check:")
    print("  • GOOGLE_API_KEY in your .env file")
    print("  • Place names are spelled correctly")
    print("  • Places exist in Google Places database")
    print("  • Try famous landmarks like 'Eiffel Tower', 'Statue of Liberty'")