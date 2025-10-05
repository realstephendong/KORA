'use client';

import React from 'react';

interface CountryConfirmationModalProps {
  country: {
    properties: {
      ADMIN?: string;
      NAME?: string;
      ISO_A2?: string;
    };
  };
  onConfirm: () => void;
  onCancel: () => void;
  isVisible: boolean;
}

const CountryConfirmationModal: React.FC<CountryConfirmationModalProps> = ({ 
  country, 
  onConfirm, 
  onCancel, 
  isVisible 
}) => {
  if (!isVisible) return null;

  const countryName = country.properties.ADMIN || country.properties.NAME || 'Unknown';

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-end p-6">
      {/* Floating Card from Right Side */}
      <div className="relative bg-white rounded-2xl shadow-2xl p-6 max-w-sm w-full transform transition-all duration-700 translate-x-0 animate-in slide-in-from-right-8">
        {/* Close Button */}
        <button
          onClick={onCancel}
          className="absolute top-4 right-4 w-8 h-8 bg-gray-100 hover:bg-gray-200 rounded-full flex items-center justify-center transition-colors duration-200"
        >
          <svg className="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
        {/* Country Flag/Icon Header */}
        <div className="flex items-center mb-6">
          <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center shadow-lg mr-4">
            <span className="text-2xl">🌍</span>
          </div>
          <div>
            <h3 className="text-2xl font-bold text-gray-900">
              {countryName}
            </h3>
            <p className="text-sm text-gray-500">Ready to explore?</p>
          </div>
        </div>

        {/* Content */}
        <div className="mb-6">
          <p className="text-gray-600 text-base leading-relaxed">
            Is this the country you'd like to explore? We'll help you plan an amazing journey here.
          </p>
        </div>

        {/* Buttons */}
        <div className="flex gap-3">
          <button
            onClick={onCancel}
            className="flex-1 px-4 py-3 bg-gray-100 text-gray-700 rounded-xl font-medium hover:bg-gray-200 transition-all duration-200"
          >
            Not Quite
          </button>
          <button
            onClick={onConfirm}
            className="flex-1 px-4 py-3 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-xl font-medium hover:from-blue-600 hover:to-blue-700 transition-all duration-200 shadow-lg hover:shadow-xl"
          >
            Let's Go! ✈️
          </button>
        </div>
      </div>
    </div>
  );
};

export default CountryConfirmationModal;
