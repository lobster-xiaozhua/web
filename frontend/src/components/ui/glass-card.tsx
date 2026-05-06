import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cn } from "@/lib/utils";

type GlassCardVariant = "default" | "elevated" | "subtle" | "borderless";

interface GlassCardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: GlassCardVariant;
  hover?: boolean;
  asChild?: boolean;
}

const variantStyles: Record<GlassCardVariant, string> = {
  default:
    "bg-[var(--glass-bg)] backdrop-blur-[24px] saturate-[180%] border border-[var(--glass-border)] rounded-[var(--glass-radius)] shadow-[var(--glass-shadow)]",
  elevated:
    "bg-[var(--glass-bg-elevated)] backdrop-blur-[24px] saturate-[180%] border border-[var(--glass-border)] rounded-[var(--glass-radius)] shadow-[var(--glass-shadow-hover)]",
  subtle:
    "bg-[var(--glass-bg-subtle)] backdrop-blur-[12px] saturate-[150%] border border-[var(--glass-border-subtle)] rounded-[var(--glass-radius)]",
  borderless:
    "bg-transparent",
};

const GlassCard = React.forwardRef<HTMLDivElement, GlassCardProps>(
  ({ className, variant = "default", hover = true, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "div";

    return (
      <Comp
        ref={ref}
        className={cn(
          variantStyles[variant],
          hover && "transition-all duration-400 ease-[cubic-bezier(0.4,0,0.2,1)] hover:-translate-y-1 hover:shadow-[var(--glass-shadow-hover)]",
          className
        )}
        {...props}
      />
    );
  }
);
GlassCard.displayName = "GlassCard";

export { GlassCard, type GlassCardProps, type GlassCardVariant };
