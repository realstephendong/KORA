'use client';

import React from "react";
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import ProtectedRoute from '@/components/ProtectedRoute';
import { useEffect, useState } from 'react';

interface TripInfo {
  icon: string;
  text: string;
  alt: string;
}

interface DayItinerary {
  day: number;
  location: string;
  description: string;
}

interface CarbonEmissionsData {
  carbon_emissions_kg: number;
  fuel_used_liters: number;
  distance_km: number;
  total_distance_km: number;
  fuel_rate_liters_per_km: number;
  stops: number;
  aircraft_model: string;
}

interface TreeData {
  trees_saved: number;
  trees_needed_to_offset: number;
  carbon_emissions_kg: number;
  environmental_impact: {
    plastic_bags_equivalent: number;
    gasoline_equivalent_gallons: number;
    coal_electricity_equivalent_kwh: number;
    sustainability_factor: number;
  };
  flight_details: {
    aircraft_model: string;
    origin_city: string;
    destination_city: string;
    stops: number;
    distance_km: number;
    total_distance_km: number;
  };
}

interface PlasticBagData {
  plastic_bags_saved: number;
  plastic_bags_needed_to_produce: number;
  carbon_emissions_kg: number;
  environmental_impact: {
    trees_equivalent: number;
    gasoline_equivalent_gallons: number;
    coal_electricity_equivalent_kwh: number;
    sustainability_factor: number;
  };
  flight_details: {
    aircraft_model: string;
    origin_city: string;
    destination_city: string;
    stops: number;
    distance_km: number;
    total_distance_km: number;
  };
}


export default function ResultPage() {
  const { user, isLoading } = useAuth();
  const router = useRouter();
  const [carbonData, setCarbonData] = useState<CarbonEmissionsData | null>(null);
  const [treeData, setTreeData] = useState<TreeData | null>(null);
  const [plasticBagData, setPlasticBagData] = useState<PlasticBagData | null>(null);

  const tripInfoData: TripInfo[] = [
    {
      icon: "https://c.animaapp.com/7Y4W5hAe/img/location-on@2x.png",
      text: "France",
      alt: "Location on",
    },
    {
      icon: "https://c.animaapp.com/7Y4W5hAe/img/map-1@2x.png",
      text: "Paris, Lyon",
      alt: "Map",
    },
    {
      icon: "https://c.animaapp.com/7Y4W5hAe/img/map-1@2x.png",
      text: "5 Days",
      alt: "Map",
    },
  ];

  const itineraryData: DayItinerary[] = [
    {
      day: 1,
      location: "Paris",
      description:
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. \n\nUt enim ad minim veniam, \nquis nostrud exercitation \nullamco laboris nisi ut aliquip ex ea commodo consequat.\n\nDuis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.",
    },
    {
      day: 2,
      location: "Paris",
      description:
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. \n\nUt enim ad minim veniam, \nquis nostrud exercitation \nullamco laboris nisi ut aliquip ex ea commodo consequat.\n\nDuis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.",
    },
    {
      day: 3,
      location: "Lyon",
      description:
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. \n\nUt enim ad minim veniam, \nquis nostrud exercitation \nullamco laboris nisi ut aliquip ex ea commodo consequat.\n\nDuis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.",
    },
  ];

  const handleBackToGlobe = () => {
    router.push('/globe');
  };

  const handleNewSearch = () => {
    router.push('/chat');
  };

  const fetchCarbonData = async () => {
    try {
      const response = await fetch('/api/carbon-data');
      if (response.ok) {
        const data = await response.json();
        setCarbonData(data);
      } else {
        console.error('Failed to fetch carbon data');
      }
    } catch (error) {
      console.error('Error fetching carbon data:', error);
    }
  };

  const fetchTreeData = async () => {
    try {
      const response = await fetch('/api/tree-data');
      if (response.ok) {
        const data = await response.json();
        setTreeData(data);
      } else {
        console.error('Failed to fetch tree data');
      }
    } catch (error) {
      console.error('Error fetching tree data:', error);
    }
  };

  const fetchPlasticBagData = async () => {
    try {
      const response = await fetch('/api/plastic-bag-data');
      if (response.ok) {
        const data = await response.json();
        setPlasticBagData(data);
      } else {
        console.error('Failed to fetch plastic bag data');
      }
    } catch (error) {
      console.error('Error fetching plastic bag data:', error);
    }
  };


  // Calculate environmental impact metrics
  const calculateEnvironmentalImpact = (emissionsKg: number) => {
    // 1 tree absorbs approximately 22 kg CO2 per year
    const treesSaved = Math.round(emissionsKg / 22);
    
    // 1 plastic bag produces approximately 0.33 kg CO2
    const plasticBagsSaved = Math.round(emissionsKg / 0.33);
    
    return { treesSaved, plasticBagsSaved };
  };

  // Fetch carbon, tree, and plastic bag data on component mount
  useEffect(() => {
    fetchCarbonData();
    fetchTreeData();
    fetchPlasticBagData();
  }, []);

  if (isLoading) {
    return (
      <ProtectedRoute>
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-lg text-gray-600 font-medium">Loading your results...</p>
          </div>
        </div>
      </ProtectedRoute>
    );
  }

  return (
    <ProtectedRoute>
      <div
        className="bg-[linear-gradient(0deg,rgba(246,245,250,1)_0%,rgba(246,245,250,1)_100%)] w-full min-w-[1920px] h-[2618px] relative"
        data-model-id="68:1178"
      >
        {/* Main background container */}
        <div className="absolute top-[39px] left-0 w-[1920px] h-[2579px] rounded-[50px] border-2 border-solid border-[#d8dfe980] bg-[linear-gradient(180deg,rgba(216,223,233,0.25)_0%,rgba(216,223,233,0)_100%),linear-gradient(0deg,rgba(246,245,250,1)_0%,rgba(246,245,250,1)_100%)]" />

        {/* Sea turtle logo */}
        <button
          onClick={() => router.push('/landing')}
          className="absolute top-[77px] left-[89px] w-[74px] h-[73px] bg-transparent border-none cursor-pointer"
        >
          <img
            className="w-full h-full"
            alt="Sea turtle"
            src="https://c.animaapp.com/7Y4W5hAe/img/sea-turtle-02-2.svg"
          />
        </button>

        {/* Trip info bar */}
        <div className="flex w-[606px] items-center justify-between pl-10 pr-2.5 py-5 absolute top-[82px] left-[659px] bg-white rounded-[40px] overflow-hidden border-[none] before:content-[''] before:absolute before:inset-0 before:p-[5px] before:rounded-[40px] before:[background:linear-gradient(1deg,rgba(238,239,164,0)_0%,rgba(238,239,164,1)_100%)] before:[-webkit-mask:linear-gradient(#fff_0_0)_content-box,linear-gradient(#fff_0_0)] before:[-webkit-mask-composite:xor] before:[mask-composite:exclude] before:z-[1] before:pointer-events-none">
          {tripInfoData.map((info, index) => (
            <div
              key={index}
              className={`${
                index === 2 ? "flex w-[138px]" : "inline-flex flex-[0_0_auto]"
              } items-center gap-2.5 relative`}
            >
              <img
                className="relative w-6 h-6 aspect-[1]"
                alt={info.alt}
                src={info.icon}
              />
              <div className="relative w-fit mt-[-1.00px] [font-family:'Onest',Helvetica] font-medium text-variable-collection-black text-xl tracking-[0] leading-[normal]">
                {info.text}
              </div>
            </div>
          ))}
        </div>

        {/* Congratulations section */}
        <div className="absolute top-[251px] left-[648px] w-[607px] h-[855px] rounded-[50px] overflow-hidden border-2 border-solid border-[#d8dfe980] backdrop-blur-sm backdrop-brightness-[100%] [-webkit-backdrop-filter:blur(4px)_brightness(100%)] bg-[linear-gradient(180deg,rgba(216,223,233,0.25)_0%,rgba(216,223,233,0)_100%),linear-gradient(0deg,rgba(255,255,255,0.2)_0%,rgba(255,255,255,0.2)_100%)]">
          <div className="absolute top-16 left-[77px] w-[454px] [font-family:'Onest',Helvetica] font-medium text-variable-collection-grey text-[25px] text-center tracking-[0] leading-[normal]">
            We&apos;ve calculated your trip!
          </div>

          <p className="absolute top-[695px] left-[93px] w-[454px] [font-family:'Onest',Helvetica] font-medium text-variable-collection-grey text-[25px] text-center tracking-[0] leading-[normal]">
            {treeData && plasticBagData && carbonData ? (
              <>
                You&apos;ve saved the equivalent of {treeData.trees_saved.toFixed(0)} trees, {plasticBagData.plastic_bags_saved.toLocaleString()} plastic bags from
                polluting the sea, and of course! {carbonData.carbon_emissions_kg.toFixed(0)} kg of CO₂ emissions avoided.
              </>
            ) : (
              <>
                You&apos;ve saved the equivalent of xxx trees, xxx plastic bags from
                polluting the sea, and of course! xx ...
              </>
            )}
          </p>

          <div className="absolute top-[108px] left-[77px] w-[454px] [font-family:'Libre_Baskerville',Helvetica] font-normal italic text-variable-collection-black text-[50px] text-center tracking-[0] leading-[normal]">
            Congratulations!
          </div>

          {/* Bar chart elements */}
          <div className="top-[234px] left-[186px] w-[45px] h-[397px] bg-white absolute rounded-[38.5px]" />
          <div className="top-[482px] left-48 w-[33px] h-[142px] bg-[#cfdecb] absolute rounded-[38.5px]" />
          <div className="top-[234px] left-[281px] w-[45px] h-[397px] bg-white absolute rounded-[38.5px]" />
          <div className="top-[234px] left-[376px] w-[45px] h-[397px] bg-white absolute rounded-[38.5px]" />
          <div className="top-[392px] left-[287px] w-[33px] h-[232px] bg-[#abc7f0] absolute rounded-[38.5px]" />
          <div className="top-[444px] left-[382px] w-[33px] h-[180px] bg-[#f1f37e] absolute rounded-[38.5px]" />

          <img
            className="absolute top-[436px] left-[169px] w-[85px] h-[91px]"
            alt="Tree"
            src="https://c.animaapp.com/7Y4W5hAe/img/tree2@2x.png"
          />

          <img
            className="absolute top-[360px] left-[269px] w-[69px] h-[73px]"
            alt="Trash bag"
            src="https://c.animaapp.com/7Y4W5hAe/img/trash-bag@2x.png"
          />
        </div>

        {/* Itinerary section */}
        <div className="absolute top-[1242px] left-[469px] w-[961px] h-[1069px] rounded-[50px] overflow-hidden bg-[linear-gradient(195deg,rgba(216,223,233,0)_0%,rgba(216,223,233,1)_100%),linear-gradient(0deg,rgba(246,245,250,1)_0%,rgba(246,245,250,1)_100%)]">
          <div className="absolute top-0 left-[-57px] w-[2047px] h-[1387px] bg-[#231f20] rounded-[50px] overflow-hidden border border-solid border-black">
            <img
              className="absolute top-[214px] left-[122px] w-[832px] h-[3px]"
              alt="Vector"
              src="https://c.animaapp.com/7Y4W5hAe/img/vector-6.svg"
            />

            <div className="absolute top-[100px] left-[474px] w-[165px] [font-family:'Libre_Baskerville',Helvetica] font-normal italic text-[#f6f5fa] text-[50px] tracking-[0] leading-[normal]">
              France
            </div>

            <div className="absolute top-[155px] left-[390px] w-[334px] [font-family:'Onest',Helvetica] font-medium text-variable-collection-grey text-[25px] text-center tracking-[0] leading-[normal]">
              Paris, Lyon
            </div>
          </div>

          {itineraryData.map((day, index) => (
            <p
              key={index}
              className={`absolute w-[828px] [font-family:'Onest',Helvetica] font-medium text-variable-collection-white text-[25px] tracking-[0] leading-[normal]`}
              style={{
                top: `${247 + index * 334}px`,
                left: index === 2 ? "66px" : "70px",
              }}
            >
              <span className="text-[#f6f5fa]">
                Day {day.day} | {day.location}
                <br />
              </span>

              <span className="text-[#f6f5fa] text-xl">
                <br />
              </span>

              <span className="text-[#a1a1a1] text-xl">
                {day.description.split("\n").map((line, lineIndex) => (
                  <React.Fragment key={lineIndex}>
                    {line}
                    {lineIndex < day.description.split("\n").length - 1 && <br />}
                  </React.Fragment>
                ))}
              </span>
            </p>
          ))}

          <img
            className="absolute top-[334px] left-[930px] w-1 h-[466px]"
            alt="Line"
            src="https://c.animaapp.com/7Y4W5hAe/img/line-2.svg"
          />

          <img
            className="absolute w-[6.24%] h-[5.93%] top-[3.32%] left-[49.43%]"
            alt="Turle pink"
            src="https://c.animaapp.com/7Y4W5hAe/img/turle-pink@2x.png"
          />
        </div>

        {/* Action buttons */}
        <button
          onClick={handleBackToGlobe}
          className="absolute top-[2363px] left-[857px] w-[66px] h-[66px] bg-transparent border-none cursor-pointer"
        >
          <img
            className="w-full h-full"
            alt="Group"
            src="https://c.animaapp.com/7Y4W5hAe/img/group-4@2x.png"
          />
        </button>

        <button
          onClick={handleNewSearch}
          className="absolute top-[2363px] left-[981px] w-[66px] h-[66px] bg-transparent border-none cursor-pointer"
        >
          <img
            className="w-full h-full"
            alt="Group"
            src="https://c.animaapp.com/7Y4W5hAe/img/group-5@2x.png"
          />
        </button>

        {/* Settings icon */}
        <button
          onClick={() => router.push('/profile')}
          className="absolute w-[3.23%] h-[2.37%] top-[2.44%] left-[94.22%] bg-transparent border-none cursor-pointer"
        >
          <img
            className="w-full h-full"
            alt="Group"
            src="https://c.animaapp.com/7Y4W5hAe/img/group-6@2x.png"
          />
        </button>
      </div>
    </ProtectedRoute>
  );
}