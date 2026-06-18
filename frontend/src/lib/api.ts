/**
 * Zugriff auf die Backend-API (Booking-Service, FastAPI).
 *
 * Hinter dem Crucible-/VS-Code-Proxy läuft das Frontend unter
 * `…/proxy/5173/…`, das Backend unter `…/proxy/8000/`. Wir leiten die
 * Backend-Basis-URL aus der aktuellen Browser-URL ab, indem wir den
 * Frontend-Proxy-Port durch den Backend-Port ersetzen. Lokal (ohne Proxy)
 * zeigen wir auf denselben Host mit dem Backend-Port.
 */
import type { Buchung } from "@/lib/mock-data"

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

// ---------------------------------------------------------------------------
// Booking-Service: Verfügbarkeit & Buchungen (CLVN-010 / 019 / 020 / 023)
// ---------------------------------------------------------------------------

/**
 * Demo-Nutzer für die Basic-Auth (ADR-003: ohne Passwort, Nutzername = Nutzer-ID).
 * Im Prototyp gibt es noch keinen Login; die SPA authentifiziert sich fest als
 * dieser Nutzer. Mit der Okta-Anbindung wird das durch das echte Token ersetzt.
 */
export const NUTZER_ID = "demo"

/** Authorization-Header für Basic-Auth ohne Passwort: `Basic base64(name:)`. */
function authHeader(): Record<string, string> {
  return { Authorization: `Basic ${btoa(`${NUTZER_ID}:`)}` }
}

/** Wird geworfen, wenn das Backend eine Buchung wegen Doppelbuchung ablehnt (409). */
export class BuchungKonfliktError extends Error {}

/** Backend-Repräsentation einer Buchung (snake_case, von/bis). */
interface BackendBuchung {
  id: string
  nutzer_id: string
  raum_id: string
  standort_id: string
  datum: string
  von: string
  bis: string
  titel: string
  notiz: string | null
  erstellt_am: string
}

/** Mappt eine Backend-Buchung auf das Frontend-Modell (raumId, startzeit, endzeit). */
function toBuchung(b: BackendBuchung): Buchung {
  return {
    id: b.id,
    raumId: b.raum_id,
    datum: b.datum,
    startzeit: b.von,
    endzeit: b.bis,
    titel: b.titel,
    notiz: b.notiz ?? undefined,
  }
}

/** Belegtes Zeitfenster eines Raums (für die Trefferliste). */
export interface Belegung {
  raumId: string
  von: string
  bis: string
}

/** Prüft die Verfügbarkeit eines Raums für Datum + Zeitraum (CLVN-010). */
export async function fetchVerfuegbarkeit(
  raumId: string,
  datum: string,
  von: string,
  bis: string,
): Promise<boolean> {
  const params = new URLSearchParams({ raum_id: raumId, datum, von, bis })
  const res = await fetch(`${apiBaseUrl()}/api/verfuegbarkeit?${params}`)
  if (!res.ok) throw new Error(`Backend antwortete mit HTTP ${res.status}`)
  const data = (await res.json()) as { verfuegbar: boolean }
  return data.verfuegbar
}

/** Lädt die belegten Zeitfenster aller Räume eines Standorts an einem Datum. */
export async function fetchBelegungen(
  standortId: string,
  datum: string,
): Promise<Belegung[]> {
  const params = new URLSearchParams({ standort_id: standortId, datum })
  const res = await fetch(`${apiBaseUrl()}/api/belegungen?${params}`)
  if (!res.ok) throw new Error(`Backend antwortete mit HTTP ${res.status}`)
  const data = (await res.json()) as { raum_id: string; von: string; bis: string }[]
  return data.map((b) => ({ raumId: b.raum_id, von: b.von, bis: b.bis }))
}

/** Lädt die eigenen Buchungen des angemeldeten Nutzers (CLVN-023). */
export async function fetchMeineBuchungen(): Promise<Buchung[]> {
  const res = await fetch(`${apiBaseUrl()}/api/buchungen`, {
    headers: authHeader(),
  })
  if (!res.ok) throw new Error(`Backend antwortete mit HTTP ${res.status}`)
  const data = (await res.json()) as BackendBuchung[]
  return data.map(toBuchung)
}

/** Eingabe für eine neue Buchung (CLVN-019). */
export interface BuchungEingabe {
  raumId: string
  standortId: string
  datum: string
  von: string
  bis: string
  titel: string
  notiz?: string
}

/**
 * Sendet eine Raumbuchung an das Backend (CLVN-019).
 *
 * @throws {BuchungKonfliktError} wenn der Raum zwischenzeitlich belegt wurde (409)
 */
export async function createBuchung(eingabe: BuchungEingabe): Promise<Buchung> {
  const res = await fetch(`${apiBaseUrl()}/api/buchungen`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeader() },
    body: JSON.stringify({
      raum_id: eingabe.raumId,
      standort_id: eingabe.standortId,
      datum: eingabe.datum,
      von: eingabe.von,
      bis: eingabe.bis,
      titel: eingabe.titel,
      notiz: eingabe.notiz ?? null,
    }),
  })
  if (res.status === 409) {
    const data = (await res.json().catch(() => null)) as { detail?: string } | null
    throw new BuchungKonfliktError(
      data?.detail ?? "Der Raum ist im gewählten Zeitraum bereits belegt.",
    )
  }
  if (!res.ok) throw new Error(`Backend antwortete mit HTTP ${res.status}`)
  return toBuchung((await res.json()) as BackendBuchung)
}
