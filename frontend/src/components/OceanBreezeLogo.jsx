import React from 'react';

export default function OceanBreezeLogo({ className = "w-8 h-8", animated = true }) {
  return (
    <div className={`relative flex items-center justify-center ${className}`}>
      <svg
        className="w-full h-full text-[#0E6E6A] overflow-visible"
        viewBox="0 0 48 48"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          {/* Gradient for Ocean Wind Breeze Ribbon */}
          <linearGradient id="breezeGrad1" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#0E6E6A" stopOpacity="0.2" />
            <stop offset="50%" stopColor="#0E6E6A" stopOpacity="1" />
            <stop offset="100%" stopColor="#276A4E" stopOpacity="0.9" />
          </linearGradient>

          <linearGradient id="breezeGrad2" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#276A4E" stopOpacity="0.3" />
            <stop offset="60%" stopColor="#2B4C6F" stopOpacity="1" />
            <stop offset="100%" stopColor="#0E6E6A" stopOpacity="0.8" />
          </linearGradient>

          {/* Ship Hull Gradient */}
          <linearGradient id="shipHullGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#10201E" />
            <stop offset="60%" stopColor="#183632" />
            <stop offset="100%" stopColor="#0E6E6A" />
          </linearGradient>

          {/* Glow filter for Navigation Beacon */}
          <filter id="beaconGlow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="2" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
        </defs>

        {/* --- 1. SWIRLING OCEAN BREEZE WIND CURRENTS --- */}
        <path
          d="M 3 14 C 14 6, 32 6, 45 12"
          stroke="url(#breezeGrad1)"
          strokeWidth="2.5"
          strokeLinecap="round"
          className={animated ? "animate-pulse" : ""}
        />
        <path
          d="M 2 22 C 12 16, 30 16, 46 20"
          stroke="url(#breezeGrad2)"
          strokeWidth="2"
          strokeLinecap="round"
        />

        {/* --- 2. OCEAN WAVE SWELLS & WATER SURGE --- */}
        <path
          d="M 4 34 Q 12 29, 20 34 T 36 34 T 44 32"
          stroke="#0E6E6A"
          strokeWidth="2.5"
          strokeLinecap="round"
          fill="none"
        />
        <path
          d="M 2 39 Q 11 35, 22 39 T 42 37"
          stroke="#2B4C6F"
          strokeWidth="1.8"
          strokeLinecap="round"
          fill="none"
          opacity="0.75"
        />

        {/* --- 3. COMMERCIAL CARGO SHIP PASSING THROUGH BREEZE --- */}
        {/* Sleek Hull slicing forward */}
        <path
          d="M 12 30 L 36 27 C 40 27, 43 24, 44 20 L 29 19 L 16 22 Z"
          fill="url(#shipHullGrad)"
          stroke="#10201E"
          strokeWidth="1"
        />

        {/* Cargo Containers Stacks (Teal, Amber, Red) */}
        <rect x="20" y="16" width="4.5" height="5" fill="#0E6E6A" rx="0.5" stroke="#10201E" strokeWidth="0.4" />
        <rect x="26" y="15.5" width="4.5" height="5.5" fill="#B07A2C" rx="0.5" stroke="#10201E" strokeWidth="0.4" />
        <rect x="32" y="15" width="4.5" height="6" fill="#B23A2E" rx="0.5" stroke="#10201E" strokeWidth="0.4" />

        {/* Superstructure Bridge & Radar Mast */}
        <path d="M 15 17 L 19 17 L 19 23 L 15 23 Z" fill="#FAFBFA" stroke="#10201E" strokeWidth="0.6" />
        <line x1="17" y1="17" x2="17" y2="12" stroke="#10201E" strokeWidth="1" />

        {/* Bow Wave Spray / White Water Wake */}
        <path
          d="M 37 27 Q 42 28, 46 25"
          stroke="#FAFBFA"
          strokeWidth="2"
          strokeLinecap="round"
        />
        <path
          d="M 32 29 Q 38 31, 44 28"
          stroke="#E4EFEE"
          strokeWidth="1.2"
          strokeLinecap="round"
          opacity="0.8"
        />

        {/* --- 4. GLOWING NAVIGATION BEACON --- */}
        <circle cx="17" cy="12" r="2" fill="#0E6E6A" filter="url(#beaconGlow)" />
        <circle cx="17" cy="12" r="0.8" fill="#FAFBFA" />
      </svg>
    </div>
  );
}
