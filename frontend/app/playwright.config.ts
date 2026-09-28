import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: false,
  retries: 0,
  reporter: 'list',
  use: {
    baseURL: process.env.E2E_BASE_URL ?? 'http://localhost:43100',
    ...devices['Desktop Chrome'],
    ...(process.env.E2E_CHROMIUM_EXECUTABLE ? { launchOptions: { executablePath: process.env.E2E_CHROMIUM_EXECUTABLE, args: ['--no-sandbox', '--disable-dev-shm-usage'] } } : {}),
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
  timeout: 90_000,
});
