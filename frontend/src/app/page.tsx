"use client";

import React, { useEffect, useRef, useState } from "react";
import Link from "next/link";
import NovelCard from "@/components/novel/NovelCard";
import type { Novel, RankingItem } from "@/types";
import { Star, ChevronDown, ArrowRight, BookOpen } from "lucide-react";

const sampleNovels: Novel[] = [
  {
    id: "1",
    title: "星辰大海",
    author: "远行者",
    cover: "",
    description:
      "在浩瀚星海中，一个少年踏上了寻找失落文明的旅程，穿越星际迷雾，揭开宇宙最深处的秘密。从荒芜星球到繁华星城，从古老遗迹到未知维度，每一步都充满危险与惊奇。",
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
    description:
      "大千世界，无奇不有。一个少年从泥瓶巷走出，手持一剑，可搬山、倒海、降妖、镇魔。修仙之路，道阻且长，但少年心中自有天地。",
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
    description:
      "蒸汽与机械的浪潮中，谁能触及非凡？历史和真实的迷雾里，又是谁在低语？当非凡之路开启，命运之轮开始转动。",
    tags: ["奇幻", "悬疑"],
    rating: 4.7,
    viewCount: 198000,
    chapterCount: 389,
    status: "completed",
    updatedAt: "2026-04-20",
  },
  {
    id: "4",
    title: "凡人修仙传",
    author: "忘语",
    cover: "",
    description:
      "一个普通山村少年，偶然下进入了当地江湖小门派，成了一名记名弟子。资质平庸的他，如何在残酷的修仙界中一步步踏上大道？",
    tags: ["仙侠", "经典"],
    rating: 4.6,
    viewCount: 345000,
    chapterCount: 678,
    status: "completed",
    updatedAt: "2026-03-15",
  },
  {
    id: "5",
    title: "深海余烬",
    author: "远瞳",
    cover: "",
    description:
      "大崩坏之后的世界，深海之下隐藏着什么？文明的余烬能否重新燃起？在这片被遗忘的海域中，新的故事正在书写。",
    tags: ["科幻", "末世"],
    rating: 4.5,
    viewCount: 89000,
    chapterCount: 198,
    status: "ongoing",
    updatedAt: "2026-05-05",
  },
  {
    id: "6",
    title: "牧神记",
    author: "宅猪",
    cover: "",
    description:
      "大墟的天黑了，天魔教主秦牧从黑暗中走出，踏上了一条前所未有的道路。神魔乱舞的时代，谁主沉浮？",
    tags: ["玄幻", "热血"],
    rating: 4.7,
    viewCount: 176000,
    chapterCount: 445,
    status: "completed",
    updatedAt: "2026-02-28",
  },
  {
    id: "7",
    title: "灵境行者",
    author: "卖报小郎君",
    cover: "",
    description:
      "灵境降临现实，人类获得超凡力量。一个普通大学生，意外踏入灵境世界。现实与虚幻的边界正在消融。",
    tags: ["都市", "灵异"],
    rating: 4.4,
    viewCount: 67000,
    chapterCount: 156,
    status: "ongoing",
    updatedAt: "2026-05-04",
  },
  {
    id: "8",
    title: "道诡异仙",
    author: "狐尾的笔",
    cover: "",
    description:
      "诡异与修仙并存的世界，一个少年在道与诡之间寻找真相。何为真？何为假？在癫狂的边缘，他找到了答案。",
    tags: ["仙侠", "诡异"],
    rating: 4.8,
    viewCount: 145000,
    chapterCount: 312,
    status: "ongoing",
    updatedAt: "2026-05-05",
  },
];

const sampleRankings: RankingItem[] = [
  { rank: 1, novel: sampleNovels[1], score: 9.8 },
  { rank: 2, novel: sampleNovels[0], score: 9.5 },
  { rank: 3, novel: sampleNovels[7], score: 9.3 },
  { rank: 4, novel: sampleNovels[2], score: 9.1 },
  { rank: 5, novel: sampleNovels[5], score: 8.9 },
];

const categories = [
  { name: "仙侠", icon: "⚔️" },
  { name: "科幻", icon: "🚀" },
  { name: "奇幻", icon: "🔮" },
  { name: "都市", icon: "🏙️" },
  { name: "玄幻", icon: "🐉" },
  { name: "悬疑", icon: "🔍" },
];

function useSectionReveal() {
  const ref = useRef<HTMLDivElement>(null);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
        }
      },
      { threshold: 0.1 }
    );
    if (ref.current) observer.observe(ref.current);
    return () => observer.disconnect();
  }, []);

  return { ref, isVisible };
}

export default function HomePage() {
  const featured = sampleNovels[0];
  const restNovels = sampleNovels.slice(1);
  const section1 = useSectionReveal();
  const section2 = useSectionReveal();
  const section3 = useSectionReveal();

  return (
    <div className="min-h-screen">
      {/* ===== 全屏 Hero 区域 ===== */}
      <section
        className="relative w-full h-[100svh] flex items-center overflow-hidden"
        style={{
          background:
            "linear-gradient(135deg, #0a0a1e 0%, #160a30 25%, #1a0a3e 50%, #0d1025 75%, #080d1a 100%)",
        }}
      >
        {/* 星云光斑 */}
        <div
          className="absolute inset-0 pointer-events-none"
          aria-hidden="true"
        >
          <div
            className="absolute top-[10%] right-[15%] w-[500px] h-[500px] rounded-full animate-pulse-glow"
            style={{
              background:
                "radial-gradient(circle, rgba(139,92,246,0.15) 0%, transparent 70%)",
              filter: "blur(60px)",
            }}
          />
          <div
            className="absolute bottom-[20%] left-[5%] w-[400px] h-[400px] rounded-full animate-pulse-glow delay-200"
            style={{
              background:
                "radial-gradient(circle, rgba(245,158,11,0.08) 0%, transparent 70%)",
              filter: "blur(50px)",
            }}
          />
          <div
            className="absolute top-[40%] right-[40%] w-[300px] h-[300px] rounded-full animate-pulse-glow delay-400"
            style={{
              background:
                "radial-gradient(circle, rgba(99,102,241,0.12) 0%, transparent 70%)",
              filter: "blur(55px)",
            }}
          />
          {/* 微弱星星粒子 */}
          {[...Array(20)].map((_, i) => (
            <div
              key={i}
              className="absolute w-[2px] h-[2px] bg-white/30 rounded-full animate-star-twinkle"
              style={{
                top: `${Math.random() * 100}%`,
                left: `${Math.random() * 100}%`,
                animationDelay: `${Math.random() * 5}s`,
              }}
            />
          ))}
        </div>

        {/* Hero 内容 — 窄列靠左 */}
        <div className="relative z-10 max-w-xl ml-8 md:ml-16 lg:ml-24">
          <h1
            className="animate-fade-up text-5xl md:text-7xl font-black tracking-tight leading-[1.1]"
            style={{
              backgroundImage:
                "linear-gradient(135deg, #ffffff 0%, #fde68a 50%, #f59e0b 100%)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
              backgroundClip: "text",
            }}
          >
            星穹书阁
          </h1>
          <p
            className="animate-fade-up delay-200 text-xl md:text-2xl text-white/50 font-light mt-6 leading-relaxed max-w-lg"
          >
            在星辰与文字之间，找到属于你的故事
          </p>
          <div className="animate-fade-up delay-300 flex items-center gap-4 mt-10">
            <Link href="#featured">
              <button className="btn-primary">
                <BookOpen className="w-5 h-5" />
                开始探索
              </button>
            </Link>
            <Link href="#categories">
              <button className="btn-outline-white">浏览分类</button>
            </Link>
          </div>
        </div>

        {/* 装饰元素 — 抽象书本轮廓 + 渐变圆 */}
        <div
          className="absolute right-[-5%] bottom-[10%] hidden lg:block animate-float pointer-events-none"
          aria-hidden="true"
        >
          <svg
            width="420"
            height="520"
            viewBox="0 0 420 520"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <defs>
              <linearGradient
                id="bookGrad"
                x1="0%"
                y1="0%"
                x2="100%"
                y2="100%"
              >
                <stop offset="0%" stopColor="rgba(245,158,11,0.15)" />
                <stop offset="50%" stopColor="rgba(139,92,246,0.1)" />
                <stop offset="100%" stopColor="rgba(245,158,11,0.05)" />
              </linearGradient>
            </defs>
            <path
              d="M210 40 C120 40 70 90 70 180 L70 480 L210 440 L350 480 L350 180 C350 90 300 40 210 40Z"
              stroke="url(#bookGrad)"
              strokeWidth="1.5"
              fill="none"
            />
            <path
              d="M210 440 L210 40"
              stroke="url(#bookGrad)"
              strokeWidth="1"
              opacity="0.5"
            />
            <line
              x1="110"
              y1="140"
              x2="190"
              y2="130"
              stroke="rgba(255,255,255,0.08)"
              strokeWidth="1"
            />
            <line
              x1="110"
              y1="170"
              x2="185"
              y2="160"
              stroke="rgba(255,255,255,0.06)"
              strokeWidth="1"
            />
            <line
              x1="230"
              y1="130"
              x2="310"
              y2="140"
              stroke="rgba(255,255,255,0.08)"
              strokeWidth="1"
            />
            <line
              x1="235"
              y1="160"
              x2="305"
              y2="170"
              stroke="rgba(255,255,255,0.06)"
              strokeWidth="1"
            />
            <circle
              cx="340"
              cy="80"
              r="35"
              fill="rgba(245,158,11,0.06)"
              stroke="rgba(245,158,11,0.15)"
              strokeWidth="1"
            />
            <circle
              cx="80"
              cy="450"
              r="25"
              fill="rgba(139,92,246,0.06)"
              stroke="rgba(139,92,246,0.12)"
              strokeWidth="1"
            />
          </svg>
        </div>

        {/* 向下箭头指示器 */}
        <a
          href="#featured"
          className="absolute bottom-8 left-1/2 -translate-x-1/2 z-10 animate-bounce-arrow"
        >
          <ChevronDown className="w-7 h-7 text-white/30" />
        </a>
      </section>

      {/* ===== 精选推荐区 — 编辑式布局 ===== */}
      <section
        id="featured"
        ref={section1.ref}
        className={`section-reveal ${section1.isVisible ? "visible" : ""} py-24 px-8 md:px-16 lg:px-24`}
      >
        <div className="max-w-7xl mx-auto">
          {/* 标题区 */}
          <div className="flex items-end justify-between mb-16">
            <div>
              <p className="text-sm font-medium tracking-widest uppercase text-[#f59e0b]/80 mb-2">
                Featured
              </p>
              <h2 className="text-3xl md:text-4xl font-bold text-white">
                本周精选
              </h2>
            </div>
            <Link
              href="/explore"
              className="hidden md:flex items-center gap-1 text-sm text-white/40 hover:text-[#f59e0b] transition-colors group"
            >
              查看全部
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </Link>
          </div>

          {/* 特色展示 — 横向布局 */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 mb-16 items-center">
            <div className="relative group">
              <div className="aspect-[4/3] rounded-2xl overflow-hidden shadow-2xl shadow-black/30">
                <img
                  src={`https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=${encodeURIComponent(`一本名为${featured.title}的${featured.tags[0]}类型小说封面，深色背景，极简设计，发光文字，科幻星空风格`)}`}
                  alt={featured.title}
                  className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
                />
              </div>
              <div className="absolute top-4 left-4 px-3 py-1 rounded-full bg-[#f59e0b]/90 text-[#0a0a1a] text-xs font-bold backdrop-blur-sm">
                编辑推荐
              </div>
            </div>
            <div className="space-y-6">
              <div>
                <span className="text-sm text-[#f59e0b]/70 font-medium tracking-wide">
                  {featured.tags.join(" · ")}
                </span>
                <h3 className="text-3xl md:text-4xl font-bold text-white mt-2 leading-tight">
                  {featured.title}
                </h3>
                <p className="text-lg text-white/40 mt-2 font-light">
                  {featured.author} 著
                </p>
              </div>
              <div className="flex items-center gap-4 text-sm text-white/50">
                <span className="flex items-center gap-1.5">
                  <Star className="w-4 h-4 fill-[#f59e0b] text-[#f59e0b]" />
                  {featured.rating.toFixed(1)}
                </span>
                <span className="text-white/20">|</span>
                <span>{featured.chapterCount} 章</span>
                <span className="text-white/20">|</span>
                <span>
                  {featured.status === "ongoing" ? "连载中" : "已完结"}
                </span>
              </div>
              <p className="text-base text-white/45 leading-relaxed max-w-md">
                {featured.description}
              </p>
              <Link href={`/novel/${featured.id}`}>
                <button className="btn-primary mt-2">
                  开始阅读
                  <ArrowRight className="w-4 h-4" />
                </button>
              </Link>
            </div>
          </div>

          {/* 水平滚动媒体条 */}
          <div className="relative">
            <div className="flex gap-6 overflow-x-auto pb-4 snap-x snap-mandatory scrollbar-hide">
              {restNovels.map((novel) => (
                <Link
                  key={novel.id}
                  href={`/novel/${novel.id}`}
                  className="shrink-0 snap-start"
                >
                  <NovelCard novel={novel} compact />
                </Link>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ===== 分类浏览区 ===== */}
      <section
        id="categories"
        ref={section2.ref}
        className={`section-reveal ${section2.isVisible ? "visible" : ""} py-24 px-8 md:px-16 lg:px-24`}
      >
        <div className="max-w-7xl mx-auto">
          <div className="mb-12">
            <p className="text-sm font-medium tracking-widest uppercase text-[#f59e0b]/80 mb-2">
              Categories
            </p>
            <h2 className="text-3xl md:text-4xl font-bold text-white">
              探索分类
            </h2>
          </div>
          <div className="flex flex-wrap gap-3">
            {categories.map((cat) => (
              <button key={cat.name} className="glass-pill text-base">
                <span className="mr-2">{cat.icon}</span>
                {cat.name}
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* ===== 排行榜区 ===== */}
      <section
        ref={section3.ref}
        className={`section-reveal ${section3.isVisible ? "visible" : ""} py-24 px-8 md:px-16 lg:px-24`}
      >
        <div className="max-w-3xl mx-auto">
          <div className="mb-12">
            <p className="text-sm font-medium tracking-widest uppercase text-[#f59e0b]/80 mb-2">
              Rankings
            </p>
            <h2 className="text-3xl md:text-4xl font-bold text-white">
              热门榜单
            </h2>
          </div>

          <div className="divide-y divide-white/[0.06]">
            {sampleRankings.map((item) => (
              <Link
                key={item.rank}
                href={`/novel/${item.novel.id}`}
                className="group flex items-center gap-6 py-5 px-2 -mx-2 rounded-lg hover:bg-white/[0.03] transition-colors"
              >
                <span
                  className={`text-2xl font-black tabular-nums w-10 text-center shrink-0 ${
                    item.rank === 1
                      ? "text-[#f59e0b]"
                      : item.rank === 2
                        ? "text-white/60"
                        : item.rank === 3
                          ? "text-white/40"
                          : "text-white/20"
                  }`}
                >
                  {String(item.rank).padStart(2, "0")}
                </span>
                <div className="flex-1 min-w-0">
                  <p className="text-base font-semibold text-white/90 group-hover:text-white truncate transition-colors">
                    {item.novel.title}
                  </p>
                  <p className="text-sm text-white/30 mt-0.5">
                    {item.novel.author}
                  </p>
                </div>
                <div className="flex items-center gap-1.5 shrink-0">
                  <Star className="w-4 h-4 fill-[#f59e0b]/60 text-[#f59e0b]/60" />
                  <span className="text-sm font-medium text-white/50 tabular-nums">
                    {item.score}
                  </span>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* 页脚区域 */}
      <footer className="py-16 px-8 border-t border-white/[0.05]">
        <div className="max-w-7xl mx-auto text-center">
          <p className="text-2xl font-bold bg-gradient-to-r from-white to-[#f59e0b] bg-clip-text text-transparent mb-2">
            星穹书阁
          </p>
          <p className="text-sm text-white/25">
            在星辰与文字之间，找到属于你的故事
          </p>
        </div>
      </footer>
    </div>
  );
}