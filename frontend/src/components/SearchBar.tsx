'use client';

import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';

interface Country {
  properties: {
    ADMIN?: string;
    NAME?: string;
    ISO_A2?: string;
  };
  geometry: any;
}

interface SearchBarProps {
  countries: Country[];
  onCountrySelect: (country: Country) => void;
}

export const SearchBar: React.FC<SearchBarProps> = ({ 
  countries, 
  onCountrySelect
}) => {
  const [searchValue, setSearchValue] = useState("");
  const [showResults, setShowResults] = useState(false);
  const [filteredCountries, setFilteredCountries] = useState<Country[]>([]);
  const searchRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (searchValue.length < 2) {
      setFilteredCountries([]);
      setShowResults(false);
      return;
    }

    const matches = countries.filter(country => {
      const name = (country.properties.ADMIN || country.properties.NAME || '').toLowerCase();
      return name.includes(searchValue.toLowerCase());
    }).slice(0, 10);

    setFilteredCountries(matches);
    setShowResults(matches.length > 0);
  }, [searchValue, countries]);

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchValue(e.target.value);
  };

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log("Search submitted:", searchValue);
    // If there's a search result, select the first one
    if (filteredCountries.length > 0) {
      handleCountrySelect(filteredCountries[0]);
    }
  };

  const handleCountrySelect = (country: Country) => {
    onCountrySelect(country);
    setSearchValue('');
    setShowResults(false);
  };

  const handleLuckyClick = () => {
    console.log("I'm feeling lucky clicked");
    if (countries.length > 0) {
      const randomIndex = Math.floor(Math.random() * countries.length);
      const randomCountry = countries[randomIndex];
      onCountrySelect(randomCountry);
      setSearchValue('');
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
    <div ref={searchRef} className="relative">
      <form
        onSubmit={handleSearchSubmit}
        className="relative w-[400px] h-[60px] flex bg-white rounded-[30px] overflow-hidden shadow-lg"
        role="search"
        aria-label="Country search"
      >
        <label
          htmlFor="country-search"
          className="mt-[18px] w-[24px] h-[24px] ml-[20px] flex-shrink-0 flex items-center justify-center group/search-icon"
        >
          <motion.img
            className="w-[20px] h-[20px] object-contain"
            alt="Search"
            src="https://c.animaapp.com/M8phbEWm/img/search@2x.png"
            aria-hidden="true"
            animate={{
              y: [0, -2, 0],
              rotate: [0, 5, 0]
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: "easeInOut"
            }}
            whileHover={{
              scale: 1.1,
              transition: { duration: 0.3 }
            }}
            whileFocus={{
              scale: 1.1,
              transition: { duration: 0.3 }
            }}
          />
        </label>

        <input
          id="country-search"
          type="search"
          value={searchValue}
          onChange={handleSearchChange}
          onFocus={() => setShowResults(filteredCountries.length > 0)}
          placeholder="Explore a country"
          className="mt-[18px] flex-1 h-[24px] ml-[15px] mr-[15px] font-medium text-black text-lg placeholder:text-gray-500 focus:outline-none peer"
          aria-label="Search for a country"
        />

        <div className="relative group">
          <button
            type="button"
            onClick={handleLuckyClick}
            className="flex w-[60px] h-[60px] items-center justify-center bg-[#231f20] rounded-[30px] cursor-pointer hover:opacity-90 transition-all duration-300 flex-shrink-0"
            aria-label="I'm feeling lucky"
          >
            <img
              className="w-[32px] h-[32px] object-contain transition-transform duration-300"
              alt="Sea turtle"
              src="https://c.animaapp.com/M8phbEWm/img/sea-turtle-02-2.svg"
              aria-hidden="true"
            />
          </button>
          
          {/* Tooltip */}
          <div className="absolute bottom-full right-0 mb-2 px-3 py-2 bg-gray-900 text-white text-sm rounded-lg opacity-0 group-hover:opacity-100 transform translate-y-2 group-hover:translate-y-0 transition-all duration-300 pointer-events-none whitespace-nowrap z-50">
            I'm feeling lucky!
            <div className="absolute top-full right-4 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-900"></div>
          </div>
        </div>
      </form>

      {/* Search Results Dropdown */}
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

export default SearchBar;
