import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react({
      // Fast Refresh optimizations
      fastRefresh: true,
      // Reduce overhead
      babel: {
        compact: true,
      },
    }),
  ],
  server: {
    port: 3000,
    // Enable HMR (Hot Module Replacement)
    hmr: {
      overlay: true,
    },
    // Optimize file watching
    watch: {
      usePolling: false, // Use native file watching (faster)
      ignored: ["**/node_modules/**", "**/dist/**", "**/.git/**"],
    },
    proxy: {
      // Proxy /api requests to the FastAPI backend server
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
        secure: false,
        ws: true, // WebSocket support
      },
    },
  },
  // Build optimizations
  build: {
    // Increase chunk size warning limit
    chunkSizeWarningLimit: 1000,
    rollupOptions: {
      output: {
        manualChunks: {
          // Split vendor code for better caching
          vendor: ["react", "react-dom", "react-router-dom"],
          mui: ["@mui/material", "@mui/icons-material"],
        },
      },
    },
  },
  // Optimize dependencies
  optimizeDeps: {
    include: [
      "react",
      "react-dom",
      "react-router-dom",
      "@mui/material",
      "@mui/icons-material",
      "axios",
    ],
  },
});
