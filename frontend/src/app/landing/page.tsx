'use client';

import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { getAuth0LoginUrl, getAuth0LogoutUrl } from '@/lib/auth0';

export default function LandingPage() {
  const { user, isLoading, logout } = useAuth();
  const router = useRouter();

  const handleCreateProfile = () => {
    // Redirect to Auth0 login
    window.location.href = getAuth0LoginUrl();
  };

  const handleLogin = () => {
    // Redirect to Auth0 login
    window.location.href = getAuth0LoginUrl();
  };

  const handleLogout = () => {
    logout();
    // Also logout from Auth0
    window.location.href = getAuth0LogoutUrl();
  };

  const handleStartPlanning = () => {
    router.push('/globe');
  };

  if (isLoading) {
    return (
      <div className="w-full h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-lg text-gray-600 font-medium">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <main className="relative min-h-screen w-full bg-gradient-to-br from-[#F6F5FA] via-[#E8E7F0] to-[#F6F5FA] bg-[length:100%_100%,200%_200%] bg-center flex flex-col items-center justify-center overflow-hidden px-4 py-8">

      {/* Content Container */}
      <div className="relative z-10 flex flex-col items-center justify-center text-center max-w-6xl mx-auto">
        {/* Header Section */}
        <div className="flex flex-col lg:flex-row items-center justify-center gap-6 lg:gap-12 mb-6 lg:mb-10">
          {/* Main heading */}
          <h1 className="text-7xl sm:text-8xl lg:text-9xl xl:text-[120px] font-bold text-[#212121] font-['Onest'] leading-tight">
            kora.
          </h1>

          {/* Sea turtle image */}
          <img
            src="https://api.builder.io/api/v1/image/assets/TEMP/472fe668b4a15471bbc91dff1f1f01a2bb09d7bb?width=358"
            alt="sea turtle"
            className="w-24 h-24 sm:w-28 sm:h-28 lg:w-32 lg:h-32 xl:w-36 xl:h-36 object-contain"
          />
        </div>

        {/* Subtitle */}
        <h2 className="text-xl sm:text-2xl lg:text-3xl xl:text-4xl font-normal text-[#212121] font-['Onest'] mb-8 lg:mb-12 max-w-4xl">
          Plan your next adventure, <span className="font-normal">sustainably</span>
        </h2>

        {/* Action buttons card */}
        <div className="w-full max-w-xl lg:max-w-2xl xl:max-w-[500px] bg-gradient-to-b from-[rgba(216,223,233,0.35)] to-[rgba(216,223,233,0.10)] backdrop-blur-[10px] rounded-3xl lg:rounded-[40px] border-2 border-[rgba(216,223,233,0.70)] p-5 lg:p-6 xl:p-8">
          {/* Action buttons */}
          <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 justify-center items-center">
            {user ? (
              <>
                <button 
                  className="w-full sm:w-auto px-5 py-2.5 lg:px-6 lg:py-3 rounded-2xl border-[3px] border-[rgba(255,255,255,0.65)] bg-[#D8DFE9] shadow-[0_2px_15px_0_#FFF] text-[#212121] text-center font-['Onest'] text-sm lg:text-base font-bold cursor-pointer transition-all duration-300 hover:transform hover:-translate-y-1 hover:shadow-[0_4px_20px_0_#FFF]"
                  onClick={() => router.push('/profile')}
                >
                  View Profile
                </button>
                <button 
                  className="w-full sm:w-auto px-5 py-2.5 lg:px-6 lg:py-3 rounded-2xl border border-[#212121] bg-[#212121] text-[#EFEFEF] text-center font-['Onest'] text-sm lg:text-base font-bold cursor-pointer transition-all duration-300 hover:bg-[#212121] hover:transform hover:-translate-y-1"
                  onClick={handleStartPlanning}
                >
                  Start Planning
                </button>
                <button 
                  className="w-full sm:w-auto px-5 py-2.5 lg:px-6 lg:py-3 rounded-2xl border border-[#212121] bg-[#212121] text-[#EFEFEF] text-center font-['Onest'] text-sm lg:text-base font-bold cursor-pointer transition-all duration-300 hover:bg-[#212121] hover:transform hover:-translate-y-1"
                  onClick={handleLogout}
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <button 
                  className="w-full sm:w-auto px-5 py-2.5 lg:px-6 lg:py-3 rounded-2xl border-[3px] border-[rgba(255,255,255,0.65)] bg-[#D8DFE9] shadow-[0_2px_15px_0_#FFF] text-[#212121] text-center font-['Onest'] text-sm lg:text-base font-bold cursor-pointer transition-all duration-300 hover:transform hover:-translate-y-1 hover:shadow-[0_4px_20px_0_#FFF]"
                  onClick={handleCreateProfile}
                >
                  Create Your Profile
                </button>
                <button 
                  className="w-full sm:w-auto px-5 py-2.5 lg:px-6 lg:py-3 rounded-2xl border border-[#212121] bg-[#212121] text-[#EFEFEF] text-center font-['Onest'] text-sm lg:text-base font-bold cursor-pointer transition-all duration-300 hover:bg-[#212121] hover:transform hover:-translate-y-1"
                  onClick={handleLogin}
                >
                  Login
                </button>
              </>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}
