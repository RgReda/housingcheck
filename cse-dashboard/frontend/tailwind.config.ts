import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#004d7a",
          light: "#3a7ca5",
          dark: "#003352"
        }
      }
    }
  },
  plugins: []
} satisfies Config;
