'use client';

import React, { useState, useEffect, useRef } from 'react';
import dynamic from 'next/dynamic';
import { useRouter } from 'next/navigation';
import CountrySearch from '@/components/CountrySearch';
import TravelModal from '@/components/TravelModal';
import CountryConfirmationModal from '@/components/CountryConfirmationModal';

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
  const [isTransitioning, setIsTransitioning] = useState(false);
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
      // This is a search-based selection, so we need confirmation
      setIsSearchSelection(true);
      setSelectedCountry(country);
      globeRef.current.selectCountry(country);
      console.log('Search selecting and zooming to country:', country.properties.ADMIN || country.properties.NAME);
      
      // Show confirmation modal after zoom completes
      setTimeout(() => {
        setShowConfirmationModal(true);
      }, 2500);
    }
  };

  const handleCountrySelected = (country: Country) => {
    // This is a direct click on the globe, so no confirmation needed
    setIsSearchSelection(false);
    setSelectedCountry(country);
    console.log('Direct click on country:', country.properties.ADMIN || country.properties.NAME);
    
    // Store the country and transition immediately
    storeSelectedCountry(country);
    transitionToWhitePage();
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
    setIsTransitioning(true);
    
    // Add a smooth transition effect
    setTimeout(() => {
      router.push('/chat');
    }, 1000);
  };

  const handleConfirmCountry = () => {
    if (selectedCountry) {
      setShowConfirmationModal(false);
      storeSelectedCountry(selectedCountry);
      transitionToWhitePage();
    }
  };

  const handleCancelCountry = () => {
    setShowConfirmationModal(false);
    setSelectedCountry(null);
    setIsSearchSelection(false);
    // Reset globe view
    if (globeRef.current) {
      globeRef.current.pointOfView({ altitude: 1.8 }, 2000);
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
      <div className={`absolute inset-0 z-0 transition-all duration-1000 ${isTransitioning ? 'opacity-0 scale-110' : 'opacity-100 scale-100'}`}>
        <Globe 
          ref={globeRef} 
          countriesData={countriesData} 
          onCountrySelected={handleCountrySelected}
        />
      </div>

      {/* Top Left Search Bar */}
      <div className="absolute top-5 left-5 z-10">
        <CountrySearch
          countries={countries}
          onCountrySelect={handleCountrySelect}
        />
      </div>

      {/* Country Confirmation Modal */}
      <CountryConfirmationModal
        country={selectedCountry!}
        onConfirm={handleConfirmCountry}
        onCancel={handleCancelCountry}
        isVisible={showConfirmationModal}
      />

      {/* Transition Overlay */}
      {isTransitioning && (
        <div className="fixed inset-0 z-50 bg-white flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-xl text-gray-600 font-medium">Preparing your journey...</p>
          </div>
        </div>
      )}

    </div>
  );
}
