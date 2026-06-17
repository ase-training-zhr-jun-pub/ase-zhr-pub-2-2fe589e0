# Technische Schulden

Dieses Dokument hält bewusst eingegangene **technische Schulden** des Calvin-Prototyps
fest: Vereinfachungen, die kurzfristig Tempo bringen, aber vor dem Produktivgang adressiert
werden müssen. Jede Schuld verweist auf die zugrunde liegende Entscheidung (ADR) und nennt
einen Tilgungs-Trigger.

## Übersicht

| ID | Technische Schuld | Quelle | Tilgungs-Trigger |
|----|-------------------|--------|------------------|
| TS-1 | Keine echte Authentifizierung (Basic-Auth ohne Passwörter) | [ADR-003](adrs/ADR-003-basic-auth-statt-okta-im-prototyp.md) | Produktivgang |
| TS-2 | Ressourcen-Stammdaten nur als Mock in der SPA | [ADR-002](adrs/ADR-002-ressourcendaten-als-mock-in-der-spa.md) | Produktivgang |
| TS-3 | Keine serverseitige Validierung der Ressourcen-IDs | [ADR-002](adrs/ADR-002-ressourcendaten-als-mock-in-der-spa.md) | Produktivgang |

---

## TS-1: Keine echte Authentifizierung (Basic-Auth ohne Passwörter)

**Quelle:** [ADR-003](adrs/ADR-003-basic-auth-statt-okta-im-prototyp.md)

**Beschreibung:** Statt einer Okta-Integration nutzt der Prototyp Basic-Auth ohne
Passwörter. Nutzer geben lediglich eine Identität an; es findet keine Passwort- oder
Token-Prüfung statt.

**Auswirkung / Risiko:** Identitäten sind nicht gesichert – jeder kann sich als beliebiger
Nutzer ausgeben. Es gibt keine belastbare Autorisierung (z. B. „nur eigene Buchungen
ändern/stornieren"). **Nicht produktionsreif.**

**Geplante Tilgung:** Okta-Integration (OIDC/JWT) vor dem Produktivgang nachliefern;
geschützte Endpunkte im Booking-Service ergänzen.

---

## TS-2: Ressourcen-Stammdaten nur als Mock in der SPA

**Quelle:** [ADR-002](adrs/ADR-002-ressourcendaten-als-mock-in-der-spa.md)

**Beschreibung:** Standorte, Räume und Ausstattungen sind als Mock-Daten in der SPA
hinterlegt (`frontend/src/lib/mock-data.ts`). Es gibt keine zentrale, persistente Quelle
für diese Stammdaten.

**Auswirkung / Risiko:** Änderungen an Standorten/Räumen erfordern einen Code-Deploy der
SPA und sind zur Laufzeit nicht pflegbar. Es existiert keine geteilte „Source of Truth"
für Ressourcendaten.

**Geplante Tilgung:** Bei Produktivgang eine echte Datenquelle bzw. einen Resource-Service
mit persistenter Speicherung und Laufzeit-Pflege einführen.

---

## TS-3: Keine serverseitige Validierung der Ressourcen-IDs

**Quelle:** [ADR-002](adrs/ADR-002-ressourcendaten-als-mock-in-der-spa.md)

**Beschreibung:** Der Booking-Service arbeitet ausschließlich mit den IDs aus den
SPA-Mock-Daten und hält keine eigenen Ressourcen-Stammdaten. Er kann daher nicht prüfen,
ob eine übergebene `raumId`/`standortId` tatsächlich existiert oder gültig ist.

**Auswirkung / Risiko:** Inkonsistenzen zwischen SPA-Mock-Daten und gespeicherten Buchungen
werden serverseitig nicht erkannt; die Datenintegrität hängt allein von der Konsistenz der
SPA ab.

**Geplante Tilgung:** Mit Einführung einer echten Ressourcen-Datenquelle (siehe TS-2) eine
serverseitige Validierung der IDs im Booking-Service ergänzen.
