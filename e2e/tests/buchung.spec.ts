import { test, expect } from "@playwright/test"

/**
 * E2E: Raumbuchungsprozess (Übung 3).
 *
 * Deckt den kompletten Flow ab: Buchungsübersicht → Suche → Standort/Datum/Raum
 * wählen → buchen → zurück zur Übersicht und prüfen, dass die neue Buchung da ist.
 *
 * Navigiert bewusst über die In-App-Links (SPA), damit der React-Context-State
 * (BookingProvider) über die Schritte hinweg erhalten bleibt — die Buchung lebt
 * im Prototyp nur im Speicher.
 */
test("Raumbuchungsprozess: neue Buchung erscheint in der Übersicht", async ({ page }) => {
  const titel = `E2E Sprint Planning ${Date.now()}`

  // 1. Buchungsübersicht öffnen
  await page.goto("/meine-buchungen")
  await expect(page.getByRole("heading", { name: "Meine Buchungen" })).toBeVisible()

  // 2. Bisherige Buchungen merken: unsere neue Buchung existiert noch nicht
  await expect(page.getByText(titel)).toHaveCount(0)

  // 3. Such-/Standort-Seite öffnen
  await page.getByRole("link", { name: "Räume finden" }).click()
  await expect(page.getByRole("heading", { name: "Räume finden" })).toBeVisible()

  // 4. Standort auswählen (Header-Select, eindeutig über aria-label)
  await page.getByRole("combobox", { name: "Standort auswählen" }).click()
  await page.getByRole("option", { name: "Köln" }).click()

  // 5. Datum auswählen: Popover öffnen und einen zukünftigen, freien Tag wählen
  await page.getByRole("button", { name: /\d{2}\.\d{2}\.\d{4}/ }).click()
  // Tag-Buttons tragen das volle Datum als Namen (z.B. "Samstag, 20. Juni 2026").
  await page.getByRole("button", { name: /20\. Juni 2026/ }).click()
  await page.keyboard.press("Escape")

  // 6. Raum auswählen (erster verfügbarer Raum)
  await page.getByRole("button", { name: "Auswählen" }).first().click()
  await expect(page.getByText("Deine Auswahl")).toBeVisible()

  // 7. Buchen: Auswahl bestätigen → Detailseite → Titel eingeben → absenden
  await page.getByRole("button", { name: "Auswahl bestätigen" }).click()
  await page.getByLabel(/Meetingtitel/).fill(titel)
  await page.getByRole("button", { name: "Buchung absenden" }).click()

  // 8. Buchungsübersicht öffnen
  await page.getByRole("link", { name: "Meine Buchungen" }).click()
  await expect(page.getByRole("heading", { name: "Meine Buchungen" })).toBeVisible()

  // 9. Verifizieren, dass die neue Buchung existiert
  await expect(page.getByText(titel)).toBeVisible()
})
