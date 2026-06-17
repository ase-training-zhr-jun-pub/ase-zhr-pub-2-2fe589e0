# ADR-002: Ressourcendaten als Mock-Daten in der SPA

**Status:** Akzeptiert
**Datum:** 2026-06-17

## Kontext und Problemstellung

Calvin verwaltet **Ressourcen-Stammdaten** – Standorte, Konferenzräume und deren
Ausstattung. Ursprünglich war denkbar, diese über einen eigenen **Resource-Service**
bereitzustellen. Für die Prototyp-Phase ist offen, wo diese Stammdaten leben und wie der
Booking-Service auf sie zugreift.

## Entscheidung

Der **Resource-Service entfällt** und wird in die **SPA integriert**:

- Standorte, Räume und Ausstattungen werden als **Mock-Daten in der SPA** hinterlegt
  (`frontend/src/lib/mock-data.ts`).
- Der **Booking-Service** hält **keine eigenen Ressourcen-Stammdaten**. Er arbeitet
  ausschließlich mit den **IDs** aus den SPA-Mock-Daten (z. B. `raumId`, `standortId`)
  und speichert Buchungen referenziert über diese IDs.

## Begründung

- **Schnelle Entwicklung (Prototyp):** Kein zusätzlicher Service, keine zusätzliche
  Persistenz und kein zusätzliches Deployment.
- **Geringe Änderungsrate:** Standorte, Räume und Ausstattung ändern sich selten; eine
  dynamische Verwaltung ist für den Prototyp nicht erforderlich.
- **Klare Schnittstelle:** Die SPA ist die Quelle der Ressourcendaten; der Booking-Service
  bleibt schlank und kümmert sich nur um Buchungen.

## Konsequenzen

**Positiv**
- Einfacher, schlanker Systemaufbau (SPA + Booking-Service, keine dritte Komponente).
- Die Ressourcendaten sind ohne Netzwerkzugriff sofort in der UI verfügbar.

**Negativ / Risiken**
- Stammdaten sind nur über einen **Code-Deploy der SPA** änderbar (keine Pflege zur Laufzeit).
- Der Booking-Service kann die **Gültigkeit von IDs nicht serverseitig prüfen** – er
  vertraut darauf, dass die SPA-Mock-Daten konsistent sind.
- **Doppelte Datenhoheit** vermeiden: Es existiert keine zentrale, persistente Quelle der
  Ressourcen-Stammdaten.

Diese Punkte sind als technische Schulden festgehalten
([Technische Schulden](../technische-schulden.md), TS-2 und TS-3) und werden mit dem
Übergang in Produktion adressiert.
