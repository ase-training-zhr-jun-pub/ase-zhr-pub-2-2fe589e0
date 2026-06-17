// Vitest-Setup: erweitert `expect` um die jest-dom-Matcher (z.B. toBeDisabled,
// toHaveAttribute), räumt nach jedem Test das gerenderte DOM auf und füllt ein
// paar Browser-APIs nach, die jsdom fehlen, ShadCN/base-ui aber erwartet.
import "@testing-library/jest-dom/vitest"
import { cleanup } from "@testing-library/react"
import { afterEach, vi } from "vitest"

afterEach(() => {
  cleanup()
})

// jsdom kennt diese APIs nicht – ohne Polyfill werfen base-ui-Komponenten.
if (!window.matchMedia) {
  window.matchMedia = vi.fn().mockImplementation((query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    addListener: vi.fn(),
    removeListener: vi.fn(),
    dispatchEvent: vi.fn(),
  }))
}

if (!globalThis.ResizeObserver) {
  globalThis.ResizeObserver = class {
    observe() {}
    unobserve() {}
    disconnect() {}
  }
}

Element.prototype.scrollIntoView ??= vi.fn()
Element.prototype.hasPointerCapture ??= vi.fn()
Element.prototype.releasePointerCapture ??= vi.fn()
