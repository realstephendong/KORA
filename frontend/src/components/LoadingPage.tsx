'use client';

import React from 'react';
import { motion } from 'framer-motion';

interface LoadingPageProps {
  message?: string;
  showTurtle?: boolean;
}

export default function LoadingPage({ 
  message = "Loading...", 
  showTurtle = true 
}: LoadingPageProps) {
  return (
    <div className="w-full h-screen bg-gradient-to-br from-[#F6F5FA] via-[#E8E7F0] to-[#F6F5FA] flex items-center justify-center overflow-hidden">
      <div className="text-center">
        {/* Animated turtle */}
        {showTurtle && (
          <motion.div
            className="mb-8"
            animate={{
              y: [0, -10, 0],
              rotate: [0, 5, -5, 0]
            }}
            transition={{
              duration: 3,
              repeat: Infinity,
              ease: "easeInOut"
            }}
          >
            <img
              src="https://c.animaapp.com/M8phbEWm/img/sea-turtle-02-2.svg"
              alt="Sea turtle"
              className="w-20 h-20 mx-auto"
            />
          </motion.div>
        )}

        {/* Loading spinner */}
        <motion.div
          className="relative mb-6"
          animate={{ rotate: 360 }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: "linear"
          }}
        >
          <div className="w-16 h-16 border-4 border-[#D8DFE9] border-t-[#212121] rounded-full mx-auto"></div>
        </motion.div>

        {/* Loading text */}
        <motion.p
          className="text-xl font-['Onest'] text-[#212121] font-medium"
          animate={{
            opacity: [0.5, 1, 0.5]
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        >
          {message}
        </motion.p>

        {/* Floating dots */}
        <div className="flex justify-center space-x-2 mt-6">
          {[0, 1, 2].map((i) => (
            <motion.div
              key={i}
              className="w-2 h-2 bg-[#212121] rounded-full"
              animate={{
                y: [0, -10, 0],
                opacity: [0.3, 1, 0.3]
              }}
              transition={{
                duration: 1.5,
                repeat: Infinity,
                delay: i * 0.2,
                ease: "easeInOut"
              }}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
