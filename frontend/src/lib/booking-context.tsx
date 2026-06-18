// Globaler Zustand des Buchungs-Flows (Prototyp, ohne Backend).
// Hält die aktuelle Suche (Standort/Datum/Zeit), die eigenen Buchungen
// und die zuletzt abgesendete Buchung für die Bestätigungsseite.

import { createContext, useContext, useMemo, useState, type ReactNode } from "react"
import { BUCHUNGEN, HEUTE, type Buchung } from "@/lib/mock-data"

export interface Suche {
  standortId: string
  datum: string
  startzeit: string
  endzeit: string
}

interface BookingContextValue {
  suche: Suche
  setSuche: (s: Partial<Suche>) => void
  /** Eigene Buchungen (inkl. neu abgesendeter). */
  meineBuchungen: Buchung[]
  /** Legt eine neue Buchung an und gibt sie zurück. */
  bucheRaum: (b: Omit<Buchung, "id">) => Buchung
  /** Entfernt eine Buchung aus der eigenen Liste und dem globalen Belegungsbestand. */
  storniereBuchung: (id: string) => void
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
