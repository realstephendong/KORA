'use client';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';

export default function CallbackPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { login } = useAuth();
  const [error, setError] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  useEffect(() => {
    const handleCallback = async () => {
      // Prevent multiple executions
      if (isProcessing) return;
      setIsProcessing(true);

      const code = searchParams.get('code');
      const error = searchParams.get('error');

      if (error) {
        setError(`Auth0 Error: ${error}`);
        return;
      }

      if (!code) {
        setError('No authorization code received');
        return;
      }

      try {
        // Exchange code for token
        const response = await fetch('/api/auth/token', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ code }),
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.details || 'Failed to exchange code for token');
        }

        const data = await response.json();
        
        // Debug: Log available tokens
        console.log('Available tokens:', {
          hasAccessToken: !!data.access_token,
          hasIdToken: !!data.id_token,
          tokenKeys: Object.keys(data)
        });
        
        // Use access token for API authentication (standard practice)
        const tokenToUse = data.access_token;
        
        if (!tokenToUse) {
          throw new Error('No access token received from Auth0');
        }
        
        // Debug: Log token details
        try {
          const tokenParts = tokenToUse.split('.');
          if (tokenParts.length === 3) {
            const header = JSON.parse(atob(tokenParts[0]));
            console.log('Token header:', header);
          }
        } catch (e) {
          console.log('Could not parse token header:', e);
        }
        
        // Store the token and user info
        login(tokenToUse, {
          sub: data.user.sub,
          email: data.user.email,
          name: data.user.name
        });

        // Redirect to profile page
        router.push('/profile');
      } catch (err) {
        console.error('Authentication error:', err);
        setError(err instanceof Error ? err.message : 'Authentication failed');
      } finally {
        setIsProcessing(false);
      }
    };

    handleCallback();
  }, [searchParams, login, router, isProcessing]);

  if (error) {
    return (
      <div className="w-full h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-red-600 mb-4">Authentication Error</h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <a 
            href="/landing" 
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Back to Landing
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-lg text-gray-600 font-medium">Completing authentication...</p>
      </div>
    </div>
  );
}
