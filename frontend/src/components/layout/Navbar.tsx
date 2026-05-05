"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useTheme } from "next-themes";
import { Search, Sun, Moon, Menu, User, BookOpen } from "lucide-react";
import { GlassInput } from "@/components/ui/glass-input";
import { GlassButton } from "@/components/ui/glass-button";

interface NavbarProps {
  onToggleSidebar?: () => void;
}

export default function Navbar({ onToggleSidebar }: NavbarProps) {
  const { theme, setTheme } = useTheme();
  const [searchQuery, setSearchQuery] = useState("");

  const toggleTheme = () => {
    setTheme(theme === "dark" ? "light" : "dark");
  };

  return (
    <nav className="glass-nav flex items-center px-4 md:px-6 gap-4">
      <GlassButton
        variant="ghost"
        size="icon"
        className="md:hidden"
        onClick={onToggleSidebar}
        aria-label="切换侧边栏"
      >
        <Menu className="h-4.5 w-4.5" />
      </GlassButton>

      <Link href="/" className="flex items-center gap-2.5 shrink-0">
        <BookOpen className="h-6 w-6 text-[var(--accent)]" />
        <span className="text-xl font-bold text-gradient tracking-tight">
          玻璃书阁
        </span>
      </Link>

      <div className="flex-1 max-w-xs mx-auto hidden sm:block">
        <GlassInput
          icon={<Search className="h-3.5 w-3.5" />}
          placeholder="搜索小说、作者..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      <div className="flex items-center gap-1.5">
        <GlassButton
          variant="ghost"
          size="icon"
          onClick={toggleTheme}
          aria-label="切换主题"
          className="group"
        >
          <Sun className="h-[18px] w-[18px] rotate-0 scale-100 transition-all duration-500 group-hover:rotate-45 dark:-rotate-90 dark:scale-0 dark:group-hover:-rotate-45" />
          <Moon className="absolute h-[18px] w-[18px] rotate-90 scale-0 transition-all duration-500 group-hover:rotate-45 dark:rotate-0 dark:scale-100 dark:group-hover:rotate-12" />
        </GlassButton>

        <Link href="/user">
          <GlassButton variant="ghost" size="icon" aria-label="用户中心">
            <User className="h-[18px] w-[18px]" />
          </GlassButton>
        </Link>
      </div>
    </nav>
  );
}
