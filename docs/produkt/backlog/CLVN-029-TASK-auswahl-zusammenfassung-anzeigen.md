---
Ticket-ID: CLVN-029
Type: Task
Story: CLVN-016
Epic: CLVN-015
Status: TODO
---
# Auswahl-Zusammenfassung mit Raumdetails und Zeitraum anzeigen

## Beschreibung

Wenn ein INNOQ-Mitarbeiter einen Konferenzraum ausgewählt hat, soll er auf einen
Blick die wichtigsten Eckdaten seiner Auswahl sehen, bevor er sie bestätigt. Dieser
Task zeigt nach getroffener Auswahl eine Zusammenfassung mit den Raumdetails und
dem gewählten Zeitraum an.

Zweiter von drei Subtasks der Story [CLVN-016](/docs/produkt/backlog/CLVN-016-STORY-raumauswahl-bestaetigen.md).
Baut auf der Auswahl aus [CLVN-028](/docs/produkt/backlog/CLVN-028-TASK-raum-auswaehlen-hervorheben.md) auf.

## Akzeptanzkriterien

- [ ] Bei getroffener Auswahl werden die Raumdetails angezeigt: Name, Standort,
      Ausstattung, Kapazität
- [ ] Der gewählte Zeitraum wird angezeigt: Datum sowie Start- und Endzeit
- [ ] Die Dauer des gewählten Zeitraums wird angezeigt
- [ ] Die Zusammenfassung verschwindet, wenn die Auswahl aufgehoben wird

## Technische Hinweise

- Frontend-only (Prototyp ohne Backend, Mock-Daten).
- Betroffen: `frontend/src/pages/raeume-finden.tsx` (neues Zusammenfassungs-Panel).
- Wiederverwenden: `AusstattungListe` (`@/components/ausstattung-badge`),
  `getStandort` / `berechneDauer` (`@/lib/mock-data`), `formatDatum` (`@/lib/date`).

## Zugehörige Story

[CLVN-016 - Raumauswahl bestätigen](/docs/produkt/backlog/CLVN-016-STORY-raumauswahl-bestaetigen.md)
