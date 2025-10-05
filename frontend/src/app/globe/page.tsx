'use client';

import React, { useState, useEffect, useRef } from 'react';
import dynamic from 'next/dynamic';
import { useRouter } from 'next/navigation';
import CountrySearch from '@/components/CountrySearch';
import TravelModal from '@/components/TravelModal';

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
      // Zoom to and pop out the selected country
      globeRef.current.selectCountry(country);
      console.log('Selecting and zooming to country:', country.properties.ADMIN || country.properties.NAME);
    }
  };

  const handleCountrySelected = (country: Country) => {
    setSelectedCountry(country);
    // Don't show modal, just show landmark indicator on globe
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
      <div className="absolute inset-0 z-0">
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

      {/* Travel Modal - Removed, using landmark indicator instead */}

    </div>
  );
}
