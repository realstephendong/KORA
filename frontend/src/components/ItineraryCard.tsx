'use client';

import { useState, useEffect } from 'react';
import { itineraryApi } from '@/lib/api-client';
import CarbonVisualization from './CarbonVisualization';

interface ItineraryData {
  id: number;
  name: string;
  cities: string[];
  carbon_emissions: {
    total_kg: number;
    breakdown: {
      driving: number;
      flights: number;
    };
  };
  distance: {
    total_km: number;
    breakdown: {
      driving: number;
      flights: number;
    };
  };
  metadata: {
    created_at: string;
    updated_at: string;
    user_id: number;
  };
  visualization: {
    carbon_emissions_kg: number;
    distance_km: number;
    city_count: number;
    emissions_per_city: number;
    distance_per_city: number;
  };
}

interface ItineraryCardProps {
  itineraryId: number;
  onExport?: (data: ItineraryData) => void;
}

export default function ItineraryCard({ itineraryId, onExport }: ItineraryCardProps) {
  const [itinerary, setItinerary] = useState<ItineraryData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchItinerary = async () => {
      try {
        setLoading(true);
        const response = await itineraryApi.exportItinerary(itineraryId);
        setItinerary(response.itinerary);
        if (onExport) {
          onExport(response.itinerary);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load itinerary');
      } finally {
        setLoading(false);
      }
    };

    fetchItinerary();
  }, [itineraryId, onExport]);

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6 animate-pulse">
        <div className="h-6 bg-gray-200 rounded mb-4"></div>
        <div className="h-4 bg-gray-200 rounded mb-2"></div>
        <div className="h-4 bg-gray-200 rounded mb-2"></div>
        <div className="h-4 bg-gray-200 rounded"></div>
      </div>
    );
  }

  if (error || !itinerary) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-600">Error: {error || 'Failed to load itinerary'}</p>
      </div>
    );
  }

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('en-US', {
      minimumFractionDigits: 1,
      maximumFractionDigits: 1
    }).format(num);
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      {/* Header */}
      <div className="flex justify-between items-start mb-4">
        <h3 className="text-xl font-bold text-gray-800">{itinerary.name}</h3>
        <span className="text-sm text-gray-500">
          {new Date(itinerary.metadata.created_at).toLocaleDateString()}
        </span>
      </div>

      {/* Cities */}
      <div className="mb-4">
        <h4 className="text-sm font-semibold text-gray-600 mb-2">Cities ({itinerary.visualization.city_count})</h4>
        <div className="flex flex-wrap gap-2">
          {itinerary.cities.map((city, index) => (
            <span
              key={index}
              className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full"
            >
              {city}
            </span>
          ))}
        </div>
      </div>

      {/* Carbon Emissions Visualization */}
      <CarbonVisualization
        carbonEmissions={itinerary.visualization.carbon_emissions_kg}
        distance={itinerary.visualization.distance_km}
        cityCount={itinerary.visualization.city_count}
        animated={true}
        className="mb-4"
      />

      {/* Breakdown */}
      <div className="grid grid-cols-2 gap-4 text-sm">
        <div>
          <h5 className="font-semibold text-gray-700 mb-1">Driving</h5>
          <p className="text-gray-600">
            {formatNumber(itinerary.carbon_emissions.breakdown.driving)} kg CO₂
          </p>
          <p className="text-gray-600">
            {formatNumber(itinerary.distance.breakdown.driving)} km
          </p>
        </div>
        <div>
          <h5 className="font-semibold text-gray-700 mb-1">Flights</h5>
          <p className="text-gray-600">
            {formatNumber(itinerary.carbon_emissions.breakdown.flights)} kg CO₂
          </p>
          <p className="text-gray-600">
            {formatNumber(itinerary.distance.breakdown.flights)} km
          </p>
        </div>
      </div>
    </div>
  );
}
