import React from 'react';

interface SupermanLogoProps {
  className?: string;
  size?: number;
}

export const SupermanLogo: React.FC<SupermanLogoProps> = ({ 
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
      {/* Shield background */}
      <path
        d="M 50 10 L 80 30 L 80 70 L 50 90 L 20 70 L 20 30 Z"
        fill="#CE1126"
        stroke="currentColor"
        strokeWidth="2"
      />
      
      {/* Yellow S shield inner */}
      <path
        d="M 50 20 L 72 35 L 72 65 L 50 80 L 28 65 L 28 35 Z"
        fill="#FCD116"
      />
      
      {/* S letter path */}
      <path
        d="M 60 38 C 60 35, 58 33, 55 33 L 45 33 C 42 33, 40 35, 40 38 L 40 42 L 48 42 L 48 40 L 52 40 L 52 45 L 42 45 C 39 45, 37 47, 37 50 L 37 55 C 37 58, 39 60, 42 60 L 55 60 C 58 60, 60 58, 60 55 L 60 52 L 52 52 L 52 54 L 48 54 L 48 50 L 58 50 C 61 50, 63 48, 63 45 L 63 38 Z"
        fill="#CE1126"
      />
    </svg>
  );
};

export const HopeSymbol: React.FC<SupermanLogoProps> = ({ 
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
      {/* Outer glow */}
      <circle
        cx="50"
        cy="50"
        r="45"
        fill="none"
        stroke="currentColor"
        strokeWidth="1"
        opacity="0.3"
      />
      
      {/* Shield shape */}
      <path
        d="M 50 15 L 75 32 L 75 68 L 50 85 L 25 68 L 25 32 Z"
        fill="currentColor"
        opacity="0.15"
      />
      
      {/* S symbol simplified */}
      <text
        x="50"
        y="65"
        fontSize="48"
        fontWeight="bold"
        textAnchor="middle"
        fill="currentColor"
        fontFamily="Arial, sans-serif"
      >
        S
      </text>
    </svg>
  );
};
