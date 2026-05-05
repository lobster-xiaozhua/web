"use client";

import React from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import ChapterList from "@/components/novel/ChapterList";
import type { Novel, Chapter, Comment } from "@/types";
import { Star, Eye, BookOpen, Heart, Share2, MessageCircle, Calendar, Clock } from "lucide-react";
import { formatNumber, formatDate } from "@/lib/utils";

const sampleNovel: Novel = {
  id: "1",
  title: "星辰大海",
  author: "远行者",
  cover: "",
  description:
    "在浩瀚星海中，一个少年踏上了寻找失落文明的旅程。穿越星际迷雾，揭开宇宙最深处的秘密。从荒芜星球到繁华星城，从古老遗迹到未知维度，每一步都充满危险与惊奇。他能否找到传说中的星海之心，拯救即将崩塌的宇宙？\n\n这是一部关于成长、勇气与宇宙终极奥秘的史诗级科幻作品。当少年林远踏上那艘银色飞船的那一刻起，命运的齿轮便开始转动。在无尽的星海中，他将面对未知的挑战，结识志同道合的伙伴，并最终发现一个足以改变整个宇宙的惊天秘密。",
  tags: ["科幻", "冒险", "星际"],
  rating: 4.8,
  viewCount: 128000,
  chapterCount: 256,
  status: "ongoing",
  updatedAt: "2026-05-04",
};

const sampleChapters: Chapter[] = Array.from({ length: 20 }, (_, i) => ({
  id: `ch-${i + 1}`,
  novelId: "1",
  title: i === 0 ? "启程" : `星海迷途·第${i + 1}节`,
  content: "",
  order: i + 1,
  wordCount: 2000 + Math.floor(Math.random() * 1000),
  publishedAt: "2026-05-01",
}));

const sampleComments: Comment[] = [
  {
    id: "c1",
    userId: "u1",
    username: "星河漫步者",
    avatar: "",
    content: "世界观设定太棒了，每个星球都有独特的生态和文化！文笔流畅，情节紧凑，一口气看了50章停不下来。",
    createdAt: "2026-05-04T10:30:00Z",
    likes: 42,
  },
  {
    id: "c2",
    userId: "u2",
    username: "深空观察者",
    avatar: "",
    content: "主角的成长轨迹很真实，不是一上来就无敌，推荐！作者对科幻元素的运用非常自然。",
    createdAt: "2026-05-03T18:20:00Z",
    likes: 28,
  },
  {
    id: "c3",
    userId: "u3",
    username: "量子读者",
    avatar: "",
    content: "文笔流畅，情节紧凑，期待后续发展。这本小说是我今年看过最好的科幻作品之一。",
    createdAt: "2026-05-02T09:15:00Z",
    likes: 15,
  },
];

export default function NovelDetailPage() {
  const params = useParams();
  const novelId = params.id as string;
  const novel = { ...sampleNovel, id: novelId };
  const coverUrl = `https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=${encodeURIComponent(`一本名为${novel.title}的${novel.tags[0]}类型小说封面，深色背景，极简设计，发光文字，科幻星空风格`)}`;

  return (
    <div className="min-h-screen">
      {/* ===== 顶部书籍信息区 — 开放式宽幅布局 ===== */}
      <section className="relative overflow-hidden">
        {/* 背景渐变 */}
        <div
          className="absolute inset-0 -z-10"
          style={{
            background:
              "linear-gradient(180deg, rgba(15,10,30,0.9) 0%, rgba(10,10,26,0) 50%, transparent 100%)",
          }}
        />
        <div className="absolute top-0 right-0 w-[500px] h-[400px] -z-10 opacity-30 pointer-events-none" style={{ background: "radial-gradient(circle, rgba(139,92,246,0.12) 0%, transparent 70%)", filter: "blur(80px)" }} />

        <div className="max-w-6xl mx-auto px-8 md:px-16 lg:px-24 pt-16 pb-16 md:pt-24 md:pb-24">
          <div className="flex flex-col md:flex-row gap-10 lg:gap-14 items-start">
            {/* 封面图 — 更大 */}
            <div className="shrink-0 mx-auto md:mx-0">
              <div className="w-56 md:w-64 lg:w-72 aspect-[3/4] rounded-2xl overflow-hidden shadow-2xl shadow-black/40 ring-1 ring-white/[0.08]">
                <img
                  src={coverUrl}
                  alt={novel.title}
                  className="w-full h-full object-cover"
                />
              </div>
            </div>

            {/* 信息区 */}
            <div className="flex-1 space-y-6 max-w-2xl">
              {/* 标签行 */}
              <div className="flex items-center gap-2">
                {novel.tags.map((tag) => (
                  <span
                    key={tag}
                    className="px-3 py-1 text-xs font-medium rounded-full bg-white/[0.06] text-white/60 border border-white/[0.08] hover:border-[#f59e0b]/30 hover:text-[#f59e0b]/80 transition-colors cursor-default"
                  >
                    {tag}
                  </span>
                ))}
                <span
                  className={`px-3 py-1 text-xs font-bold rounded-full ${
                    novel.status === "ongoing"
                      ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/20"
                      : "bg-blue-500/15 text-blue-400 border border-blue-500/20"
                  }`}
                >
                  {novel.status === "ongoing" ? "连载中" : "已完结"}
                </span>
              </div>

              {/* 标题 */}
              <h1 className="text-4xl md:text-5xl font-black text-white tracking-tight leading-tight">
                {novel.title}
              </h1>
              <p className="text-lg text-white/35 font-light">
                {novel.author} 著
              </p>

              {/* 元数据 — 精致排版 */}
              <div className="flex flex-wrap items-center gap-x-5 gap-y-2 text-sm text-white/40">
                <span className="flex items-center gap-1.5">
                  <Star className="w-4 h-4 fill-[#f59e0b] text-[#f59e0b]" />
                  <span className="font-semibold text-white/70">{novel.rating.toFixed(1)}</span>
                </span>
                <span className="text-white/15">|</span>
                <span className="flex items-center gap-1.5">
                  <Eye className="w-4 h-4" />
                  {formatNumber(novel.viewCount)} 阅读
                </span>
                <span className="text-white/15">|</span>
                <span className="flex items-center gap-1.5">
                  <BookOpen className="w-4 h-4" />
                  {novel.chapterCount} 章
                </span>
                <span className="text-white/15">|</span>
                <span className="flex items-center gap-1.5">
                  <Calendar className="w-4 h-4" />
                  更新于 {formatDate(novel.updatedAt)}
                </span>
              </div>

              {/* 描述文字 — 大字号+大行高 */}
              <p className="text-base md:text-lg text-white/45 leading-relaxed max-w-xl whitespace-pre-line">
                {novel.description}
              </p>

              {/* CTA 按钮组 */}
              <div className="flex items-center gap-4 pt-2">
                <Link href={`/read/ch-1?novelId=${novel.id}`}>
                  <button className="btn-primary text-base">
                    <BookOpen className="w-5 h-5" />
                    开始阅读
                  </button>
                </Link>
                <button className="btn-outline-white text-base">
                  <Heart className="w-5 h-5" />
                  收藏
                </button>
                <button className="w-11 h-11 rounded-xl flex items-center justify-center border border-white/10 text-white/40 hover:text-white/70 hover:border-white/25 transition-all">
                  <Share2 className="w-4.5 h-4.5" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ===== 章节列表 — 干净列表 ===== */}
      <section className="max-w-4xl mx-auto px-8 md:px-16 lg:px-24 pb-20">
        <ChapterList chapters={sampleChapters} novelId={novel.id} />
      </section>

      {/* ===== 评论区 — 减少嵌套层级 ===== */}
      <section className="max-w-3xl mx-auto px-8 md:px-16 lg:px-24 pb-28">
        <div className="mb-8">
          <h3 className="text-xl font-bold text-white">读者评论</h3>
          <p className="text-sm text-white/25 mt-1">共 {sampleComments.length} 条评论</p>
        </div>

        {/* 评论输入区 — 无卡片包裹 */}
        <div className="mb-10 p-6 rounded-2xl bg-white/[0.03] border border-white/[0.06]">
          <textarea
            placeholder="写下你的评论..."
            rows={3}
            className="w-full bg-transparent text-white/80 placeholder:text-white/20 resize-none outline-none text-[15px] leading-relaxed"
          />
          <div className="flex justify-end mt-3">
            <button className="btn-primary text-sm py-2 px-5">
              发表评论
            </button>
          </div>
        </div>

        {/* 评论列表 — 分隔线而非卡片 */}
        <div className="divide-y divide-white/[0.06]">
          {sampleComments.map((comment) => (
            <div key={comment.id} className="py-6 first:pt-0 last:pb-0">
              <div className="flex items-start gap-4">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-[#f59e0b]/30 to-purple-500/30 shrink-0 flex items-center justify-center ring-1 ring-white/[0.08]">
                  <span className="text-sm font-bold text-white/70">
                    {comment.username[0]}
                  </span>
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[15px] font-semibold text-white/85">
                      {comment.username}
                    </span>
                    <span className="text-xs text-white/20 flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {formatDate(comment.createdAt)}
                    </span>
                  </div>
                  <p className="text-[15px] text-white/45 leading-relaxed">
                    {comment.content}
                  </p>
                  <button className="flex items-center gap-1.5 mt-3 text-xs text-white/25 hover:text-[#f59e0b]/70 transition-colors">
                    <Heart className="w-3.5 h-3.5" />
                    {comment.likes}
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}