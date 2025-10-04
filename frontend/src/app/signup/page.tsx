import React from "react";
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { getAuth0LoginUrl, getAuth0LogoutUrl } from '@/lib/auth0';

export default function SignupPage() {
    const { user, isLoading, logout } = useAuth();
    const router = useRouter();

    const handleLogin = () => {
    // Redirect to Auth0 login
    window.location.href = getAuth0LoginUrl();
  };

  const handleSignUp = () => {
    
  }

  return (
    <div>
      <div
      className="bg-[linear-gradient(0deg,rgba(246,245,250,1)_0%,rgba(246,245,250,1)_100%)] w-full min-w-[1920px] min-h-[1316px] flex"
      data-model-id="44:314"
    >
      <div className="mt-[309px] w-[607px] h-[697px] ml-[656px] flex flex-col rounded-[50px] overflow-hidden border-2 border-solid border-[#d8dfe980] bg-[linear-gradient(180deg,rgba(216,223,233,0.25)_0%,rgba(216,223,233,0)_100%),linear-gradient(0deg,rgba(246,245,250,1)_0%,rgba(246,245,250,1)_100%)]">
        <div className="flex ml-11 w-[520px] h-[72px] relative mt-[54px] items-center px-5 py-2.5 bg-white rounded-[20px] overflow-hidden border-variable-collection-black">
          <p className="relative w-fit mt-[-1.00px] [font-family:'Onest',Helvetica] font-normal text-variable-collection-black text-xl tracking-[0] leading-[normal]">
            <span className="font-medium text-[#212121]">
              First Name
              <br />
            </span>

            <span className="text-[#a1a1a1]">Stephen</span>
          </p>
        </div>

        <div className="flex ml-11 w-[520px] h-[72px] relative mt-[17px] items-center px-5 py-2.5 bg-white rounded-[20px] overflow-hidden border-variable-collection-black">
          <p className="relative w-fit mt-[-1.00px] [font-family:'Onest',Helvetica] font-normal text-variable-collection-black text-xl tracking-[0] leading-[normal]">
            <span className="font-medium text-[#212121]">
              Last Name
              <br />
            </span>

            <span className="text-[#a1a1a1]">Something</span>
          </p>
        </div>

        <div className="flex ml-11 w-[520px] h-[72px] relative mt-[17px] items-center px-5 py-2.5 bg-white rounded-[20px] overflow-hidden border-variable-collection-black">
          <p className="relative w-fit mt-[-1.00px] [font-family:'Onest',Helvetica] font-normal text-variable-collection-black text-xl tracking-[0] leading-[normal]">
            <span className="font-medium text-[#212121]">
              Email
              <br />
            </span>

            <span className="text-[#a1a1a1]">stephen@waterloo.ca</span>
          </p>
        </div>

        <div className="flex ml-11 w-[520px] h-[72px] relative mt-[17px] flex-col items-start justify-center gap-[9px] pt-2.5 pb-[15px] px-5 bg-white rounded-[20px] overflow-hidden border-variable-collection-black">
          <div className="relative w-fit mt-[-1.00px] [font-family:'Onest',Helvetica] font-medium text-variable-collection-black text-xl tracking-[0] leading-[normal]">
            Password
          </div>

          <div className="inline-flex items-center gap-2 relative flex-[0_0_auto]">
            <div className="relative w-3 h-3 bg-[#d9d9d9] rounded-md" />

            <div className="relative w-3 h-3 bg-[#d9d9d9] rounded-md" />

            <div className="relative w-3 h-3 bg-[#d9d9d9] rounded-md" />

            <div className="relative w-3 h-3 bg-[#d9d9d9] rounded-md" />

            <div className="relative w-3 h-3 bg-[#d9d9d9] rounded-md" />

            <div className="relative w-3 h-3 bg-[#d9d9d9] rounded-md" />
          </div>
        </div>

        <div className="flex ml-11 w-[520px] h-[72px] relative mt-[17px] flex-col items-start justify-center gap-[9px] pt-2.5 pb-[15px] px-5 bg-white rounded-[20px] overflow-hidden border-variable-collection-black">
          <div className="relative w-fit mt-[-1.00px] [font-family:'Onest',Helvetica] font-medium text-variable-collection-black text-xl tracking-[0] leading-[normal]">
            Confirm Password
          </div>

          <div className="inline-flex items-center gap-2 relative flex-[0_0_auto]">
            <div className="relative w-3 h-3 bg-[#d9d9d9] rounded-md" />

            <div className="relative w-3 h-3 bg-[#d9d9d9] rounded-md" />

            <div className="relative w-3 h-3 bg-[#d9d9d9] rounded-md" />

            <div className="relative w-3 h-3 bg-[#d9d9d9] rounded-md" />

            <div className="relative w-3 h-3 bg-[#d9d9d9] rounded-md" />

            <div className="relative w-3 h-3 bg-[#d9d9d9] rounded-md" />
          </div>
        </div>


        {/* Action buttons */}
          <div className="flex flex-col sm:flex-row gap-6 sm:gap-8 justify-center items-center">
            
                <button className="relative w-fit [font-family:'Onest',Helvetica] font-bold text-[#efefef] text-xl text-center tracking-[0] leading-[normal] w-full sm:w-auto px-5 py-2.5 lg:px-6 lg:py-3 rounded-full bg-[#D8DFE9] text-[#212121] text-center font-['Onest'] text-sm lg:text-base font-bold cursor-pointer transition-all duration-300 hover:transform hover:-translate-y-1 hover:shadow-[0_4px_20px_0_#FFF]"
                  onClick={handleSignUp}
                  >Sign Up
                </button>

                <p className="ml-[150px] w-[301px] h-[26px] mt-[17px] [font-family:'Onest',Helvetica] font-normal text-variable-collection-black text-xl tracking-[0] leading-[normal]">
                    <span className="text-[#777f8b]">Already have an account?</span>
                    <span className="font-medium text-[#212121]">&nbsp;</span>
                </p>
                <button className="font-medium text-[#212121] underline"
                    onClick={handleLogin}
                >Login
                </button>

          </div>
          
        
      </div>
    </div>
    </div>
  );
}