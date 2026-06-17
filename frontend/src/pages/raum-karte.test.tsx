import { describe, it, expect, vi } from "vitest"
import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { RaumKarte } from "@/pages/raeume-finden"
import { getRaum } from "@/lib/mock-data"

// Beispielraum aus den Mock-Daten (Köln "Dom": 12 Personen, mit Whiteboard).
const raum = getRaum("koeln-dom")!

describe("RaumKarte", () => {
  it("zeigt Name, Kapazität und Ausstattung des Raums", () => {
    render(<RaumKarte raum={raum} verfuegbar selected={false} onSelect={() => {}} />)

    expect(screen.getByText(raum.name)).toBeInTheDocument()
    expect(screen.getByText(/12 Personen/)).toBeInTheDocument()
    expect(screen.getByText("Whiteboard")).toBeInTheDocument()
  })

  it("kann einen verfügbaren Raum auswählen und meldet die Auswahl", async () => {
    const onSelect = vi.fn()
    render(<RaumKarte raum={raum} verfuegbar selected={false} onSelect={onSelect} />)

    const button = screen.getByRole("button", { name: "Auswählen" })
    expect(button).toHaveAttribute("aria-pressed", "false")

    await userEvent.click(button)
    expect(onSelect).toHaveBeenCalledTimes(1)
  })

  it("hebt einen ausgewählten Raum sichtbar hervor", () => {
    render(<RaumKarte raum={raum} verfuegbar selected onSelect={() => {}} />)

    const button = screen.getByRole("button", { name: "Ausgewählt" })
    expect(button).toHaveAttribute("aria-pressed", "true")
  })

  it("lässt einen belegten Raum nicht auswählen", async () => {
    const onSelect = vi.fn()
    render(
      <RaumKarte raum={raum} verfuegbar={false} selected={false} onSelect={onSelect} />,
    )

    const button = screen.getByRole("button", { name: "Nicht verfügbar" })
    expect(button).toBeDisabled()
    expect(screen.getByText("Belegt")).toBeInTheDocument()

    await userEvent.click(button)
    expect(onSelect).not.toHaveBeenCalled()
  })
})
