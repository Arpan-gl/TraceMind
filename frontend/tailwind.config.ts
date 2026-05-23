import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: '#0ea5e9',
          600: '#0ea5e9',
          500: '#38bdf8',
        },
        surface: {
          DEFAULT: '#0f1724',
          800: '#0b1220',
        },
        panel: '#0b1220',
        muted: '#94a3b8',
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui'],
      },
    },
  },
  plugins: [],
} satisfies Config;
