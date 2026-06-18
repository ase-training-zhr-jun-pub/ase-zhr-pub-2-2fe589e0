# E2E-Tests (Playwright)

End-to-End-Tests für den Calvin-Frontend-Prototyp. Die Tests fahren die echte UI
im Browser und decken den Buchungs-Flow durchgängig ab.

> Der Prototyp läuft ohne Backend (Mock-Daten). Die Buchung lebt nur im Speicher
> (React-Context), daher navigieren die Tests über die In-App-Links statt per
> `page.goto`, damit der Zustand über die Schritte erhalten bleibt.

## Setup

```bash
cd e2e
npm install                              # @playwright/test
npx playwright install chromium          # Browser-Binary
sudo npx playwright install-deps chromium  # System-Bibliotheken (libglib u.a.)
```

## Ausführen

```bash
cd e2e
npm test            # headless
npm run test:headed # mit sichtbarem Browser
npm run report      # HTML-Report des letzten Laufs
```

Playwright startet automatisch einen Vite-Dev-Server auf **Port 5174** ohne den
Crucible-Proxy-Pfad (`VSCODE_PROXY_URI` wird geleert, siehe `playwright.config.ts`),
sodass die App stabil unter `http://localhost:5174/` erreichbar ist.

## Abgedeckte Szenarien

- **`tests/buchung.spec.ts` – Raumbuchungsprozess:**
  Buchungsübersicht öffnen → bisherigen Stand merken → Suche öffnen →
  Standort wählen → Datum wählen → Raum auswählen → buchen →
  zurück zur Übersicht → verifizieren, dass die neue Buchung erscheint.
