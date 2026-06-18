// Globaler Zustand des Buchungs-Flows (Prototyp, ohne Backend).
// Hält die aktuelle Suche (Standort/Datum/Zeit), die eigenen Buchungen
// und die zuletzt abgesendete Buchung für die Bestätigungsseite.

import { createContext, useContext, useMemo, useState, type ReactNode } from "react"
import { BUCHUNGEN, HEUTE, istRaumVerfuegbar, type Buchung } from "@/lib/mock-data"

export interface Suche {
  standortId: string
  datum: string
  startzeit: string
  endzeit: string
}

/** Felder, die bei einer Buchungsänderung aktualisiert werden können. */
export type BuchungPatch = Partial<
  Pick<Buchung, "datum" | "startzeit" | "endzeit" | "raumId" | "titel" | "notiz">
>

/** Ergebnis von aendereBuchung: Erfolg oder Fehler mit Grund. */
export type AenderungErgebnis =
  | { ok: true; buchung: Buchung }
  | { ok: false; grund: string }

interface BookingContextValue {
  suche: Suche
  setSuche: (s: Partial<Suche>) => void
  /** Eigene Buchungen (inkl. neu abgesendeter). */
  meineBuchungen: Buchung[]
  /** Legt eine neue Buchung an und gibt sie zurück. */
  bucheRaum: (b: Omit<Buchung, "id">) => Buchung
  /** Entfernt eine Buchung aus der eigenen Liste und dem globalen Belegungsbestand. */
  storniereBuchung: (id: string) => void
  /**
   * Ändert eine bestehende Buchung (CLVN-027).
   * Prüft die Verfügbarkeit des Zielraums – die zu ändernde Buchung selbst
   * wird dabei nicht als Konflikt gewertet.
   */
  aendereBuchung: (id: string, patch: BuchungPatch) => AenderungErgebnis
  /** Zuletzt abgesendete Buchung (für die Bestätigungsseite). */
  letzteBuchung: Buchung | null
}

const BookingContext = createContext<BookingContextValue | null>(null)

// Nur die eigenen Buchungen als Startbestand der "Meine Buchungen"-Liste.
const EIGENE_BUCHUNG_IDS = ["b-1001", "b-1002", "b-1003", "b-0900"]

export function BookingProvider({ children }: { children: ReactNode }) {
  const [suche, setSucheState] = useState<Suche>({
    standortId: "koeln",
    datum: HEUTE,
    startzeit: "09:00",
    endzeit: "10:30",
  })
  const [meineBuchungen, setMeineBuchungen] = useState<Buchung[]>(() =>
    BUCHUNGEN.filter((b) => EIGENE_BUCHUNG_IDS.includes(b.id)),
  )
  const [letzteBuchung, setLetzteBuchung] = useState<Buchung | null>(null)

  const value = useMemo<BookingContextValue>(
    () => ({
      suche,
      setSuche: (s) => setSucheState((prev) => ({ ...prev, ...s })),
      meineBuchungen,
      bucheRaum: (b) => {
        const neu: Buchung = { ...b, id: `b-${Date.now()}` }
        // In den globalen Belegungsbestand übernehmen (Verfügbarkeitsprüfung)
        BUCHUNGEN.push(neu)
        setMeineBuchungen((prev) => [...prev, neu])
        setLetzteBuchung(neu)
        return neu
      },
      storniereBuchung: (id) => {
        // Aus dem globalen Belegungsbestand entfernen (Raum wird wieder verfügbar)
        const idx = BUCHUNGEN.findIndex((b) => b.id === id)
        if (idx !== -1) BUCHUNGEN.splice(idx, 1)
        setMeineBuchungen((prev) => prev.filter((b) => b.id !== id))
      },
      aendereBuchung: (id, patch) => {
        // Aktuelle Buchung suchen
        const alt = meineBuchungen.find((b) => b.id === id)
        if (!alt) {
          return { ok: false, grund: "Buchung nicht gefunden." }
        }

        const geaendert: Buchung = { ...alt, ...patch }

        // Verfügbarkeitsprüfung: alte Buchung vorübergehend aus globalem Array entfernen,
        // damit sie nicht als Konflikt mit sich selbst gewertet wird.
        const altIdx = BUCHUNGEN.findIndex((b) => b.id === id)
        if (altIdx !== -1) BUCHUNGEN.splice(altIdx, 1)

        const verfuegbar = istRaumVerfuegbar(
          geaendert.raumId,
          geaendert.datum,
          geaendert.startzeit,
          geaendert.endzeit,
        )

        if (!verfuegbar) {
          // Alte Buchung wieder einfügen und Fehler melden
          if (altIdx !== -1) BUCHUNGEN.splice(altIdx, 0, alt)
          return {
            ok: false,
            grund: "Der Raum ist im gewählten Zeitraum bereits belegt.",
          }
        }

        // Globales Array mit geänderter Buchung aktualisieren
        BUCHUNGEN.splice(altIdx, 0, geaendert)

        // Eigene Buchungen aktualisieren
        setMeineBuchungen((prev) => prev.map((b) => (b.id === id ? geaendert : b)))

        return { ok: true, buchung: geaendert }
      },
      letzteBuchung,
    }),
    [suche, meineBuchungen, letzteBuchung],
  )

  return <BookingContext.Provider value={value}>{children}</BookingContext.Provider>
}

export function useBooking(): BookingContextValue {
  const ctx = useContext(BookingContext)
  if (!ctx) throw new Error("useBooking muss innerhalb von BookingProvider verwendet werden")
  return ctx
}
