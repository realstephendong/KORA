'use client';

import React from 'react';

interface CountryBubbleProps {
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

const CountryBubble: React.FC<CountryBubbleProps> = ({ 
  country, 
  onConfirm, 
  onCancel, 
  isVisible 
}) => {
  if (!isVisible) return null;

  const countryName = country.properties.ADMIN || country.properties.NAME || 'Unknown';

  return (
    <div className="fixed inset-0 z-50 pointer-events-none">
      {/* Floating Bubble positioned in center-right */}
      <div className="absolute top-1/2 right-8 transform -translate-y-1/2 pointer-events-auto">
        <div className="relative">
          {/* Main Bubble */}
          <div className="bg-white rounded-3xl shadow-2xl p-6 max-w-sm w-80 transform transition-all duration-700 animate-in slide-in-from-right-8 fade-in-0 scale-100" style={{boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25), 0 0 0 1px rgba(255, 107, 53, 0.1)'}}>
            {/* Pulsing Ring Animation - matching globe colors */}
            <div className="absolute -inset-2 rounded-3xl opacity-20 animate-ping" style={{background: '#F2F37F'}}></div>
            <div className="absolute -inset-1 rounded-3xl opacity-30 animate-pulse" style={{background: '#ff6b35'}}></div>
            
            {/* Bubble Content */}
            <div className="relative z-10">
              {/* Country Header with Flag */}
              <div className="flex items-center mb-4">
                <div className="w-10 h-10 rounded-full flex items-center justify-center shadow-lg mr-3" style={{background: 'linear-gradient(135deg, #ff6b35, #F2F37F)'}}>
                  <span className="text-lg">🌍</span>
                </div>
                <div>
                  <h3 className="text-xl font-bold text-gray-900" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'}}>
                    {countryName}
                  </h3>
                  <p className="text-sm text-gray-500" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'}}>Ready to explore?</p>
                </div>
              </div>

              {/* Floating Particles - matching globe colors */}
              <div className="absolute -top-2 -right-2 w-3 h-3 rounded-full animate-bounce" style={{background: '#F2F37F'}}></div>
              <div className="absolute -bottom-1 -left-1 w-2 h-2 rounded-full animate-bounce" style={{background: '#ff6b35', animationDelay: '0.5s'}}></div>
              <div className="absolute top-2 -left-3 w-2 h-2 rounded-full animate-bounce" style={{background: '#CFDECB', animationDelay: '1s'}}></div>

              {/* Content */}
              <div className="mb-4">
                <p className="text-gray-600 text-sm leading-relaxed" style={{fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'}}>
                  Is this your destination? We'll help you plan an amazing journey here.
                </p>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-2">
                <button
                  onClick={onCancel}
                  className="flex-1 px-3 py-2 bg-gray-100 text-gray-700 rounded-xl text-sm font-medium hover:bg-gray-200 transition-all duration-200"
                  style={{fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'}}
                >
                  Not Quite
                </button>
                <button
                  onClick={onConfirm}
                  className="flex-1 px-3 py-2 text-white rounded-xl text-sm font-medium transition-all duration-200 shadow-lg hover:shadow-xl"
                  style={{background: 'linear-gradient(135deg, #ff6b35, #F2F37F)', fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'}}
                >
                  Let's Go! ✈️
                </button>
              </div>
            </div>
          </div>

          {/* Floating Tail/Connector */}
          <div className="absolute -left-4 top-1/2 transform -translate-y-1/2">
            <div className="w-8 h-8 bg-white rounded-full shadow-lg flex items-center justify-center">
              <div className="w-3 h-3 rounded-full animate-pulse" style={{background: '#ff6b35'}}></div>
            </div>
          </div>

          {/* Animated Dots Trail */}
          <div className="absolute -left-8 top-1/2 transform -translate-y-1/2">
            <div className="flex space-x-1">
              <div className="w-1 h-1 rounded-full animate-bounce" style={{background: '#F2F37F'}}></div>
              <div className="w-1 h-1 rounded-full animate-bounce" style={{background: '#ff6b35', animationDelay: '0.2s'}}></div>
              <div className="w-1 h-1 rounded-full animate-bounce" style={{background: '#CFDECB', animationDelay: '0.4s'}}></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CountryBubble;
