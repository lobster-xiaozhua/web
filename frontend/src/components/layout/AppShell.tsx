"use client";

import React, { useState } from "react";
import { usePathname } from "next/navigation";
import Navbar from "@/components/layout/Navbar";
import Sidebar from "@/components/layout/Sidebar";
import ToastContainer from "@/components/ui/toast";
import ErrorBoundary from "@/components/ui/error-boundary";
import { cn } from "@/lib/utils";

interface AppShellProps {
  children: React.ReactNode;
}

export default function AppShell({ children }: AppShellProps) {
  const pathname = usePathname();
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const isReaderPage = pathname.startsWith("/read");

  if (isReaderPage) {
    return (
      <ErrorBoundary>
        {children}
        <ToastContainer />
      </ErrorBoundary>
    );
  }

  return (
    <div className="min-h-screen">
      <Navbar onToggleSidebar={() => setSidebarOpen(!sidebarOpen)} />

      <Sidebar
        collapsed={sidebarCollapsed}
        onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
      />

      <div
        className={cn(
          "pt-[56px] transition-all duration-300",
          sidebarCollapsed ? "pl-0 md:pl-0" : "pl-0 md:pl-[220px]"
        )}
      >
        <main className={cn("p-6 md:p-10 lg:p-12 pb-[72px] page-enter", "relative z-10")}>
          <ErrorBoundary>
            {children}
          </ErrorBoundary>
        </main>
      </div>

      {sidebarOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/20 backdrop-blur-sm md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <div
        className={cn(
          "glass-sidebar md:hidden z-40 flex flex-col py-4",
          sidebarOpen && "open"
        )}
        style={{ top: 56 }}
      >
        <Sidebar onToggle={() => setSidebarOpen(false)} />
      </div>

      <ToastContainer />
    </div>
  );
}
