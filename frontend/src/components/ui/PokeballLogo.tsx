import React from 'react';

interface PokeballLogoProps {
  className?: string;
  size?: number;
}

export const PokeballLogo: React.FC<PokeballLogoProps> = ({ 
  className = '', 
  size = 40 
}) => {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 100 100"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      {/* Outer circle */}
      <circle
        cx="50"
        cy="50"
        r="48"
        stroke="currentColor"
        strokeWidth="2"
        fill="none"
      />
      
      {/* Top half - Red */}
      <path
        d="M 2 50 A 48 48 0 0 1 98 50 L 65 50 A 15 15 0 0 0 35 50 Z"
        fill="#DC0A2D"
        stroke="currentColor"
        strokeWidth="1"
      />
      
      {/* Bottom half - White */}
      <path
        d="M 2 50 A 48 48 0 0 0 98 50 L 65 50 A 15 15 0 0 1 35 50 Z"
        fill="#FFFFFF"
        stroke="currentColor"
        strokeWidth="1"
      />
      
      {/* Center line */}
      <line
        x1="2"
        y1="50"
        x2="35"
        y2="50"
        stroke="currentColor"
        strokeWidth="2"
      />
      <line
        x1="65"
        y1="50"
        x2="98"
        y2="50"
        stroke="currentColor"
        strokeWidth="2"
      />
      
      {/* Center button - outer circle */}
      <circle
        cx="50"
        cy="50"
        r="15"
        fill="#FFFFFF"
        stroke="currentColor"
        strokeWidth="2"
      />
      
      {/* Center button - inner circle */}
      <circle
        cx="50"
        cy="50"
        r="8"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
      />
    </svg>
  );
};

interface PikachuLogoProps {
  className?: string;
  size?: number;
}

export const PikachuLogo: React.FC<PikachuLogoProps> = ({ 
  className = '', 
  size = 40 
}) => {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 100 100"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      {/* Lightning bolt - Pikachu themed */}
      <path
        d="M 50 10 L 35 45 L 50 45 L 40 80 L 70 40 L 55 40 Z"
        fill="#FFCB05"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinejoin="round"
      />
      
      {/* Electric sparkles */}
      <circle cx="25" cy="30" r="3" fill="#F7D02C" />
      <circle cx="75" cy="35" r="2.5" fill="#F7D02C" />
      <circle cx="30" cy="70" r="2" fill="#F7D02C" />
      <circle cx="70" cy="65" r="3" fill="#F7D02C" />
    </svg>
  );
};
