// Tests für die Buchung-Bearbeiten-Seite (CLVN-027).
// Seed-Buchung b-1001: raumId "koeln-rheinauhafen", Datum 2026-06-18, 09:00–10:30,
// Titel "Sprint Planning Team Phoenix"

import { describe, it, expect } from "vitest"
import { render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { MemoryRouter, Route, Routes } from "react-router-dom"
import { BookingProvider } from "@/lib/booking-context"
import { BuchungBearbeiten } from "@/pages/buchung-bearbeiten"

function renderSeite(id = "b-1001") {
  render(
    <BookingProvider>
      <MemoryRouter initialEntries={[`/buchung/${id}/bearbeiten`]}>
        <Routes>
          <Route path="/buchung/:id/bearbeiten" element={<BuchungBearbeiten />} />
          <Route path="/meine-buchungen" element={<div>Meine Buchungen Seite</div>} />
        </Routes>
      </MemoryRouter>
    </BookingProvider>,
  )
}

describe("BuchungBearbeiten", () => {
  it("zeigt das Formular mit vorausgefüllten Werten für eine bekannte Buchung", () => {
    renderSeite()

    // Titel-Feld enthält den gespeicherten Titel
    const titelInput = screen.getByRole("textbox", { name: /meetingtitel/i })
    expect(titelInput).toHaveValue("Sprint Planning Team Phoenix")
  })

  it("zeigt einen Hinweis und Link zurück, wenn die Buchung nicht existiert", () => {
    renderSeite("nicht-vorhanden")

    expect(screen.getByText(/buchung wurde nicht gefunden/i)).toBeInTheDocument()
    // ShadCN Button mit nativeButton=false rendert den Link mit role="button"
    expect(
      screen.getByRole("button", { name: /zurück zu meinen buchungen/i }),
    ).toBeInTheDocument()
  })

  it("ändert den Titel und leitet nach Speichern zur Übersichtsseite weiter", async () => {
    renderSeite()

    const titelInput = screen.getByRole("textbox", { name: /meetingtitel/i })

    // Titel ändern
    await userEvent.clear(titelInput)
    await userEvent.type(titelInput, "Neuer Titel für Test")

    // Speichern klicken
    await userEvent.click(screen.getByRole("button", { name: /speichern/i }))

    // Nach erfolgreichem Speichern Weiterleitung zur Übersichtsseite
    await waitFor(() => {
      expect(screen.getByText("Meine Buchungen Seite")).toBeInTheDocument()
    })
  })

  it("deaktiviert den Speichern-Button, wenn der Titel leer ist", async () => {
    renderSeite()

    const titelInput = screen.getByRole("textbox", { name: /meetingtitel/i })
    await userEvent.clear(titelInput)

    expect(screen.getByRole("button", { name: /speichern/i })).toBeDisabled()
  })

  it("navigiert bei Abbrechen zurück ohne zu speichern", async () => {
    renderSeite()

    // ShadCN Button mit nativeButton=false rendert den Link mit role="button"
    await userEvent.click(screen.getByRole("button", { name: /abbrechen/i }))

    expect(screen.getByText("Meine Buchungen Seite")).toBeInTheDocument()
  })
})
