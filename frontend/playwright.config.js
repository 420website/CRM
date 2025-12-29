import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./tests/playwright",
  use: {
    headless: true, // see the browser
    ignoreHTTPSErrors: true, // in case you switch to HTTPS
  },
});
