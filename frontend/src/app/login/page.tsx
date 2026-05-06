"use client";

import React, { useState } from "react";
import Link from "next/link";
import { GlassCard } from "@/components/ui/glass-card";
import { GlassButton } from "@/components/ui/glass-button";
import { GlassInput } from "@/components/ui/glass-input";
import { BookOpen, Eye, EyeOff } from "lucide-react";

export default function LoginPage() {
  const [isRegister, setIsRegister] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [username, setUsername] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <GlassCard hover={false} className="w-full max-w-md p-8 space-y-6">
        <div className="text-center space-y-2">
          <div className="flex items-center justify-center gap-2">
            <BookOpen className="h-8 w-8 text-[#667eea]" />
            <h1 className="text-2xl font-bold bg-gradient-to-r from-[#667eea] to-[#764ba2] bg-clip-text text-transparent">
              玻璃书阁
            </h1>
          </div>
          <p className="text-sm text-[var(--text-secondary)]">
            {isRegister ? "创建账号，开始阅读之旅" : "欢迎回来，继续你的阅读"}
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {isRegister && (
            <div>
              <label className="text-sm text-[var(--text-secondary)] mb-1 block">
                用户名
              </label>
              <GlassInput
                placeholder="请输入用户名"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
              />
            </div>
          )}

          <div>
            <label className="text-sm text-[var(--text-secondary)] mb-1 block">
              邮箱
            </label>
            <GlassInput
              type="email"
              placeholder="请输入邮箱"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          <div>
            <label className="text-sm text-[var(--text-secondary)] mb-1 block">
              密码
            </label>
            <div className="relative">
              <GlassInput
                type={showPassword ? "text" : "password"}
                placeholder="请输入密码"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
              <button
                type="button"
                className="absolute right-3 top-1/2 -translate-y-1/2 text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors"
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? (
                  <EyeOff className="h-4 w-4" />
                ) : (
                  <Eye className="h-4 w-4" />
                )}
              </button>
            </div>
          </div>

          <GlassButton
            variant="primary"
            size="lg"
            className="w-full"
            type="submit"
          >
            {isRegister ? "注册" : "登录"}
          </GlassButton>
        </form>

        <div className="text-center">
          <button
            className="text-sm text-[#667eea] hover:underline"
            onClick={() => setIsRegister(!isRegister)}
          >
            {isRegister ? "已有账号？去登录" : "没有账号？去注册"}
          </button>
        </div>

        <div className="relative">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-[var(--glass-border)]" />
          </div>
          <div className="relative flex justify-center text-xs">
            <span className="px-2 bg-transparent text-[var(--text-secondary)]">
              或者
            </span>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <GlassButton variant="ghost" className="w-full">
            微信登录
          </GlassButton>
          <GlassButton variant="ghost" className="w-full">
            QQ登录
          </GlassButton>
        </div>

        <p className="text-center text-xs text-[var(--text-secondary)]">
          登录即表示同意{" "}
          <Link href="#" className="text-[#667eea] hover:underline">
            用户协议
          </Link>{" "}
          和{" "}
          <Link href="#" className="text-[#667eea] hover:underline">
            隐私政策
          </Link>
        </p>
      </GlassCard>
    </div>
  );
}
