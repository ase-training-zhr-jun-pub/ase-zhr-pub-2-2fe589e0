import { defineConfig, devices } from "@playwright/test"

/**
 * Playwright-Konfiguration für die Calvin-E2E-Tests.
 *
 * Der Frontend-Prototyp läuft hier ohne Backend (Mock-Daten). Für E2E starten
 * wir einen eigenen Vite-Dev-Server auf Port 5174 OHNE den Crucible-Proxy-Pfad
 * (VSCODE_PROXY_URI wird geleert → Vite served unter "/"), damit baseURL
 * stabil http://localhost:5174 ist.
 */
export default defineConfig({
  testDir: "./tests",
  timeout: 30_000,
  expect: { timeout: 10_000 },
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: 0,
  reporter: [["list"]],
  use: {
    baseURL: "http://localhost:5174",
    trace: "on-first-retry",
    screenshot: "only-on-failure",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: {
    command: "npm run dev -- --port 5174 --strictPort",
    cwd: "../frontend",
    url: "http://localhost:5174",
    timeout: 120_000,
    reuseExistingServer: !process.env.CI,
    // Proxy-Basis-Pfad leeren → App wird unter "/" ausgeliefert (siehe vite.config.ts).
    env: { VSCODE_PROXY_URI: "" },
  },
})
