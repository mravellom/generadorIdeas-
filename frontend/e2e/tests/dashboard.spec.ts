import { test, expect } from '@playwright/test';

const MOCK_IDEAS = [
  {
    id: 1,
    name: 'TestStartup',
    description: 'A failed startup for testing',
    failure_reason: 'Bad timing',
    industry: 'SaaS',
    year: 2020,
    source_url: 'https://example.com',
    analysis: null,
    execution: null,
  },
  {
    id: 2,
    name: 'AnalyzedStartup',
    description: 'Already analyzed',
    failure_reason: null,
    industry: 'AI',
    year: 2022,
    source_url: null,
    analysis: {
      id: 1,
      problem: 'No market',
      failure_type: 'market',
      current_opportunity: 'alta',
      pain_score: 4,
      paying_capacity: 3,
      mvp_ease: 5,
      tech_advantage: 4,
      total_score: 16,
    },
    execution: null,
  },
];

test.beforeEach(async ({ page }) => {
  // Mock API responses so tests don't need a running backend
  await page.route('**/api/ideas/', (route) => {
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(MOCK_IDEAS) });
  });
  await page.route('**/api/ideas/top*', (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([MOCK_IDEAS[1]]),
    });
  });
  await page.route('**/api/scraper/run', (route) => {
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ message: 'Scraped 5 startups', count: 5 }) });
  });
  await page.route('**/api/ideas/analyze-all', (route) => {
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ analyzed: 1, errors: 0, pending: 0 }) });
  });
  await page.route('**/api/ideas/execute-all', (route) => {
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ executed: 1, errors: 0, pending: 0 }) });
  });
});

test.describe('Dashboard', () => {
  test('loads and shows title', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveURL(/dashboard/);
    await expect(page.locator('h1')).toHaveText('Dead Startups');
  });

  test('shows idea count in subtitle', async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page.locator('.subtitle')).toContainText('2 ideas en la base de datos');
  });

  test('shows filter buttons', async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page.getByRole('button', { name: 'Todas', exact: true })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Analizadas', exact: true })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Top Oportunidades' })).toBeVisible();
  });

  test('shows action buttons', async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page.getByRole('button', { name: /Scrapear/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /Analizar todas/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /Generar MVPs/i })).toBeVisible();
  });

  test('renders idea cards', async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page.locator('.idea-card')).toHaveCount(2);
    await expect(page.locator('.idea-card').first()).toContainText('TestStartup');
  });

  test('shows score badge for analyzed ideas', async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page.locator('.badge')).toContainText('16/20');
  });

  test('filter Analizadas shows only analyzed', async ({ page }) => {
    await page.goto('/dashboard');
    await page.getByRole('button', { name: 'Analizadas' }).click();
    await expect(page.locator('.idea-card')).toHaveCount(1);
    await expect(page.locator('.idea-card')).toContainText('AnalyzedStartup');
  });

  test('filter Top calls top endpoint', async ({ page }) => {
    await page.goto('/dashboard');
    await page.getByRole('button', { name: 'Top Oportunidades' }).click();
    await expect(page.locator('.idea-card')).toHaveCount(1);
  });

  test('scraper button shows result message', async ({ page }) => {
    await page.goto('/dashboard');
    await page.getByRole('button', { name: /Scrapear/i }).click();
    await expect(page.locator('.action-message')).toContainText('5 startups encontradas');
  });

  test('analyze all button shows result', async ({ page }) => {
    await page.goto('/dashboard');
    await page.getByRole('button', { name: /Analizar todas/i }).click();
    await expect(page.locator('.action-message')).toContainText('Analizadas: 1');
  });

  test('generate MVPs button shows result', async ({ page }) => {
    await page.goto('/dashboard');
    await page.getByRole('button', { name: /Generar MVPs/i }).click();
    await expect(page.locator('.action-message')).toContainText('Planes generados: 1');
  });
});
