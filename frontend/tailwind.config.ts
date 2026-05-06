import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./src/app/**/*.{ts,tsx}",
    "./src/components/**/*.{ts,tsx}",
    "./src/lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        glass: {
          bg: "var(--glass-bg)",
          border: "var(--glass-border)",
        },
      },
      backdropBlur: {
        glass: "16px",
      },
      borderRadius: {
        glass: "var(--glass-radius)",
      },
      boxShadow: {
        glass: "0 8px 32px rgba(0, 0, 0, 0.12)",
        "glass-hover": "0 12px 40px rgba(0, 0, 0, 0.2)",
      },
      spacing: {
        navbar: "64px",
        sidebar: "240px",
        player: "56px",
      },
      maxWidth: {
        reader: "800px",
      },
    },
  },
  plugins: [],
};

export default config;
