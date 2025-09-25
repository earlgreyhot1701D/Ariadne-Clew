// playwright.config.js
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  timeout: 30 * 1000,
  use: {
    headless: true,
    baseURL: 'http://localhost:5000', // adjust if frontend runs on another port
  },
  reporter: [['list'], ['html', { outputFolder: 'playwright-report' }]],
});
