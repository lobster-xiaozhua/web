"use client";

import React from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";

interface PageNavProps {
  onPrev?: () => void;
  onNext?: () => void;
  hasPrev?: boolean;
  hasNext?: boolean;
}

export default function PageNav({
  onPrev,
  onNext,
  hasPrev = true,
  hasNext = true,
}: PageNavProps) {
  return (
    <>
      {hasPrev && (
        <button
          onClick={onPrev}
          className={cn(
            "fixed left-4 top-1/2 -translate-y-1/2 z-30",
            "w-12 h-12 rounded-full",
            "glass-button flex items-center justify-center",
            "opacity-0 hover:opacity-100 transition-opacity",
            "shadow-lg"
          )}
          aria-label="上一章"
        >
          <ChevronLeft className="h-6 w-6" />
        </button>
      )}

      {hasNext && (
        <button
          onClick={onNext}
          className={cn(
            "fixed right-4 top-1/2 -translate-y-1/2 z-30",
            "w-12 h-12 rounded-full",
            "glass-button flex items-center justify-center",
            "opacity-0 hover:opacity-100 transition-opacity",
            "shadow-lg"
          )}
          aria-label="下一章"
        >
          <ChevronRight className="h-6 w-6" />
        </button>
      )}
    </>
  );
}
