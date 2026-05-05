import React from "react";
import { render, screen } from "@testing-library/react";
import { GlassCard } from "@/components/ui/glass-card";
import { GlassButton } from "@/components/ui/glass-button";
import { GlassInput } from "@/components/ui/glass-input";

jest.mock("next-themes", () => ({
  useTheme: () => ({ theme: "light", setTheme: jest.fn() }),
  ThemeProvider: ({ children }: { children: React.ReactNode }) => (
    <div>{children}</div>
  ),
}));

jest.mock("next/navigation", () => ({
  usePathname: () => "/",
  useRouter: () => ({ push: jest.fn() }),
  useSearchParams: () => new URLSearchParams(),
}));

describe("GlassCard 组件", () => {
  it("渲染子内容", () => {
    render(<GlassCard>测试卡片</GlassCard>);
    expect(screen.getByText("测试卡片")).toBeInTheDocument();
  });

  it("默认应用 glass-card 类名", () => {
    const { container } = render(<GlassCard>内容</GlassCard>);
    expect(container.firstChild).toHaveClass("glass-card");
  });

  it("hover=false 时应用 glass-panel 类名", () => {
    const { container } = render(<GlassCard hover={false}>内容</GlassCard>);
    expect(container.firstChild).toHaveClass("glass-panel");
  });
});

describe("GlassButton 组件", () => {
  it("渲染按钮文本", () => {
    render(<GlassButton>点击</GlassButton>);
    expect(screen.getByText("点击")).toBeInTheDocument();
  });

  it("支持 primary 变体", () => {
    render(<GlassButton variant="primary">主要按钮</GlassButton>);
    const button = screen.getByText("主要按钮");
    expect(button).toBeInTheDocument();
  });

  it("支持点击事件", () => {
    const handleClick = jest.fn();
    render(<GlassButton onClick={handleClick}>点击</GlassButton>);
    screen.getByText("点击").click();
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
});

describe("GlassInput 组件", () => {
  it("渲染输入框", () => {
    render(<GlassInput placeholder="请输入" />);
    expect(screen.getByPlaceholderText("请输入")).toBeInTheDocument();
  });

  it("支持图标前缀", () => {
    render(
      <GlassInput icon={<span data-testid="icon">🔍</span>} placeholder="搜索" />
    );
    expect(screen.getByTestId("icon")).toBeInTheDocument();
  });
});
