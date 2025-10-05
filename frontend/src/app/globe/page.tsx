'use client';

import React, { useState, useEffect, useRef } from 'react';
import dynamic from 'next/dynamic';
import { useRouter } from 'next/navigation';
import CountrySearch from '@/components/CountrySearch';
import TravelModal from '@/components/TravelModal';
import CountryBubble from '@/components/CountryBubble';

// Dynamically import Globe to avoid SSR issues
const Globe = dynamic(() => import('@/components/Globe'), { ssr: false });

interface Country {
  properties: {
    ADMIN?: string;
    NAME?: string;
    ISO_A2?: string;
  };
  geometry: any;
}

export default function GlobePage() {
  const [countriesData, setCountriesData] = useState<any>(null);
  const [countries, setCountries] = useState<Country[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedCountry, setSelectedCountry] = useState<Country | null>(null);
  const [showTravelModal, setShowTravelModal] = useState(false);
  const [showConfirmationModal, setShowConfirmationModal] = useState(false);
  const [isSearchSelection, setIsSearchSelection] = useState(false);
  const [isFadingOut, setIsFadingOut] = useState(false);
  const globeRef = useRef<any>(null);
  const router = useRouter();

  // Load countries data
  useEffect(() => {
    const loadCountriesData = async () => {
      try {
        const response = await fetch('/ne_110m_admin_0_countries.geojson');
        const data = await response.json();
        setCountriesData(data);
        
        // Process countries for the search component
        if (data.features) {
          const countryList: Country[] = data.features.filter((d: any) => d.properties.ISO_A2 !== 'AQ');
          setCountries(countryList);
        }
        setIsLoading(false);
      } catch (error) {
        console.error('Error loading countries data:', error);
        setIsLoading(false);
      }
    };

    loadCountriesData();
  }, []);

  const handleCountrySelect = (country: Country) => {
    if (globeRef.current && country) {
      console.log('handleCountrySelect called - setting isSearchSelection to true');
      // This is a search-based selection, so we need confirmation
      setIsSearchSelection(true);
      setSelectedCountry(country);
      globeRef.current.selectCountry(country, true);
      console.log('Search selecting and zooming to country:', country.properties.ADMIN || country.properties.NAME);
      
      // Show confirmation modal immediately
      console.log('Showing confirmation modal');
      setShowConfirmationModal(true);
    }
  };

  const handleCountrySelected = (country: Country) => {
    console.log('handleCountrySelected called, isSearchSelection:', isSearchSelection);
    
    // Only proceed if this is NOT a search selection
    if (isSearchSelection) {
      console.log('Ignoring handleCountrySelected for search selection');
      return;
    }
    
    // This is a direct click on the globe, show bubble for confirmation
    setIsSearchSelection(false);
    setSelectedCountry(country);
    console.log('Direct click on country:', country.properties.ADMIN || country.properties.NAME);
    
    // Show bubble for direct clicks immediately
    console.log('Showing bubble for direct click');
    setShowConfirmationModal(true);
  };

  const storeSelectedCountry = (country: Country) => {
    // Store the selected country in localStorage for backend communication
    const countryData = {
      name: country.properties.ADMIN || country.properties.NAME,
      isoCode: country.properties.ISO_A2,
      selectedAt: new Date().toISOString()
    };
    localStorage.setItem('selectedCountry', JSON.stringify(countryData));
    console.log('Stored country for backend:', countryData);
  };

  const transitionToWhitePage = () => {
    if (globeRef.current && selectedCountry) {
      // Use the enhanced zoom method for smoother transition
      globeRef.current.enhancedZoomToCountry(selectedCountry);
      
      // Start fade-out effect while zoom is still happening
      setTimeout(() => {
        setIsFadingOut(true);
      }, 800); // Start fade while zoom is still in progress
      
      // Navigate after zoom and fade complete
      setTimeout(() => {
        router.push('/chat');
      }, 2000); // Match the zoom duration
    } else {
      // Fallback if no globe or country
      router.push('/chat');
    }
  };

  const handleConfirmCountry = () => {
    if (selectedCountry) {
      setShowConfirmationModal(false);
      storeSelectedCountry(selectedCountry);
      transitionToWhitePage();
    }
  };

  const handleCancelCountry = () => {
    console.log('Cancelling country selection - resetting globe appearance');
    setShowConfirmationModal(false);
    setSelectedCountry(null);
    setIsSearchSelection(false);
    // Reset globe view, appearance, and resume rotation
    if (globeRef.current) {
      globeRef.current.resetView();
      globeRef.current.resetAppearance();
      globeRef.current.resumeRotation();
    }
  };

  const handleTravel = () => {
    if (selectedCountry) {
      // Add fade effect before navigation
      setShowTravelModal(false);
      setTimeout(() => {
        router.push('/chat');
      }, 300);
    }
  };

  const handleCloseModal = () => {
    setShowTravelModal(false);
    setSelectedCountry(null);
  };

  if (isLoading) {
    return (
      <div className="w-full h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-lg text-gray-600 font-medium">Loading the world...</p>
        </div>
      </div>
    );
  }

  console.log('Rendering page with:', { countriesData: !!countriesData, countries: countries.length });

  return (
    <div className="relative w-full h-screen overflow-hidden bg-white">
      {/* Background Globe */}
      <div className={`absolute inset-0 z-0 transition-opacity duration-600 ease-in-out ${isFadingOut ? 'opacity-0' : 'opacity-100'}`}>
        <Globe 
          ref={globeRef} 
          countriesData={countriesData} 
          onCountrySelected={handleCountrySelected}
          isSearchSelection={isSearchSelection}
        />
      </div>

      {/* Top Left Search Bar and Back Button */}
      <div className={`absolute top-5 left-5 z-10 transition-opacity duration-600 ease-in-out ${isFadingOut ? 'opacity-0' : 'opacity-100'}`}>
        <div className="flex gap-3">
          {/* Back Button */}
          <button
            onClick={() => router.push('/landing')}
            className="bg-transparent hover:bg-black/10 text-gray-800 font-semibold py-4 px-8 transition-all duration-300 flex items-center gap-3"
          >
            <img 
              src="Group 4.svg"
              alt="Back"
              className="w-8 h-8"
            />
          </button>
          
          {/* Search Bar */}
          <CountrySearch
            countries={countries}
            onCountrySelect={handleCountrySelect}
          />
        </div>
      </div>

      {/* Profile Button - Top Right */}
      <div className={`absolute top-5 right-5 z-10 transition-opacity duration-600 ease-in-out ${isFadingOut ? 'opacity-0' : 'opacity-100'}`}>
        <button
          onClick={() => router.push('/profile')}
          className="bg-white/90 hover:bg-white text-gray-800 font-semibold py-3 px-6 rounded-full shadow-lg border border-gray-200 transition-all duration-300 hover:shadow-xl flex items-center gap-2"
        >
          <svg 
            className="w-5 h-5" 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              strokeWidth={2} 
              d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" 
            />
          </svg>
          Profile
        </button>
      </div>

      {/* Country Bubble */}
      <div className={`transition-opacity duration-600 ease-in-out ${isFadingOut ? 'opacity-0' : 'opacity-100'}`}>
        <CountryBubble
          country={selectedCountry!}
          onConfirm={handleConfirmCountry}
          onCancel={handleCancelCountry}
          isVisible={showConfirmationModal}
        />
      </div>


    </div>
  );
}
