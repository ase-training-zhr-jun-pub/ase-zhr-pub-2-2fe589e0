# ADR-001: Technologie-Stack für den Booking-Service

**Status:** Akzeptiert
**Datum:** 2026-06-17

## Kontext und Problemstellung

Die Buchungslogik von Calvin wird gemäß
[ADR-001 (Frontend-Prototyp und Booking Service)](../../arc42/adrs/ADR-001-frontend-prototyp-und-booking-service.md)
in einen eigenständigen **Booking-Service** ausgelagert. Offen ist, mit welcher
Technologie dieser Service umgesetzt wird.

Der Service wird im weiteren Verlauf **selbst implementiert**. Die Auswahl wird daher
maßgeblich von der vorhandenen Erfahrung getrieben.

## Entscheidungstreiber

- **Vertrautheit / Tempo (höchste Priorität):** Die Technologie muss dem Entwickler
  vertraut sein, damit zügig entwickelt werden kann. Profil: **iOS-/Swift-Entwickler**
  (Swift im Alltag), zusätzlich ältere, eingerostete **Java-Kenntnisse**.
- **REST-API:** Der Service stellt eine REST-Schnittstelle (JSON über HTTPS) bereit.
- **Dateibasierte Datenbank:** Kompatibilität mit einer dateibasierten DB (SQLite, H2, …).
- **Okta perspektivisch:** Eine spätere Okta-Integration (OAuth2/OIDC) muss möglich sein.
- **Schnelle Entwicklung:** Geringe Reibung beim Aufsetzen und Iterieren.

## Betrachtete Optionen

1. **Swift / Vapor** (server-side Swift)
2. **Java / Spring Boot**
3. **Python / FastAPI**

## Entscheidung

Gewählt wird **Swift / Vapor** mit **SQLite** (über das Fluent-ORM,
`FluentSQLiteDriver`).

Ausschlaggebend ist der höchstgewichtete Treiber **Vertrautheit/Tempo**: Swift ist die
Alltagssprache des Entwicklers. Server-side Swift mit Vapor erlaubt es, in genau dieser
Sprache zu bleiben und schnell voranzukommen. Alle Muss-Anforderungen werden erfüllt:

- **REST-API:** Vapor ist ein vollwertiges REST-Framework (Routing, Controller,
  `Codable`-basiertes JSON, async/await).
- **Dateibasierte DB:** Fluent bietet einen offiziellen **SQLite**-Treiber → exakt die
  geforderte dateibasierte Datenbank.
- **Okta perspektivisch:** Der Service tritt als **OAuth2/OIDC-Resource-Server** auf und
  validiert von Okta ausgestellte **JWT-Access-Tokens** (Signaturprüfung gegen die Okta-JWKS,
  Prüfung von Issuer/Audience/Ablauf) mit **JWTKit**. Der eigentliche Login-Flow liegt bei
  der SPA + Okta. Damit ist die Okta-Integration perspektivisch möglich.
- **Schnelle Entwicklung:** Für einen Swift-erfahrenen Entwickler ist Vapor (inkl.
  Vapor Toolbox, gutem Tooling und vertrauter Sprache) der schnellste Weg.

Java/Spring Boot wäre beim Kriterium Okta/Ökosystem überlegen, scheitert hier aber am
wichtigsten Treiber: Die Java-Kenntnisse sind veraltet, was das Tempo bremst.

## Vor- und Nachteile der Optionen

### Option 1 — Swift / Vapor  ✅ gewählt

**Pro**
- **Höchste Vertrautheit:** Swift ist die Hauptsprache des Entwicklers → schnellstes Tempo.
- REST-Framework mit `Codable`/async-await, sauberer DX.
- **SQLite** nativ über Fluent (`FluentSQLiteDriver`) — genau die geforderte dateibasierte DB.
- Statisch typisiert, kompiliert — wenig Laufzeitüberraschungen.
- Okta-Anbindung als Resource-Server via JWTKit (JWKS-Validierung) gut machbar.

**Contra**
- **Kleineres Ökosystem** für server-side Swift; weniger fertige Integrationen und Beispiele
  (insbesondere für Okta) als im JVM-Umfeld.
- Backend-Swift ≠ iOS-Swift: Vapor-Konzepte (Fluent, Middleware, EventLoop/async) müssen
  dennoch eingearbeitet werden.
- Deployment/Hosting von Linux-Swift ist weniger verbreitet als JVM-Stacks.
- Okta-Integration ist eher „selbst zusammenbauen" als ein fertiger Starter.

### Option 2 — Java / Spring Boot

**Pro**
- **Reifster Stack** für REST-Services; sehr große Community und Dokumentation.
- **Okta erstklassig:** `okta-spring-boot-starter` bzw. Spring Security OAuth2 Resource Server
  — Okta-Integration weitgehend out-of-the-box.
- **H2** (explizit in den Anforderungen genannt) ist nativ, SQLite via JDBC ebenfalls möglich.
- Spring Initializr + Spring Data JPA beschleunigen das Grundgerüst.

**Contra**
- **Java-Kenntnisse veraltet** → widerspricht dem Top-Treiber Vertrautheit/Tempo.
- Mehr Boilerplate/Konfiguration; höhere Einstiegshürde nach längerer Pause.
- JVM-Startzeit/Speicherbedarf höher (für einen kleinen Service nachrangig).

### Option 3 — Python / FastAPI

**Pro**
- Sehr **schnelle Entwicklung**, automatische OpenAPI-Doku.
- **SQLite** eingebaut (SQLAlchemy/SQLModel).
- OAuth2/OIDC (Okta) über etablierte Libraries umsetzbar.

**Contra**
- **Keine Vorerfahrung** des Entwicklers in Python → verletzt die Kernanforderung
  „Technologie, in der du dich auskennst".
- Dynamische Typisierung; Typsicherheit nur via optionale Tooling-Disziplin.

## Konsequenzen

**Positiv**
- Entwicklung in vertrauter Sprache → schnelles Vorankommen, geringe Reibung.
- Dateibasierte SQLite-DB hält das Setup für die Prototyp-Phase einfach (keine externe DB).
- Klare REST-Schnittstelle zur bestehenden React-SPA.

**Negativ / Risiken**
- **Okta:** Es gibt keinen fertigen „Starter"; die Resource-Server-Validierung (JWKS,
  Issuer/Audience) muss manuell mit JWTKit umgesetzt werden. → Früh ein kleines Spike
  einplanen, um das Risiko zu verifizieren.
- **Ökosystem/Hosting:** Weniger verbreiteter Stack; Deployment- und Bibliotheks-Lücken
  möglich. → Bei Bedarf Fallback auf **Spring Boot** (Option 2), das alle Anforderungen
  ebenfalls erfüllt und bei Okta/Ökosystem stärker ist.

**Datenbank-Hinweis:** Fluent abstrahiert die DB. SQLite dient als dateibasierte DB für die
Prototyp-Phase; ein späterer Wechsel auf PostgreSQL o. ä. ist über den Treiber möglich.
