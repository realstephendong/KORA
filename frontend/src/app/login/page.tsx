'use client';

import React, { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { getAuth0LoginUrl } from '@/lib/auth0';

export default function LoginPage() {
  const { user, isLoading } = useAuth();
  const router = useRouter();
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // This form is for UI purposes only - Auth0 handles authentication
    // Redirect to Auth0 login
    window.location.href = getAuth0LoginUrl();
  };

  if (isLoading) {
    return (
      <div className="w-full h-screen flex items-center justify-center bg-[#F6F5FA]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#212121] mx-auto mb-4"></div>
          <p className="text-lg text-[#212121] font-medium">Loading...</p>
        </div>
      </div>
    );
  }

  if (user) {
    router.push('/profile');
    return null;
  }

  return (
    <div className="w-full min-h-screen bg-[#F6F5FA] relative flex items-center justify-center px-4 py-8 overflow-hidden">
      {/* Background SVG */}
      <svg 
        className="absolute left-0 top-[160px] w-[1660px] h-[1149px] flex-shrink-0 stroke-[#FFF] stroke-[10px] opacity-20 hidden lg:block" 
        viewBox="0 0 1665 1159" 
        fill="none" 
        xmlns="http://www.w3.org/2000/svg"
      >
        <path 
          d="M0 5H613.453C666.949 5 728.444 25.2155 728.444 94.4644C728.444 140.573 728.443 260.777 728.443 346.943C728.443 386.084 736.455 407.65 761.941 430.816C787.427 453.983 809.437 457.484 866.433 457.484H1525.88C1584.88 457.484 1626.37 481.57 1645.87 517.27C1662.32 547.378 1659.87 617.917 1659.87 673.403L1659.87 802.868C1659.87 848.891 1644.87 879.859 1614.87 898.354C1584.77 916.913 1546.38 924.161 1491.38 924.161H590.454C557.457 924.161 512.46 928.755 471.463 902.655C437.966 881.33 431.967 843.299 431.967 814.051V521.103C431.967 487.554 428.016 466.074 408.469 455.725C388.97 445.402 375.471 445.832 352.973 445.832H138.989C124.49 445.832 111.991 445.832 100.992 456.585C91.4929 465.872 91.4929 473.36 91.4929 486.263V1073.57C90.993 1084.89 88.9929 1116.58 72.4941 1132.49C50.1986 1154 28.4976 1154 0 1154" 
          strokeDasharray="20 40 60 80"
        />
      </svg>

      {/* Login Container */}
      <div className="relative z-10 w-full max-w-[607px] h-[545px] flex-shrink-0 rounded-[50px] border-2 border-[rgba(216,223,233,0.50)] bg-gradient-to-b from-[rgba(216,223,233,0.25)] to-[rgba(216,223,233,0.00)] backdrop-blur-sm">
        <form onSubmit={handleSubmit} className="relative w-full h-full p-11">
          {/* Email Input */}
          <div className="flex w-[520px] h-[72px] px-5 py-2.5 items-center rounded-[20px] bg-white absolute left-11 top-[80px]">
            <div className="flex flex-col w-full">
              <span className="text-[#212121] font-['Onest'] text-xl font-normal leading-normal">
                Email
              </span>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                placeholder="Enter your email"
                className="w-full text-[#212121] font-['Onest'] text-xl font-normal leading-normal border-none outline-none bg-transparent placeholder:text-[#A1A1A1]"
              />
            </div>
          </div>

          {/* Password Input */}
          <div className="flex w-[520px] h-[72px] px-5 py-2.5 flex-col justify-center items-start gap-2 rounded-[20px] bg-white absolute left-11 top-[169px]">
            <span className="text-[#212121] font-['Onest'] text-xl font-normal leading-normal">
              Password
            </span>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleInputChange}
              placeholder="Enter your password"
              className="w-full text-[#212121] font-['Onest'] text-xl font-normal leading-normal border-none outline-none bg-transparent placeholder:text-[#A1A1A1]"
            />
          </div>

          {/* Login Button */}
          <button
            type="submit"
            className="flex w-[520px] h-[70px] px-5 py-2.5 justify-center items-center flex-shrink-0 rounded-[25px] border border-[#212121] bg-[#231F20] absolute left-11 top-[291px] cursor-pointer text-[#EFEFEF] text-center font-['Onest'] text-xl font-bold leading-normal hover:bg-[rgba(35,31,32,0.9)] transition-colors duration-300"
          >
            Login
          </button>

          {/* Signup Link */}
          <div className="text-[#212121] font-['Onest'] text-xl font-medium leading-normal absolute left-[150px] top-[378px] w-[299px] h-[26px]">
            <span className="font-['Onest'] font-normal text-xl text-[rgba(119,128,139,1)]">
              Don't have an account?{' '}
            </span>
            <a 
              href="/signup" 
              className="font-['Onest'] font-normal text-xl text-[#212121] underline hover:text-[rgba(33,33,33,0.8)] transition-colors duration-300"
            >
              Sign up
            </a>
          </div>
        </form>
      </div>
    </div>
  );
}
