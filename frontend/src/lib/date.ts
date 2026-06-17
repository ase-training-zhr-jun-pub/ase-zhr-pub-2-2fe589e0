// Kleine Datums-Helfer für den Prototyp (deutsche Formatierung, ISO <-> Date).

const WOCHENTAGE = [
  "Sonntag",
  "Montag",
  "Dienstag",
  "Mittwoch",
  "Donnerstag",
  "Freitag",
  "Samstag",
]

/** ISO-Datum "YYYY-MM-DD" -> Date (lokale Zeit, Mitternacht). */
export function isoToDate(iso: string): Date {
  const [y, m, d] = iso.split("-").map(Number)
  return new Date(y, m - 1, d)
}

/** Date -> ISO-Datum "YYYY-MM-DD". */
export function dateToIso(date: Date): string {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, "0")
  const d = String(date.getDate()).padStart(2, "0")
  return `${y}-${m}-${d}`
}

/** ISO-Datum -> "18.06.2026". */
export function formatDatum(iso: string): string {
  const date = isoToDate(iso)
  const d = String(date.getDate()).padStart(2, "0")
  const m = String(date.getMonth() + 1).padStart(2, "0")
  return `${d}.${m}.${date.getFullYear()}`
}

/** ISO-Datum -> "Donnerstag, 18.06.2026". */
export function formatDatumLang(iso: string): string {
  const date = isoToDate(iso)
  return `${WOCHENTAGE[date.getDay()]}, ${formatDatum(iso)}`
}
