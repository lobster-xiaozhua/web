"use client";

import React, { useEffect, useRef, useState } from "react";
import Link from "next/link";
import NovelCard from "@/components/novel/NovelCard";
import LoadingSpinner from "@/components/ui/loading-spinner";
import { novelsApi, type NovelItem } from "@/lib/api";
import { Star, ChevronDown, ArrowRight, BookOpen } from "lucide-react";

const sampleRankings: { rank: number; title: string; author: string; score: number }[] = [
  { rank: 1, title: "剑来", author: "烽火戏诸侯", score: 9.8 },
  { rank: 2, title: "星辰大海", author: "远行者", score: 9.5 },
  { rank: 3, title: "道诡异仙", author: "狐尾的笔", score: 9.3 },
  { rank: 4, title: "诡秘之主", author: "爱潜水的乌贼", score: 9.1 },
  { rank: 5, title: "牧神记", author: "宅猪", score: 8.9 },
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
  const [novels, setNovels] = useState<NovelItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [featuredNovel, setFeaturedNovel] = useState<NovelItem | null>(null);
  const section1 = useSectionReveal();
  const section2 = useSectionReveal();
  const section3 = useSectionReveal();

  useEffect(() => {
    async function loadNovels() {
      try {
        const data = await novelsApi.list({ page: 1, page_size: 20 });
        const items = data.items || [];
        setNovels(items);
        if (items.length > 0) {
          setFeaturedNovel(items[0]);
        }
      } catch {
      } finally {
        setLoading(false);
      }
    }
    loadNovels();
  }, []);

  const restNovels = featuredNovel ? novels.filter((n) => n.id !== featuredNovel.id) : novels;

  return (
    <div className="min-h-screen">
      <section
        className="relative w-full h-[100svh] flex items-center overflow-hidden"
        style={{
          background:
            "linear-gradient(135deg, #0a0a1e 0%, #160a30 25%, #1a0a3e 50%, #0d1025 75%, #080d1a 100%)",
        }}
      >
        <div className="absolute inset-0 pointer-events-none" aria-hidden="true">
          <div
            className="absolute top-[10%] right-[15%] w-[500px] h-[500px] rounded-full animate-pulse-glow"
            style={{
              background: "radial-gradient(circle, rgba(139,92,246,0.15) 0%, transparent 70%)",
              filter: "blur(60px)",
            }}
          />
          <div
            className="absolute bottom-[20%] left-[5%] w-[400px] h-[400px] rounded-full animate-pulse-glow delay-200"
            style={{
              background: "radial-gradient(circle, rgba(245,158,11,0.08) 0%, transparent 70%)",
              filter: "blur(50px)",
            }}
          />
          <div
            className="absolute top-[40%] right-[40%] w-[300px] h-[300px] rounded-full animate-pulse-glow delay-400"
            style={{
              background: "radial-gradient(circle, rgba(99,102,241,0.12) 0%, transparent 70%)",
              filter: "blur(55px)",
            }}
          />
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

        <div className="relative z-10 max-w-xl ml-8 md:ml-16 lg:ml-24">
          <h1
            className="animate-fade-up text-5xl md:text-7xl font-black tracking-tight leading-[1.1]"
            style={{
              backgroundImage: "linear-gradient(135deg, #ffffff 0%, #fde68a 50%, #f59e0b 100%)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
              backgroundClip: "text",
            }}
          >
            星穹书阁
          </h1>
          <p className="animate-fade-up delay-200 text-xl md:text-2xl text-white/50 font-light mt-6 leading-relaxed max-w-lg">
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

        <div
          className="absolute right-[-5%] bottom-[10%] hidden lg:block animate-float pointer-events-none"
          aria-hidden="true"
        >
          <svg width="420" height="520" viewBox="0 0 420 520" fill="none" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <linearGradient id="bookGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="rgba(245,158,11,0.15)" />
                <stop offset="50%" stopColor="rgba(139,92,246,0.1)" />
                <stop offset="100%" stopColor="rgba(245,158,11,0.05)" />
              </linearGradient>
            </defs>
            <path d="M210 40 C120 40 70 90 70 180 L70 480 L210 440 L350 480 L350 180 C350 90 300 40 210 40Z" stroke="url(#bookGrad)" strokeWidth="1.5" fill="none" />
            <path d="M210 440 L210 40" stroke="url(#bookGrad)" strokeWidth="1" opacity="0.5" />
            <circle cx="340" cy="80" r="35" fill="rgba(245,158,11,0.06)" stroke="rgba(245,158,11,0.15)" strokeWidth="1" />
            <circle cx="80" cy="450" r="25" fill="rgba(139,92,246,0.06)" stroke="rgba(139,92,246,0.12)" strokeWidth="1" />
          </svg>
        </div>

        <a href="#featured" className="absolute bottom-8 left-1/2 -translate-x-1/2 z-10 animate-bounce-arrow">
          <ChevronDown className="w-7 h-7 text-white/30" />
        </a>
      </section>

      <section
        id="featured"
        ref={section1.ref}
        className={`section-reveal ${section1.isVisible ? "visible" : ""} py-24 px-8 md:px-16 lg:px-24`}
      >
        <div className="max-w-7xl mx-auto">
          <div className="flex items-end justify-between mb-16">
            <div>
              <p className="text-sm font-medium tracking-widest uppercase text-[#f59e0b]/80 mb-2">Featured</p>
              <h2 className="text-3xl md:text-4xl font-bold text-white">本周精选</h2>
            </div>
          </div>

          {loading ? (
            <LoadingSpinner text="加载中..." />
          ) : featuredNovel ? (
            <>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 mb-16 items-center">
                <div className="relative group">
                  <div className="aspect-[4/3] rounded-2xl overflow-hidden shadow-2xl shadow-black/30">
                    <img
                      src={featuredNovel.cover_url || `https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=${encodeURIComponent(`一本名为${featuredNovel.title}的小说封面，深色背景，极简设计，发光文字，科幻星空风格`)}&image_size=landscape_4_3`}
                      alt={featuredNovel.title}
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
                      {featuredNovel.category}
                    </span>
                    <h3 className="text-3xl md:text-4xl font-bold text-white mt-2 leading-tight">
                      {featuredNovel.title}
                    </h3>
                    <p className="text-lg text-white/40 mt-2 font-light">{featuredNovel.author} 著</p>
                  </div>
                  <div className="flex items-center gap-4 text-sm text-white/50">
                    <span className="flex items-center gap-1.5">
                      <Star className="w-4 h-4 fill-[#f59e0b] text-[#f59e0b]" />
                      {featuredNovel.rating.toFixed(1)}
                    </span>
                    <span className="text-white/20">|</span>
                    <span>{featuredNovel.status === "ongoing" ? "连载中" : "已完结"}</span>
                  </div>
                  <p className="text-base text-white/45 leading-relaxed max-w-md">
                    {featuredNovel.description || "暂无简介"}
                  </p>
                  <Link href={`/novel/${featuredNovel.id}`}>
                    <button className="btn-primary mt-2">
                      开始阅读
                      <ArrowRight className="w-4 h-4" />
                    </button>
                  </Link>
                </div>
              </div>

              <div className="relative">
                <div className="flex gap-6 overflow-x-auto pb-4 snap-x snap-mandatory scrollbar-hide">
                  {restNovels.map((novel) => (
                    <Link key={novel.id} href={`/novel/${novel.id}`} className="shrink-0 snap-start">
                      <div className="w-48 glass-card p-4 rounded-xl">
                        <div className="aspect-[3/4] rounded-lg overflow-hidden mb-3">
                          <img
                            src={novel.cover_url || `https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=${encodeURIComponent(`一本名为${novel.title}的${novel.category}类型小说封面，深色背景，极简设计`)}&image_size=portrait_4_3`}
                            alt={novel.title}
                            className="w-full h-full object-cover"
                          />
                        </div>
                        <h4 className="text-sm font-semibold text-white/90 truncate">{novel.title}</h4>
                        <p className="text-xs text-white/40 mt-1">{novel.author}</p>
                      </div>
                    </Link>
                  ))}
                </div>
              </div>
            </>
          ) : (
            <div className="text-center py-20">
              <p className="text-white/30 text-lg">暂无小说数据</p>
              <p className="text-white/20 text-sm mt-2">请将小说文件放入 books 目录后重启</p>
            </div>
          )}
        </div>
      </section>

      <section
        id="categories"
        ref={section2.ref}
        className={`section-reveal ${section2.isVisible ? "visible" : ""} py-24 px-8 md:px-16 lg:px-24`}
      >
        <div className="max-w-7xl mx-auto">
          <div className="mb-12">
            <p className="text-sm font-medium tracking-widest uppercase text-[#f59e0b]/80 mb-2">Categories</p>
            <h2 className="text-3xl md:text-4xl font-bold text-white">探索分类</h2>
          </div>
          <div className="flex flex-wrap gap-3">
            {categories.map((cat) => (
              <Link key={cat.name} href={`/?category=${cat.name}`}>
                <button className="glass-pill text-base">
                  <span className="mr-2">{cat.icon}</span>
                  {cat.name}
                </button>
              </Link>
            ))}
          </div>
        </div>
      </section>

      <section
        ref={section3.ref}
        className={`section-reveal ${section3.isVisible ? "visible" : ""} py-24 px-8 md:px-16 lg:px-24`}
      >
        <div className="max-w-3xl mx-auto">
          <div className="mb-12">
            <p className="text-sm font-medium tracking-widest uppercase text-[#f59e0b]/80 mb-2">Rankings</p>
            <h2 className="text-3xl md:text-4xl font-bold text-white">热门榜单</h2>
          </div>
          <div className="divide-y divide-white/[0.06]">
            {sampleRankings.map((item) => (
              <div key={item.rank} className="flex items-center gap-6 py-5 px-2 -mx-2 rounded-lg hover:bg-white/[0.03] transition-colors">
                <span
                  className={`text-2xl font-black tabular-nums w-10 text-center shrink-0 ${
                    item.rank === 1 ? "text-[#f59e0b]" : item.rank === 2 ? "text-white/60" : item.rank === 3 ? "text-white/40" : "text-white/20"
                  }`}
                >
                  {String(item.rank).padStart(2, "0")}
                </span>
                <div className="flex-1 min-w-0">
                  <p className="text-base font-semibold text-white/90 truncate">{item.title}</p>
                  <p className="text-sm text-white/30 mt-0.5">{item.author}</p>
                </div>
                <div className="flex items-center gap-1.5 shrink-0">
                  <Star className="w-4 h-4 fill-[#f59e0b]/60 text-[#f59e0b]/60" />
                  <span className="text-sm font-medium text-white/50 tabular-nums">{item.score}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <footer className="py-16 px-8 border-t border-white/[0.05]">
        <div className="max-w-7xl mx-auto text-center">
          <p className="text-2xl font-bold bg-gradient-to-r from-white to-[#f59e0b] bg-clip-text text-transparent mb-2">
            星穹书阁
          </p>
          <p className="text-sm text-white/25">v1.5.0 · 在星辰与文字之间，找到属于你的故事</p>
        </div>
      </footer>
    </div>
  );
}
