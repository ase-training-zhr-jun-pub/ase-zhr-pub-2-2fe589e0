# Qualitätsanforderungen

Dieses Dokument definiert die wesentlichen Qualitätsanforderungen an Calvin in Form von
**Qualitätsszenarien** (arc42, [Kapitel 10](https://docs.arc42.org/section-10/)).

Jedes Szenario folgt dem Template:

> **\<Environment\> \<Source\> \<Event\> \<Artifact\> \<Response\> \<Measure\>**

| Bestandteil | Bedeutung |
|---|---|
| **Environment** | Betriebssituation/Umgebung, in der das Szenario auftritt (Normalbetrieb, Last, Ausfall …). |
| **Source** | Auslöser des Stimulus (Mensch, System, Infrastruktur). |
| **Event** | Der Stimulus – das auslösende Ereignis. |
| **Artifact** | Das betroffene System bzw. die betroffene Komponente. |
| **Response** | Die geforderte Reaktion des Systems. |
| **Measure** | Messbares Kriterium, an dem die Reaktion überprüft wird. |

## Methodik & Kontext (Interview)

Die Szenarien wurden auf Basis eines kurzen Interviews priorisiert. Festgelegte Eckwerte:

- **Abgedeckte Qualitätsmerkmale:** Zuverlässigkeit/Integrität, Performance/Antwortzeit,
  Verfügbarkeit/Robustheit, Benutzbarkeit (Erlernbarkeit).
- **Last-Annahme:** bis zu **~50 gleichzeitige Nutzer** im Normalbetrieb.
- **Sicherheit/Zugriffsschutz:** als wichtig eingestuft, aber bewusst **kein eigenes
  Top-5-Szenario** dieser Übung (siehe [Nicht abgedeckt](#nicht-abgedeckt)).

## Priorisierung (Qualitätsbaum)

| Priorität | Qualitätsmerkmal | Szenario |
|---|---|---|
| 1 | Zuverlässigkeit / Integrität | [QS-3](#qs-3-verhinderung-von-doppelbuchungen) |
| 2 | Performance / Antwortzeit | [QS-1](#qs-1-performance-bei-der-raumsuche), [QS-2](#qs-2-schneller-aufbau-der-buchungsübersicht) |
| 3 | Verfügbarkeit / Robustheit | [QS-4](#qs-4-verfügbarkeit-und-robustheit-während-der-arbeitszeit) |
| 4 | Benutzbarkeit / Erlernbarkeit | [QS-5](#qs-5-erlernbarkeit-für-neue-mitarbeiter) |

> Die Priorisierung ist ein Ausgangspunkt aus dem Interview und kann im weiteren
> Verlauf verfeinert werden.

---

## QS-1: Performance bei der Raumsuche

**Qualitätsmerkmal:** Performance / Antwortzeit

> Im Normalbetrieb sucht ein INNOQ-Mitarbeiter auf der Calvin-Website nach verfügbaren
> Räumen an einem Standort für einen gewählten Zeitraum. Die Suchergebnisliste mit allen
> verfügbaren Räumen wird – auch bei bis zu 50 gleichzeitigen Nutzern – in unter **500 ms**
> für 95 % der Anfragen angezeigt.

| Bestandteil | Inhalt |
|---|---|
| **Environment** | Normalbetrieb während der Kernarbeitszeit, bis zu 50 gleichzeitige Nutzer. |
| **Source** | INNOQ-Mitarbeiter (z. B. Alex, Senior Consultant). |
| **Event** | Sendet eine Suchanfrage für verfügbare Räume an einem Standort und Zeitraum ab. |
| **Artifact** | Calvin SPA und Booking Service (Such-/Verfügbarkeits-Endpunkt). |
| **Response** | Die Liste der verfügbaren Räume mit Verfügbarkeitsstatus wird angezeigt. |
| **Measure** | Antwortzeit < 500 ms für 95 % der Anfragen, auch bei 50 gleichzeitigen Nutzern. |

**Begründung:** Mitarbeiter sind meist nur einen Tag pro Woche im Büro; eine schnelle
Raumfindung ist entscheidend, um den Bürotag effizient zu nutzen.

---

## QS-2: Schneller Aufbau der Buchungsübersicht

**Qualitätsmerkmal:** Performance / Antwortzeit (First Contentful Paint)

> Im Normalbetrieb ruft ein Consultant die Buchungen eines Standorts auf der Calvin-Website
> auf. Die Buchungen sind sichtbar und interaktiv (First Contentful Paint) in **300 ms**
> für 95 % der Anfragen.

| Bestandteil | Inhalt |
|---|---|
| **Environment** | Normalbetrieb, übliche Netzwerk- und Geräteverhältnisse. |
| **Source** | INNOQ-Mitarbeiter (Consultant). |
| **Event** | Öffnet die Buchungsübersicht eines Standorts bzw. „Meine Buchungen". |
| **Artifact** | Calvin-Website (SPA). |
| **Response** | Die Buchungen sind sichtbar und interaktiv (First Contentful Paint). |
| **Measure** | First Contentful Paint in 300 ms für 95 % der Anfragen. |

**Begründung:** Transparenz über die Raumbelegung ist ein zentrales Bedürfnis; ein
unmittelbarer Seitenaufbau stärkt das Vertrauen in die Verlässlichkeit der Anzeige.

---

## QS-3: Verhinderung von Doppelbuchungen

**Qualitätsmerkmal:** Zuverlässigkeit / Datenintegrität

> In einer normalen Betriebssituation versuchen zwei INNOQ-Mitarbeiter nahezu gleichzeitig
> (innerhalb derselben Sekunde), denselben Raum für denselben Zeitraum zu buchen. Das System
> verarbeitet die erste vollständige Buchungsanfrage erfolgreich und lehnt die zweite mit
> einer verständlichen Fehlermeldung ab. Doppelbuchungen werden in **99,9 %** der Fälle
> serverseitig verhindert.

| Bestandteil | Inhalt |
|---|---|
| **Environment** | Normalbetrieb mit zwei konkurrierenden Buchungsversuchen innerhalb derselben Sekunde. |
| **Source** | Zwei INNOQ-Mitarbeiter. |
| **Event** | Buchen denselben Raum für denselben Zeitraum gleichzeitig. |
| **Artifact** | Booking Service (transaktionale Buchungslogik). |
| **Response** | Erste Anfrage wird bestätigt; zweite wird mit verständlicher Fehlermeldung abgelehnt; der Raum bleibt eindeutig einmal vergeben. |
| **Measure** | Doppelbuchungen werden in ≥ 99,9 % der Fälle verhindert. |

**Begründung:** Die Sicherheit, dass ein gebuchter Raum tatsächlich frei ist, ist das
Kernversprechen von Calvin und essenziell für das Nutzervertrauen.

---

## QS-4: Verfügbarkeit und Robustheit während der Arbeitszeit

**Qualitätsmerkmal:** Verfügbarkeit / Robustheit

> Während der typischen INNOQ-Arbeitszeiten (8:00–18:00 Uhr an Werktagen) ist Calvin
> erreichbar und funktionsfähig. Fällt der Booking Service vorübergehend aus, zeigt die SPA
> statt einer weißen Seite eine verständliche Meldung und versucht erneut. Das System erreicht
> **98 % Verfügbarkeit** in der Kernzeit und ist nach einem Ausfall innerhalb von **30 Minuten**
> wieder betriebsbereit.

| Bestandteil | Inhalt |
|---|---|
| **Environment** | Kernarbeitszeit (8:00–18:00 Uhr, werktags); transienter Teilausfall (Booking Service kurz nicht erreichbar). |
| **Source** | INNOQ-Mitarbeiter (Zugriff) bzw. Infrastruktur (Ausfall). |
| **Event** | Mitarbeiter greift auf Calvin zu, während eine Komponente vorübergehend nicht erreichbar ist. |
| **Artifact** | Calvin-Gesamtsystem (SPA + Booking Service). |
| **Response** | System bleibt erreichbar; bei Ausfall verständliche Fehlermeldung und automatischer Wiederholungsversuch statt Totalausfall; anschließende Wiederherstellung. |
| **Measure** | 98 % Verfügbarkeit während der Kernzeit; Wiederherstellung < 30 Minuten nach einem Ausfall. |

**Begründung:** Ausfälle sind durch alternative Wege kompensierbar, dennoch soll Calvin
während der Arbeitszeit verlässlich verfügbar sein und nicht ungeschützt „weiß" ausfallen.

---

## QS-5: Erlernbarkeit für neue Mitarbeiter

**Qualitätsmerkmal:** Benutzbarkeit / Erlernbarkeit

> Ein neuer INNOQ-Mitarbeiter nutzt Calvin an seinem ersten Bürotag zum ersten Mal, ohne
> vorherige Schulung oder Anleitung. Er findet und bucht selbstständig einen passenden
> Konferenzraum. **Mindestens 90 %** der Erstnutzer schließen die Buchung beim ersten Versuch
> in **unter 3 Minuten** und ohne Fehlbedienung ab.

| Bestandteil | Inhalt |
|---|---|
| **Environment** | Erstnutzung ohne Schulung, ohne Dokumentation. |
| **Source** | Neuer INNOQ-Mitarbeiter. |
| **Event** | Möchte zum ersten Mal einen Konferenzraum buchen. |
| **Artifact** | Calvin-Website (Buchungs-Flow). |
| **Response** | Schließt Suche, Auswahl und Buchung selbstständig und korrekt ab. |
| **Measure** | ≥ 90 % der Erstnutzer buchen beim ersten Versuch erfolgreich in < 3 Minuten, ohne Fehlbedienung. |

**Begründung:** Die unkomplizierte Buchung „ohne Bürokratie" ist ein Produktversprechen;
seltene, aber wichtige Bürotage erlauben keine lange Einarbeitung.

---

## Nicht abgedeckt

Bewusst **nicht** als eigenes Szenario in dieser Übung enthalten, aber als relevant notiert:

- **Sicherheit / Zugriffsschutz** – Login sowie Autorisierung (nur eigene Buchungen
  ändern/stornieren). Als wichtig eingestuft, jedoch außerhalb der Top-5 dieser Übung.
  Im Prototyp gilt **Basic-Auth ohne Passwörter** statt Okta
  ([ADR-003](adrs/ADR-003-basic-auth-statt-okta-im-prototyp.md)); die fehlende echte
  Authentifizierung ist als technische Schuld festgehalten
  ([Technische Schulden](technische-schulden.md), TS-1).
- **Erweiterbarkeit** – z. B. Aufnahme weiterer Standorte oder die spätere
  Arbeitsplatzbuchung.
