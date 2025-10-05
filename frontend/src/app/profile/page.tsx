'use client';

import { useAuth } from '@/contexts/AuthContext';
import ProtectedRoute from '@/components/ProtectedRoute';
import { apiClient } from '@/lib/api-client';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

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
  const router = useRouter();
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
        
        // Load saved profile data if available
        if (data.user) {
          const userData = data.user;
          
          // Set budget if available
          if (userData.budget) {
            setBudgetRange(userData.budget);
          }
          
          // Set interests if available
          if (userData.interests && Array.isArray(userData.interests)) {
            setSelectedInterests(userData.interests);
          }
          
          // Set profile picture if available
          if (userData.profile_picture) {
            const imageIndex = profileImages.findIndex(img => img.includes(userData.profile_picture));
            if (imageIndex !== -1) {
              setCurrentImageIndex(imageIndex);
            }
          }
        }
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
      <div className="bg-[linear-gradient(0deg,rgba(246,245,250,1)_0%,rgba(246,245,250,1)_100%)] w-full min-h-screen">
        <div className="flex flex-col items-center justify-center min-h-screen py-8 px-4">
          
          {/* Navigation Buttons */}
          <div className="mb-6 flex gap-4">
            <button
              onClick={() => router.push('/landing')}
              className="px-6 py-3 bg-[#d8dfe9] hover:bg-gray-200 text-[#231f20] font-bold rounded-[25px] border border-solid border-black transition-colors [font-family:'Onest',Helvetica]"
            >
              ← Back to Landing
            </button>
            <button
              onClick={() => router.push('/globe')}
              className="px-6 py-3 bg-[#eeefa4] hover:bg-yellow-200 text-[#231f20] font-bold rounded-[25px] border border-solid border-black transition-colors [font-family:'Onest',Helvetica]"
            >
              🌍 Explore Globe
            </button>
          </div>
          
          {/* Main Content Card */}
          <div className="w-full max-w-[500px] rounded-[50px] border-2 border-solid border-[#d8dfe980] bg-[linear-gradient(180deg,rgba(216,223,233,0.25)_0%,rgba(216,223,233,0)_100%)] p-6 shadow-lg">
            
            {/* User Info Section */}
            {profileData && (
              <div className="mb-6 text-center">
                <h1 className="[font-family:'Onest',Helvetica] font-bold text-[#231f20] text-xl mb-1">
                  {profileData.auth0_info.name}
                </h1>
                <p className="[font-family:'Onest',Helvetica] text-[#666] text-sm">
                  {profileData.auth0_info.email}
                </p>
              </div>
            )}

            {/* Profile Picture Section - Now Inside */}
            <div className="mb-8 flex items-center justify-center space-x-6">
              <button
                type="button"
                onClick={prevImage}
                aria-label="Previous"
                className="inline-flex items-center justify-center px-4 py-3 bg-[#d8dfe9] rotate-180 rounded-[25px] border border-solid hover:bg-gray-200 transition-colors"
              >
                <span className="[font-family:'Onest',Helvetica] font-bold text-black text-[35px]">
                  &gt;
                </span>
              </button>

              <div className="w-28 h-28 flex items-center justify-center">
                <img
                  className="w-24 h-24 object-contain"
                  alt="Turtle profile"
                  src={profileImages[currentImageIndex]}
                />
              </div>

              <button
                type="button"
                onClick={nextImage}
                aria-label="Next"
                className="inline-flex items-center justify-center px-4 py-3 bg-[#d8dfe9] rounded-[25px] border border-solid hover:bg-gray-200 transition-colors"
              >
                <span className="[font-family:'Onest',Helvetica] font-bold text-black text-[35px]">
                  &gt;
                </span>
              </button>
            </div>
            
            {/* Error Display */}
            {error && (
              <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-red-600 [font-family:'Onest',Helvetica]">Error: {error}</p>
              </div>
            )}

            {/* Budget Section */}
            <div className="mb-6">
              <div className="flex w-full items-center px-4 py-2 bg-white rounded-[20px] border border-black">
                <div className="flex flex-col w-full">
                  <span className="[font-family:'Onest',Helvetica] font-medium text-[#212121] text-lg mb-1">
                    Budget
                  </span>
                  <input
                    type="text"
                    value={budgetRange}
                    onChange={handleBudgetChange}
                    onBlur={validateBudget}
                    placeholder="$000-$0000"
                    className="text-[#231f20] placeholder-[#a1a1a1] bg-transparent border-none outline-none w-full [font-family:'Onest',Helvetica] text-lg"
                    required
                  />
                </div>
              </div>
              {budgetError && (
                <p className="mt-2 text-red-500 text-sm [font-family:'Onest',Helvetica]">
                  {budgetError}
                </p>
              )}
            </div>

            {/* Interests Section */}
            <div className="mb-6">
              <h2 className="[font-family:'Onest',Helvetica] font-medium text-black text-lg mb-4">
                Pick your interests!
              </h2>
              
              {/* Interests Grid */}
              <div className="grid grid-cols-3 gap-2 mb-3">
                {interests.slice(0, 3).map((interest) => (
                  <button
                    key={interest.id}
                    type="button"
                    onClick={() => toggleInterest(interest.label)}
                    className={`inline-flex items-center justify-center px-3 py-2 rounded-[25px] border border-solid border-black overflow-hidden transition-colors text-sm ${
                      isSelected(interest.label) ? "bg-[#eeefa4]" : "hover:bg-gray-100"
                    }`}
                  >
                    <span className="[font-family:'Onest',Helvetica] font-bold text-[#231f20] text-center">
                      {interest.label}
                    </span>
                  </button>
                ))}
              </div>

              {/* Fourth Interest Button */}
              <button
                type="button"
                onClick={() => toggleInterest(interests[3].label)}
                className={`inline-flex items-center justify-center px-3 py-2 rounded-[25px] border border-solid border-black overflow-hidden transition-colors text-sm w-full ${
                  isSelected(interests[3].label) ? "bg-[#eeefa4]" : "hover:bg-gray-100"
                }`}
              >
                <span className="[font-family:'Onest',Helvetica] font-bold text-[#231f20] text-center">
                  {interests[3].label}
                </span>
              </button>
            </div>

            {/* Save Button */}
            <div className="text-center">
              <button
                type="button"
                onClick={async () => {
                  if (validateBudget()) {
                    try {
                      // Prepare profile data
                      const profileData = {
                        budget: budgetRange,
                        interests: selectedInterests,
                        profile_picture: profileImages[currentImageIndex]
                      };
                      
                      // Send to backend
                      const response = await apiClient.put('/api/profile', profileData);
                      
                      if (response.status === 'success') {
                        // Redirect to landing page after successful save
                        router.push('/landing');
                      } else {
                        alert('Failed to save profile. Please try again.');
                      }
                    } catch (error) {
                      console.error('Error saving profile:', error);
                      alert('Failed to save profile. Please try again.');
                    }
                  }
                }}
                className="w-full h-[60px] bg-[#231f20] border border-black items-center justify-center px-4 py-2 rounded-[25px] border-solid disabled:bg-gray-400 disabled:cursor-not-allowed hover:bg-gray-800 transition-colors"
                disabled={!budgetRange.trim()}
              >
                <span className="[font-family:'Onest',Helvetica] font-bold text-[#efefef] text-lg text-center">
                  I&apos;m happy with my profile!
                </span>
              </button>
            </div>

          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}
