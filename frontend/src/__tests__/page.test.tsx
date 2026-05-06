import React from "react";
import { render, screen } from "@testing-library/react";
import Home from "@/app/page";

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

describe("首页", () => {
  it("渲染首页标题", () => {
    render(<Home />);
    expect(screen.getByText("沉浸阅读，尽在玻璃书阁")).toBeInTheDocument();
  });

  it("渲染推荐书籍区域", () => {
    render(<Home />);
    expect(screen.getByText("推荐书籍")).toBeInTheDocument();
  });

  it("渲染热门排行区域", () => {
    render(<Home />);
    expect(screen.getByText("热门排行")).toBeInTheDocument();
  });

  it("渲染示例小说卡片", () => {
    render(<Home />);
    expect(screen.getByText("星辰大海")).toBeInTheDocument();
  });
});
