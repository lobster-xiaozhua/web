"use client";

import React, { useState } from "react";
import Link from "next/link";
import NovelCard from "@/components/novel/NovelCard";
import type { Novel, ReadingHistory } from "@/types";
import {
  BookMarked,
  Clock,
  Settings,
  Heart,
  ChevronRight,
  X,
  User as UserIcon,
} from "lucide-react";
import { formatDate } from "@/lib/utils";

const favoriteNovels: Novel[] = [
  {
    id: "1",
    title: "星辰大海",
    author: "远行者",
    cover: "",
    description:
      "在浩瀚星海中，一个少年踏上了寻找失落文明的旅程。",
    tags: ["科幻", "冒险"],
    rating: 4.8,
    viewCount: 128000,
    chapterCount: 256,
    status: "ongoing",
    updatedAt: "2026-05-04",
  },
  {
    id: "2",
    title: "剑来",
    author: "烽火戏诸侯",
    cover: "",
    description: "大千世界，无奇不有。一个少年从泥瓶巷走出。",
    tags: ["仙侠", "热血"],
    rating: 4.9,
    viewCount: 256000,
    chapterCount: 512,
    status: "ongoing",
    updatedAt: "2026-05-03",
  },
  {
    id: "3",
    title: "诡秘之主",
    author: "爱潜水的乌贼",
    cover: "",
    description: "蒸汽与机械的浪潮中，谁能触及非凡？",
    tags: ["奇幻", "悬疑"],
    rating: 4.7,
    viewCount: 198000,
    chapterCount: 389,
    status: "completed",
    updatedAt: "2026-04-20",
  },
];

const readingHistory: ReadingHistory[] = [
  {
    novelId: "1",
    chapterId: "ch-45",
    progress: 72,
    lastReadAt: "2026-05-05T08:30:00Z",
  },
  {
    novelId: "2",
    chapterId: "ch-120",
    progress: 45,
    lastReadAt: "2026-05-04T22:15:00Z",
  },
  {
    novelId: "3",
    chapterId: "ch-89",
    progress: 88,
    lastReadAt: "2026-05-03T19:45:00Z",
  },
];

export default function UserPage() {
  const [showSettings, setShowSettings] = useState(false);

  return (
    <div className="min-h-screen">
      {/* ===== 用户头部 — 开放式布局 ===== */}
      <section className="relative overflow-hidden pb-8">
        {/* 背景光斑 */}
        <div
          className="absolute inset-0 -z-10 pointer-events-none"
          style={{
            background:
              "linear-gradient(180deg, rgba(15,10,30,0.7) 0%, transparent 70%)",
          }}
        />
        <div
          className="absolute top-0 left-[20%] w-[400px] h-[300px] -z-10 opacity-20"
          style={{
            background:
              "radial-gradient(circle, rgba(245,158,11,0.12) 0%, transparent 70%)",
            filter: "blur(60px)",
          }}
        />

        <div className="max-w-6xl mx-auto px-8 md:px-16 lg:px-24 pt-12 md:pt-16">
          <div className="flex items-center gap-6">
            {/* 头像 */}
            <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-[#f59e0b]/20 to-purple-500/20 flex items-center justify-center ring-1 ring-white/[0.08] shadow-lg shadow-black/20">
              <UserIcon className="w-9 h-9 text-white/60" />
            </div>
            {/* 信息 */}
            <div className="flex-1 min-w-0">
              <h1 className="text-2xl md:text-3xl font-bold text-white tracking-tight">
                读书人
              </h1>
              <p className="text-sm text-white/35 mt-1">
                已阅读 1,280 章 · 收藏 {favoriteNovels.length} 本
              </p>
            </div>
            <button
              onClick={() => setShowSettings(true)}
              className="hidden sm:flex items-center gap-2 px-5 py-2.5 rounded-xl border border-white/[0.1] text-white/50 hover:text-white/80 hover:border-white/20 hover:bg-white/[0.03] transition-all"
            >
              <Settings className="w-4 h-4" />
              设置
            </button>
          </div>
        </div>
      </section>

      {/* ===== 我的收藏 — 瀑布流大图展示 ===== */}
      <section className="max-w-6xl mx-auto px-8 md:px-16 lg:px-24 py-16">
        <div className="flex items-center gap-3 mb-10">
          <Heart className="w-5 h-5 text-[#f59e0b]" />
          <h2 className="text-2xl font-bold text-white">我的收藏</h2>
          <span className="text-sm text-white/25 ml-2">
            {favoriteNovels.length} 本
          </span>
        </div>

        {/* masonry 风格网格 — 大图展示 */}
        <div className="grid grid-cols-2 lg:grid-cols-3 gap-x-6 gap-y-10">
          {favoriteNovels.map((novel) => (
            <Link key={novel.id} href={`/novel/${novel.id}`} className="group block">
              <div className="space-y-3">
                <div className="relative aspect-[2/3] rounded-2xl overflow-hidden shadow-lg shadow-black/20 transition-all duration-500 group-hover:shadow-2xl group-hover:shadow-black/40 group-hover:-translate-y-1">
                  <img
                    src={`https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=${encodeURIComponent(`一本名为${novel.title}的${novel.tags[0]}类型小说封面，深色背景，极简设计，发光文字`)}`}
                    alt={novel.title}
                    className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/50 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-400" />
                  <div className="absolute bottom-0 left-0 right-0 p-4 translate-y-4 opacity-0 group-hover:translate-y-0 group-hover:opacity-100 transition-all duration-400">
                    <span className="text-xs text-[#f59e0b]/80 font-medium">
                      {novel.tags[0]}
                    </span>
                  </div>
                </div>
                <div>
                  <h3 className="text-base font-semibold text-white/90 truncate group-hover:text-white transition-colors">
                    {novel.title}
                  </h3>
                  <div className="flex items-center justify-between mt-1">
                    <p className="text-sm text-white/30 truncate">{novel.author}</p>
                    <span className="text-xs text-[#f59e0b]/60 font-medium tabular-nums">
                      ★ {novel.rating.toFixed(1)}
                    </span>
                  </div>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </section>

      {/* ===== 阅读历史 — 时间线布局 ===== */}
      <section className="max-w-3xl mx-auto px-8 md:px-16 lg:px-24 py-16 border-t border-white/[0.05]">
        <div className="flex items-center gap-3 mb-10">
          <Clock className="w-5 h-5 text-[#f59e0b]" />
          <h2 className="text-2xl font-bold text-white">阅读历史</h2>
        </div>

        <div className="relative pl-10">
          {/* 时间线竖线 */}
          <div className="absolute left-[11px] top-0 bottom-0 w-[2px] bg-gradient-to-b from-[#f59e0b]/30 via-white/[0.06] to-transparent" />

          {readingHistory.map((history, idx) => {
            const novel = favoriteNovels.find((n) => n.id === history.novelId);
            return (
              <div
                key={`${history.novelId}-${history.chapterId}`}
                className="relative pb-10 last:pb-0"
              >
                {/* 圆点 */}
                <div
                  className={`absolute -left-[23px] top-1.5 w-4 h-4 rounded-full border-2 ${
                    idx === 0
                      ? "bg-[#f59e0b] border-[#f59e0b]/30 shadow-lg shadow-[#f59e0b]/20"
                      : "bg-[#0a0a1a] border-white/[0.12]"
                  }`}
                />

                <Link
                  href={`/read/${history.chapterId}?novelId=${history.novelId}`}
                  className="block p-5 rounded-2xl hover:bg-white/[0.02] transition-colors group"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="min-w-0 flex-1">
                      <p className="text-base font-semibold text-white/85 group-hover:text-white truncate transition-colors">
                        {novel?.title || "未知小说"}
                      </p>
                      <p className="text-sm text-white/30 mt-1.5">
                        阅读至第{history.chapterId.replace("ch-", "")}章 · 进度{" "}
                        <span className="text-[#f59e0b]/70 font-medium tabular-nums">
                          {history.progress}%
                        </span>
                      </p>

                      {/* 进度条 */}
                      <div className="mt-3 h-1 rounded-full bg-white/[0.06] overflow-hidden max-w-[200px]">
                        <div
                          className="h-full rounded-full bg-gradient-to-r from-[#f59e0b] to-[#fbbf24]"
                          style={{ width: `${history.progress}%` }}
                        />
                      </div>
                    </div>

                    <div className="shrink-0 flex items-center gap-2 text-xs text-white/20">
                      <span>{formatDate(history.lastReadAt)}</span>
                      <ChevronRight className="w-4 h-4 group-hover:text-[#f59e0b]/50 group-hover:translate-x-0.5 transition-all" />
                    </div>
                  </div>
                </Link>
              </div>
            );
          })}
        </div>
      </section>

      {/* ===== 设置弹窗 — 清洁表单布局 ===== */}
      {showSettings && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div
            className="absolute inset-0 bg-black/50 backdrop-blur-sm"
            onClick={() => setShowSettings(false)}
          />
          <div className="relative w-full max-w-md bg-[#12121c]/95 backdrop-blur-2xl rounded-2xl border border-white/[0.08] shadow-2xl shadow-black/40 overflow-hidden animate-fade-up">
            {/* 弹窗头 */}
            <div className="flex items-center justify-between px-6 py-5 border-b border-white/[0.06]">
              <h3 className="text-lg font-bold text-white">账户设置</h3>
              <button
                onClick={() => setShowSettings(false)}
                className="w-8 h-8 rounded-lg flex items-center justify-center text-white/30 hover:text-white/70 hover:bg-white/[0.06] transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* 表单内容 — 分组明确 */}
            <div className="p-6 space-y-6">
              {/* 基本信息 */}
              <div className="space-y-4">
                <p className="text-xs font-medium tracking-widest uppercase text-white/25">
                  基本信息Basic Info
                </p>
                <div className="space-y-3">
                  <div>
                    <label className="text-xs text-white/35 mb-1.5 block">
                      用户名
                    </label>
                    <input
                      type="text"
                      defaultValue="读书人"
                      className="w-full px-4 py-2.5 rounded-xl bg-white/[0.03] border border-white/[0.07] text-white/80 text-sm outline-none focus:border-[#f59e0b]/40 focus:bg-white/[0.05] transition-all placeholder:text-white/15"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-white/35 mb-1.5 block">
                      邮箱
                    </label>
                    <input
                      type="email"
                      defaultValue="reader@example.com"
                      className="w-full px-4 py-2.5 rounded-xl bg-white/[0.03] border border-white/[0.07] text-white/80 text-sm outline-none focus:border-[#f59e0b]/40 focus:bg-white/[0.05] transition-all placeholder:text-white/15"
                    />
                  </div>
                </div>
              </div>

              {/* 阅读偏好 */}
              <div className="space-y-4 pt-2 border-t border-white/[0.05]">
                <p className="text-xs font-medium tracking-widest uppercase text-white/25">
                  阅读偏好Reading Preferences
                </p>
                <div className="space-y-3">
                  <div>
                    <label className="text-xs text-white/35 mb-1.5 block">
                      默认字体大小
                    </label>
                    <input
                      type="number"
                      defaultValue="18"
                      className="w-full px-4 py-2.5 rounded-xl bg-white/[0.03] border border-white/[0.07] text-white/80 text-sm outline-none focus:border-[#f59e0b]/40 focus:bg-white/[0.05] transition-all"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-white/35 mb-1.5 block">
                      默认阅读主题
                    </label>
                    <select
                      defaultValue="dark"
                      className="w-full px-4 py-2.5 rounded-xl bg-white/[0.03] border border-white/[0.07] text-white/80 text-sm outline-none focus:border-[#f59e0b]/40 focus:bg-white/[0.05] transition-all appearance-none cursor-pointer"
                    >
                      <option value="light" className="bg-[#14141e]">日间模式</option>
                      <option value="dark" className="bg-[#14141e]">夜间模式</option>
                      <option value="sepia" className="bg-[#14141e]">护眼模式</option>
                    </select>
                  </div>
                </div>
              </div>
            </div>

            {/* 操作按钮 */}
            <div className="flex justify-end gap-3 px-6 py-4 border-t border-white/[0.06]">
              <button
                onClick={() => setShowSettings(false)}
                className="px-5 py-2 rounded-xl text-sm text-white/45 hover:text-white/70 hover:bg-white/[0.04] transition-all"
              >
                取消
              </button>
              <button className="btn-primary text-sm py-2 px-5">
                保存更改
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}