"use client";

import React from "react";

interface ErrorBoundaryProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

export default class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="flex flex-col items-center justify-center min-h-[400px] px-8">
          <div className="text-6xl mb-6">📚</div>
          <h2 className="text-xl font-bold text-white/80 mb-3">出了点问题</h2>
          <p className="text-sm text-white/40 mb-6 text-center max-w-md">
            页面渲染时发生了错误，请尝试刷新页面
          </p>
          <button
            onClick={() => {
              this.setState({ hasError: false, error: null });
              window.location.reload();
            }}
            className="btn-primary text-sm py-2.5 px-6"
          >
            刷新页面
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
