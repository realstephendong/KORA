'use client';

import { useAuth } from '@/contexts/AuthContext';
import ProtectedRoute from '@/components/ProtectedRoute';
import { apiClient } from '@/lib/api-client';
import { useEffect, useState } from 'react';

interface UserProfile {
  id: number;
  auth0_sub: string;
  created_at: string;
  updated_at: string;
}

interface ApiResponse {
  user: UserProfile;
  auth0_info: {
    sub: string;
    email: string;
    name: string;
  };
  status: string;
}

export default function ProfilePage() {
  const { user, isLoading } = useAuth();
  const [profileData, setProfileData] = useState<ApiResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const [selectedInterests, setSelectedInterests] = useState<string[]>([]);
  const [budgetRange, setBudgetRange] = useState("");
  const [budgetError, setBudgetError] = useState("");

  const interests = [
    { id: 1, label: "Fashion" },
    { id: 2, label: "Food & treats" },
    { id: 3, label: "Nature & Wildlife" },
    { id: 4, label: "Learning about Culture" },
  ];

  const toggleInterest = (label: string) => {
    setSelectedInterests((prev) =>
      prev.includes(label)
        ? prev.filter((item) => item !== label)
        : [...prev, label],
    );
  };

  const isSelected = (label: string) => selectedInterests.includes(label);

  // Budget validation
  const handleBudgetChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    // Only allow numbers
    if (value === '' || /^\d+$/.test(value)) {
      setBudgetRange(value);
      setBudgetError('');
    }
  };

  const validateBudget = () => {
    if (!budgetRange.trim()) {
      setBudgetError('Budget is required');
      return false;
    }
    if (!/^\d+$/.test(budgetRange)) {
      setBudgetError('Please enter only numbers');
      return false;
    }
    setBudgetError('');
    return true;
  };
  
  // Profile picture management
  const profileImages = [ 
    '/assets/turtles/turtle blue.svg',
    '/assets/turtles/turtle green.svg',
    '/assets/turtles/turtle pink.svg',
    '/assets/turtles/turtle purple.svg'
  ];
  const [currentImageIndex, setCurrentImageIndex] = useState(0);

  // Profile picture navigation functions
  const nextImage = () => {
    setCurrentImageIndex((prev) => (prev + 1) % profileImages.length);
  };

  const prevImage = () => {
    setCurrentImageIndex((prev) => (prev - 1 + profileImages.length) % profileImages.length);
  };

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const data = await apiClient.get('/api/profile');
        setProfileData(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch profile');
      } finally {
        setLoading(false);
      }
    };

    if (user) {
      fetchProfile();
    }
  }, [user]);

  if (loading) {
    return (
      <div className="w-full h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-lg text-gray-600 font-medium">Loading profile...</p>
        </div>
      </div>
    );
  }

  return (
    <ProtectedRoute>
      <div className="bg-[linear-gradient(0deg,rgba(246,245,250,1)_0%,rgba(246,245,250,1)_100%)] w-full min-h-screen relative">
        <main className="max-w-4xl mx-auto py-4 px-4">
          <div className="bg-white rounded-[20px] border-2 border-solid border-[#d8dfe980] bg-gradient-to-b from-[rgba(216,223,233,0.25)] to-transparent p-6 shadow-lg">
            
            {/* Profile Picture Selector */}
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-gray-800 mb-4" style={{fontFamily: 'Onest, sans-serif'}}>Choose Your Profile Picture</h2>
              <div className="flex items-center space-x-6">
                <button
                  onClick={prevImage}
                  className="bg-gray-200 hover:bg-gray-300 text-gray-700 font-bold py-2 px-4 rounded-full transition-colors"
                  aria-label="Previous image"
                >
                  ‹
                </button>
                
                <div className="relative w-24 h-24 bg-gray-100 rounded-full overflow-hidden border-4 border-gray-300 flex items-center justify-center">
                  <img
                    src={profileImages[currentImageIndex]}
                    alt={`Profile picture ${currentImageIndex + 1}`}
                    className="w-16 h-16 object-contain"
                  />
                </div>
                
                <button
                  onClick={nextImage}
                  className="bg-gray-200 hover:bg-gray-300 text-gray-700 font-bold py-2 px-4 rounded-full transition-colors"
                  aria-label="Next image"
                >
                  ›
                </button>
              </div>
              
              <div className="mt-3">
                <p className="text-sm text-gray-600">
                  {currentImageIndex + 1} of {profileImages.length}
                </p>
              </div>
            </div>

            {/* Error Display */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
                <p className="text-red-600">Error: {error}</p>
              </div>
            )}

            {/* Profile Data Display */}
            {profileData && (
              <div className="bg-gray-50 rounded-lg p-4 mb-6 text-left">
                <h3 className="text-lg font-semibold text-gray-800 mb-3" style={{fontFamily: 'Onest, sans-serif'}}>User Information</h3>
                <div className="space-y-2">
                  <p className="text-base" style={{fontFamily: 'Onest, sans-serif'}}><span className="font-medium">Name:</span> {profileData.auth0_info.name}</p>
                  <p className="text-base" style={{fontFamily: 'Onest, sans-serif'}}><span className="font-medium">Email:</span> {profileData.auth0_info.email}</p>
                  <p className="text-base" style={{fontFamily: 'Onest, sans-serif'}}><span className="font-medium">Subject ID:</span> {profileData.auth0_info.sub}</p>
                </div>
              </div>
            )}

            {/* Budget Section */}
            <div className="mb-6">
              <label className="block text-lg font-medium text-gray-800 mb-3" style={{fontFamily: 'Onest, sans-serif'}}>
                Budget <span className="text-red-500">*</span>
              </label>
              <div className="flex w-full max-w-md items-center px-5 py-2.5 bg-white rounded-[20px] border border-gray-300 focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-200">
                <span className="text-gray-500 mr-2">$</span>
                <input
                  type="text"
                  value={budgetRange}
                  onChange={handleBudgetChange}
                  onBlur={validateBudget}
                  placeholder="0-00000"
                  className="flex-1 outline-none text-gray-800 placeholder-gray-400"
                  style={{fontFamily: 'Onest, sans-serif'}}
                  required
                />
              </div>
              {budgetError && (
                <p className="text-red-500 text-sm mt-2">{budgetError}</p>
              )}
            </div>

            {/* Interests Section */}
            <div className="mb-6">
              <h2 className="text-lg font-medium text-gray-800 mb-4" style={{fontFamily: 'Onest, sans-serif'}}>
                Pick your interests!
              </h2>
              <div className="flex flex-wrap gap-3">
                {interests.map((interest) => (
                  <button
                    key={interest.id}
                    type="button"
                    onClick={() => toggleInterest(interest.label)}
                    className={`inline-flex items-center justify-center px-5 py-2.5 rounded-[25px] border border-solid border-gray-800 overflow-hidden transition-colors ${
                      isSelected(interest.label) ? "bg-[#eeefa4]" : "bg-transparent hover:bg-gray-100"
                    }`}
                    aria-pressed={isSelected(interest.label)}
                  >
                    <span className="font-bold text-gray-800 text-lg">
                      {interest.label}
                    </span>
                  </button>
                ))}
              </div>
            </div>

            {/* Save Button */}
            <div className="text-center">
              <button
                type="button"
                onClick={() => {
                  if (validateBudget()) {
                    // Handle profile save logic here
                    console.log('Profile saved with budget:', budgetRange);
                    alert('Profile saved successfully!');
                  }
                }}
                className="bg-[#231f20] hover:bg-gray-800 text-white font-bold py-3 px-8 rounded-[25px] transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
                disabled={!budgetRange.trim()}
              >
                I&apos;m happy with my profile!
              </button>
            </div>
          </div>
        </main>
      </div>
    </ProtectedRoute>
  );
}
