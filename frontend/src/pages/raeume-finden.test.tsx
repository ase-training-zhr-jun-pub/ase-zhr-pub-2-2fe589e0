import { describe, it, expect } from "vitest"
import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { MemoryRouter } from "react-router-dom"
import { RaeumeFinden } from "@/pages/raeume-finden"
import { BookingProvider } from "@/lib/booking-context"

// Standard-Suche ist Köln am 2026-06-17, 09:00–10:30: Dom, Rheinauhafen und
// Hohenzollernbrücke sind verfügbar, Flora ist belegt. Wir steuern nur die
// verfügbaren Räume an (Buttons "Auswählen"), bleiben damit datumsunabhängig.
function renderSeite() {
  render(
    <BookingProvider>
      <MemoryRouter>
        <RaeumeFinden />
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
