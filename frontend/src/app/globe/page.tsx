'use client';

import React, { useState, useEffect, useRef } from 'react';
import dynamic from 'next/dynamic';
import { useRouter } from 'next/navigation';
import SearchBar from '@/components/SearchBar';
import TravelModal from '@/components/TravelModal';
import CountryBubble from '@/components/CountryBubble';
import LoadingPage from '@/components/LoadingPage';

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
  const [isNavigatingBack, setIsNavigatingBack] = useState(false);
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
      <LoadingPage message="Loading the world..." />
    );
  }

  if (isNavigatingBack) {
    return (
      <LoadingPage message="Returning to home..." />
    );
  }

  console.log('Rendering page with:', { countriesData: !!countriesData, countries: countries.length });

  return (
    <div className="globe-page relative w-full h-screen overflow-hidden bg-white rounded-none">
      {/* Background Globe */}
      <div className={`absolute inset-0 z-0 transition-opacity duration-600 ease-in-out ${isFadingOut ? 'opacity-0' : 'opacity-100'}`}>
        <Globe 
          ref={globeRef} 
          countriesData={countriesData} 
          onCountrySelected={handleCountrySelected}
          isSearchSelection={isSearchSelection}
        />
      </div>

      {/* Back Button */}
      <div className={`absolute top-5 left-5 z-10 transition-opacity duration-600 ease-in-out ${isFadingOut ? 'opacity-0' : 'opacity-100'}`}>
        <button
          onClick={() => {
            setIsNavigatingBack(true);
            setTimeout(() => {
              router.push('/landing');
            }, 1500);
          }}
          className="w-14 h-14 rounded-full hover:scale-105 transition-all duration-200 flex items-center justify-center group overflow-hidden"
          aria-label="Go back"
        >
          <svg 
            width="60" 
            height="60" 
            viewBox="0 0 61 61" 
            fill="none" 
            xmlns="http://www.w3.org/2000/svg"
            className="group-hover:opacity-90 transition-opacity duration-200"
            preserveAspectRatio="xMidYMid meet"
          >
            <circle cx="30.5" cy="30.5" r="30.5" fill="#212121"/>
            <mask id="mask0_199_11" style={{maskType:"alpha"}} maskUnits="userSpaceOnUse" x="12" y="12" width="37" height="37">
              <rect x="12.2002" y="12.2" width="36.6" height="36.6" fill="#D9D9D9"/>
            </mask>
            <g mask="url(#mask0_199_11)">
              <path d="M30.4996 44.9875C28.7009 44.9875 27.0156 44.6473 25.4439 43.9669C23.8718 43.2865 22.5012 42.3617 21.3321 41.1925C20.1629 40.0234 19.2381 38.6528 18.5577 37.0808C17.8773 35.509 17.5371 33.8237 17.5371 32.025H19.8246C19.8246 34.9988 20.8603 37.5214 22.9318 39.5928C25.0033 41.6643 27.5259 42.7 30.4996 42.7C33.4734 42.7 35.996 41.6643 38.0674 39.5928C40.1389 37.5214 41.1746 34.9988 41.1746 32.025C41.1746 29.0513 40.1389 26.5287 38.0674 24.4572C35.996 22.3857 33.4734 21.35 30.4996 21.35H30.0947L32.5172 23.7725L30.9102 25.4263L25.6901 20.1918L30.9396 14.9568L32.5465 16.6107L30.0947 19.0625H30.4996C32.2983 19.0625 33.9836 19.4027 35.5554 20.0831C37.1274 20.7635 38.498 21.6883 39.6671 22.8575C40.8363 24.0266 41.7611 25.3972 42.4415 26.9693C43.1219 28.541 43.4621 30.2263 43.4621 32.025C43.4621 33.8237 43.1219 35.509 42.4415 37.0808C41.7611 38.6528 40.8363 40.0234 39.6671 41.1925C38.498 42.3617 37.1274 43.2865 35.5554 43.9669C33.9836 44.6473 32.2983 44.9875 30.4996 44.9875Z" fill="#F6F5FA"/>
            </g>
          </svg>
        </button>
      </div>

      {/* Top Left Search Bar */}
      <div className={`absolute top-5 left-24 z-10 transition-opacity duration-600 ease-in-out ${isFadingOut ? 'opacity-0' : 'opacity-100'}`}>
        <SearchBar
          countries={countries}
          onCountrySelect={handleCountrySelect}
        />
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
