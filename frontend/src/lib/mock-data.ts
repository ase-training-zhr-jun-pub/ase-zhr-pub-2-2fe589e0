// Zentrale Mock-Daten für den Calvin Frontend-Prototyp.
// Kein Backend — alle Daten werden hier gemockt (siehe Rule "prototyp-scope").

// ---------------------------------------------------------------------------
// Standorte
// ---------------------------------------------------------------------------

export interface Standort {
  id: string
  name: string
}

/** Die acht INNOQ-Bürostandorte (siehe Glossar). */
export const STANDORTE: Standort[] = [
  { id: "monheim", name: "Monheim" },
  { id: "berlin", name: "Berlin" },
  { id: "hamburg", name: "Hamburg" },
  { id: "koeln", name: "Köln" },
  { id: "muenchen", name: "München" },
  { id: "zuerich", name: "Zürich" },
  { id: "baar", name: "Baar" },
  { id: "offenbach", name: "Offenbach" },
]

// ---------------------------------------------------------------------------
// Ausstattung
// ---------------------------------------------------------------------------

export type Ausstattung =
  | "Bildschirm"
  | "Whiteboard"
  | "Videokonferenz"
  | "Beamer"
  | "Flipchart"
  | "Telefonkonferenz"

// ---------------------------------------------------------------------------
// Konferenzräume
// ---------------------------------------------------------------------------

export interface Raum {
  id: string
  standortId: string
  name: string
  /** Maximale Personenzahl */
  kapazitaet: number
  etage: string
  raumnummer: string
  ausstattung: Ausstattung[]
  beschreibung: string
}

/**
 * Räume je Standort. Namen sind thematisch nach Wahrzeichen des jeweiligen
 * Standorts benannt, damit sich der Prototyp realistisch anfühlt.
 */
export const RAEUME: Raum[] = [
  // --- Köln ---
  {
    id: "koeln-dom",
    standortId: "koeln",
    name: "Dom",
    kapazitaet: 12,
    etage: "3. OG",
    raumnummer: "3.01",
    ausstattung: ["Bildschirm", "Whiteboard", "Videokonferenz", "Flipchart"],
    beschreibung:
      "Großer Konferenzraum mit Blick über die Stadt – ideal für Kundenworkshops.",
  },
  {
    id: "koeln-rheinauhafen",
    standortId: "koeln",
    name: "Rheinauhafen",
    kapazitaet: 8,
    etage: "2. OG",
    raumnummer: "2.14",
    ausstattung: ["Bildschirm", "Whiteboard", "Videokonferenz"],
    beschreibung: "Heller Meetingraum für Team-Meetings und Workshops.",
  },
  {
    id: "koeln-hohenzollern",
    standortId: "koeln",
    name: "Hohenzollernbrücke",
    kapazitaet: 4,
    etage: "2. OG",
    raumnummer: "2.05",
    ausstattung: ["Bildschirm", "Telefonkonferenz"],
    beschreibung: "Kompakter Raum für kurze Besprechungen.",
  },
  {
    id: "koeln-flora",
    standortId: "koeln",
    name: "Flora",
    kapazitaet: 6,
    etage: "1. OG",
    raumnummer: "1.08",
    ausstattung: ["Whiteboard", "Flipchart"],
    beschreibung: "Kreativraum mit viel Wandfläche für Design-Sessions.",
  },

  // --- Berlin ---
  {
    id: "berlin-brandenburger-tor",
    standortId: "berlin",
    name: "Brandenburger Tor",
    kapazitaet: 14,
    etage: "4. OG",
    raumnummer: "4.10",
    ausstattung: ["Bildschirm", "Whiteboard", "Videokonferenz", "Beamer"],
    beschreibung: "Repräsentativer Raum für größere Runden und Präsentationen.",
  },
  {
    id: "berlin-alexanderplatz",
    standortId: "berlin",
    name: "Alexanderplatz",
    kapazitaet: 8,
    etage: "3. OG",
    raumnummer: "3.22",
    ausstattung: ["Bildschirm", "Videokonferenz", "Whiteboard"],
    beschreibung: "Zentraler Meetingraum für Projektteams.",
  },
  {
    id: "berlin-tempelhof",
    standortId: "berlin",
    name: "Tempelhof",
    kapazitaet: 6,
    etage: "3. OG",
    raumnummer: "3.05",
    ausstattung: ["Bildschirm", "Telefonkonferenz"],
    beschreibung: "Ruhiger Raum für fokussierte Besprechungen.",
  },
  {
    id: "berlin-museumsinsel",
    standortId: "berlin",
    name: "Museumsinsel",
    kapazitaet: 4,
    etage: "2. OG",
    raumnummer: "2.11",
    ausstattung: ["Whiteboard"],
    beschreibung: "Kleiner Raum für 1:1s und schnelle Abstimmungen.",
  },

  // --- Hamburg ---
  {
    id: "hamburg-speicherstadt",
    standortId: "hamburg",
    name: "Speicherstadt",
    kapazitaet: 10,
    etage: "5. OG",
    raumnummer: "5.03",
    ausstattung: ["Bildschirm", "Whiteboard", "Videokonferenz", "Flipchart"],
    beschreibung: "Loft-artiger Raum mit Hafenblick.",
  },
  {
    id: "hamburg-elbphilharmonie",
    standortId: "hamburg",
    name: "Elbphilharmonie",
    kapazitaet: 6,
    etage: "4. OG",
    raumnummer: "4.07",
    ausstattung: ["Bildschirm", "Videokonferenz"],
    beschreibung: "Moderner Meetingraum für hybride Termine.",
  },
  {
    id: "hamburg-landungsbruecken",
    standortId: "hamburg",
    name: "Landungsbrücken",
    kapazitaet: 4,
    etage: "4. OG",
    raumnummer: "4.02",
    ausstattung: ["Telefonkonferenz"],
    beschreibung: "Telefonbox-naher Raum für vertrauliche Calls.",
  },

  // --- München ---
  {
    id: "muenchen-marienplatz",
    standortId: "muenchen",
    name: "Marienplatz",
    kapazitaet: 12,
    etage: "2. OG",
    raumnummer: "2.20",
    ausstattung: ["Bildschirm", "Whiteboard", "Videokonferenz", "Beamer"],
    beschreibung: "Großer Workshopraum mit flexibler Bestuhlung.",
  },
  {
    id: "muenchen-isar",
    standortId: "muenchen",
    name: "Isar",
    kapazitaet: 8,
    etage: "1. OG",
    raumnummer: "1.15",
    ausstattung: ["Bildschirm", "Whiteboard", "Videokonferenz"],
    beschreibung: "Heller Raum für Team-Meetings.",
  },
  {
    id: "muenchen-englischer-garten",
    standortId: "muenchen",
    name: "Englischer Garten",
    kapazitaet: 4,
    etage: "1. OG",
    raumnummer: "1.03",
    ausstattung: ["Bildschirm", "Telefonkonferenz"],
    beschreibung: "Grüner Rückzugsraum für kleine Runden.",
  },

  // --- Monheim ---
  {
    id: "monheim-rhein",
    standortId: "monheim",
    name: "Rhein",
    kapazitaet: 10,
    etage: "2. OG",
    raumnummer: "2.04",
    ausstattung: ["Bildschirm", "Whiteboard", "Videokonferenz"],
    beschreibung: "Hauptkonferenzraum am Standort Monheim.",
  },
  {
    id: "monheim-gaenseliesel",
    standortId: "monheim",
    name: "Gänseliesel",
    kapazitaet: 6,
    etage: "1. OG",
    raumnummer: "1.09",
    ausstattung: ["Bildschirm", "Videokonferenz"],
    beschreibung: "Kompakter Raum für hybride Meetings.",
  },

  // --- Zürich ---
  {
    id: "zuerich-grossmuenster",
    standortId: "zuerich",
    name: "Grossmünster",
    kapazitaet: 10,
    etage: "3. OG",
    raumnummer: "3.12",
    ausstattung: ["Bildschirm", "Whiteboard", "Videokonferenz", "Flipchart"],
    beschreibung: "Großzügiger Raum für Kundenworkshops.",
  },
  {
    id: "zuerich-limmat",
    standortId: "zuerich",
    name: "Limmat",
    kapazitaet: 6,
    etage: "2. OG",
    raumnummer: "2.08",
    ausstattung: ["Bildschirm", "Videokonferenz"],
    beschreibung: "Meetingraum mit moderner Technik.",
  },
  {
    id: "zuerich-uetliberg",
    standortId: "zuerich",
    name: "Uetliberg",
    kapazitaet: 4,
    etage: "2. OG",
    raumnummer: "2.01",
    ausstattung: ["Telefonkonferenz"],
    beschreibung: "Ruhiger Raum für Calls.",
  },

  // --- Baar ---
  {
    id: "baar-zugersee",
    standortId: "baar",
    name: "Zugersee",
    kapazitaet: 8,
    etage: "1. OG",
    raumnummer: "1.06",
    ausstattung: ["Bildschirm", "Whiteboard", "Videokonferenz"],
    beschreibung: "Heller Raum mit Seeblick.",
  },
  {
    id: "baar-hoellgrotten",
    standortId: "baar",
    name: "Höllgrotten",
    kapazitaet: 4,
    etage: "EG",
    raumnummer: "0.03",
    ausstattung: ["Bildschirm", "Telefonkonferenz"],
    beschreibung: "Kleiner Besprechungsraum im Erdgeschoss.",
  },

  // --- Offenbach ---
  {
    id: "offenbach-mainufer",
    standortId: "offenbach",
    name: "Mainufer",
    kapazitaet: 10,
    etage: "4. OG",
    raumnummer: "4.18",
    ausstattung: ["Bildschirm", "Whiteboard", "Videokonferenz", "Beamer"],
    beschreibung: "Großer Konferenzraum mit Beamer.",
  },
  {
    id: "offenbach-buesing-palais",
    standortId: "offenbach",
    name: "Büsing-Palais",
    kapazitaet: 6,
    etage: "3. OG",
    raumnummer: "3.09",
    ausstattung: ["Bildschirm", "Videokonferenz"],
    beschreibung: "Stilvoller Raum für Team-Meetings.",
  },
]

// ---------------------------------------------------------------------------
// Buchungen
// ---------------------------------------------------------------------------

export interface Buchung {
  id: string
  raumId: string
  /** ISO-Datum, z.B. "2026-06-18" */
  datum: string
  /** "HH:MM" */
  startzeit: string
  /** "HH:MM" */
  endzeit: string
  titel: string
  notiz?: string
}

/**
 * Bestehende Buchungen. Dienen zwei Zwecken:
 *  1. Belegung von Räumen (Verfügbarkeitsprüfung, CLVN-010/011)
 *  2. "Meine Buchungen"-Übersicht (CLVN-023)
 *
 * Heute ist im Prototyp der 2026-06-17.
 */
export const BUCHUNGEN: Buchung[] = [
  // Zukünftige eigene Buchungen
  {
    id: "b-1001",
    raumId: "koeln-rheinauhafen",
    datum: "2026-06-18",
    startzeit: "09:00",
    endzeit: "10:30",
    titel: "Sprint Planning Team Phoenix",
    notiz: "Bitte Whiteboard vorbereiten.",
  },
  {
    id: "b-1002",
    raumId: "berlin-tempelhof",
    datum: "2026-06-24",
    startzeit: "14:00",
    endzeit: "15:00",
    titel: "Kunden-Sync ACME",
  },
  {
    id: "b-1003",
    raumId: "koeln-dom",
    datum: "2026-07-02",
    startzeit: "10:00",
    endzeit: "16:00",
    titel: "Architektur-Workshop",
    notiz: "Ganztägig, Catering bestellt.",
  },
  // Vergangene Buchung
  {
    id: "b-0900",
    raumId: "koeln-hohenzollern",
    datum: "2026-06-03",
    startzeit: "10:00",
    endzeit: "11:00",
    titel: "1:1 mit Teamlead",
  },
  // Fremdbelegungen (nur für Verfügbarkeitsprüfung relevant)
  {
    id: "b-2001",
    raumId: "koeln-flora",
    datum: "2026-06-17",
    startzeit: "09:00",
    endzeit: "12:00",
    titel: "Belegt",
  },
  {
    id: "b-2002",
    raumId: "berlin-brandenburger-tor",
    datum: "2026-06-17",
    startzeit: "13:00",
    endzeit: "18:00",
    titel: "Belegt",
  },
  {
    id: "b-2003",
    raumId: "muenchen-isar",
    datum: "2026-06-17",
    startzeit: "08:00",
    endzeit: "18:00",
    titel: "Belegt",
  },
]

// ---------------------------------------------------------------------------
// Hilfsfunktionen
// ---------------------------------------------------------------------------

export function getStandort(id: string): Standort | undefined {
  return STANDORTE.find((s) => s.id === id)
}

export function getRaum(id: string): Raum | undefined {
  return RAEUME.find((r) => r.id === id)
}

export function getRaeumeByStandort(standortId: string): Raum[] {
  return RAEUME.filter((r) => r.standortId === standortId)
}

/** Wandelt "HH:MM" in Minuten seit Mitternacht. */
function toMinutes(zeit: string): number {
  const [h, m] = zeit.split(":").map(Number)
  return h * 60 + m
}

/** Prüft, ob sich zwei Zeitintervalle überschneiden. */
export function ueberschneidet(
  start1: string,
  end1: string,
  start2: string,
  end2: string,
): boolean {
  return toMinutes(start1) < toMinutes(end2) && toMinutes(start2) < toMinutes(end1)
}

/**
 * Prüft die Verfügbarkeit eines Raums für Datum + Zeitraum (CLVN-010).
 * Berücksichtigt bestehende Buchungen.
 */
export function istRaumVerfuegbar(
  raumId: string,
  datum: string,
  startzeit: string,
  endzeit: string,
): boolean {
  return !BUCHUNGEN.some(
    (b) =>
      b.raumId === raumId &&
      b.datum === datum &&
      ueberschneidet(startzeit, endzeit, b.startzeit, b.endzeit),
  )
}

/** Berechnet die Dauer zwischen zwei Zeiten als lesbaren String, z.B. "1 h 30 min". */
export function berechneDauer(startzeit: string, endzeit: string): string {
  const diff = toMinutes(endzeit) - toMinutes(startzeit)
  if (diff <= 0) return "–"
  const h = Math.floor(diff / 60)
  const m = diff % 60
  const teile: string[] = []
  if (h > 0) teile.push(`${h} h`)
  if (m > 0) teile.push(`${m} min`)
  return teile.join(" ")
}

/** Auswählbare Uhrzeiten innerhalb der Büroöffnungszeiten (08:00–19:00, 30-min-Raster). */
export const ZEITSLOTS: string[] = (() => {
  const slots: string[] = []
  for (let h = 8; h <= 19; h++) {
    slots.push(`${String(h).padStart(2, "0")}:00`)
    if (h < 19) slots.push(`${String(h).padStart(2, "0")}:30`)
  }
  return slots
})()

/** "Heute" im Prototyp-Kontext. */
export const HEUTE = "2026-06-17"
