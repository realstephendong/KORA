import React, { useState } from 'react';

export default function LoginPage() {
    return (
         <div
      className="bg-[linear-gradient(0deg,rgba(246,245,250,1)_0%,rgba(246,245,250,1)_100%)] w-full min-w-[1920px] min-h-[1316px] relative"
      data-model-id="53:929"
    >
      <img
        className="absolute top-[155px] left-0 w-[1665px] h-[1159px]"
        alt="Vector"
        src="https://c.animaapp.com/13nUlnDZ/img/vector-1.png"
      />

      <div className="absolute top-[385px] left-[656px] w-[607px] h-[545px] flex flex-col rounded-[50px] overflow-hidden border-2 border-solid border-[#d8dfe980] bg-[linear-gradient(180deg,rgba(216,223,233,0.25)_0%,rgba(216,223,233,0)_100%),linear-gradient(0deg,rgba(246,245,250,1)_0%,rgba(246,245,250,1)_100%)]">
        <div className="flex ml-11 w-[520px] h-[72px] relative mt-20 items-center px-5 py-2.5 bg-white rounded-[20px] overflow-hidden border-variable-collection-black">
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

        <div className="flex ml-11 w-[520px] h-[70px] relative mt-[111px] items-center justify-center px-5 py-2.5 bg-[#231f20] rounded-[25px] overflow-hidden border border-solid border-variable-collection-black">
          <div className="relative w-fit [font-family:'Onest',Helvetica] font-bold text-[#efefef] text-xl text-center tracking-[0] leading-[normal]">
            Login
          </div>
        </div>

        <p className="ml-[150px] w-[299px] h-[26px] mt-[17px] [font-family:'Onest',Helvetica] font-normal text-variable-collection-black text-xl tracking-[0] leading-[normal]">
          <span className="text-[#777f8b]">Don’t have an account?</span>

          <span className="font-medium text-[#212121]">&nbsp;</span>

          <span className="font-medium text-[#212121] underline">Sign up</span>
        </p>
      </div>
    </div>
    )
}
