"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import ChapterList from "@/components/novel/ChapterList";
import LoadingSpinner from "@/components/ui/loading-spinner";
import { novelsApi, chaptersApi, bookmarksApi, type NovelDetail, type ChapterBrief } from "@/lib/api";
import { toast } from "@/components/ui/toast";
import { Star, Eye, BookOpen, Heart, Share2, Calendar } from "lucide-react";
import { formatNumber, formatDate, getStatusLabel, formatWordCount } from "@/lib/utils";

export default function NovelDetailPage() {
  const params = useParams();
  const novelId = params.id as string;
  const [novel, setNovel] = useState<NovelDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [bookmarked, setBookmarked] = useState(false);

  useEffect(() => {
    async function loadNovel() {
      try {
        const data = await novelsApi.get(novelId);
        setNovel(data);
      } catch (e: unknown) {
        const msg = e instanceof Error ? e.message : "加载失败";
        toast("error", msg);
      } finally {
        setLoading(false);
      }
    }
    loadNovel();
  }, [novelId]);

  useEffect(() => {
    async function checkBookmark() {
      try {
        const result = await bookmarksApi.check(novelId);
        setBookmarked(result.bookmarked);
      } catch {}
    }
    checkBookmark();
  }, [novelId]);

  const handleBookmark = async () => {
    try {
      if (bookmarked) {
        toast("info", "已取消收藏");
        setBookmarked(false);
      } else {
        await bookmarksApi.create(novelId);
        setBookmarked(true);
        toast("success", "已加入收藏");
      }
    } catch {
      toast("error", "操作失败，请先登录");
    }
  };

  const handleShare = async () => {
    if (navigator.share) {
      await navigator.share({ title: novel?.title, url: window.location.href });
    } else {
      await navigator.clipboard.writeText(window.location.href);
      toast("success", "链接已复制到剪贴板");
    }
  };

  if (loading) return <LoadingSpinner text="加载小说详情..." />;

  if (!novel) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px]">
        <p className="text-white/40 text-lg">小说不存在</p>
        <Link href="/" className="text-[#f59e0b] text-sm mt-4 hover:underline">返回首页</Link>
      </div>
    );
  }

  const coverUrl = novel.cover_url || `https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=${encodeURIComponent(`一本名为${novel.title}的${novel.category}类型小说封面，深色背景，极简设计，发光文字，科幻星空风格`)}&image_size=portrait_4_3`;

  const chapters: ChapterBrief[] = novel.chapters || [];

  return (
    <div className="min-h-screen">
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 -z-10" style={{ background: "linear-gradient(180deg, rgba(15,10,30,0.9) 0%, rgba(10,10,26,0) 50%, transparent 100%)" }} />
        <div className="absolute top-0 right-0 w-[500px] h-[400px] -z-10 opacity-30 pointer-events-none" style={{ background: "radial-gradient(circle, rgba(139,92,246,0.12) 0%, transparent 70%)", filter: "blur(80px)" }} />

        <div className="max-w-6xl mx-auto px-8 md:px-16 lg:px-24 pt-16 pb-16 md:pt-24 md:pb-24">
          <div className="flex flex-col md:flex-row gap-10 lg:gap-14 items-start">
            <div className="shrink-0 mx-auto md:mx-0">
              <div className="w-56 md:w-64 lg:w-72 aspect-[3/4] rounded-2xl overflow-hidden shadow-2xl shadow-black/40 ring-1 ring-white/[0.08]">
                <img src={coverUrl} alt={novel.title} className="w-full h-full object-cover" />
              </div>
            </div>

            <div className="flex-1 space-y-6 max-w-2xl">
              <div className="flex items-center gap-2">
                <span className="px-3 py-1 text-xs font-medium rounded-full bg-white/[0.06] text-white/60 border border-white/[0.08]">
                  {novel.category}
                </span>
                <span className={`px-3 py-1 text-xs font-bold rounded-full ${
                  novel.status === "ongoing" ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/20" : "bg-blue-500/15 text-blue-400 border border-blue-500/20"
                }`}>
                  {getStatusLabel(novel.status)}
                </span>
              </div>

              <h1 className="text-4xl md:text-5xl font-black text-white tracking-tight leading-tight">{novel.title}</h1>
              <p className="text-lg text-white/35 font-light">{novel.author} 著</p>

              <div className="flex flex-wrap items-center gap-x-5 gap-y-2 text-sm text-white/40">
                <span className="flex items-center gap-1.5">
                  <Star className="w-4 h-4 fill-[#f59e0b] text-[#f59e0b]" />
                  <span className="font-semibold text-white/70">{novel.rating.toFixed(1)}</span>
                </span>
                <span className="text-white/15">|</span>
                <span className="flex items-center gap-1.5">
                  <BookOpen className="w-4 h-4" />
                  {chapters.length} 章
                </span>
                <span className="text-white/15">|</span>
                <span className="flex items-center gap-1.5">
                  <Calendar className="w-4 h-4" />
                  更新于 {formatDate(novel.updated_at)}
                </span>
              </div>

              <p className="text-base md:text-lg text-white/45 leading-relaxed max-w-xl whitespace-pre-line">
                {novel.description || "暂无简介"}
              </p>

              <div className="flex items-center gap-4 pt-2">
                {chapters.length > 0 ? (
                  <Link href={`/read/${chapters[0].id}?novelId=${novel.id}&chapterIndex=${chapters[0].chapter_index}`}>
                    <button className="btn-primary text-base">
                      <BookOpen className="w-5 h-5" />
                      开始阅读
                    </button>
                  </Link>
                ) : (
                  <button className="btn-primary text-base opacity-50 cursor-not-allowed" disabled>
                    <BookOpen className="w-5 h-5" />
                    暂无章节
                  </button>
                )}
                <button
                  onClick={handleBookmark}
                  className={`btn-outline-white text-base ${bookmarked ? "!border-[#f59e0b]/50 !text-[#f59e0b]" : ""}`}
                >
                  <Heart className={`w-5 h-5 ${bookmarked ? "fill-[#f59e0b]" : ""}`} />
                  {bookmarked ? "已收藏" : "收藏"}
                </button>
                <button onClick={handleShare} className="w-11 h-11 rounded-xl flex items-center justify-center border border-white/10 text-white/40 hover:text-white/70 hover:border-white/25 transition-all">
                  <Share2 className="w-4.5 h-4.5" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="max-w-4xl mx-auto px-8 md:px-16 lg:px-24 pb-20">
        <ChapterList chapters={chapters.map(c => ({
          id: c.id,
          novelId: novel.id,
          title: c.title,
          content: "",
          order: c.chapter_index,
          wordCount: c.word_count,
          publishedAt: c.created_at,
        }))} novelId={novel.id} />
      </section>
    </div>
  );
}
