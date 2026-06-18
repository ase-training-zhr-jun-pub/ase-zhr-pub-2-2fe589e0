import { describe, it, expect, beforeEach } from "vitest"
import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { MemoryRouter } from "react-router-dom"
import { MeineBuchungen } from "@/pages/meine-buchungen"
import { BookingProvider } from "@/lib/booking-context"
import { BUCHUNGEN } from "@/lib/mock-data"

// Titel der eigenen Buchungen aus den Mock-Daten:
// b-1001 (kommend): "Sprint Planning Team Phoenix"
// b-1002 (kommend): "Kunden-Sync ACME"
// b-1003 (kommend): "Architektur-Workshop"
// b-0900 (vergangen): "1:1 mit Teamlead"

// Snapshot der globalen Mock-Buchungen, damit jeder Test einen sauberen Zustand hat.
// (storniereBuchung mutiert BUCHUNGEN direkt; ohne Reset würden Tests sich gegenseitig beeinflussen.)
const URSPRUENGLICHE_BUCHUNGEN = [...BUCHUNGEN]

beforeEach(() => {
  // BUCHUNGEN-Array auf den Ursprungszustand zurücksetzen.
  BUCHUNGEN.length = 0
  URSPRUENGLICHE_BUCHUNGEN.forEach((b) => BUCHUNGEN.push(b))
})

function renderSeite() {
  render(
    <BookingProvider>
      <MemoryRouter>
        <MeineBuchungen />
      </MemoryRouter>
    </BookingProvider>,
  )
}

describe("MeineBuchungen – Buchung stornieren (CLVN-026)", () => {
  it("entfernt eine kommende Buchung nach Bestätigung der Stornierung", async () => {
    renderSeite()

    // "Sprint Planning Team Phoenix" ist eine kommende Buchung und sichtbar.
    expect(screen.getByText("Sprint Planning Team Phoenix")).toBeInTheDocument()

    // Ersten Stornieren-Button anklicken (gehört zur ersten kommenden Buchung).
    const stornieren = screen.getAllByRole("button", { name: "Stornieren" })
    await userEvent.click(stornieren[0])

    // Im Popover den Bestätigungs-Button anklicken.
    // Nach dem Öffnen gibt es mehrere "Stornieren"-Buttons; der letzte ist der im Popup.
    const alleStornieren = screen.getAllByRole("button", { name: "Stornieren" })
    await userEvent.click(alleStornieren[alleStornieren.length - 1])

    // Die Buchung ist danach nicht mehr im Dokument.
    expect(screen.queryByText("Sprint Planning Team Phoenix")).not.toBeInTheDocument()
  })

  it("zeigt bei vergangenen Buchungen keinen Stornieren-Button", () => {
    renderSeite()

    // "1:1 mit Teamlead" ist die vergangene Buchung.
    expect(screen.getByText("1:1 mit Teamlead")).toBeInTheDocument()

    // Anzahl der Stornieren-Buttons: nur kommende Buchungen (b-1001, b-1002, b-1003).
    const stornierenButtons = screen.getAllByRole("button", { name: "Stornieren" })
    // 3 kommende Buchungen → 3 Stornieren-Buttons, aber KEIN vierter für die vergangene.
    expect(stornierenButtons).toHaveLength(3)
  })
})
