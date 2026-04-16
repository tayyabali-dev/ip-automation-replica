import React from 'react';

interface OmnitrixLogoProps {
  className?: string;
  size?: number;
}

export const OmnitrixLogo: React.FC<OmnitrixLogoProps> = ({ 
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
      <circle cx="50" cy="50" r="46" stroke="currentColor" strokeWidth="2" fill="#0a0a0a" />
      <circle cx="50" cy="50" r="40" stroke="currentColor" strokeWidth="1.5" fill="none" opacity="0.4" />

      {/* Omnitrix hourglass shape */}
      <path
        d="M 35 25 L 50 45 L 65 25 Z"
        fill="currentColor"
      />
      <path
        d="M 35 75 L 50 55 L 65 75 Z"
        fill="currentColor"
      />

      {/* Center circle */}
      <circle cx="50" cy="50" r="8" fill="currentColor" opacity="0.3" />
      <circle cx="50" cy="50" r="4" fill="currentColor" />
    </svg>
  );
};
