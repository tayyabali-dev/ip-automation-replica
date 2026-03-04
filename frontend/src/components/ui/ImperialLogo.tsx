'use client';

import React from 'react';

interface ImperialLogoProps {
  className?: string;
  size?: number;
}

// Galactic Empire-style cog/gear logo
export function ImperialLogo({ className = '', size = 40 }: ImperialLogoProps) {
  return (
    <svg
      viewBox="0 0 100 100"
      width={size}
      height={size}
      className={className}
      fill="currentColor"
    >
      {/* Outer ring */}
      <circle cx="50" cy="50" r="45" fill="none" stroke="currentColor" strokeWidth="3" opacity="0.9" />
      {/* Inner ring */}
      <circle cx="50" cy="50" r="30" fill="none" stroke="currentColor" strokeWidth="2" opacity="0.7" />
      {/* Center dot */}
      <circle cx="50" cy="50" r="8" fill="currentColor" />
      {/* 6 spokes */}
      <line x1="50" y1="5" x2="50" y2="20" stroke="currentColor" strokeWidth="4" strokeLinecap="round" />
      <line x1="50" y1="80" x2="50" y2="95" stroke="currentColor" strokeWidth="4" strokeLinecap="round" />
      <line x1="11" y1="27.5" x2="24" y2="35" stroke="currentColor" strokeWidth="4" strokeLinecap="round" />
      <line x1="76" y1="65" x2="89" y2="72.5" stroke="currentColor" strokeWidth="4" strokeLinecap="round" />
      <line x1="11" y1="72.5" x2="24" y2="65" stroke="currentColor" strokeWidth="4" strokeLinecap="round" />
      <line x1="76" y1="35" x2="89" y2="27.5" stroke="currentColor" strokeWidth="4" strokeLinecap="round" />
      {/* Outer triangles/teeth */}
      <polygon points="50,2 46,12 54,12" fill="currentColor" opacity="0.8" />
      <polygon points="50,98 46,88 54,88" fill="currentColor" opacity="0.8" />
      <polygon points="8,25 14,33 18,26" fill="currentColor" opacity="0.8" />
      <polygon points="92,75 86,67 82,74" fill="currentColor" opacity="0.8" />
      <polygon points="8,75 14,67 18,74" fill="currentColor" opacity="0.8" />
      <polygon points="92,25 86,33 82,26" fill="currentColor" opacity="0.8" />
    </svg>
  );
}

// Rebel Alliance-style phoenix logo
export function RebelLogo({ className = '', size = 40 }: ImperialLogoProps) {
  return (
    <svg
      viewBox="0 0 100 100"
      width={size}
      height={size}
      className={className}
      fill="currentColor"
    >
      <path d="M50 8 C50 8, 35 30, 20 50 C10 65, 15 80, 30 85 C35 87, 40 85, 45 80 L50 70 L55 80 C60 85, 65 87, 70 85 C85 80, 90 65, 80 50 C65 30, 50 8, 50 8Z" />
      <circle cx="50" cy="55" r="6" fill="none" stroke="currentColor" strokeWidth="2" />
      <circle cx="50" cy="55" r="2" />
    </svg>
  );
}
