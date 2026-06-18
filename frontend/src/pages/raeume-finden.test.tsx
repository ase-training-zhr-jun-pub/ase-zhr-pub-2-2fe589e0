import { describe, it, expect } from "vitest"
import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { MemoryRouter, Route, Routes } from "react-router-dom"
import { RaeumeFinden } from "@/pages/raeume-finden"
import { BookingProvider } from "@/lib/booking-context"

// Standard-Suche ist Köln am 2026-06-17, 09:00–10:30: Dom, Rheinauhafen und
// Hohenzollernbrücke sind verfügbar, Flora ist belegt. Wir steuern nur die
// verfügbaren Räume an (Buttons "Auswählen"), bleiben damit datumsunabhängig.
function renderSeite() {
  render(
    <BookingProvider>
      <MemoryRouter>
        <Routes>
          <Route path="/" element={<RaeumeFinden />} />
          {/* Ziel der Bestätigungs-Weiterleitung (CLVN-030), hier nur ein Stub. */}
          <Route path="/raeume/:raumId" element={<div>Buchungsdetails-Seite</div>} />
        </Routes>
      </MemoryRouter>
    </BookingProvider>,
  )
}

describe("RaeumeFinden – Raumauswahl in der Trefferliste", () => {
  it("hebt genau den angeklickten Raum hervor", async () => {
    renderSeite()

    await userEvent.click(screen.getAllByRole("button", { name: "Auswählen" })[0])

    expect(screen.getAllByRole("button", { name: "Ausgewählt" })).toHaveLength(1)
  })

  it("verschiebt die Hervorhebung beim Auswählen eines anderen Raums", async () => {
    renderSeite()
    const auswaehlen = () => screen.getAllByRole("button", { name: "Auswählen" })

    await userEvent.click(auswaehlen()[0])
    // Nach der ersten Auswahl ist auswaehlen()[0] ein anderer verfügbarer Raum.
    await userEvent.click(auswaehlen()[0])

    // Weiterhin genau ein Raum ausgewählt – die alte Auswahl wurde aufgehoben.
    expect(screen.getAllByRole("button", { name: "Ausgewählt" })).toHaveLength(1)
  })

  it("hebt die Auswahl bei erneutem Klick wieder auf", async () => {
    renderSeite()

    await userEvent.click(screen.getAllByRole("button", { name: "Auswählen" })[0])
    await userEvent.click(screen.getByRole("button", { name: "Ausgewählt" }))

    expect(
      screen.queryByRole("button", { name: "Ausgewählt" }),
    ).not.toBeInTheDocument()
  })
})

describe("RaeumeFinden – Auswahl-Zusammenfassung & Bestätigung (CLVN-029/030)", () => {
  it("zeigt erst nach einer Auswahl die Zusammenfassung mit Zeitraum und Dauer", async () => {
    renderSeite()

    // Vor der Auswahl gibt es keine Zusammenfassung.
    expect(screen.queryByText("Deine Auswahl")).not.toBeInTheDocument()

    await userEvent.click(screen.getAllByRole("button", { name: "Auswählen" })[0])

    expect(screen.getByText("Deine Auswahl")).toBeInTheDocument()
    // Zeitraum und Dauer der Standard-Suche (09:00–10:30 = 1 h 30 min).
    expect(screen.getByText("09:00–10:30")).toBeInTheDocument()
    expect(screen.getByText("1 h 30 min")).toBeInTheDocument()
  })

  it("entfernt die Zusammenfassung, wenn die Auswahl aufgehoben wird", async () => {
    renderSeite()

    await userEvent.click(screen.getAllByRole("button", { name: "Auswählen" })[0])
    expect(screen.getByText("Deine Auswahl")).toBeInTheDocument()

    await userEvent.click(screen.getByRole("button", { name: "Ausgewählt" }))
    expect(screen.queryByText("Deine Auswahl")).not.toBeInTheDocument()
  })

  it("leitet bei Bestätigung zur Buchungsdetails-Seite weiter", async () => {
    renderSeite()

    await userEvent.click(screen.getAllByRole("button", { name: "Auswählen" })[0])
    const bestaetigen = screen.getByRole("button", { name: "Auswahl bestätigen" })
    expect(bestaetigen).toBeEnabled()

    await userEvent.click(bestaetigen)

    expect(screen.getByText("Buchungsdetails-Seite")).toBeInTheDocument()
  })
})

describe("RaeumeFinden – Kapazitätsfilter (CLVN-004)", () => {
  it("zeigt zunächst alle Köln-Räume (4 Räume)", () => {
    renderSeite()
    // Köln hat: Dom (12), Rheinauhafen (8), Hohenzollernbrücke (4), Flora (6)
    // Ergebnisüberschrift: "4 Räume in Köln"
    expect(screen.getByRole("heading", { level: 2 })).toHaveTextContent("4 Räume in Köln")
  })

  it("filtert auf Räume mit mindestens 8 Personen Kapazität", async () => {
    renderSeite()

    // Kapazitäts-Select öffnen und "8 Personen" wählen
    const kapSelect = screen.getByRole("combobox", { name: "Mindestkapazität" })
    await userEvent.click(kapSelect)
    await userEvent.click(screen.getByRole("option", { name: "8 Personen" }))

    // Nur Dom (12) und Rheinauhafen (8) übrig
    expect(screen.getByRole("heading", { level: 2 })).toHaveTextContent("2 Räume in Köln")
    expect(screen.getByText("Dom")).toBeInTheDocument()
    expect(screen.getByText("Rheinauhafen")).toBeInTheDocument()
    expect(screen.queryByText("Hohenzollernbrücke")).not.toBeInTheDocument()
    expect(screen.queryByText("Flora")).not.toBeInTheDocument()
  })

  it("zeigt den aktiven Kapazitätsfilter als Badge an", async () => {
    renderSeite()

    const kapSelect = screen.getByRole("combobox", { name: "Mindestkapazität" })
    await userEvent.click(kapSelect)
    await userEvent.click(screen.getByRole("option", { name: "6 Personen" }))

    expect(screen.getByText("≥ 6 Personen")).toBeInTheDocument()
  })

  it("entfernt den Kapazitätsfilter einzeln über das X im Badge", async () => {
    renderSeite()

    const kapSelect = screen.getByRole("combobox", { name: "Mindestkapazität" })
    await userEvent.click(kapSelect)
    await userEvent.click(screen.getByRole("option", { name: "8 Personen" }))

    // Kapazitätsfilter über X-Button entfernen
    await userEvent.click(
      screen.getByRole("button", { name: "Kapazitätsfilter 8 Personen entfernen" }),
    )

    // Alle 4 Räume wieder sichtbar
    expect(screen.getByRole("heading", { level: 2 })).toHaveTextContent("4 Räume in Köln")
  })
})

describe("RaeumeFinden – Ausstattungsfilter (CLVN-005)", () => {
  it("filtert auf Räume mit Videokonferenz", async () => {
    renderSeite()

    // "Videokonferenz"-Badge als Toggle aktivieren
    await userEvent.click(screen.getByRole("button", { name: "Videokonferenz" }))

    // Dom, Rheinauhafen haben Videokonferenz; Hohenzollernbrücke und Flora nicht
    expect(screen.getByRole("heading", { level: 2 })).toHaveTextContent("2 Räume in Köln")
    expect(screen.getByText("Dom")).toBeInTheDocument()
    expect(screen.getByText("Rheinauhafen")).toBeInTheDocument()
    expect(screen.queryByText("Hohenzollernbrücke")).not.toBeInTheDocument()
    expect(screen.queryByText("Flora")).not.toBeInTheDocument()
  })

  it("kombiniert mehrere Ausstattungsmerkmale (UND-Verknüpfung)", async () => {
    renderSeite()

    // Videokonferenz UND Flipchart: nur Dom hat beides
    await userEvent.click(screen.getByRole("button", { name: "Videokonferenz" }))
    await userEvent.click(screen.getByRole("button", { name: "Flipchart" }))

    expect(screen.getByRole("heading", { level: 2 })).toHaveTextContent("1 Räume in Köln")
    expect(screen.getByText("Dom")).toBeInTheDocument()
  })

  it("zeigt aktive Ausstattungsfilter als Badges an", async () => {
    renderSeite()

    await userEvent.click(screen.getByRole("button", { name: "Beamer" }))

    // Badge mit "Beamer" taucht im Aktiv-Filter-Bereich auf
    // (es gibt jetzt zwei Elemente mit "Beamer": den Toggle-Button und das aktive Badge)
    const beamerBadges = screen.getAllByText("Beamer")
    expect(beamerBadges.length).toBeGreaterThanOrEqual(2)
  })

  it("entfernt einen Ausstattungsfilter einzeln über das X im Badge", async () => {
    renderSeite()

    await userEvent.click(screen.getByRole("button", { name: "Videokonferenz" }))
    // Jetzt 2 Räume sichtbar

    // X-Button zum Entfernen des Filters
    await userEvent.click(
      screen.getByRole("button", { name: "Ausstattungsfilter Videokonferenz entfernen" }),
    )

    // Alle 4 Räume wieder sichtbar
    expect(screen.getByRole("heading", { level: 2 })).toHaveTextContent("4 Räume in Köln")
  })
})

describe("RaeumeFinden – Kombinierte Filter & Zurücksetzen", () => {
  it("kombiniert Kapazitäts- und Ausstattungsfilter", async () => {
    renderSeite()

    // Mindestens 8 Personen UND Whiteboard:
    // Dom (12, hat Whiteboard) ✓, Rheinauhafen (8, hat Whiteboard) ✓,
    // Hohenzollernbrücke (4 → fällt durch Kapazität raus),
    // Flora (6 → fällt durch Kapazität raus)
    const kapSelect = screen.getByRole("combobox", { name: "Mindestkapazität" })
    await userEvent.click(kapSelect)
    await userEvent.click(screen.getByRole("option", { name: "8 Personen" }))

    await userEvent.click(screen.getByRole("button", { name: "Whiteboard" }))

    expect(screen.getByRole("heading", { level: 2 })).toHaveTextContent("2 Räume in Köln")
  })

  it("setzt alle Filter über 'Filter zurücksetzen' zurück", async () => {
    renderSeite()

    const kapSelect = screen.getByRole("combobox", { name: "Mindestkapazität" })
    await userEvent.click(kapSelect)
    await userEvent.click(screen.getByRole("option", { name: "12 Personen" }))

    await userEvent.click(screen.getByRole("button", { name: "Whiteboard" }))

    // Nur noch 1 Raum (Dom: 12 Personen + Whiteboard)
    expect(screen.getByRole("heading", { level: 2 })).toHaveTextContent("1 Räume in Köln")

    // Zurücksetzen
    await userEvent.click(screen.getByRole("button", { name: "Filter zurücksetzen" }))

    // Alle 4 Räume wieder da
    expect(screen.getByRole("heading", { level: 2 })).toHaveTextContent("4 Räume in Köln")
    expect(screen.queryByText("Filter zurücksetzen")).not.toBeInTheDocument()
  })

  it("zeigt Leer-Meldung, wenn kein Raum den Filtern entspricht", async () => {
    renderSeite()

    // Unmögliche Kombination: ≥ 20 Personen in Köln → kein Raum
    const kapSelect = screen.getByRole("combobox", { name: "Mindestkapazität" })
    await userEvent.click(kapSelect)
    await userEvent.click(screen.getByRole("option", { name: "20 Personen" }))

    expect(screen.getByRole("status")).toHaveTextContent(
      "Keine Räume gefunden. Bitte passe die Filter an.",
    )
    expect(screen.getByRole("heading", { level: 2 })).toHaveTextContent("0 Räume in Köln")
  })
})
