import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import path from "path";

// Resolve project root reliably in both CommonJS and ESM by using the current working directory
const rootDir = path.resolve(process.cwd());

export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./vitest.setup.ts"],
    include: ["src/__tests__/**/*.test.{js,jsx,ts,tsx}"],
    watch: false,
  },
});
