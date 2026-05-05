"use client";

import React from "react";
import Link from "next/link";
import type { Novel } from "@/types";
import { Star } from "lucide-react";

interface NovelCardProps {
  novel: Novel;
  compact?: boolean;
}

export default function NovelCard({ novel, compact }: NovelCardProps) {
  const coverUrl = `https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=${encodeURIComponent(`一本名为${novel.title}的${novel.tags[0] || '小说'}类型小说封面，深色背景，极简设计，发光文字`)}`;

  if (compact) {
    return (
      <div className="group w-[160px] shrink-0 cursor-pointer">
        <div className="relative aspect-[2/3] rounded-xl overflow-hidden shadow-lg shadow-black/20 transition-all duration-500 group-hover:shadow-2xl group-hover:shadow-black/40">
          <img
            src={coverUrl}
            alt={novel.title}
            className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
        </div>
        <div className="mt-3 space-y-0.5">
          <h3 className="text-sm font-semibold text-white/90 truncate">
            {novel.title}
          </h3>
          <p className="text-xs text-white/35 truncate">{novel.author}</p>
        </div>
      </div>
    );
  }

  return (
    <Link href={`/novel/${novel.id}`} className="group block">
      <div className="w-full">
        {/* 封面 — 纯媒体块，无卡片包裹 */}
        <div className="relative aspect-[2/3] rounded-xl overflow-hidden shadow-lg shadow-black/15 transition-all duration-500 group-hover:shadow-2xl group-hover:shadow-black/30">
          <img
            src={coverUrl}
            alt={novel.title}
            className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
          />
          {novel.status === "ongoing" && (
            <span className="absolute top-3 right-3 px-2 py-0.5 text-[10px] font-bold rounded-full bg-emerald-500/80 text-white backdrop-blur-sm tracking-wider uppercase">
              连载中
            </span>
          )}
          <div className="absolute inset-0 bg-gradient-to-t from-black/50 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-400" />
        </div>

        {/* 信息区 — 极简 */}
        <div className="mt-3 px-0.5">
          <div className="flex items-start justify-between gap-2">
            <h3 className="text-sm font-semibold text-white/90 truncate flex-1 leading-snug">
              {novel.title}
            </h3>
            <span className="shrink-0 flex items-center gap-0.5 text-xs text-[#f59e0b]/80 font-medium">
              <Star className="w-3 h-3 fill-[#f59e0b]/60 text-[#f59e0b]/60" />
              {novel.rating.toFixed(1)}
            </span>
          </div>
          <p className="text-xs text-white/30 mt-1 truncate">{novel.author}</p>
        </div>
      </div>
    </Link>
  );
}