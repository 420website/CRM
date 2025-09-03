import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { configDefaults } from "vitest/config";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    host: "0.0.0.0",
    allowedHosts: ["frontend", "localhost"],
  },
  test: {
    include: [
      "tests/**/*.test.{js,ts,jsx,tsx}",
      "tests/**/*.spec.{js,ts,jsx,tsx}",
    ],
    exclude: ["tests/e2e/**"],
    setupFiles: ["tests/setup.js"], // Optional setup file
    environment: "jsdom", // Needed for DOM-related tests in React
    clearMocks: true,
    restoreMocks: true,
    coverage: {
      reporter: ["text", "html"],
      include: ["src/services/**/*.js"],
      exclude: ["src/services/**/index.js"],
    },
  },
});
