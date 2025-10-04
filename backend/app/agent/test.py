import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

from app.services.culture_data import _generate_ai_itineraries

# Test the _generate_ai_itineraries method with Paris attractions
poi_list = ["Eiffel Tower", "Louvre Museum", "Notre-Dame Cathedral", "Arc de Triomphe", "Champs-Élysées"]
start_date = "2025-01-15"
end_date = "2025-01-17"
num_days = 3

print("Testing AI Itinerary Generation...")
print(f"Points of Interest: {', '.join(poi_list)}")
print(f"Trip Duration: {start_date} to {end_date} ({num_days} days)")
print("=" * 60)

itineraries = _generate_ai_itineraries(poi_list, num_days, start_date, end_date)

if itineraries:
    print(f"Successfully Generated {len(itineraries)} Different Itinerary Options!")
    print("=" * 60)
    
    for i, itinerary in enumerate(itineraries, 1):
        print(f"\n🎯 ITINERARY OPTION {i}:")
        print("-" * 40)
        
        for day_plan in itinerary:
            print(f"  {day_plan}")
        
        print()
    
    print("=" * 60)
    print("Itinerary Analysis:")
    print(f"  • Total Options Generated: {len(itineraries)}")
    print(f"  • Days Covered: {num_days}")
    print(f"  • Attractions Included: {len(poi_list)}")
    
    # Analyze itinerary diversity
    all_attractions_used = set()
    for itinerary in itineraries:
        for day_plan in itinerary:
            # Extract attraction names from day plans
            attractions_in_day = day_plan.split(": ")[1] if ": " in day_plan else day_plan
            attractions_in_day = attractions_in_day.split(" → ")
            for attraction in attractions_in_day:
                attraction = attraction.strip()
                if attraction:
                    all_attractions_used.add(attraction)
    
    print(f"  • Unique Attractions Used: {len(all_attractions_used)}")
    print(f"  • Attraction Coverage: {len(all_attractions_used)}/{len(poi_list)} ({len(all_attractions_used)/len(poi_list)*100:.1f}%)")
    
    if len(all_attractions_used) == len(poi_list):
        print("  ✅ All attractions are included in the itineraries!")
    else:
        missing = set(poi_list) - all_attractions_used
        print(f"  ⚠️  Missing attractions: {', '.join(missing)}")
    
else:
    print("No itineraries generated. Please check your GOOGLE_API_KEY environment variable.")
    print("Make sure you have a valid Google API key set in your .env file.")