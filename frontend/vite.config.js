// import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { configDefaults } from "vitest/config";
import tailwindcss from "@tailwindcss/vite";
// import { viteStaticCopy } from "vite-plugin-static-copy";
import path from "node:path";
import { createRequire } from "node:module";

import { defineConfig, normalizePath } from "vite";
import { viteStaticCopy } from "vite-plugin-static-copy";

const require = createRequire(import.meta.url);

const pdfjsDistPath = path.dirname(require.resolve("pdfjs-dist/package.json"));
const cMapsDir = normalizePath(path.join(pdfjsDistPath, "cmaps"));

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
    viteStaticCopy({
      targets: [
        {
          src: cMapsDir,
          dest: "",
        },
      ],
    }),
  ],
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
