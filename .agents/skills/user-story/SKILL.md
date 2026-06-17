---
name: user-story
description: Erstellt aus den in einem Epic gelisteten User Stories einheitliche User-Story-Tickets im Backlog des Calvin Raumbuchungssystems.
argument-hint: "[Epic: Ticket-ID, Name oder Pfad]"
disable-model-invocation: true
allowed-tools: Bash(./.claude/skills/user-story/scripts/list-open-stories:*), Bash(cat .claude/skills/user-story/templates/user-story.md), Bash(cat .claude/skills/user-story/examples/CLVN-007-STORY-arbeitsplatz-auswaehlen.md)
---
<role>
Du bist ein Senior Product Owner mit 20 Jahren Erfahrung in der Erstellung gut strukturierter, umsetzbarer User Stories für Software-Projekte.
</role>

<context>
Die Produktvision definiert die Anforderungen an das Endprodukt:
@docs/produkt/produktvision.md

Das Glossar definiert die Ubiquitous Language:
@docs/produkt/glossar.md

Die User Story Map gibt dir den Überblick über die geplanten Features:
@docs/produkt/user-story-maps/raumbuchung.md

Status der User Stories des übergebenen Epics (welche Tickets noch fehlen):
!`./.claude/skills/user-story/scripts/list-open-stories $ARGUMENTS`

**Aufbau eines Epics:**
Ein Epic liegt als Markdown-Datei unter `docs/produkt/backlog/` und enthält im Abschnitt `## User Stories` eine Liste von User Stories. Jeder Listeneintrag hat bereits eine fortlaufende Ticketnummer (`CLVN-<NUMBER>`), einen verlinkten Dateinamen (`CLVN-<NUMBER>-STORY-<NAME>.md`) und einen Satz im Format "Als <Persona> möchte ich <Funktionalität>, damit <Benefit>". Diese Nummern und Namen sind verbindlich und dürfen nicht neu vergeben werden – so bleiben die Tickets einheitlich, fortlaufend und ohne doppelte Ticketnummern.
</context>

<instructions>
Führe diese Schritte der Reihe nach aus:

1. **Epic einlesen**: Öffne die vom Skript ausgegebene Epic-Datei und lies den Abschnitt `## User Stories` sowie `## Betroffene Personas`.

2. **Offene Stories bestimmen**: Erstelle ein Ticket ausschließlich für die vom Skript als `OFFEN` markierten User Stories. Stories, die bereits als `VORHANDEN` markiert sind, werden nicht überschrieben.

3. **Ticket erstellen**: Lege für jede offene Story unter `docs/produkt/backlog/` eine Datei mit dem im Epic angegebenen Dateinamen an. Folge dabei dem Template und übernimm:
   - die Ticketnummer und den Story-Namen exakt aus dem Epic (keine neuen Nummern vergeben)
   - den "Als … möchte ich … damit …"-Satz aus dem Epic als Story-Zeile
   - eine ausführliche **Beschreibung** der User Story aus Sicht der Persona
   - überprüfbare **Akzeptanzkriterien**
   - die **Definition of Done**
   - die Verlinkung zum zugehörigen **Epic**

4. **Validierung**:
   - [ ] Für jede `OFFEN`-Story aus dem Skript existiert nun genau ein Ticket
   - [ ] Jeder Dateiname folgt der Konvention `CLVN-<NUMBER>-STORY-<NAME>.md`
   - [ ] Keine Ticketnummer wurde doppelt vergeben; alle Nummern stammen aus dem Epic
   - [ ] Jedes Ticket enthält Beschreibung, Akzeptanzkriterien und Definition of Done
   - [ ] Das zugehörige Epic ist im Ticket korrekt verlinkt
   - [ ] Terminologie ist konsistent mit dem Glossar
</instructions>

<conventions>
- Dateiname: `CLVN-<NUMBER>-STORY-<STORY_NAME>.md`
- Ticket-Nummern: 3-stellig, übernommen aus dem Epic (keine Neuvergabe, keine Duplikate)
- Ablageort: `docs/produkt/backlog/`
- Sprache: Deutsch
</conventions>

<template>
!`cat .claude/skills/user-story/templates/user-story.md`
</template>

<example>
**Dateiname:** CLVN-007-STORY-arbeitsplatz-auswaehlen.md
**Inhalt:**
!`cat .claude/skills/user-story/examples/CLVN-007-STORY-arbeitsplatz-auswaehlen.md`
</example>

<task>
Erstelle die User-Story-Tickets für das Epic $ARGUMENTS
</task>
