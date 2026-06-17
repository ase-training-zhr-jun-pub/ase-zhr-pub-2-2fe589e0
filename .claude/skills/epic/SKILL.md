---
name: epic
description: Erstellt aus einem Backbone-Item einer User-Story-Map ein einheitliches Epic im Backlog. Aufruf mit /epic "<Backbone-Item>" <Pfad-zur-User-Story-Map>.
---

# Epic aus Backbone-Item erstellen

Du erstellst aus **einem** Backbone-Item einer User-Story-Map ein einheitliches Epic
und legst es im Backlog ab.

## Eingabe

`$ARGUMENTS` enthält zwei Angaben:

1. **Backbone-Item** – die Überschrift (`##`) aus der User-Story-Map, die zum Epic werden soll.
2. **User-Story-Map** – der Pfad zur Markdown-Datei der User-Story-Map.

Beispiel:

```
/epic "Räume finden" docs/produkt/user-story-maps/raumbuchung.md
```

Wenn eine der beiden Angaben fehlt oder mehrdeutig ist, frage gezielt nach, bevor du fortfährst.

## Regeln

- Halte dich an das Wording aus `docs/produkt/glossar.md` (Ubiquitous Language).
- Nutze die Dokumentation unter `docs/`, wenn du etwas nicht genau weißt (z. B. Personas).
- Das **Epic entspricht dem Backbone-Item** – Titel und Inhalt leiten sich direkt daraus ab.
- Die Post-its (Listenpunkte) unterhalb des Backbone-Items werden zu **User-Stories**.
  **Wichtig:** Es werden **keine** User-Story-Tickets erstellt – nur die User-Story-Sätze
  werden im Epic aufgelistet.

## Ablauf

1. **User-Story-Map lesen.** Öffne die in `$ARGUMENTS` angegebene Datei und finde das
   genannte Backbone-Item (die passende `##`-Überschrift). Die direkt darunter liegenden
   Listenpunkte sind die zugehörigen Post-its.

2. **Nächste Ticketnummer ermitteln.** Sieh im Verzeichnis `docs/produkt/backlog` nach,
   welche Epics dort bereits liegen (Dateien `CLVN-<NUMBER>-EPIC-*`). Wähle die nächste
   freie, fortlaufende Nummer (höchste vorhandene Nummer + 1; ist das Verzeichnis leer
   oder existiert es noch nicht, beginne bei `1`). **Keine doppelten Ticketnummern.**
   Existiert für dieses Backbone-Item bereits ein Epic, aktualisiere es, statt ein neues
   anzulegen.

3. **Epic-Namen bilden.** Einheitliches Schema:

   ```
   CLVN-<NUMBER>-EPIC-<NAME>
   ```

   - `<NUMBER>`: die ermittelte fortlaufende Ticketnummer.
   - `<NAME>`: der Backbone-Item-Titel in `Kebab-Case` (Leerzeichen → `-`, Umlaute
     ausschreiben: ä→ae, ö→oe, ü→ue, ß→ss). Beispiel: „Räume finden" → `Raeume-finden`.

4. **User-Stories formulieren.** Wandle jedes Post-it in einen User-Story-Satz um.
   Verwende die Persona aus `docs/produkt/personas/` als Rolle und das Schema:

   ```
   Als INNOQ-Mitarbeiter möchte ich <Ziel>, um <Nutzen>.
   ```

   Leite das `<Ziel>` aus dem Post-it ab und ergänze einen plausiblen `<Nutzen>` passend
   zum Produktkontext. Übernimm einen vorhandenen Marker wie `[MVP]` / `[Future]` am
   Zeilenende der jeweiligen User-Story.

5. **Epic-Datei schreiben** nach `docs/produkt/backlog/<EPIC-NAME>.md` mit folgender Struktur:

   ```markdown
   # CLVN-<NUMBER>-EPIC-<NAME>

   ## Beschreibung

   <Kurzbeschreibung des Epics, abgeleitet aus dem Backbone-Item und dem Produktkontext.>

   ## Quelle

   - User-Story-Map: `<Pfad zur User-Story-Map>`
   - Backbone-Item: <Backbone-Item-Titel>

   ## User-Stories

   - Als INNOQ-Mitarbeiter möchte ich <Ziel>, um <Nutzen>. [MVP|Future]
   - ...
   ```

6. **Zusammenfassen.** Nenne am Ende den Dateipfad, die vergebene Ticketnummer und die
   Anzahl der aufgelisteten User-Stories.
