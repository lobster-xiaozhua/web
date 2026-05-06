import * as React from "react";
import { cn } from "@/lib/utils";

interface GlassInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  icon?: React.ReactNode;
}

const GlassInput = React.forwardRef<HTMLInputElement, GlassInputProps>(
  ({ className, icon, ...props }, ref) => {
    if (icon) {
      return (
        <div className="relative group">
          <div className="absolute left-3.5 top-1/2 -translate-y-1/2 text-[var(--text-muted)] group-focus-within:text-[var(--accent)] transition-colors duration-300 pointer-events-none">
            {icon}
          </div>
          <input
            className={cn(
              "bg-[var(--glass-bg)] backdrop-blur-[24px] saturate-[180%] border border-[var(--glass-border)] rounded-xl shadow-[var(--glass-shadow)] py-3 pl-11 pr-4 text-sm text-[var(--text-primary)] outline-none w-full transition-all duration-300 placeholder:text-[var(--text-muted)] focus:border-[var(--accent)] focus:shadow-[0_0_0_3px_var(--accent-glow),var(--glass-shadow)]",
              className
            )}
            ref={ref}
            {...props}
          />
        </div>
      );
    }

    return (
      <input
        className={cn(
          "bg-[var(--glass-bg)] backdrop-blur-[24px] saturate-[180%] border border-[var(--glass-border)] rounded-xl shadow-[var(--glass-shadow)] py-3 px-4 text-sm text-[var(--text-primary)] outline-none w-full transition-all duration-300 placeholder:text-[var(--text-muted)] focus:border-[var(--accent)] focus:shadow-[0_0_0_3px_var(--accent-glow),var(--glass-shadow)]",
          className
        )}
        ref={ref}
        {...props}
      />
    );
  }
);
GlassInput.displayName = "GlassInput";

interface GlassTextareaProps
  extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  autoResize?: boolean;
}

const GlassTextarea = React.forwardRef<HTMLTextAreaElement, GlassTextareaProps>(
  ({ className, autoResize = false, onChange, ...props }, ref) => {
    const internalRef = React.useRef<HTMLTextAreaElement | null>(null);

    const setRefs = React.useCallback(
      (node: HTMLTextAreaElement | null) => {
        internalRef.current = node;
        if (typeof ref === "function") ref(node);
        else if (ref) (ref as React.MutableRefObject<HTMLTextAreaElement | null>).current = node;
      },
      [ref]
    );

    const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
      if (autoResize && internalRef.current) {
        internalRef.current.style.height = "auto";
        internalRef.current.style.height = `${internalRef.current.scrollHeight}px`;
      }
      onChange?.(e);
    };

    return (
      <textarea
        className={cn(
          "bg-[var(--glass-bg)] backdrop-blur-[24px] saturate-[180%] border border-[var(--glass-border)] rounded-xl shadow-[var(--glass-shadow)] py-3 px-4 text-sm text-[var(--text-primary)] outline-none w-full min-h-[100px] resize-y transition-all duration-300 placeholder:text-[var(--text-muted)] focus:border-[var(--accent)] focus:shadow-[0_0_0_3px_var(--accent-glow),var(--glass-shadow)]",
          className
        )}
        ref={setRefs}
        onChange={handleChange}
        {...props}
      />
    );
  }
);
GlassTextarea.displayName = "GlassTextarea";

export { GlassInput, GlassTextarea, type GlassInputProps, type GlassTextareaProps };
