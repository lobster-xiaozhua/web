"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Home,
  BookMarked,
  Grid3X3,
  Trophy,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { GlassButton } from "@/components/ui/glass-button";

interface SidebarProps {
  collapsed?: boolean;
  onToggle?: () => void;
}

const navItems = [
  { href: "/", label: "首页", icon: Home },
  { href: "/user", label: "书架", icon: BookMarked },
  { href: "/novel/categories", label: "分类", icon: Grid3X3 },
  { href: "/novel/rankings", label: "排行", icon: Trophy },
];

export default function Sidebar({ collapsed = false, onToggle }: SidebarProps) {
  const pathname = usePathname();

  return (
    <aside
      className={cn(
        "glass-sidebar flex flex-col py-6",
        collapsed && "collapsed"
      )}
    >
      <nav className="flex-1 px-3 space-y-1">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link key={item.href} href={item.href}>
              <div
                className={cn(
                  "relative flex items-center gap-4 px-4 py-3 rounded-r-xl transition-all duration-300 group",
                  isActive
                    ? "text-[var(--accent)] font-semibold"
                    : "text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
                )}
              >
                {isActive && (
                  <span className="absolute left-0 top-1/2 -translate-y-1/2 w-[3px] h-5 bg-[var(--accent)] rounded-r-full" />
                )}
                <item.icon className="h-5 w-5 shrink-0 transition-colors" />
                {!collapsed && (
                  <span className="text-sm truncate">{item.label}</span>
                )}
              </div>
            </Link>
          );
        })}
      </nav>

      <div className="px-3 pt-6 mt-auto">
        <div className="section-divider mb-4" />
        <GlassButton
          variant="ghost"
          size="sm"
          className="w-full justify-center text-[var(--text-muted)] hover:text-[var(--text-secondary)]"
          onClick={onToggle}
        >
          {collapsed ? (
            <ChevronRight className="h-4 w-4" />
          ) : (
            <>
              <ChevronLeft className="h-4 w-4 mr-1.5" />
              <span className="text-xs">收起</span>
            </>
          )}
        </GlassButton>
      </div>
    </aside>
  );
}
