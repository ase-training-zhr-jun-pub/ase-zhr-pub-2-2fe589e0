/**
 * Zugriff auf die Backend-API (Booking-Service, Vapor).
 *
 * Hinter dem Crucible-/VS-Code-Proxy läuft das Frontend unter
 * `…/proxy/5173/…`, das Backend unter `…/proxy/8080/`. Wir leiten die
 * Backend-Basis-URL aus der aktuellen Browser-URL ab, indem wir den
 * Frontend-Proxy-Port durch den Backend-Port ersetzen. Lokal (ohne Proxy)
 * zeigen wir auf denselben Host mit dem Backend-Port.
 */
const BACKEND_PORT = "8000"

export function apiBaseUrl(): string {
  const { origin, pathname } = window.location

  // Hinter dem Proxy: ".../proxy/5173/..." -> ".../proxy/8080"
  const proxyMatch = pathname.match(/^(.*\/proxy\/)\d+(?:\/|$)/)
  if (proxyMatch) {
    return origin + proxyMatch[1] + BACKEND_PORT
  }

  // Lokale Entwicklung: Backend auf eigenem Port am selben Host.
  return origin.replace(/:\d+$/, `:${BACKEND_PORT}`)
}

/** Fragt den Smoke-Test-Endpunkt `/api/hello` ab und liefert die Antwort. */
export async function fetchHello(): Promise<string> {
  const res = await fetch(`${apiBaseUrl()}/api/hello`)
  if (!res.ok) {
    throw new Error(`Backend antwortete mit HTTP ${res.status}`)
  }
  return res.text()
}
