'use client';

import React from 'react';

export function StarfieldBackground() {
  return (
    <div className="starfield">
      <div className="stars-layer" />
      <div className="stars-layer" />
      <div className="stars-layer" />
      {/* Nebula glows */}
      <div
        className="nebula-glow"
        style={{
          top: '10%',
          left: '20%',
          width: '500px',
          height: '500px',
          background: 'radial-gradient(circle, rgba(79, 195, 247, 0.15) 0%, transparent 70%)',
        }}
      />
      <div
        className="nebula-glow"
        style={{
          bottom: '10%',
          right: '15%',
          width: '400px',
          height: '400px',
          background: 'radial-gradient(circle, rgba(255, 232, 31, 0.1) 0%, transparent 70%)',
        }}
      />
      <div
        className="nebula-glow"
        style={{
          top: '50%',
          left: '60%',
          width: '300px',
          height: '300px',
          background: 'radial-gradient(circle, rgba(239, 83, 80, 0.08) 0%, transparent 70%)',
        }}
      />
    </div>
  );
}
