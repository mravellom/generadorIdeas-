import { test, expect } from '@playwright/test';

test.beforeEach(async ({ page }) => {
  await page.route('**/api/ideas/', (route) => {
    route.fulfill({ status: 200, contentType: 'application/json', body: '[]' });
  });
  await page.route('**/api/ideas/top*', (route) => {
    route.fulfill({ status: 200, contentType: 'application/json', body: '[]' });
  });
});

test.describe('Navigation', () => {
  test('redirects root to dashboard', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveURL(/dashboard/);
  });

  test('navbar is visible', async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page.locator('app-navbar')).toBeVisible();
  });
});
