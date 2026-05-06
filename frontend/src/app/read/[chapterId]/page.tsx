"use client";

import React, { useState, useMemo, useCallback, useEffect } from "react";
import { useParams, useSearchParams, useRouter } from "next/navigation";
import Link from "next/link";
import LoadingSpinner from "@/components/ui/loading-spinner";
import { chaptersApi, novelsApi, type ChapterContent, type NovelDetail } from "@/lib/api";
import { toast } from "@/components/ui/toast";
import { ArrowLeft, List, ChevronLeft, ChevronRight, Type, Sun, Moon, Minus, X } from "lucide-react";

export default function ReaderPage() {
  const params = useParams();
  const searchParams = useSearchParams();
  const router = useRouter();
  const chapterId = params.chapterId as string;
  const novelId = searchParams.get("novelId") || "";
  const chapterIndex = parseInt(searchParams.get("chapterIndex") || "1", 10);

  const [fontSize, setFontSize] = useState(18);
  const [theme, setTheme] = useState<"light" | "dark" | "sepia">("dark");
  const [progress, setProgress] = useState(0);
  const [showToc, setShowToc] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const [chapter, setChapter] = useState<ChapterContent | null>(null);
  const [novel, setNovel] = useState<NovelDetail | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadChapter() {
      try {
        if (novelId && chapterIndex) {
          const data = await chaptersApi.getContent(novelId, chapterIndex);
          setChapter(data);
        }
      } catch (e: unknown) {
        const msg = e instanceof Error ? e.message : "加载章节失败";
        toast("error", msg);
      } finally {
        setLoading(false);
      }
    }
    loadChapter();
  }, [novelId, chapterIndex]);

  useEffect(() => {
    async function loadNovel() {
      if (!novelId) return;
      try {
        const data = await novelsApi.get(novelId);
        setNovel(data);
      } catch {}
    }
    loadNovel();
  }, [novelId]);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 60);
      const docHeight = document.documentElement.scrollHeight - window.innerHeight;
      if (docHeight > 0) {
        setProgress(Math.round((window.scrollY / docHeight) * 100));
      }
    };
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLTextAreaElement || e.target instanceof HTMLInputElement) return;
      switch (e.key) {
        case "ArrowLeft":
          handlePrev();
          break;
        case "ArrowRight":
          handleNext();
          break;
        case "Escape":
          setShowToc(false);
          setShowSettings(false);
          break;
        case "t":
        case "T":
          setShowToc((v) => !v);
          break;
        case "s":
        case "S":
          setShowSettings((v) => !v);
          break;
        case "+":
        case "=":
          setFontSize((s) => Math.min(28, s + 2));
          break;
        case "-":
          setFontSize((s) => Math.max(14, s - 2));
          break;
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [novelId, novel]);

  const handlePrev = useCallback(() => {
    if (novel && chapterIndex > 1) {
      const prevChapter = novel.chapters.find(c => c.chapter_index === chapterIndex - 1);
      if (prevChapter) {
        router.push(`/read/${prevChapter.id}?novelId=${novelId}&chapterIndex=${prevChapter.chapter_index}`);
      }
    }
  }, [router, novelId, chapterIndex, novel]);

  const handleNext = useCallback(() => {
    if (novel) {
      const nextChapter = novel.chapters.find(c => c.chapter_index === chapterIndex + 1);
      if (nextChapter) {
        router.push(`/read/${nextChapter.id}?novelId=${novelId}&chapterIndex=${nextChapter.chapter_index}`);
      } else {
        toast("info", "已是最后一章");
      }
    }
  }, [router, novelId, chapterIndex, novel]);

  const themeStyles = {
    light: { bg: "#faf8f5", text: "#2c2416" },
    dark: { bg: "#0a0a12", text: "#d4d0c8" },
    sepia: { bg: "#f4ecd8", text: "#3d3426" },
  };

  const currentTheme = themeStyles[theme];
  const paragraphs = useMemo(() => {
    if (!chapter?.content) return [];
    return chapter.content.split("\n").filter((p: string) => p.trim());
  }, [chapter]);

  if (loading) return <LoadingSpinner text="加载章节内容..." />;

  return (
    <div className="min-h-screen flex flex-col" style={{ backgroundColor: currentTheme.bg }}>
      <header
        className={`fixed top-0 left-0 right-0 z-50 flex items-center px-6 h-[56px] transition-all duration-500 ${
          scrolled ? "bg-[rgba(10,10,18,0.85)] backdrop-blur-xl border-b border-white/[0.06]" : "bg-transparent"
        }`}
      >
        <Link href={`/novel/${novelId}`}>
          <button className="w-10 h-10 rounded-xl flex items-center justify-center text-white/50 hover:text-white hover:bg-white/[0.08] transition-all">
            <ArrowLeft className="w-5 h-5" />
          </button>
        </Link>
        <span className="text-sm font-medium truncate ml-3 max-w-[50%]" style={{ color: scrolled ? currentTheme.text : "rgba(255,255,255,0.7)" }}>
          {novel?.title || ""} · 第{chapterIndex}章 {chapter?.title || ""}
        </span>
        <div className="flex-1" />
        <button onClick={() => setShowSettings(!showSettings)} className="w-10 h-10 rounded-xl flex items-center justify-center text-white/40 hover:text-white hover:bg-white/[0.08] transition-all">
          <Type className="w-4.5 h-4.5" />
        </button>
        <button onClick={() => setShowToc(!showToc)} className="w-10 h-10 rounded-xl flex items-center justify-center text-white/40 hover:text-white hover:bg-white/[0.08] transition-all ml-1">
          <List className="w-5 h-5" />
        </button>
      </header>

      <main className="flex-1 pt-[72px] pb-[80px] px-6">
        <article className="max-w-2xl mx-auto" style={{ color: currentTheme.text }}>
          <h1 className="text-2xl md:text-3xl font-bold mb-16 tracking-tight leading-tight" style={{ color: currentTheme.text }}>
            第{chapterIndex}章 {chapter?.title || ""}
          </h1>
          <div className="space-y-8 text-justify" style={{ fontSize: `${fontSize}px`, lineHeight: 2.0 }}>
            {paragraphs.map((para, idx) => (
              <p key={idx} className="indent-[2em]" style={{ marginBottom: "2rem" }}>{para}</p>
            ))}
          </div>
        </article>
      </main>

      <button onClick={handlePrev} className="fixed left-6 top-1/2 -translate-y-1/2 w-14 h-14 md:w-16 md:h-16 rounded-full bg-black/20 backdrop-blur-sm border border-white/10 flex items-center justify-center text-white/30 hover:text-white/70 hover:bg-black/30 transition-all duration-300 z-30 hidden sm:flex" aria-label="上一章">
        <ChevronLeft className="w-6 h-6" />
      </button>
      <button onClick={handleNext} className="fixed right-6 top-1/2 -translate-y-1/2 w-14 h-14 md:w-16 md:h-16 rounded-full bg-black/20 backdrop-blur-sm border border-white/10 flex items-center justify-center text-white/30 hover:text-white/70 hover:bg-black/30 transition-all duration-300 z-30 hidden sm:flex" aria-label="下一章">
        <ChevronRight className="w-6 h-6" />
      </button>

      <div className="fixed bottom-0 left-0 right-0 z-40">
        <div className="h-[2px] bg-white/[0.06]">
          <div className="h-full bg-[#f59e0b] transition-all duration-300 ease-out" style={{ width: `${progress}%` }} />
        </div>
      </div>

      {showToc && novel && (
        <div className="fixed inset-0 z-50 flex">
          <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" onClick={() => setShowToc(false)} />
          <div className="ml-auto w-80 max-w-[85vw] h-full bg-[#0e0e1a]/95 backdrop-blur-2xl border-l border-white/[0.06] overflow-auto animate-slide-in-right">
            <div className="p-8">
              <div className="flex items-center justify-between mb-8">
                <h3 className="text-lg font-bold text-white">目录</h3>
                <button onClick={() => setShowToc(false)} className="w-8 h-8 rounded-lg flex items-center justify-center text-white/35 hover:text-white/70 hover:bg-white/[0.06] transition-colors">
                  <X className="w-4 h-4" />
                </button>
              </div>
              <div className="divide-y divide-white/[0.05]">
                {novel.chapters.map((ch) => (
                  <Link
                    key={ch.id}
                    href={`/read/${ch.id}?novelId=${novelId}&chapterIndex=${ch.chapter_index}`}
                    onClick={() => setShowToc(false)}
                  >
                    <button
                      className={`w-full text-left py-4 px-3 -mx-3 rounded-lg hover:bg-white/[0.04] transition-colors group ${ch.chapter_index === chapterIndex ? "text-[#f59e0b]" : ""}`}
                    >
                      <span className="text-xs text-white/15 font-mono mr-3 tabular-nums">
                        {String(ch.chapter_index).padStart(2, "0")}
                      </span>
                      <span className={`text-[15px] group-hover:text-white/80 transition-colors ${ch.chapter_index === chapterIndex ? "text-[#f59e0b]" : "text-white/45"}`}>
                        {ch.title}
                      </span>
                    </button>
                  </Link>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {showSettings && (
        <div className="fixed bottom-20 left-1/2 -translate-x-1/2 z-50 w-[320px] max-w-[90vw] p-5 rounded-2xl bg-[#14141e]/95 backdrop-blur-xl border border-white/[0.08] shadow-2xl shadow-black/40 animate-fade-up">
          <div className="flex items-center justify-between mb-5">
            <span className="text-sm font-semibold text-white/70">阅读设置</span>
            <button onClick={() => setShowSettings(false)} className="w-7 h-7 rounded-md flex items-center justify-center text-white/25 hover:text-white/60 hover:bg-white/[0.06] transition-colors">
              <X className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="mb-5">
            <label className="text-xs text-white/30 block mb-3">字号</label>
            <div className="flex items-center gap-4">
              <button onClick={() => setFontSize(Math.max(14, fontSize - 2))} className="w-9 h-9 rounded-lg bg-white/[0.05] border border-white/[0.08] flex items-center justify-center text-white/40 hover:text-white/70 hover:border-white/15 transition-all">
                <Minus className="w-3.5 h-3.5" />
              </button>
              <span className="flex-1 text-center text-base font-medium text-white/70 tabular-nums">{fontSize}px</span>
              <button onClick={() => setFontSize(Math.min(28, fontSize + 2))} className="w-9 h-9 rounded-lg bg-white/[0.05] border border-white/[0.08] flex items-center justify-center text-white/40 hover:text-white/70 hover:border-white/15 transition-all">
                <Type className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          <div>
            <label className="text-xs text-white/30 block mb-3">主题</label>
            <div className="grid grid-cols-3 gap-2">
              {([
                { key: "light" as const, icon: Sun, label: "日间", bg: "#faf8f5" },
                { key: "dark" as const, icon: Moon, label: "夜间", bg: "#0a0a12" },
                { key: "sepia" as const, label: "护眼", bg: "#f4ecd8" },
              ]).map(({ key, icon: Icon, label, bg }) => (
                <button
                  key={key}
                  onClick={() => setTheme(key)}
                  className={`relative flex flex-col items-center gap-2 py-3 px-2 rounded-xl border transition-all ${
                    theme === key ? "border-[#f59e0b]/50 bg-[#f59e0b]/10" : "border-white/[0.07] bg-transparent hover:border-white/15"
                  }`}
                >
                  <div className="w-8 h-6 rounded-md ring-1 ring-inset" style={{ backgroundColor: bg, borderColor: theme === key ? "#f59e0b" : "rgba(255,255,255,0.1)" }} />
                  {Icon && <Icon className={`w-4 h-4 ${theme === key ? "text-[#f59e0b]" : "text-white/30"}`} />}
                  {!Icon && <span className={`text-[10px] ${theme === key ? "text-[#f59e0b]" : "text-white/30"}`}>A</span>}
                  <span className={`text-[11px] ${theme === key ? "text-white/90 font-medium" : "text-white/35"}`}>{label}</span>
                </button>
              ))}
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-white/[0.06]">
            <p className="text-[10px] text-white/20 text-center">
              快捷键: ← → 翻页 · T 目录 · S 设置 · +/- 字号
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
