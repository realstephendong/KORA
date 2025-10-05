'use client';

import React from "react";
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import ProtectedRoute from '@/components/ProtectedRoute';
import { useEffect, useState } from 'react';
import Image from 'next/image';
import { itineraryApi } from '@/lib/api-client';

interface TripInfo {
  icon: string;
  text: string;
  alt: string;
}

interface DayItinerary {
  day: number;
  location: string;
  description: string;
}

interface SavedItinerary {
  id: number;
  user_id: number;
  name: string;
  cities: string[];
  total_distance_km: number;
  carbon_emissions_kg: number;
  country?: string;
  travel_dates?: {
    departure: string;
    return: string;
  };
  duration_days?: number;
  attractions?: {
    [city: string]: string[];
  };
  flight_info?: {
    departure_flight?: any;
    return_flight?: any;
  };
  estimated_costs?: {
    flights?: number;
    hotels?: number;
    food?: number;
    total?: number;
  };
  created_at: string;
  updated_at: string;
}


// Trip Info Component
const TripInfoBar = ({ tripInfoData }: { tripInfoData: TripInfo[] }) => (
  <div className="flex items-center justify-between px-4 py-3 bg-white rounded-[25px] overflow-hidden border-2 border-gray-200 min-w-[300px] max-w-[500px]">
    {tripInfoData.map((info, index) => (
      <div
        key={index}
        className="flex items-center gap-2 relative flex-1 justify-center"
      >
        <Image
          className="w-4 h-4 aspect-[1] flex-shrink-0"
          alt={info.alt}
          src={info.icon}
          width={16}
          height={16}
        />
        <div className="font-medium text-black text-sm tracking-[0] leading-[normal] whitespace-nowrap">
          {info.text}
        </div>
      </div>
    ))}
  </div>
);

// Congratulations Section Component
const CongratulationsSection = ({ 
  itinerary 
}: { 
  itinerary: SavedItinerary | null; 
}) => {
  if (!itinerary) {
    return (
      <section className="w-full max-w-2xl mx-auto mb-8 rounded-[30px] overflow-hidden border-2 border-solid border-[#d8dfe980] backdrop-blur-sm backdrop-brightness-[100%] [-webkit-backdrop-filter:blur(4px)_brightness(100%)] bg-[rgba(255,255,255,0.2)] relative min-h-[400px]">
        <div className="p-6 text-center">
          <div className="text-gray-600 text-lg mb-4">
            {itinerary === null ? 'Loading your trip data...' : 'No itineraries found'}
          </div>
        </div>
      </section>
    );
  }

  // Calculate environmental impact metrics
  const calculateEnvironmentalImpact = (emissionsKg: number) => {
    // 1 tree absorbs approximately 22 kg CO2 per year
    const treesSaved = Math.round(emissionsKg / 22);
    
    // 1 plastic bag produces approximately 0.33 kg CO2
    const plasticBagsSaved = Math.round(emissionsKg / 0.33);
    
    return { treesSaved, plasticBagsSaved };
  };

  const { treesSaved, plasticBagsSaved } = calculateEnvironmentalImpact(itinerary.carbon_emissions_kg);

  return (
  <section className="w-full max-w-2xl mx-auto mb-8 rounded-[30px] overflow-hidden border-2 border-solid border-[#d8dfe980] backdrop-blur-sm backdrop-brightness-[100%] [-webkit-backdrop-filter:blur(4px)_brightness(100%)] bg-[rgba(255,255,255,0.2)] relative min-h-[400px]">
    <div className="p-6 text-center">
      <div className="text-gray-600 text-lg mb-4">
        We&apos;ve calculated your trip!
      </div>

      <h1 className="text-3xl md:text-4xl font-normal italic text-black mb-8">
        Congratulations!
      </h1>

      {/* Bar chart container */}
      <div className="relative h-48 mb-6 flex items-end justify-center gap-2">
        {/* Bar chart elements */}
        <div className="w-7 h-48 bg-white rounded-[23px]" />
        <div className="w-5 h-20 bg-[#cfdecb] rounded-[23px]" />
        <div className="w-7 h-48 bg-white rounded-[23px]" />
        <div className="w-7 h-48 bg-white rounded-[23px]" />
        <div className="w-5 h-32 bg-[#abc7f0] rounded-[23px]" />
        <div className="w-5 h-24 bg-[#f1f37e] rounded-[23px]" />

        {/* Icons positioned over bars */}
        <Image
          className="absolute bottom-4 left-1/2 transform -translate-x-1/2 w-12 h-12"
          alt="Tree"
          src="https://c.animaapp.com/7Y4W5hAe/img/tree2@2x.png"
          width={48}
          height={48}
        />

        <Image
          className="absolute bottom-8 left-1/2 transform -translate-x-1/2 w-10 h-10"
          alt="Trash bag"
          src="https://c.animaapp.com/7Y4W5hAe/img/trash-bag@2x.png"
          width={40}
          height={40}
        />
      </div>

      <p className="text-gray-600 text-sm md:text-base leading-relaxed">
        You&apos;ve saved the equivalent of {treesSaved} trees, {plasticBagsSaved.toLocaleString()} plastic bags from
        polluting the sea, and of course! {itinerary.carbon_emissions_kg.toFixed(0)} kg of CO₂ emissions avoided.
      </p>
    </div>
  </section>
  );
};

// Itinerary Section Component
const ItinerarySection = ({ itinerary }: { itinerary: SavedItinerary | null }) => {
  if (!itinerary) {
    return (
      <section className="w-full max-w-6xl mx-auto mb-8 rounded-[30px] overflow-hidden bg-[rgba(216,223,233,1)] relative">
        <div className="bg-[#231f20] rounded-t-[30px] p-8 text-center relative">
          <h2 className="text-3xl md:text-4xl font-normal italic text-[#f6f5fa] mb-2">
            {itinerary === null ? 'Loading...' : 'No itineraries found'}
          </h2>
        </div>
      </section>
    );
  }

  return (
  <section className="w-full max-w-6xl mx-auto mb-8 rounded-[30px] overflow-hidden bg-[rgba(216,223,233,1)] relative">
    {/* Header */}
    <div className="bg-[#231f20] rounded-t-[30px] p-8 text-center relative">

      <h2 className="text-3xl md:text-4xl font-normal italic text-[#f6f5fa] mb-2">
        {itinerary.name}
      </h2>

      <div className="text-gray-400 text-lg">
        {itinerary.cities.join(', ')}
      </div>

      <Image
        className="absolute top-4 right-4 w-8 h-8"
        alt="Turtle pink"
        src="https://c.animaapp.com/7Y4W5hAe/img/turle-pink@2x.png"
        width={32}
        height={32}
      />
    </div>

    {/* Itinerary Content */}
    <div className="bg-[rgba(246,245,250,1)] p-6">
      <div className="grid gap-6 md:gap-8">
        {/* Basic Trip Details */}
        <article className="relative p-6 bg-white rounded-lg shadow-sm border-l-4 border-blue-500">
          <h3 className="text-xl font-semibold text-gray-800 mb-3">
            Trip Details
          </h3>
          
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-600 font-medium">Total Distance:</span>
              <span className="text-gray-800 font-semibold">{itinerary.total_distance_km.toFixed(1)} km</span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-gray-600 font-medium">Carbon Emissions:</span>
              <span className="text-gray-800 font-semibold">{itinerary.carbon_emissions_kg.toFixed(1)} kg CO₂</span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-gray-600 font-medium">Cities:</span>
              <span className="text-gray-800 font-semibold">{itinerary.cities.join(' → ')}</span>
            </div>
            
            {itinerary.country && (
              <div className="flex justify-between items-center">
                <span className="text-gray-600 font-medium">Country:</span>
                <span className="text-gray-800 font-semibold">{itinerary.country}</span>
              </div>
            )}
            
            {itinerary.duration_days && (
              <div className="flex justify-between items-center">
                <span className="text-gray-600 font-medium">Duration:</span>
                <span className="text-gray-800 font-semibold">{itinerary.duration_days} days</span>
              </div>
            )}
            
            <div className="flex justify-between items-center">
              <span className="text-gray-600 font-medium">Created:</span>
              <span className="text-gray-800 font-semibold">
                {new Date(itinerary.created_at).toLocaleDateString()}
              </span>
            </div>
          </div>
        </article>

        {/* Travel Dates */}
        {itinerary.travel_dates && (
          <article className="relative p-6 bg-white rounded-lg shadow-sm border-l-4 border-green-500">
            <h3 className="text-xl font-semibold text-gray-800 mb-3">
              Travel Dates
            </h3>
            
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-600 font-medium">Departure:</span>
                <span className="text-gray-800 font-semibold">
                  {new Date(itinerary.travel_dates.departure).toLocaleDateString()}
                </span>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-gray-600 font-medium">Return:</span>
                <span className="text-gray-800 font-semibold">
                  {new Date(itinerary.travel_dates.return).toLocaleDateString()}
                </span>
              </div>
            </div>
          </article>
        )}

        {/* Attractions */}
        {itinerary.attractions && Object.keys(itinerary.attractions).length > 0 && (
          <article className="relative p-6 bg-white rounded-lg shadow-sm border-l-4 border-purple-500">
            <h3 className="text-xl font-semibold text-gray-800 mb-3">
              Attractions & Points of Interest
            </h3>
            
            <div className="space-y-4">
              {Object.entries(itinerary.attractions).map(([city, attractions]) => (
                <div key={city} className="border-l-2 border-gray-200 pl-4">
                  <h4 className="font-semibold text-gray-700 mb-2">{city}</h4>
                  <ul className="list-disc list-inside space-y-1">
                    {attractions.map((attraction, index) => (
                      <li key={index} className="text-gray-600 text-sm">
                        {attraction}
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </article>
        )}

        {/* Flight Information */}
        {itinerary.flight_info && (
          <article className="relative p-6 bg-white rounded-lg shadow-sm border-l-4 border-orange-500">
            <h3 className="text-xl font-semibold text-gray-800 mb-3">
              Flight Information
            </h3>
            
            <div className="space-y-3">
              {itinerary.flight_info.departure_flight && (
                <div>
                  <h4 className="font-semibold text-gray-700 mb-2">Departure Flight</h4>
                  <div className="text-sm text-gray-600">
                    {JSON.stringify(itinerary.flight_info.departure_flight, null, 2)}
                  </div>
                </div>
              )}
              
              {itinerary.flight_info.return_flight && (
                <div>
                  <h4 className="font-semibold text-gray-700 mb-2">Return Flight</h4>
                  <div className="text-sm text-gray-600">
                    {JSON.stringify(itinerary.flight_info.return_flight, null, 2)}
                  </div>
                </div>
              )}
            </div>
          </article>
        )}

        {/* Estimated Costs */}
        {itinerary.estimated_costs && (
          <article className="relative p-6 bg-white rounded-lg shadow-sm border-l-4 border-red-500">
            <h3 className="text-xl font-semibold text-gray-800 mb-3">
              Estimated Costs
            </h3>
            
            <div className="space-y-3">
              {itinerary.estimated_costs.flights && (
                <div className="flex justify-between items-center">
                  <span className="text-gray-600 font-medium">Flights:</span>
                  <span className="text-gray-800 font-semibold">${itinerary.estimated_costs.flights}</span>
                </div>
              )}
              
              {itinerary.estimated_costs.hotels && (
                <div className="flex justify-between items-center">
                  <span className="text-gray-600 font-medium">Hotels:</span>
                  <span className="text-gray-800 font-semibold">${itinerary.estimated_costs.hotels}</span>
                </div>
              )}
              
              {itinerary.estimated_costs.food && (
                <div className="flex justify-between items-center">
                  <span className="text-gray-600 font-medium">Food:</span>
                  <span className="text-gray-800 font-semibold">${itinerary.estimated_costs.food}</span>
                </div>
              )}
              
              {itinerary.estimated_costs.total && (
                <div className="flex justify-between items-center border-t pt-3">
                  <span className="text-gray-800 font-bold">Total:</span>
                  <span className="text-gray-900 font-bold text-lg">${itinerary.estimated_costs.total}</span>
                </div>
              )}
            </div>
          </article>
        )}
      </div>
    </div>
  </section>
  );
};

// Navigation Controls Component
const NavigationControls = ({ 
  currentIndex,
  totalItineraries,
  onPrevious,
  onNext
}: { 
  currentIndex: number;
  totalItineraries: number;
  onPrevious: () => void;
  onNext: () => void;
}) => {
  console.log('NavigationControls - totalItineraries:', totalItineraries, 'currentIndex:', currentIndex);
  
  if (totalItineraries <= 1) {
    console.log('NavigationControls - Hiding navigation (only 1 or 0 itineraries)');
    // Show a debug message when there are no multiple itineraries
    return (
      <div className="flex justify-center items-center gap-4 mb-6">
        <div className="text-sm text-gray-500 italic">
          {totalItineraries === 0 ? 'No itineraries found' : 'Only 1 itinerary - no navigation needed'}
        </div>
      </div>
    );
  }

  return (
    <div className="flex justify-center items-center gap-4 mb-6">
      <button
        onClick={onPrevious}
        disabled={currentIndex === 0}
        className={`w-10 h-10 rounded-full flex items-center justify-center transition-all ${
          currentIndex === 0 
            ? 'bg-gray-300 text-gray-500 cursor-not-allowed' 
            : 'bg-blue-500 text-white hover:bg-blue-600 hover:scale-110'
        }`}
        aria-label="Previous Itinerary"
      >
        ←
      </button>
      
      <div className="text-sm text-gray-600 font-medium">
        {currentIndex + 1} of {totalItineraries}
      </div>
      
      <button
        onClick={onNext}
        disabled={currentIndex === totalItineraries - 1}
        className={`w-10 h-10 rounded-full flex items-center justify-center transition-all ${
          currentIndex === totalItineraries - 1 
            ? 'bg-gray-300 text-gray-500 cursor-not-allowed' 
            : 'bg-blue-500 text-white hover:bg-blue-600 hover:scale-110'
        }`}
        aria-label="Next Itinerary"
      >
        →
      </button>
    </div>
  );
};

// Action Buttons Component
const ActionButtons = ({ 
  onBackToGlobe, 
  onNewSearch 
}: { 
  onBackToGlobe: () => void; 
  onNewSearch: () => void; 
}) => (
  <div className="flex justify-center gap-4 mb-8">
    <button
      onClick={onBackToGlobe}
      className="w-12 h-12 bg-transparent border-none cursor-pointer hover:opacity-80 transition-opacity hover:scale-110 transform"
      aria-label="Back to Globe"
    >
      <Image
        className="w-full h-full"
        alt="Back to Globe"
        src="https://c.animaapp.com/7Y4W5hAe/img/group-4@2x.png"
        width={48}
        height={48}
      />
    </button>

    <button
      onClick={onNewSearch}
      className="w-12 h-12 bg-transparent border-none cursor-pointer hover:opacity-80 transition-opacity hover:scale-110 transform"
      aria-label="New Search"
    >
      <Image
        className="w-full h-full"
        alt="New Search"
        src="https://c.animaapp.com/7Y4W5hAe/img/group-5@2x.png"
        width={48}
        height={48}
      />
    </button>
  </div>
);

export default function ResultPage() {
  const { user, token, isLoading } = useAuth();
  const router = useRouter();
  const [itineraries, setItineraries] = useState<SavedItinerary[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);

  // Get current itinerary
  const currentItinerary = itineraries[currentIndex] || null;

  const tripInfoData: TripInfo[] = currentItinerary ? [
    {
      icon: "https://c.animaapp.com/7Y4W5hAe/img/location-on@2x.png",
      text: currentItinerary.name,
      alt: "Location on",
    },
    {
      icon: "https://c.animaapp.com/7Y4W5hAe/img/map-1@2x.png",
      text: currentItinerary.cities.join(', '),
      alt: "Map",
    },
    {
      icon: "https://c.animaapp.com/7Y4W5hAe/img/map-1@2x.png",
      text: `${currentItinerary.total_distance_km.toFixed(0)} km`,
      alt: "Distance",
    },
  ] : [
    {
      icon: "https://c.animaapp.com/7Y4W5hAe/img/location-on@2x.png",
      text: "Loading...",
      alt: "Location on",
    },
    {
      icon: "https://c.animaapp.com/7Y4W5hAe/img/map-1@2x.png",
      text: "Loading...",
      alt: "Map",
    },
    {
      icon: "https://c.animaapp.com/7Y4W5hAe/img/map-1@2x.png",
      text: "Loading...",
      alt: "Distance",
    },
  ];


  const handleBackToGlobe = () => {
    router.push('/globe');
  };

  const handleNewSearch = () => {
    router.push('/chat');
  };

  const handlePreviousItinerary = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
    }
  };

  const handleNextItinerary = () => {
    if (currentIndex < itineraries.length - 1) {
      setCurrentIndex(currentIndex + 1);
    }
  };

  const fetchSavedItineraries = async () => {
    try {
      if (!token) {
        console.error('No token available for API call');
        setLoading(false);
        return;
      }
      
      console.log('Fetching all itineraries...');
      const data = await itineraryApi.getAllItineraries();
      console.log('Received itineraries data:', data);
      console.log('Number of itineraries:', data.itineraries?.length || 0);
      setItineraries(data.itineraries);
    } catch (error) {
      console.error('Error fetching saved itineraries:', error);
    } finally {
      setLoading(false);
    }
  };


  // Fetch saved itineraries on component mount
  useEffect(() => {
    if (token) {
      // Add a small delay to ensure API client is updated with the token
      const timeoutId = setTimeout(() => {
        fetchSavedItineraries();
      }, 100);
      
      return () => clearTimeout(timeoutId);
    } else {
      setLoading(false);
    }
  }, [token]);

  if (isLoading || loading) {
    return (
      <ProtectedRoute>
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-lg text-gray-600 font-medium">Loading your results...</p>
          </div>
        </div>
      </ProtectedRoute>
    );
  }

  return (
    <ProtectedRoute>
      <main className="min-h-screen bg-[#f6f5fa] relative">
        {/* Main background container */}
        <div className="absolute inset-4 rounded-[30px] bg-[rgba(216,223,233,0.25)]" />

        {/* Header Section */}
        <header className="relative z-10 flex items-center justify-between p-6">
          {/* Sea turtle logo */}
          <button
            onClick={() => router.push('/landing')}
            className="w-12 h-12 bg-transparent border-none cursor-pointer hover:opacity-80 transition-opacity"
            aria-label="Go to Landing Page"
          >
            <Image
              className="w-full h-full"
              alt="Sea turtle"
              src="https://c.animaapp.com/7Y4W5hAe/img/sea-turtle-02-2.svg"
              width={48}
              height={48}
            />
          </button>

          {/* Trip info bar */}
          <TripInfoBar tripInfoData={tripInfoData} />

          {/* Settings icon */}
          <button
            onClick={() => router.push('/profile')}
            className="w-10 h-10 bg-transparent border-none cursor-pointer hover:opacity-80 transition-opacity"
            aria-label="Go to Profile"
          >
            <Image
              className="w-full h-full"
              alt="Settings"
              src="https://c.animaapp.com/7Y4W5hAe/img/group-6@2x.png"
              width={40}
              height={40}
            />
          </button>
        </header>

        {/* Main Content */}
        <div className="relative z-10 px-6 pb-8">
          <div className="max-w-7xl mx-auto space-y-8">
            {/* Navigation controls */}
            <NavigationControls
              currentIndex={currentIndex}
              totalItineraries={itineraries.length}
              onPrevious={handlePreviousItinerary}
              onNext={handleNextItinerary}
            />

            {/* Congratulations section */}
            <CongratulationsSection 
              itinerary={currentItinerary}
            />

            {/* Itinerary section */}
            <ItinerarySection itinerary={currentItinerary} />

            {/* Action buttons */}
            <ActionButtons 
              onBackToGlobe={handleBackToGlobe}
              onNewSearch={handleNewSearch}
            />
          </div>
        </div>
      </main>
    </ProtectedRoute>
  );
}