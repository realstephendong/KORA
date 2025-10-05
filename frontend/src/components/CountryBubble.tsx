'use client';

import React from 'react';
import { motion } from 'framer-motion';

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
          {/* Main Bubble - New Design with Framer Motion */}
          <motion.div 
            className="relative w-[387px] min-h-[216px] max-h-[320px] rounded-[50px] overflow-hidden border border-gray-200 shadow-lg backdrop-blur-sm flex flex-col"
            style={{
              background: 'linear-gradient(330deg,rgba(216,223,233,0)_0%,rgba(216,223,233,1)_100%),linear-gradient(0deg,rgba(246,245,250,1)_0%,rgba(246,245,250,1)_100%)'
            }}
            animate={{
              y: [-10, -20, -15, -25, -12, -18, -22, -8, -16, -10],
              x: [-8, 6, -4, 10, -6, 4, -10, 8, -3, 0],
              rotate: [0.5, -0.4, 0.6, -0.5, 0.2, -0.6, 0.4, -0.2, 0.5, 0]
            }}
            transition={{
              duration: 12,
              repeat: Infinity,
              ease: "easeInOut"
            }}
          >
            {/* Content Container */}
            <div className="flex-1 flex flex-col justify-center px-[43px] pt-6">
              {/* "you're going to" text */}
              <div className="font-medium text-black text-xl tracking-[0] leading-[normal]" style={{fontFamily: 'Onest, Helvetica, sans-serif'}}>
                you're going to
              </div>

              {/* Country name */}
              <div className="font-black text-black text-[clamp(28px,4.5vw,50px)] tracking-[0] leading-tight break-words" style={{fontFamily: 'Onest, Helvetica, sans-serif'}}>
                {countryName}
              </div>
            </div>

            {/* Action Buttons Container */}
            <div className="flex justify-start items-center gap-6 px-8 pb-8">
              <button
                onClick={onCancel}
                className="px-6 py-3 border border-[#d8dfe9] bg-[#eeefa4] text-black rounded-full font-bold hover:bg-[#e6e794] hover:shadow-lg hover:scale-105 transition-all duration-200 text-sm"
                style={{fontFamily: 'Onest, Helvetica, sans-serif'}}
              >
                Not quite
              </button>
              
              <button
                onClick={onConfirm}
                className="px-6 py-3 bg-black text-white rounded-full font-bold hover:bg-gray-800 hover:shadow-lg hover:scale-105 transition-all duration-200 text-sm"
                style={{fontFamily: 'Onest, Helvetica, sans-serif'}}
              >
                Yes, proceed!
              </button>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default CountryBubble;
