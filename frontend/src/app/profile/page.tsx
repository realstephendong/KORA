'use client';

import { useAuth } from '@/contexts/AuthContext';
import ProtectedRoute from '@/components/ProtectedRoute';
import { apiClient } from '@/lib/api-client';
import { useEffect, useState } from 'react';
import Image from 'next/image';

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
  
  const [selectedInterests, setSelectedInterests] = useState([
    "Food & treats",
    "Learning about Culture",
  ]);
  const [budgetRange, setBudgetRange] = useState("$000-$0000");

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
  
  // Profile picture management
  const profileImages = [
    'trashbag.svg',
    'tree1.svg', 
    'tree2.svg',
    'turtle blue.svg',
    'turtle green.svg',
    'turtle pink.svg',
    'turtle purple.svg'
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
        <main className="max-w-4xl mx-auto py-8 px-4">
          <div className="bg-white rounded-[50px] border-2 border-solid border-[#d8dfe980] bg-gradient-to-b from-[rgba(216,223,233,0.25)] to-transparent p-8 shadow-lg">
            
            {/* Profile Picture Selector */}
            <div className="text-center mb-8">
              <h2 className="text-2xl font-bold text-gray-800 mb-6">Choose Your Profile Picture</h2>
              <div className="flex items-center justify-center space-x-4">
                <button
                  onClick={prevImage}
                  className="bg-gray-200 hover:bg-gray-300 text-gray-700 font-bold py-2 px-4 rounded-full transition-colors"
                  aria-label="Previous image"
                >
                  ‹
                </button>
                
                <div className="relative w-32 h-32 bg-gray-100 rounded-full overflow-hidden border-4 border-gray-300">
                  <Image
                    src={`/profile/${profileImages[currentImageIndex]}`}
                    alt={`Profile picture ${currentImageIndex + 1}`}
                    fill
                    className="object-contain p-2"
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
              
              <div className="text-center mt-4">
                <p className="text-sm text-gray-600">
                  {currentImageIndex + 1} of {profileImages.length}
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  {profileImages[currentImageIndex].replace('.svg', '').replace(/([A-Z])/g, ' $1').trim()}
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
              <div className="bg-gray-50 rounded-lg p-6 mb-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">User Information</h3>
                <div className="space-y-2">
                  <p><span className="font-medium">Name:</span> {profileData.auth0_info.name}</p>
                  <p><span className="font-medium">Email:</span> {profileData.auth0_info.email}</p>
                  <p><span className="font-medium">Subject ID:</span> {profileData.auth0_info.sub}</p>
                </div>
              </div>
            )}

            {/* Budget Section */}
            <div className="mb-6">
              <label className="block text-xl font-medium text-gray-800 mb-2">
                Budget
              </label>
              <div className="flex w-full items-center px-5 py-2.5 bg-white rounded-[20px] border border-gray-300">
                <span className="text-gray-500">
                  {budgetRange}
                </span>
              </div>
            </div>

            {/* Interests Section */}
            <div className="mb-8">
              <h2 className="text-xl font-medium text-gray-800 mb-4">
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
                className="bg-[#231f20] hover:bg-gray-800 text-white font-bold py-3 px-8 rounded-[25px] transition-colors"
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
