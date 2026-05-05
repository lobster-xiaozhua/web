import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const glassButtonVariants = cva(
  "inline-flex items-center justify-center whitespace-nowrap text-sm font-medium transition-all duration-300 ease-[cubic-bezier(0.4,0,0.2,1)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent)]/30 disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default:
          "bg-[var(--glass-bg)] backdrop-blur-[24px] saturate-[180%] border border-[var(--glass-border)] shadow-[var(--glass-shadow)] text-[var(--text-primary)] hover:bg-[var(--glass-bg-elevated)] hover:shadow-[var(--glass-shadow-hover)] hover:-translate-y-px active:translate-y-0",
        primary:
          "bg-gradient-to-r from-amber-400 to-orange-500 border border-transparent shadow-[0_4px_20px_rgba(245,158,11,0.35)] text-white hover:shadow-[0_6px_28px_rgba(245,158,11,0.45)] hover:-translate-y-px active:translate-y-0",
        ghost:
          "bg-transparent border-transparent shadow-none text-[var(--text-secondary)] hover:bg-[var(--glass-bg-subtle)] hover:text-[var(--text-primary)]",
        outline:
          "bg-transparent border border-[var(--glass-border)] shadow-none text-[var(--text-primary)] hover:bg-[var(--glass-bg-subtle)] hover:border-[var(--accent)]/40",
      },
      size: {
        sm: "h-8 px-3 text-xs rounded-lg",
        md: "h-9 px-4 py-2 rounded-xl",
        lg: "h-12 px-8 text-base rounded-xl",
        icon: "h-9 w-9 rounded-xl",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "md",
    },
  }
);

interface GlassButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof glassButtonVariants> {
  asChild?: boolean;
}

const GlassButton = React.forwardRef<HTMLButtonElement, GlassButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button";
    return (
      <Comp
        className={cn(glassButtonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    );
  }
);
GlassButton.displayName = "GlassButton";

export { GlassButton, glassButtonVariants, type GlassButtonProps };
