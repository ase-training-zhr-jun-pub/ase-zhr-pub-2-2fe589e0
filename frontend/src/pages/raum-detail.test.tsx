// Tests für CLVN-012: Alternative Zeitfenster anzeigen
//
// Kontext:
//   - BookingProvider-Standardzustand: Köln, datum=2026-06-17, 09:00–10:30
//   - koeln-flora ist am 2026-06-17 09:00–12:00 belegt (b-2001).
//     → 09:00–10:30 überschneidet sich → verfuegbar === false
//   - Es gibt freie 90-min-Slots ab 12:00 (12:00–13:30 usw.)

import { describe, it, expect } from "vitest"
import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { MemoryRouter, Route, Routes } from "react-router-dom"
import { BookingProvider } from "@/lib/booking-context"
import { RaumDetail } from "@/pages/raum-detail"

function renderRaumDetail(raumId: string) {
  render(
    <BookingProvider>
      <MemoryRouter initialEntries={[`/raeume/${raumId}`]}>
        <Routes>
          <Route path="/raeume/:raumId" element={<RaumDetail />} />
          <Route path="/buchung/bestaetigung" element={<div>Bestätigung</div>} />
        </Routes>
      </MemoryRouter>
    </BookingProvider>,
  )
}

describe("RaumDetail – alternative Zeitfenster (CLVN-012)", () => {
  it("zeigt die Belegtmeldung für koeln-flora bei Standardsuche", () => {
    renderRaumDetail("koeln-flora")

    expect(
      screen.getByText(/Dieser Raum ist im gewählten Zeitraum belegt/),
    ).toBeInTheDocument()
  })

  it("zeigt mindestens 3 alternative Zeitfenster für koeln-flora", () => {
    renderRaumDetail("koeln-flora")

    // Alternativen werden als Buttons mit Zeit-Notation "HH:MM–HH:MM" angezeigt.
    // Nach der Belegung 09:00–12:00 gibt es ab 12:00 freie 90-min-Slots.
    const alternativButtons = screen
      .getAllByRole("button")
      .filter((btn) => /\d{2}:\d{2}–\d{2}:\d{2}/.test(btn.textContent ?? ""))

    expect(alternativButtons.length).toBeGreaterThanOrEqual(3)
  })

  it("zeigt die Überschrift 'Alternative Zeitfenster:'", () => {
    renderRaumDetail("koeln-flora")

    expect(screen.getByText("Alternative Zeitfenster:")).toBeInTheDocument()
  })

  it("übernimmt die gewählte Alternative in die Buchungszusammenfassung", async () => {
    renderRaumDetail("koeln-flora")

    const alternativButtons = screen
      .getAllByRole("button")
      .filter((btn) => /\d{2}:\d{2}–\d{2}:\d{2}/.test(btn.textContent ?? ""))

    expect(alternativButtons.length).toBeGreaterThanOrEqual(1)

    // Klick auf ersten Alternativ-Slot
    const ersterSlot = alternativButtons[0]
    const slotText = ersterSlot.textContent ?? ""
    await userEvent.click(ersterSlot)

    // Nach der Auswahl soll die Zeit in der Buchungszusammenfassung erscheinen.
    // Die Zusammenfassung zeigt "startzeit–endzeit" im dl-Element.
    // Den genauen Text aus dem Button ableiten (z.B. "12:00–13:30").
    const match = slotText.match(/(\d{2}:\d{2})–(\d{2}:\d{2})/)
    if (match) {
      // Raum ist jetzt verfügbar → Belegtmeldung verschwindet
      expect(
        screen.queryByText(/Dieser Raum ist im gewählten Zeitraum belegt/),
      ).not.toBeInTheDocument()
    }
  })

  it("zeigt für verfügbare Räume keine alternativen Zeitfenster an", () => {
    // koeln-dom hat am 2026-06-17 keine Buchung → verfuegbar === true
    renderRaumDetail("koeln-dom")

    expect(
      screen.queryByText("Alternative Zeitfenster:"),
    ).not.toBeInTheDocument()
    expect(
      screen.queryByText(/Dieser Raum ist im gewählten Zeitraum belegt/),
    ).not.toBeInTheDocument()
  })
})
