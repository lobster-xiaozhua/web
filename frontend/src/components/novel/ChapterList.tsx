"use client";

import React from "react";
import Link from "next/link";
import type { Chapter } from "@/types";
import { cn } from "@/lib/utils";

interface ChapterListProps {
  chapters: Chapter[];
  novelId: string;
  currentChapterId?: string;
}

export default function ChapterList({
  chapters,
  novelId,
  currentChapterId,
}: ChapterListProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-bold text-white">章节目录</h3>
        <span className="text-sm text-white/30">
          共 {chapters.length} 章
        </span>
      </div>

      <div className="divide-y divide-white/[0.06]">
        {chapters.map((chapter, index) => {
          const isCurrent = currentChapterId === chapter.id;
          return (
            <Link
              key={chapter.id}
              href={`/read/${chapter.id}?novelId=${novelId}`}
              className={cn(
                "group flex items-center gap-5 py-4 px-3 -mx-3 rounded-lg transition-all duration-200",
                isCurrent
                  ? "bg-[#f59e0b]/[0.06]"
                  : "hover:bg-white/[0.03]"
              )}
            >
              {/* 左侧序号 */}
              <span
                className={cn(
                  "text-sm font-mono tabular-nums w-8 text-center shrink-0 transition-colors",
                  isCurrent ? "text-[#f59e0b] font-semibold" : "text-white/20"
                )}
              >
                {String(index + 1).padStart(2, "0")}
              </span>

              {/* 当前章节指示条 */}
              <div
                className={cn(
                  "w-[2px] h-6 rounded-full shrink-0 transition-colors",
                  isCurrent ? "bg-[#f59e0b]" : "bg-transparent group-hover:bg-white/10"
                )}
              />

              {/* 章节标题 */}
              <span
                className={cn(
                  "flex-1 text-[15px] truncate transition-colors",
                  isCurrent
                    ? "text-white font-medium"
                    : "text-white/60 group-hover:text-white/90"
                )}
              >
                第{chapter.order}章 {chapter.title}
              </span>

              {/* 字数 */}
              <span className="text-xs text-white/20 shrink-0 tabular-nums hidden sm:block">
                {(chapter.wordCount / 1000).toFixed(1)}k字
              </span>
            </Link>
          );
        })}
      </div>
    </div>
  );
}