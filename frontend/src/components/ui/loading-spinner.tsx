"use client";

import React from "react";

interface LoadingSpinnerProps {
  size?: "sm" | "md" | "lg";
  text?: string;
}

const sizeMap = {
  sm: "w-5 h-5",
  md: "w-8 h-8",
  lg: "w-12 h-12",
};

export default function LoadingSpinner({ size = "md", text }: LoadingSpinnerProps) {
  return (
    <div className="flex flex-col items-center justify-center py-12">
      <div
        className={`${sizeMap[size]} border-2 border-white/10 border-t-[#f59e0b] rounded-full animate-spin`}
      />
      {text && (
        <p className="text-sm text-white/30 mt-4">{text}</p>
      )}
    </div>
  );
}
