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
