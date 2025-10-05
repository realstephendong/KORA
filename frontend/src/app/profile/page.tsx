'use client';

import { useAuth } from '@/contexts/AuthContext';
import ProtectedRoute from '@/components/ProtectedRoute';
import { apiClient } from '@/lib/api-client';
import React, { useState } from "react";
import turlePink from "./turle-pink.png";

export const Profile = () => {
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

  return (
    <div className="bg-[linear-gradient(0deg,rgba(246,245,250,1)_0%,rgba(246,245,250,1)_100%)] w-full min-w-[1920px] h-[1316px] relative">
      <main className="top-[249px] left-[656px] w-[607px] h-[783px] rounded-[50px] border-2 border-solid border-[#d8dfe980] bg-[linear-gradient(180deg,rgba(216,223,233,0.25)_0%,rgba(216,223,233,0)_100%),linear-gradient(0deg,rgba(246,245,250,1)_0%,rgba(246,245,250,1)_100%)] absolute overflow-hidden">
        <button
          type="button"
          className="inline-flex items-center justify-center px-5 py-2.5 top-[131px] left-[445px] bg-[#d8dfe9] rounded-[25px] border border-solid absolute overflow-hidden"
          aria-label="Next"
        >
          <span className="relative w-fit mt-[-1.00px] [font-family:'Onest-Bold',Helvetica] font-bold text-variable-collection-black text-[40px] text-center tracking-[0] leading-[normal]">
            &gt;
          </span>
        </button>

        <div className="flex w-[520px] items-center px-5 py-2.5 top-[315px] left-11 bg-white rounded-[20px] absolute overflow-hidden border-variable-collection-black">
          <label className="relative w-fit mt-[-1.00px] [font-family:'Onest-Medium',Helvetica] font-normal text-variable-collection-black text-xl tracking-[0] leading-[normal]">
            <span className="font-medium text-[#212121]">
              Budget
              <br />
            </span>
            <span className="[font-family:'Onest-Regular',Helvetica] text-[#a1a1a1]">
              {budgetRange}
            </span>
          </label>
        </div>

        <div className="flex w-[520px] items-center px-[5px] py-2.5 top-[404px] left-11 rounded-[20px] absolute overflow-hidden border-variable-collection-black">
          <h2 className="relative w-fit mt-[-1.00px] [font-family:'Onest-Medium',Helvetica] font-medium text-variable-collection-black text-xl tracking-[0] leading-[normal]">
            Pick your interests!
          </h2>
        </div>

        <button
          type="button"
          className="inline-flex top-[131px] left-[98px] border-[#d8dfe9] rotate-180 items-center justify-center px-5 py-2.5 absolute rounded-[25px] overflow-hidden border border-solid"
          aria-label="Previous"
        >
          <span className="relative w-fit mt-[-1.00px] [font-family:'Onest-Bold',Helvetica] font-bold text-variable-collection-black text-[40px] text-center tracking-[0] leading-[normal]">
            &gt;
          </span>
        </button>

        <button
          type="button"
          className="flex w-[520px] h-[70px] top-[638px] left-11 bg-[#231f20] border-variable-collection-black items-center justify-center px-5 py-2.5 absolute rounded-[25px] overflow-hidden border border-solid"
        >
          <span className="relative w-fit [font-family:'Onest-Bold',Helvetica] font-bold text-[#efefef] text-xl text-center tracking-[0] leading-[normal]">
            I&apos;m happy with my profile!
          </span>
        </button>

        <div className="absolute top-[458px] left-11 flex flex-wrap gap-[11px]">
          {interests.slice(0, 3).map((interest) => (
            <button
              key={interest.id}
              type="button"
              onClick={() => toggleInterest(interest.label)}
              className={`inline-flex items-center justify-center px-5 py-2.5 rounded-[25px] border border-solid border-variable-collection-black overflow-hidden ${
                isSelected(interest.label) ? "bg-[#eeefa4]" : "bg-transparent"
              }`}
              aria-pressed={isSelected(interest.label)}
            >
              <span className="relative w-fit mt-[-1.00px] [font-family:'Onest-Bold',Helvetica] font-bold text-[#231f20] text-xl text-center tracking-[0] leading-[normal]">
                {interest.label}
              </span>
            </button>
          ))}
        </div>

        <button
          type="button"
          onClick={() => toggleInterest(interests[3].label)}
          className={`inline-flex items-center justify-center px-5 py-2.5 top-[521px] left-11 rounded-[25px] border border-solid border-variable-collection-black absolute overflow-hidden ${
            isSelected(interests[3].label) ? "bg-[#d8dfe9]" : "bg-transparent"
          }`}
          aria-pressed={isSelected(interests[3].label)}
        >
          <span className="relative w-fit mt-[-1.00px] [font-family:'Onest-Bold',Helvetica] font-bold text-[#231f20] text-xl text-center tracking-[0] leading-[normal]">
            {interests[3].label}
          </span>
        </button>
      </main>

      <img
        className="absolute w-[8.13%] h-[12.53%] top-[24.62%] left-[46.25%]"
        alt="Turle pink"
        src={turlePink.src}
      />
    </div>
  );
};
