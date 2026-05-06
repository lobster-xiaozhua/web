"use client";

import React from "react";
import { Minus, Plus, Type, Moon, Sun } from "lucide-react";
import { GlassButton } from "@/components/ui/glass-button";

interface ReadingBarProps {
  chapterTitle: string;
  progress: number;
  fontSize: number;
  theme: "light" | "dark" | "sepia";
  onFontSizeChange: (size: number) => void;
  onThemeChange: (theme: "light" | "dark" | "sepia") => void;
}

export default function ReadingBar({
  chapterTitle,
  progress,
  fontSize,
  theme,
  onFontSizeChange,
  onThemeChange,
}: ReadingBarProps) {
  const cycleTheme = () => {
    const themes: Array<"light" | "dark" | "sepia"> = [
      "light",
      "dark",
      "sepia",
    ];
    const idx = themes.indexOf(theme);
    onThemeChange(themes[(idx + 1) % themes.length]);
  };

  return (
    <div className="glass-player flex items-center px-4 gap-4">
      <span className="text-sm text-[var(--text-secondary)] truncate flex-1">
        {chapterTitle}
      </span>

      <div className="flex-1 flex items-center gap-2">
        <div className="flex-1 h-1.5 rounded-full bg-[rgba(255,255,255,0.1)] overflow-hidden">
          <div
            className="h-full rounded-full bg-gradient-to-r from-[#667eea] to-[#764ba2] transition-all"
            style={{ width: `${progress}%` }}
          />
        </div>
        <span className="text-xs text-[var(--text-secondary)] shrink-0">
          {progress}%
        </span>
      </div>

      <div className="flex items-center gap-1 shrink-0">
        <GlassButton
          variant="ghost"
          size="icon"
          onClick={() => onFontSizeChange(Math.max(12, fontSize - 2))}
          aria-label="缩小字体"
        >
          <Minus className="h-4 w-4" />
        </GlassButton>

        <GlassButton
          variant="ghost"
          size="icon"
          onClick={() => onFontSizeChange(Math.min(28, fontSize + 2))}
          aria-label="放大字体"
        >
          <Plus className="h-4 w-4" />
        </GlassButton>

        <GlassButton
          variant="ghost"
          size="icon"
          onClick={cycleTheme}
          aria-label="切换阅读主题"
        >
          {theme === "dark" ? (
            <Moon className="h-4 w-4" />
          ) : theme === "sepia" ? (
            <Type className="h-4 w-4" />
          ) : (
            <Sun className="h-4 w-4" />
          )}
        </GlassButton>
      </div>
    </div>
  );
}
