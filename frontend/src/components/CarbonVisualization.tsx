'use client';

import { useState, useEffect } from 'react';

interface CarbonVisualizationProps {
  carbonEmissions: number;
  distance: number;
  cityCount: number;
  className?: string;
  animated?: boolean;
}

export default function CarbonVisualization({ 
  carbonEmissions, 
  distance, 
  cityCount, 
  className = '',
  animated = true 
}: CarbonVisualizationProps) {
  const [animatedEmissions, setAnimatedEmissions] = useState(0);
  const [animatedDistance, setAnimatedDistance] = useState(0);

  useEffect(() => {
    if (animated) {
      // Animate the numbers
      const duration = 2000; // 2 seconds
      const steps = 60;
      const stepDuration = duration / steps;
      
      let currentStep = 0;
      const interval = setInterval(() => {
        currentStep++;
        const progress = currentStep / steps;
        
        // Easing function for smooth animation
        const easeOutCubic = 1 - Math.pow(1 - progress, 3);
        
        setAnimatedEmissions(carbonEmissions * easeOutCubic);
        setAnimatedDistance(distance * easeOutCubic);
        
        if (currentStep >= steps) {
          clearInterval(interval);
          setAnimatedEmissions(carbonEmissions);
          setAnimatedDistance(distance);
        }
      }, stepDuration);

      return () => clearInterval(interval);
    } else {
      setAnimatedEmissions(carbonEmissions);
      setAnimatedDistance(distance);
    }
  }, [carbonEmissions, distance, animated]);

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('en-US', {
      minimumFractionDigits: 1,
      maximumFractionDigits: 1
    }).format(num);
  };

  const getCarbonIntensity = () => {
    if (animatedDistance === 0) return 0;
    return animatedEmissions / animatedDistance;
  };

  const getEmissionsPerCity = () => {
    if (cityCount === 0) return 0;
    return animatedEmissions / cityCount;
  };

  const getDistancePerCity = () => {
    if (cityCount === 0) return 0;
    return animatedDistance / cityCount;
  };

  // Calculate progress bars (0-100%)
  const emissionsProgress = Math.min((animatedEmissions / 1000) * 100, 100);
  const distanceProgress = Math.min((animatedDistance / 10000) * 100, 100);

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Main Stats */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-6 border border-green-200">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-lg font-semibold text-green-800">Carbon Emissions</h3>
            <div className="w-8 h-8 bg-green-200 rounded-full flex items-center justify-center">
              <span className="text-green-600 text-sm">🌱</span>
            </div>
          </div>
          <div className="text-3xl font-bold text-green-900 mb-2">
            {formatNumber(animatedEmissions)} kg
          </div>
          <div className="w-full bg-green-200 rounded-full h-3 mb-2">
            <div 
              className="bg-gradient-to-r from-green-400 to-green-600 h-3 rounded-full transition-all duration-1000 ease-out"
              style={{ width: `${emissionsProgress}%` }}
            ></div>
          </div>
          <div className="text-sm text-green-700">
            {formatNumber(getEmissionsPerCity())} kg per city
          </div>
        </div>

        <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-6 border border-blue-200">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-lg font-semibold text-blue-800">Total Distance</h3>
            <div className="w-8 h-8 bg-blue-200 rounded-full flex items-center justify-center">
              <span className="text-blue-600 text-sm">🗺️</span>
            </div>
          </div>
          <div className="text-3xl font-bold text-blue-900 mb-2">
            {formatNumber(animatedDistance)} km
          </div>
          <div className="w-full bg-blue-200 rounded-full h-3 mb-2">
            <div 
              className="bg-gradient-to-r from-blue-400 to-blue-600 h-3 rounded-full transition-all duration-1000 ease-out"
              style={{ width: `${distanceProgress}%` }}
            ></div>
          </div>
          <div className="text-sm text-blue-700">
            {formatNumber(getDistancePerCity())} km per city
          </div>
        </div>
      </div>

      {/* Carbon Intensity */}
      <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-6 border border-purple-200">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-lg font-semibold text-purple-800">Carbon Intensity</h3>
          <div className="w-8 h-8 bg-purple-200 rounded-full flex items-center justify-center">
            <span className="text-purple-600 text-sm">⚡</span>
          </div>
        </div>
        <div className="text-2xl font-bold text-purple-900 mb-2">
          {formatNumber(getCarbonIntensity())} kg/km
        </div>
        <div className="text-sm text-purple-700">
          Emissions per kilometer traveled
        </div>
      </div>

      {/* Environmental Impact */}
      <div className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-xl p-6 border border-orange-200">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-lg font-semibold text-orange-800">Environmental Impact</h3>
          <div className="w-8 h-8 bg-orange-200 rounded-full flex items-center justify-center">
            <span className="text-orange-600 text-sm">🌍</span>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <div className="text-orange-700 font-medium">Trees to offset</div>
            <div className="text-xl font-bold text-orange-900">
              {Math.ceil(animatedEmissions / 22)} trees
            </div>
          </div>
          <div>
            <div className="text-orange-700 font-medium">Equivalent to</div>
            <div className="text-xl font-bold text-orange-900">
              {Math.ceil(animatedEmissions / 0.4)} miles driven
            </div>
          </div>
        </div>
      </div>

      {/* City Breakdown */}
      <div className="bg-gradient-to-br from-indigo-50 to-indigo-100 rounded-xl p-6 border border-indigo-200">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-lg font-semibold text-indigo-800">Trip Overview</h3>
          <div className="w-8 h-8 bg-indigo-200 rounded-full flex items-center justify-center">
            <span className="text-indigo-600 text-sm">🏙️</span>
          </div>
        </div>
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <div className="text-2xl font-bold text-indigo-900">{cityCount}</div>
            <div className="text-sm text-indigo-700">Cities</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-indigo-900">
              {formatNumber(getEmissionsPerCity())}
            </div>
            <div className="text-sm text-indigo-700">kg per city</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-indigo-900">
              {formatNumber(getDistancePerCity())}
            </div>
            <div className="text-sm text-indigo-700">km per city</div>
          </div>
        </div>
      </div>
    </div>
  );
}
