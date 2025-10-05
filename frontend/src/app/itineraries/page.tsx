'use client';

import { useState, useEffect } from 'react';
import ProtectedRoute from '@/components/ProtectedRoute';
import ItineraryCard from '@/components/ItineraryCard';
import { itineraryApi, debugApi } from '@/lib/api-client';

interface Itinerary {
  id: number;
  name: string;
  cities: string[];
  total_distance_km: number;
  carbon_emissions_kg: number;
  created_at: string;
  updated_at: string;
}

export default function ItinerariesPage() {
  const [itineraries, setItineraries] = useState<Itinerary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedItinerary, setSelectedItinerary] = useState<number | null>(null);

  useEffect(() => {
    const fetchItineraries = async () => {
      try {
        setLoading(true);
        console.log('Testing authentication first...');
        
        // Test authentication first
        try {
          const authTest = await debugApi.testAuth();
          console.log('Auth test successful:', authTest);
        } catch (authErr) {
          console.error('Auth test failed:', authErr);
          setError('Authentication failed. Please try logging in again.');
          return;
        }
        
        console.log('Fetching itineraries...');
        const response = await itineraryApi.getAllItineraries();
        console.log('Itineraries response:', response);
        setItineraries(response.itineraries);
      } catch (err) {
        console.error('Error fetching itineraries:', err);
        setError(err instanceof Error ? err.message : 'Failed to load itineraries');
      } finally {
        setLoading(false);
      }
    };

    fetchItineraries();
  }, []);

  const handleItinerarySelect = (itineraryId: number) => {
    setSelectedItinerary(selectedItinerary === itineraryId ? null : itineraryId);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('en-US', {
      minimumFractionDigits: 1,
      maximumFractionDigits: 1
    }).format(num);
  };

  if (loading) {
    return (
      <ProtectedRoute>
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
          <div className="max-w-6xl mx-auto p-6">
            <div className="animate-pulse">
              <div className="h-8 bg-gray-200 rounded mb-6"></div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="bg-white rounded-lg shadow-md p-6">
                    <div className="h-6 bg-gray-200 rounded mb-4"></div>
                    <div className="h-4 bg-gray-200 rounded mb-2"></div>
                    <div className="h-4 bg-gray-200 rounded mb-2"></div>
                    <div className="h-4 bg-gray-200 rounded"></div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </ProtectedRoute>
    );
  }

  if (error) {
    return (
      <ProtectedRoute>
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
          <div className="max-w-6xl mx-auto p-6">
            <div className="bg-red-50 border border-red-200 rounded-lg p-6">
              <h2 className="text-xl font-bold text-red-800 mb-2">Error Loading Itineraries</h2>
              <p className="text-red-600">{error}</p>
            </div>
          </div>
        </div>
      </ProtectedRoute>
    );
  }

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="max-w-6xl mx-auto p-6">
          {/* Header */}
          <div className="mb-8">
            <div className="flex justify-between items-center mb-4">
              <h1 className="text-3xl font-bold text-gray-800">Your Travel Itineraries</h1>
              <div className="flex gap-2">
                <a 
                  href="/chat" 
                  className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                >
                  New Trip
                </a>
                <a 
                  href="/globe" 
                  className="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition-colors"
                >
                  Globe
                </a>
                <a 
                  href="/api/auth/logout" 
                  className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors"
                >
                  Logout
                </a>
              </div>
            </div>
            <p className="text-gray-600">
              View and analyze your saved travel plans with carbon footprint data
            </p>
          </div>

          {itineraries.length === 0 ? (
            <div className="text-center py-12">
              <div className="bg-white rounded-lg shadow-md p-8">
                <h3 className="text-xl font-semibold text-gray-800 mb-2">No Itineraries Yet</h3>
                <p className="text-gray-600 mb-4">
                  Start planning your sustainable travel adventure!
                </p>
                <a 
                  href="/chat" 
                  className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors inline-block"
                >
                  Plan Your First Trip
                </a>
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {itineraries.map((itinerary) => (
                <div key={itinerary.id} className="space-y-4">
                  {/* Itinerary Summary Card */}
                  <div 
                    className="bg-white rounded-lg shadow-md p-6 cursor-pointer hover:shadow-lg transition-shadow"
                    onClick={() => handleItinerarySelect(itinerary.id)}
                  >
                    <div className="flex justify-between items-start mb-4">
                      <h3 className="text-xl font-bold text-gray-800">{itinerary.name}</h3>
                      <span className="text-sm text-gray-500">
                        {formatDate(itinerary.created_at)}
                      </span>
                    </div>

                    {/* Quick Stats */}
                    <div className="grid grid-cols-3 gap-4 mb-4">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-green-600">
                          {formatNumber(itinerary.carbon_emissions_kg)}
                        </div>
                        <div className="text-xs text-gray-600">kg CO₂</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-blue-600">
                          {formatNumber(itinerary.total_distance_km)}
                        </div>
                        <div className="text-xs text-gray-600">km</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-purple-600">
                          {itinerary.cities.length}
                        </div>
                        <div className="text-xs text-gray-600">cities</div>
                      </div>
                    </div>

                    {/* Cities */}
                    <div className="mb-4">
                      <h4 className="text-sm font-semibold text-gray-600 mb-2">Cities</h4>
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

                    {/* Action Button */}
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-500">
                        Click to view detailed analysis
                      </span>
                      <div className="text-blue-600">
                        {selectedItinerary === itinerary.id ? '▼' : '▶'}
                      </div>
                    </div>
                  </div>

                  {/* Detailed Itinerary Card */}
                  {selectedItinerary === itinerary.id && (
                    <ItineraryCard 
                      itineraryId={itinerary.id}
                      onExport={(data) => {
                        console.log('Exported itinerary data:', data);
                      }}
                    />
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </ProtectedRoute>
  );
}
