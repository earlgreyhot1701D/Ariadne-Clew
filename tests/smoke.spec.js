// tests/smoke.spec.js
import { test, expect } from '@playwright/test';

test('frontend loads and submits recap', async ({ page }) => {
  // Adjust if you run frontend separately
  await page.goto('http://localhost:5000');

  // Fill session id and submit
  await page.fill('#session-id', 'smoke-session');
  await page.click('#submit-btn');

  // Status should update
  await expect(page.locator('#status')).toContainText(/Recap|Error/);

  // Recap output should eventually appear
  await expect(page.locator('#recap-output')).toBeVisible();
});
