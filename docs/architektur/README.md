# Architekturdokumentation

Diese Dokumentation beschreibt die Architektur des Calvin-Raumbuchungssystems und
orientiert sich an [arc42](https://docs.arc42.org/).

## Inhalt

- [Qualitätsanforderungen](qualitätsanforderungen.md) — Qualitätsziele und
  Qualitätsszenarien (arc42 Kapitel 10).
- [Technische Schulden](technische-schulden.md) — bewusst eingegangene Vereinfachungen
  des Prototyps und ihre geplante Tilgung.

## Architekturentscheidungen (ADRs)

- [ADR-001: Technologie-Stack für den Booking-Service](adrs/ADR-001-technologie-stack-fuer-booking-service.md)
  — Swift / Vapor mit SQLite.
- [ADR-002: Ressourcendaten als Mock-Daten in der SPA](adrs/ADR-002-ressourcendaten-als-mock-in-der-spa.md)
  — kein separater Resource-Service; Booking-Service arbeitet nur mit IDs.
- [ADR-003: Basic-Auth ohne Passwörter statt Okta im Prototyp](adrs/ADR-003-basic-auth-statt-okta-im-prototyp.md)
  — Okta wird zum Produktivgang nachgeliefert.
