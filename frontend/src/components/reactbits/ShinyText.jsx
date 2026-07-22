import React from 'react';

export default function ShinyText({ text, className = "", speed = 4 }) {
  return (
    <span
      className={`inline-block bg-clip-text text-transparent bg-gradient-to-r from-[#10201E] via-[#0E6E6A] to-[#10201E] bg-[length:200%_100%] animate-pulse ${className}`}
      style={{
        animationDuration: `${speed}s`,
      }}
    >
      {text}
    </span>
  );
}
