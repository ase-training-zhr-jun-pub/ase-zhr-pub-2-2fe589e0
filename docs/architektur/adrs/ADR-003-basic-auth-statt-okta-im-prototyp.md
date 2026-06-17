# ADR-003: Basic-Auth ohne Passwörter statt Okta im Prototyp

**Status:** Akzeptiert
**Datum:** 2026-06-17

## Kontext und Problemstellung

Calvin benötigt eine Möglichkeit, Nutzer zu identifizieren (z. B. um „Meine Buchungen"
zuzuordnen). In [ADR-001](ADR-001-technologie-stack-fuer-booking-service.md) wurde eine
**perspektivische Okta-Integration** als Anforderung berücksichtigt. Für den **Prototyp**
ist zu entscheiden, ob Okta bereits jetzt integriert wird.

## Entscheidung

Für den Prototyp wird **auf eine Okta-Integration verzichtet**. Stattdessen kommt
**Basic-Auth ohne Passwörter** zum Einsatz: Nutzer geben (nur) eine Identität/einen
Benutzernamen an, ohne Passwortprüfung gegen ein Drittsystem.

Die **Okta-Integration wird nachgeliefert**, sobald das System in Produktion geht.

## Begründung

- **Schnelles Testen mit verschiedenen Nutzern:** Ohne Passwörter lässt sich der Nutzer
  trivial wechseln, um Mehrnutzer-Szenarien (z. B. konkurrierende Buchungen) zu testen.
- **Keine Abhängigkeit zu Drittsystemen:** Der Prototyp ist ohne Okta-Tenant, Netzwerk-
  zugang oder Konfiguration lauffähig.
- **Kein Vorab-Aufwand:** Die Okta-Anbindung (OIDC/JWT-Validierung) kostet Einrichtungs-
  und Integrationsaufwand, der im Prototyp keinen Mehrwert bringt.

## Konsequenzen

**Positiv**
- Prototyp ist eigenständig und ohne externe Abhängigkeiten lauffähig.
- Einfacher Nutzerwechsel beschleunigt manuelles Testen.

**Negativ / Risiken**
- **Keine echte Authentifizierung/Autorisierung:** Identitäten sind nicht gesichert; jeder
  kann sich als beliebiger Nutzer ausgeben. **Nicht produktionsreif.**
- Die spätere Umstellung auf Okta muss eingeplant werden (Tokens, geschützte Endpunkte).

Dieser Verzicht ist als technische Schuld festgehalten
([Technische Schulden](../technische-schulden.md), TS-1) mit dem Produktivgang als
Tilgungs-Trigger. Die in [ADR-001](ADR-001-technologie-stack-fuer-booking-service.md)
geforderte „perspektivische Okta-Möglichkeit" bleibt gültig – sie wird lediglich
**verschoben**, nicht verworfen.
