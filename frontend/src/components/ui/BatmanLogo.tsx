import React from 'react';

interface BatmanLogoProps {
  className?: string;
  size?: number;
}

export const BatmanLogo: React.FC<BatmanLogoProps> = ({ 
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
      {/* Batman symbol - simplified bat */}
      <path
        d="M 50 25 L 45 30 C 40 32, 35 35, 30 40 L 25 45 C 23 47, 20 50, 18 55 L 15 60 L 20 58 C 25 56, 30 54, 35 52 L 40 50 L 42 55 C 43 57, 44 60, 45 65 L 46 70 L 50 60 L 54 70 L 55 65 C 56 60, 57 57, 58 55 L 60 50 L 65 52 C 70 54, 75 56, 80 58 L 85 60 L 82 55 C 80 50, 77 47, 75 45 L 70 40 C 65 35, 60 32, 55 30 L 50 25 Z"
        fill="currentColor"
        stroke="currentColor"
        strokeWidth="1"
        strokeLinejoin="round"
      />
      
      {/* Wing tips */}
      <path
        d="M 15 60 L 10 65 L 8 68 L 12 66 L 15 60 Z"
        fill="currentColor"
      />
      <path
        d="M 85 60 L 90 65 L 92 68 L 88 66 L 85 60 Z"
        fill="currentColor"
      />
      
      {/* Head detail */}
      <circle
        cx="50"
        cy="27"
        r="3"
        fill="currentColor"
      />
    </svg>
  );
};

export const BatSignalLogo: React.FC<BatmanLogoProps> = ({ 
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
      {/* Outer glow circle */}
      <circle
        cx="50"
        cy="50"
        r="48"
        fill="none"
        stroke="currentColor"
        strokeWidth="1"
        opacity="0.3"
      />
      
      {/* Inner circle */}
      <circle
        cx="50"
        cy="50"
        r="35"
        fill="currentColor"
        opacity="0.1"
      />
      
      {/* Bat symbol in center */}
      <path
        d="M 50 35 L 47 37 C 44 38, 41 40, 38 43 L 35 46 C 34 47, 32 49, 31 51 L 29 54 L 32 53 C 35 52, 38 51, 41 50 L 43 49 L 44 52 C 45 53, 45 55, 46 57 L 47 60 L 50 53 L 53 60 L 54 57 C 55 55, 55 53, 56 52 L 57 49 L 59 50 C 62 51, 65 52, 68 53 L 71 54 L 69 51 C 68 49, 66 47, 65 46 L 62 43 C 59 40, 56 38, 53 37 L 50 35 Z"
        fill="currentColor"
      />
    </svg>
  );
};
