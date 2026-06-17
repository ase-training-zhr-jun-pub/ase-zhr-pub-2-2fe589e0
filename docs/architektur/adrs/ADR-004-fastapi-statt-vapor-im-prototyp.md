# ADR-004: FastAPI statt Swift/Vapor für den Booking-Service (Prototyp)

**Status:** Akzeptiert
**Datum:** 2026-06-17
**Löst ab:** [ADR-001 (Technologie-Stack für den Booking-Service)](ADR-001-technologie-stack-fuer-booking-service.md)

## Kontext und Problemstellung

[ADR-001](ADR-001-technologie-stack-fuer-booking-service.md) wählte **Swift/Vapor**,
getrieben vom höchstgewichteten Treiber **Vertrautheit/Tempo** (iOS-/Swift-Entwickler).
Beim erstmaligen Aufsetzen des Backends in der Trainings-/Devcontainer-Umgebung zeigte
sich, dass genau dieser Treiber unterlaufen wird:

- Ein **Cold Build** von Vapor übersetzt den kompletten Abhängigkeitsbaum
  (SwiftNIO, swift-crypto, swift-certificates, async-http-client, swift-collections, …)
  aus dem Quellcode — im Container **viele Minuten** für ~900 Build-Schritte.
- Dieser Aufwand fällt zwar nur einmalig an (danach ist `.build/` warm), bremst aber den
  ersten Durchstich und das Tooling-Setup (Toolchain-Installation via Swiftly) im
  Workshop-Kontext spürbar.

Das Ziel „schnell einen lauffähigen, iterierbaren Service" wurde dadurch verfehlt.

## Entscheidung

Für den **Prototyp** wird der Booking-Service mit **Python/FastAPI** umgesetzt
(ausgeführt über **uvicorn**). In ADR-001 war FastAPI ausdrücklich als Option 3 betrachtet
und nur wegen fehlender Python-Vorerfahrung verworfen worden — dieser Nachteil wiegt für
den Prototyp-Umfang geringer als der konkrete Tempo-Verlust durch die Swift-Build-Zeiten.

## Begründung

- **Tempo (Top-Treiber aus ADR-001):** FastAPI ist in **~10 s** lauffähig
  (`pip install` + `uvicorn`), Hot-Reload ist praktisch verzögerungsfrei. Kein
  Compile-Schritt, keine Toolchain-Installation.
- **REST-API:** FastAPI ist ein vollwertiges REST-Framework inkl. automatischer
  OpenAPI-Doku.
- **Dateibasierte DB:** SQLite ist in Python eingebaut (bzw. via SQLModel/SQLAlchemy) —
  die in ADR-001 geforderte dateibasierte DB bleibt erfüllt.
- **Okta perspektivisch:** OAuth2/OIDC-Resource-Server (JWT-Validierung gegen Okta-JWKS)
  ist mit etablierten Python-Libraries umsetzbar; bleibt damit möglich (im Prototyp ohnehin
  durch Basic-Auth ersetzt, siehe [ADR-003](ADR-003-basic-auth-statt-okta-im-prototyp.md)).

## Konsequenzen

**Positiv**
- Sofort lauffähiger, schnell iterierbarer Service — der ursprüngliche Tempo-Anspruch wird
  tatsächlich eingelöst.
- Kleiner, vertrauter Stack (`fastapi`, `uvicorn`) mit großem Ökosystem.

**Negativ / Risiken**
- **Keine Python-Vorerfahrung** des Entwicklers (der in ADR-001 entscheidende Nachteil) —
  für den überschaubaren Prototyp-Umfang akzeptiert, mittelfristig Einarbeitung nötig.
- **Dynamische Typisierung:** Typsicherheit nur über Tooling-Disziplin (Type Hints,
  optional `mypy`/`pyright`).
- **Swift-Setup ersetzt:** Die SDK-Einrichtung wurde von Swift auf Python umgestellt —
  `scripts/install-sdk.sh` installiert nun die Python-Toolchain, der Devcontainer nutzt die
  `ms-python.python`-Extension und richtet im `postCreateCommand` ein venv ein;
  `.swift-version` wurde entfernt.

## Offene Punkte

- Bei Bedarf bleibt der in ADR-001 genannte Fallback **Spring Boot** möglich.
