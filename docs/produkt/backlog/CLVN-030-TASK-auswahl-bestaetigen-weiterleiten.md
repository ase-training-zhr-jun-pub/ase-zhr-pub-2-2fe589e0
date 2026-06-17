---
Ticket-ID: CLVN-030
Type: Task
Story: CLVN-016
Epic: CLVN-015
Status: TODO
---
# Auswahl bestätigen und zum Buchungsschritt weiterleiten

## Beschreibung

Nachdem ein INNOQ-Mitarbeiter seine Raumauswahl gesehen hat, soll er sie verbindlich
bestätigen und damit in den nächsten Schritt des Buchungsprozesses gelangen. Dieser
Task ergänzt die Bestätigungsschaltfläche und die Weiterleitung zur Eingabe weiterer
Buchungsdetails (Meetingtitel, Buchungsnotiz).

Dritter von drei Subtasks der Story [CLVN-016](/docs/produkt/backlog/CLVN-016-STORY-raumauswahl-bestaetigen.md).
Baut auf der Zusammenfassung aus [CLVN-029](/docs/produkt/backlog/CLVN-029-TASK-auswahl-zusammenfassung-anzeigen.md) auf.

## Akzeptanzkriterien

- [ ] Eine Bestätigungsschaltfläche ermöglicht das Fortfahren zum nächsten
      Buchungsschritt
- [ ] Die Schaltfläche ist nur bei gültiger Auswahl aktiv
- [ ] Nach Bestätigung wird der Mitarbeiter zur Eingabe weiterer Buchungsdetails
      (Meetingtitel, Buchungsnotiz) weitergeleitet

## Technische Hinweise

- Frontend-only (Prototyp ohne Backend, Mock-Daten).
- Betroffen: `frontend/src/pages/raeume-finden.tsx` (Bestätigungs-Button im Panel).
- Weiterleitung per `useNavigate()` zur bestehenden Buchungs-Eingabeseite
  (`/raeume/:raumId`), die Meetingtitel und Buchungsnotiz erfasst (CLVN-017/018).

## Zugehörige Story

[CLVN-016 - Raumauswahl bestätigen](/docs/produkt/backlog/CLVN-016-STORY-raumauswahl-bestaetigen.md)
