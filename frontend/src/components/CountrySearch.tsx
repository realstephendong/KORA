'use client';

import React, { useState, useEffect, useRef } from 'react';

interface Country {
  properties: {
    ADMIN?: string;
    NAME?: string;
    ISO_A2?: string;
  };
  geometry: any;
}

interface CountrySearchProps {
  countries: Country[];
  onCountrySelect: (country: Country) => void;
}

const CountrySearch: React.FC<CountrySearchProps> = ({ 
  countries, 
  onCountrySelect
}) => {
  const [query, setQuery] = useState('');
  const [showResults, setShowResults] = useState(false);
  const [filteredCountries, setFilteredCountries] = useState<Country[]>([]);
  const searchRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (query.length < 2) {
      setFilteredCountries([]);
      setShowResults(false);
      return;
    }

    const matches = countries.filter(country => {
      const name = (country.properties.ADMIN || country.properties.NAME || '').toLowerCase();
      return name.includes(query.toLowerCase());
    }).slice(0, 10);

    setFilteredCountries(matches);
    setShowResults(matches.length > 0);
  }, [query, countries]);

  const handleCountrySelect = (country: Country) => {
    onCountrySelect(country);
    setQuery('');
    setShowResults(false);
  };

  const handleFeelingLucky = () => {
    if (countries.length > 0) {
      const randomIndex = Math.floor(Math.random() * countries.length);
      const randomCountry = countries[randomIndex];
      onCountrySelect(randomCountry);
      setQuery('');
      setShowResults(false);
    }
  };

  // Hide results when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setShowResults(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div ref={searchRef} className="relative w-96">
      <div className="flex items-center bg-white/95 rounded-full shadow-lg transition-all duration-300 hover:shadow-xl hover:scale-105">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => setShowResults(filteredCountries.length > 0)}
          placeholder="Search for a country..."
          className="flex-1 px-4 py-4 text-base font-medium outline-none bg-transparent rounded-l-full"
        />
        
        <button
          onClick={handleFeelingLucky}
          className="px-4 py-4 bg-gray-100 text-gray-600 rounded-r-full font-medium transition-all duration-200 hover:bg-gray-200 hover:text-gray-800 border-l border-gray-200"
        >
          🎲
        </button>
      </div>
      
      {showResults && (
        <div className="absolute top-full left-0 right-0 mt-2 bg-white/98 rounded-xl shadow-2xl max-h-96 overflow-y-auto z-50 border border-gray-100">
          {filteredCountries.map((country, index) => (
            <div
              key={index}
              onClick={() => handleCountrySelect(country)}
              className="px-4 py-4 cursor-pointer border-b border-gray-100 last:border-b-0 hover:bg-slate-100 transition-colors duration-150 hover:scale-105"
            >
              <div className="font-medium text-gray-900">
                {country.properties.ADMIN || country.properties.NAME}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default CountrySearch;
