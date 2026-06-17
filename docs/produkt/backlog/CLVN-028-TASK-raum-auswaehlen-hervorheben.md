---
Ticket-ID: CLVN-028
Type: Task
Story: CLVN-016
Epic: CLVN-015
Status: TODO
---
# Raum in der Trefferliste auswählen und hervorheben

## Beschreibung

Damit ein INNOQ-Mitarbeiter seine Raumauswahl bestätigen kann, muss er zunächst
einen Konferenzraum in der Trefferliste auswählen können. Aktuell führt ein Klick
auf eine Raumkarte direkt zur Detailseite – es gibt keinen sichtbaren Auswahl-
Zustand. Dieser Task führt eine echte In-Listen-Auswahl mit visueller Rückmeldung
ein, ohne sofort weiterzunavigieren.

Erster von drei Subtasks der Story [CLVN-016](/docs/produkt/backlog/CLVN-016-STORY-raumauswahl-bestaetigen.md).

## Akzeptanzkriterien

- [ ] Ein verfügbarer Konferenzraum kann durch Klick/Tap ausgewählt werden
- [ ] Der ausgewählte Konferenzraum wird visuell hervorgehoben
- [ ] Die Auswahl kann geändert werden, indem ein anderer Raum ausgewählt wird
- [ ] Die Auswahl kann wieder aufgehoben werden
- [ ] Belegte Räume sind nicht auswählbar

## Technische Hinweise

- Frontend-only (Prototyp ohne Backend, Mock-Daten gemäß `prototyp-scope.md`).
- Betroffen: `frontend/src/pages/raeume-finden.tsx` (Komponente `RaumKarte` und
  `RaeumeFinden`).
- Lokaler Auswahl-Zustand (z. B. `selectedId`); Hervorhebung über `cn()`-Klassen.
- Auswahl bei Änderung der Suche (Standort/Datum/Zeitraum) zurücksetzen.

## Zugehörige Story

[CLVN-016 - Raumauswahl bestätigen](/docs/produkt/backlog/CLVN-016-STORY-raumauswahl-bestaetigen.md)
