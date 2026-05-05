"use client";

import React, { useState, useMemo, useCallback, useEffect } from "react";
import { useParams, useSearchParams, useRouter } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, List, ChevronLeft, ChevronRight, Type, Sun, Moon, Minus, X } from "lucide-react";

const sampleParagraphs = [
  "星空之下，一艘银色的飞船划过漆黑的宇宙。驾驶舱内，少年林远紧握着操纵杆，目光坚定地注视着前方那片未知的星域。",
  "「距离目标星系还有三个标准时。」飞船的AI助手提醒道。林远点了点头，他已经在太空中漂泊了整整三个月，为了寻找父亲留下的线索。",
  "三个月前，林远还是地球上一个普通的天文系学生。直到那天，他在父亲遗留的旧电脑中发现了一段加密的星际坐标，以及一句意味深长的话——「星辰大海的尽头，有你需要的一切答案。」",
  "飞船缓缓驶入一片星云。五颜六色的气体在舷窗外翻涌，如同宇宙最绚烂的画卷。林远忍不住屏住了呼吸，即使见过无数次星云的照片，亲眼看到的震撼仍然无法言喻。",
  "然而，就在他沉浸在美景中时，警报突然响起。飞船的传感器检测到前方有异常的能量波动，而且这个波动的频率……与父亲留下的坐标信号完全一致。",
  "「不可能……」林远喃喃自语，手指飞快地在控制台上操作。数据不断刷新，最终确认了一个令人震惊的事实——这个能量源，来自一个不应该存在的方向。",
  "根据现有的星图，那个方向是一片被称为「虚空之眼」的区域。传说中，那里是宇宙的边界，任何进入的飞船都再也没有回来过。没有人知道那里有什么，因为所有探测器都在接近时失去了信号。",
  "林远深吸一口气，做出了一个大胆的决定。他调整航向，朝着虚空之眼飞去。飞船的引擎发出低沉的轰鸣，仿佛也在为即将到来的未知旅程而颤抖。",
  "随着飞船不断深入，周围的星光逐渐变得稀疏。原本璀璨的星空，像是被某种力量一点点吞噬。林远感到一阵莫名的寒意，但他的决心没有丝毫动摇。",
  "终于，在穿越了最后一层星云之后，眼前的景象让他彻底愣住了。那不是虚空，不是黑暗，而是一座——漂浮在宇宙中的巨大城市。",
  "城市的建筑风格古老而神秘，完全不属于任何已知文明。高耸的尖塔散发着淡蓝色的光芒，无数光桥连接着不同的区域，整座城市笼罩在一层半透明的能量护盾之中。",
  "「这是……」林远的声音在颤抖。他终于明白了父亲那句话的含义。星辰大海的尽头，确实有答案——一个关于宇宙起源、关于人类未来的终极答案。",
  "飞船缓缓降落在城市的外围平台上。当林远踏出舱门的那一刻，脚下的地面泛起了柔和的光芒，仿佛在欢迎这位时隔千年的访客。",
  "空气中弥漫着一种奇异的香味，像是雨后泥土的清新，又像是远方花田的芬芳。林远环顾四周，发现平台的边缘刻满了文字——一种他从未见过，却能奇妙地理解的文字。",
  "「勇者至此，星辰为证。」他轻声念出那行文字，心中涌起一股难以名状的感动。这不是偶然，不是巧合。父亲来过这里，而他也终于走到了这里。",
  "城市深处传来悠远的钟声，回荡在空旷的宇宙中。林远握紧了拳头，迈出了第一步。属于他的星辰大海，才刚刚开始。",
];

export default function ReaderPage() {
  const params = useParams();
  const searchParams = useSearchParams();
  const router = useRouter();
  const chapterId = params.chapterId as string;
  const novelId = searchParams.get("novelId") || "1";

  const [fontSize, setFontSize] = useState(18);
  const [theme, setTheme] = useState<"light" | "dark" | "sepia">("dark");
  const [progress, setProgress] = useState(35);
  const [showToc, setShowToc] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  const paragraphs = useMemo(() => sampleParagraphs, []);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 60);
    };
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const handlePrev = useCallback(() => {
    router.push(`/read/prev-chapter?novelId=${novelId}`);
  }, [router, novelId]);

  const handleNext = useCallback(() => {
    router.push(`/read/next-chapter?novelId=${novelId}`);
  }, [router, novelId]);

  const themeStyles = {
    light: { bg: "#faf8f5", text: "#2c2416" },
    dark: { bg: "#0a0a12", text: "#d4d0c8" },
    sepia: { bg: "#f4ecd8", text: "#3d3426" },
  };

  const currentTheme = themeStyles[theme];

  return (
    <div
      className="min-h-screen flex flex-col"
      style={{ backgroundColor: currentTheme.bg }}
    >
      {/* ===== 顶部栏 — 滚动触发透明度 ===== */}
      <header
        className={`fixed top-0 left-0 right-0 z-50 flex items-center px-6 h-[56px] transition-all duration-500 ${
          scrolled
            ? "bg-[rgba(10,10,18,0.85)] backdrop-blur-xl border-b border-white/[0.06]"
            : "bg-transparent"
        }`}
        style={scrolled ? undefined : { backgroundColor: "transparent" }}
      >
        <Link href={`/novel/${novelId}`}>
          <button className="w-10 h-10 rounded-xl flex items-center justify-center text-white/50 hover:text-white hover:bg-white/[0.08] transition-all">
            <ArrowLeft className="w-5 h-5" />
          </button>
        </Link>
        <span
          className="text-sm font-medium truncate ml-3 max-w-[50%]"
          style={{ color: scrolled ? currentTheme.text : "rgba(255,255,255,0.7)" }}
        >
          星辰大海 · 第一章 启程
        </span>
        <div className="flex-1" />
        <button
          onClick={() => setShowSettings(!showSettings)}
          className="w-10 h-10 rounded-xl flex items-center justify-center text-white/40 hover:text-white hover:bg-white/[0.08] transition-all"
        >
          <Type className="w-4.5 h-4.5" />
        </button>
        <button
          onClick={() => setShowToc(!showToc)}
          className="w-10 h-10 rounded-xl flex items-center justify-center text-white/40 hover:text-white hover:bg-white/[0.08) transition-all ml-1"
        >
          <List className="w-5 h-5" />
        </button>
      </header>

      {/* ===== 正文区域 — 沉浸式阅读 ===== */}
      <main className="flex-1 pt-[72px] pb-[80px] px-6">
        <article
          className="max-w-2xl mx-auto"
          style={{ color: currentTheme.text }}
        >
          <h1
            className="text-2xl md:text-3xl font-bold mb-16 tracking-tight leading-tight"
            style={{ color: currentTheme.text }}
          >
            第一章 启程
          </h1>
          <div
            className="space-y-8 text-justify"
            style={{ fontSize: `${fontSize}px`, lineHeight: 2.0 }}
          >
            {paragraphs.map((para, idx) => (
              <p key={idx} className="indent-[2em]" style={{ marginBottom: "2rem" }}>
                {para}
              </p>
            ))}
          </div>
        </article>
      </main>

      {/* ===== 翻页按钮 — 大且透明 ===== */}
      <button
        onClick={handlePrev}
        className="fixed left-6 top-1/2 -translate-y-1/2 w-14 h-14 md:w-16 md:h-16 rounded-full bg-black/20 backdrop-blur-sm border border-white/10 flex items-center justify-center text-white/30 hover:text-white/70 hover:bg-black/30 opacity-0 group-hover:opacity-100 focus:opacity-100 transition-all duration-300 z-30 hidden sm:flex"
        aria-label="上一章"
      >
        <ChevronLeft className="w-6 h-6" />
      </button>
      <button
        onClick={handleNext}
        className="fixed right-6 top-1/2 -translate-y-1/2 w-14 h-14 md:w-16 md:h-16 rounded-full bg-black/20 backdrop-blur-sm border border-white/10 flex items-center justify-center text-white/30 hover:text-white/70 hover:bg-black/30 opacity-0 group-hover:opacity-100 focus:opacity-100 transition-all duration-300 z-30 hidden sm:flex"
        aria-label="下一章"
      >
        <ChevronRight className="w-6 h-6" />
      </button>

      {/* ===== 进度条 — 极细 amber色 ===== */}
      <div className="fixed bottom-0 left-0 right-0 z-40">
        <div className="h-[2px] bg-white/[0.06]">
          <div
            className="h-full bg-[#f59e0b] transition-all duration-300 ease-out"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* ===== 目录抽屉 — 从右侧滑出 ===== */}
      {showToc && (
        <div className="fixed inset-0 z-50 flex">
          <div
            className="absolute inset-0 bg-black/40 backdrop-blur-sm"
            onClick={() => setShowToc(false)}
          />
          <div className="ml-auto w-80 max-w-[85vw] h-full bg-[#0e0e1a]/95 backdrop-blur-2xl border-l border-white/[0.06] overflow-auto animate-slide-in-right">
            <div className="p-8">
              <div className="flex items-center justify-between mb-8">
                <h3 className="text-lg font-bold text-white">目录</h3>
                <button
                  onClick={() => setShowToc(false)}
                  className="w-8 h-8 rounded-lg flex items-center justify-center text-white/35 hover:text-white/70 hover:bg-white/[0.06] transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
              <div className="divide-y divide-white/[0.05]">
                {Array.from({ length: 20 }, (_, i) => (
                  <button
                    key={i}
                    onClick={() => setShowToc(false)}
                    className="w-full text-left py-4 px-3 -mx-3 rounded-lg hover:bg-white/[0.04] transition-colors group"
                  >
                    <span className="text-xs text-white/15 font-mono mr-3 tabular-nums">
                      {String(i + 1).padStart(2, "0")}
                    </span>
                    <span className="text-[15px] text-white/45 group-hover:text-white/80 transition-colors">
                      第{i + 1}章 {i === 0 ? "启程" : `星海迷途·第${i + 1}节`}
                    </span>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ===== 设置面板 ===== */}
      {showSettings && (
        <div className="fixed bottom-20 left-1/2 -translate-x-1/2 z-50 w-[320px] max-w-[90vw] p-5 rounded-2xl bg-[#14141e]/95 backdrop-blur-xl border border-white/[0.08] shadow-2xl shadow-black/40 animate-fade-up">
          <div className="flex items-center justify-between mb-5">
            <span className="text-sm font-semibold text-white/70">阅读设置</span>
            <button
              onClick={() => setShowSettings(false)}
              className="w-7 h-7 rounded-md flex items-center justify-center text-white/25 hover:text-white/60 hover:bg-white/[0.06] transition-colors"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* 字号调节 */}
          <div className="mb-5">
            <label className="text-xs text-white/30 block mb-3">字号</label>
            <div className="flex items-center gap-4">
              <button
                onClick={() => setFontSize(Math.max(14, fontSize - 2))}
                className="w-9 h-9 rounded-lg bg-white/[0.05] border border-white/[0.08] flex items-center justify-center text-white/40 hover:text-white/70 hover:border-white/15 transition-all"
              >
                <Minus className="w-3.5 h-3.5" />
              </button>
              <span className="flex-1 text-center text-base font-medium text-white/70 tabular-nums">
                {fontSize}px
              </span>
              <button
                onClick={() => setFontSize(Math.min(28, fontSize + 2))}
                className="w-9 h-9 rounded-lg bg-white/[0.05] border border-white/[0.08] flex items-center justify-center text-white/40 hover:text-white/70 hover:border-white/15 transition-all"
              >
                <Type className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          {/* 主题切换 */}
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
                    theme === key
                      ? "border-[#f59e0b]/50 bg-[#f59e0b]/10"
                      : "border-white/[0.07] bg-transparent hover:border-white/15"
                  }`}
                >
                  <div
                    className="w-8 h-6 rounded-md ring-1 ring-inset"
                    style={{
                      backgroundColor: bg,
                      borderColor: theme === key ? "#f59e0b" : "rgba(255,255,255,0.1)",
                    }}
                  />
                  {Icon && <Icon className={`w-4 h-4 ${theme === key ? "text-[#f59e0b]" : "text-white/30"}`} />}
                  {!Icon && (
                    <span className={`text-[10px] ${theme === key ? "text-[#f59e0b]" : "text-white/30"}`}>A</span>
                  )}
                  <span className={`text-[11px] ${theme === key ? "text-white/90 font-medium" : "text-white/35"}`}>
                    {label}
                  </span>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}