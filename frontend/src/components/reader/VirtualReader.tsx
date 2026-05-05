"use client";

import React, { useRef, useCallback } from "react";
import { useVirtualizer } from "@tanstack/react-virtual";

interface VirtualReaderProps {
  paragraphs: string[];
  fontSize?: number;
  theme?: "light" | "dark" | "sepia";
}

export default function VirtualReader({
  paragraphs,
  fontSize = 18,
  theme = "light",
}: VirtualReaderProps) {
  const parentRef = useRef<HTMLDivElement>(null);

  const virtualizer = useVirtualizer({
    count: paragraphs.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => fontSize * 2.5,
    overscan: 10,
  });

  const getThemeClass = useCallback(() => {
    switch (theme) {
      case "dark":
        return "bg-[rgba(20,20,30,0.6)] text-gray-200";
      case "sepia":
        return "bg-[rgba(244,233,210,0.6)] text-[#5b4636]";
      default:
        return "bg-[rgba(255,255,255,0.6)] text-gray-900";
    }
  }, [theme]);

  return (
    <div
      ref={parentRef}
      className={`h-full overflow-auto rounded-2xl ${getThemeClass()}`}
      style={{ maxHeight: "calc(100vh - 160px)" }}
    >
      <div
        style={{
          height: `${virtualizer.getTotalSize()}px`,
          width: "100%",
          position: "relative",
        }}
      >
        {virtualizer.getVirtualItems().map((virtualItem) => (
          <div
            key={virtualItem.key}
            style={{
              position: "absolute",
              top: 0,
              left: 0,
              width: "100%",
              height: `${virtualItem.size}px`,
              transform: `translateY(${virtualItem.start}px)`,
            }}
            className="px-8 flex items-start"
          >
            <p
              style={{ fontSize: `${fontSize}px`, lineHeight: 1.8 }}
              className="text-justify py-2"
            >
              {paragraphs[virtualItem.index]}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
