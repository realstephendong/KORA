'use client';

import React from 'react';

interface TravelModalProps {
  country: {
    properties: {
      ADMIN?: string;
      NAME?: string;
      ISO_A2?: string;
    };
  };
  onTravel: () => void;
  onClose: () => void;
  isVisible: boolean;
}

const TravelModal: React.FC<TravelModalProps> = ({ 
  country, 
  onTravel, 
  onClose, 
  isVisible 
}) => {
  if (!isVisible) return null;

  const countryName = country.properties.ADMIN || country.properties.NAME || 'Unknown';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/20"
        onClick={onClose}
      />
      
      {/* Modal */}
      <div className="relative bg-white rounded-2xl shadow-2xl p-8 mx-4 max-w-sm w-full transform transition-all duration-300 scale-100">
        {/* Pinpoint Icon */}
        <div className="flex justify-center mb-6">
          <div className="w-16 h-16 bg-gradient-to-br from-orange-400 to-orange-500 rounded-full flex items-center justify-center shadow-lg">
            <svg 
              className="w-8 h-8 text-white" 
              fill="currentColor" 
              viewBox="0 0 20 20"
            >
              <path 
                fillRule="evenodd" 
                d="M5.05 4.05a7 7 0 119.9 9.9L10 18l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" 
                clipRule="evenodd" 
              />
            </svg>
          </div>
        </div>

        {/* Content */}
        <div className="text-center mb-8">
          <h3 className="text-2xl font-bold text-gray-900 mb-2">
            {countryName}
          </h3>
          <p className="text-gray-600 text-lg">
            Ready to explore this destination?
          </p>
        </div>

        {/* Buttons */}
        <div className="flex gap-3">
          <button
            onClick={onClose}
            className="flex-1 px-6 py-3 bg-gray-100 text-gray-700 rounded-xl font-semibold hover:bg-gray-200 transition-colors duration-200"
          >
            Cancel
          </button>
          <button
            onClick={onTravel}
            className="flex-1 px-6 py-3 bg-gradient-to-r from-orange-400 to-orange-500 text-white rounded-xl font-semibold hover:from-orange-500 hover:to-orange-600 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105"
          >
            Travel Here
          </button>
        </div>
      </div>
    </div>
  );
};

export default TravelModal;
