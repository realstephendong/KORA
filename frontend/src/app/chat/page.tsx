import React, { useState } from "react";

export const Chatbox = () => {
  const [inputValue, setInputValue] = useState("");
  const [location, setLocation] = useState("France");

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInputValue(e.target.value);
  };

  const handleSubmit = () => {
    if (inputValue.trim()) {
      console.log("Submitted:", inputValue);
      setInputValue("");
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      handleSubmit();
    }
  };

  return (
    <div className="bg-[linear-gradient(0deg,rgba(246,245,250,1)_0%,rgba(246,245,250,1)_100%)] w-full min-w-[1920px] min-h-[1316px] relative">
      <main className="absolute top-[39px] left-0 w-[1920px] h-[1214px] rounded-[50px] overflow-hidden border-2 border-solid border-[#d8dfe980] bg-[linear-gradient(180deg,rgba(216,223,233,0.25)_0%,rgba(216,223,233,0)_100%),linear-gradient(0deg,rgba(246,245,250,1)_0%,rgba(246,245,250,1)_100%)]">
        <section
          className="absolute top-[294px] left-[482px] w-[955px] h-[498px] rounded-[40px] overflow-hidden border-2 border-solid border-[#d8dfe9] bg-[linear-gradient(180deg,rgba(216,223,233,0)_0%,rgba(218,224,234,0.3)_100%),linear-gradient(0deg,rgba(239,240,164,0)_0%,rgba(239,240,164,0)_100%)]"
          aria-label="Chat conversation"
        >
          <div className="inline-flex items-center justify-center gap-2.5 p-[15px] absolute top-[363px] left-[282px] rounded-[25px] overflow-hidden border border-solid border-black">
            <p className="relative w-fit mt-[-0.50px] [font-family:'Onest-Medium',Helvetica] font-medium text-black text-xl tracking-[0] leading-[normal]">
              What cities are you interested in?
            </p>
          </div>

          <div className="absolute top-[420px] left-0 w-[955px] h-[78px] bg-[#486a9b]" />
        </section>

        <div className="absolute top-[818px] left-[482px] w-[955px] h-[102px] flex gap-[387px] rounded-[50px] overflow-hidden border-2 border-solid border-[#d8dfe980] bg-[linear-gradient(180deg,rgba(216,223,233,0.25)_0%,rgba(216,223,233,0)_100%),linear-gradient(0deg,rgba(255,255,255,0.2)_0%,rgba(255,255,255,0.2)_100%)]">
          <label htmlFor="chat-input" className="sr-only">
            Ask Kora anything about your travel plans
          </label>
          <input
            id="chat-input"
            type="text"
            value={inputValue}
            onChange={handleInputChange}
            onKeyPress={handleKeyPress}
            placeholder="Ask Kora anything about your travel plans"
            className="mt-[38px] w-[454px] h-[26px] ml-[45px] [font-family:'Onest-Light',Helvetica] font-light text-variable-collection-grey text-xl tracking-[0] leading-[normal] bg-transparent placeholder:text-variable-collection-grey"
            aria-label="Chat input"
          />

          <button
            onClick={handleSubmit}
            className="mt-[31px] w-10 h-10 flex bg-variable-collection-black rounded-[20px] cursor-pointer hover:opacity-90 transition-opacity"
            aria-label="Send message"
            type="button"
          >
            <img
              className="mt-2 w-6 h-6 ml-2 aspect-[1]"
              alt=""
              src="/chat/arrowButton.svg"
            />
          </button>
        </div>

        <img
          className="absolute w-[3.23%] h-[5.11%] top-[3.05%] left-[94.22%]"
          alt="Menu"
          src="/chat/arrowButton.svg"
        />
      </main>

      <img
        className="absolute top-[77px] left-[89px] w-[74px] h-[73px]"
        alt="Kora logo"
        src="/chat/sea turtle-02 2.svg"
      />

      <div className="flex w-[606px] items-center justify-between pl-10 pr-2.5 py-2.5 absolute top-[82px] left-[659px] bg-white rounded-[40px] overflow-hidden border-[none] before:content-[''] before:absolute before:inset-0 before:p-[5px] before:rounded-[40px] before:[background:linear-gradient(1deg,rgba(238,239,164,0)_0%,rgba(238,239,164,1)_100%)] before:[-webkit-mask:linear-gradient(#fff_0_0)_content-box,linear-gradient(#fff_0_0)] before:[-webkit-mask-composite:xor] before:[mask-composite:exclude] before:z-[1] before:pointer-events-none">
        <div className="inline-flex items-center gap-2.5 relative flex-[0_0_auto]">
          <img
            className="relative w-6 h-6 aspect-[1]"
            alt=""
            src="/chat/arrowButton.svg"
          />

          <div className="relative w-fit mt-[-1.00px] [font-family:'Onest-Medium',Helvetica] font-medium text-variable-collection-black text-xl tracking-[0] leading-[normal]">
            {location}
          </div>
        </div>

        <button
          className="relative w-10 h-10 bg-variable-collection-black rounded-[20px] cursor-pointer hover:opacity-90 transition-opacity"
          aria-label="Search location"
          type="button"
        >
          <div className="relative top-2 left-[9px] w-[21px] h-[25px]">
            <div className="absolute top-0 left-0 w-[19px] h-[19px] bg-variable-collection-black rounded-[9.43px] border-[1.5px] border-solid border-white" />

            <img
              className="absolute top-[15px] left-3 w-[9px] h-2.5"
              alt=""
              src="/chat/arrowButton.svg"
            />
          </div>
        </button>
      </div>

      <img
        className="absolute top-[593px] left-[527px] w-[230px] h-[186px]"
        alt="Kora character illustration"
        src="/chat/sea zine-03 1.svg"
      />
    </div>
  );
};