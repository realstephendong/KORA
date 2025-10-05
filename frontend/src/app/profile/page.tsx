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
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8">
        <div className="max-w-4xl mx-auto px-4">
          <div className="bg-white rounded-lg shadow-lg p-8">
            <div className="flex items-center justify-between mb-8">
              <h1 className="text-3xl font-bold text-gray-800">Your Profile</h1>
              <a 
                href="/api/auth/logout" 
                className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors"
              >
                Logout
              </a>
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
                <p className="text-red-600">Error: {error}</p>
              </div>
            )}

            {profileData && (
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="bg-gray-50 rounded-lg p-6">
                    <h3 className="text-lg font-semibold text-gray-800 mb-4">Auth0 Information</h3>
                    <div className="space-y-2">
                      <p><span className="font-medium">Name:</span> {profileData.auth0_info.name}</p>
                      <p><span className="font-medium">Email:</span> {profileData.auth0_info.email}</p>
                      <p><span className="font-medium">Subject ID:</span> {profileData.auth0_info.sub}</p>
                    </div>
                  </div>

                  <div className="bg-gray-50 rounded-lg p-6">
                    <h3 className="text-lg font-semibold text-gray-800 mb-4">Database Information</h3>
                    <div className="space-y-2">
                      <p><span className="font-medium">User ID:</span> {profileData.user.id}</p>
                      <p><span className="font-medium">Created:</span> {new Date(profileData.user.created_at).toLocaleDateString()}</p>
                      <p><span className="font-medium">Last Updated:</span> {new Date(profileData.user.updated_at).toLocaleDateString()}</p>
                    </div>
                  </div>
                </div>

                <div className="bg-blue-50 rounded-lg p-6">
                  <h3 className="text-lg font-semibold text-gray-800 mb-4">Quick Actions</h3>
                  <div className="flex flex-wrap gap-4">
                    <a 
                      href="/globe" 
                      className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                    >
                      Back to Globe
                    </a>
                    <a 
                      href="/chat" 
                      className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
                    >
                      Start Planning
                    </a>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}
