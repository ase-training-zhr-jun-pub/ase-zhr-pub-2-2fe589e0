# Backend — Booking-Service

Kontext für Claude Code bei Arbeit im `backend/`-Verzeichnis. Der Booking-Service ist
das Backend von **Calvin**, INNOQs internem Raum- und Arbeitsplatzbuchungssystem.

## Dokumentation (immer zuerst hier nachsehen)

- Architektur (arc42): [`../docs/arc42/arc42.md`](../docs/arc42/arc42.md)
- Architektur-Übersicht & ADRs: [`../docs/architektur/README.md`](../docs/architektur/README.md)
- Maßgebliche Technologie-Entscheidung: [ADR-004 — FastAPI statt Vapor](../docs/architektur/adrs/ADR-004-fastapi-statt-vapor-im-prototyp.md)
- Auth im Prototyp: [ADR-003 — Basic-Auth statt Okta](../docs/architektur/adrs/ADR-003-basic-auth-statt-okta-im-prototyp.md)
- Ressourcendaten: [ADR-002 — Mock-Daten in der SPA](../docs/architektur/adrs/ADR-002-ressourcendaten-als-mock-in-der-spa.md)
- Domäne/Begriffe: [`../docs/produkt/glossar.md`](../docs/produkt/glossar.md), [Produktvision](../docs/produkt/produktvision.md)
- Backlog (User Stories CLVN-XXX): [`../docs/produkt/backlog/backlog.md`](../docs/produkt/backlog/backlog.md)

## Technologie

- **Python 3** mit **FastAPI** (0.115), ausgeführt über **uvicorn** (0.34, `[standard]`)
- Virtuelle Umgebung unter `backend/.venv/`
- Formatter/Linter: **Ruff** (`ruff format`), siehe `requirements-dev.txt`
- Noch keine Datenbank/Persistenz und keine Tests im Prototyp (siehe Code Smells)

## Ordnerstruktur

```text
backend/
├── main.py               # FastAPI-App, CORS, Lifespan (init_db + seed), Router-Registrierung
├── database.py           # SQLite-Verbindung (+ Lock), Schema-Init
├── schemas.py            # Pydantic-Modelle an der API-Grenze
├── repository.py         # Datenzugriff (SQL), keine Geschäftslogik
├── service.py            # Buchungslogik, Verfügbarkeit, Doppelbuchungsschutz
├── auth.py               # Basic-Auth-Dependency -> nutzer_id (ADR-003)
├── seed.py               # Beispieldaten (spiegelt SPA-Mock-Buchungen)
├── routers/
│   ├── verfuegbarkeit.py # GET /api/verfuegbarkeit, GET /api/belegungen
│   └── buchungen.py      # GET/POST /api/buchungen
├── requirements.txt      # Runtime-Abhängigkeiten (fastapi, uvicorn)
├── requirements-dev.txt  # Dev-Tools (ruff)
├── calvin.db             # SQLite-Datei (nicht eingecheckt, beim Start geseedet)
├── README.md             # Kurzanleitung Entwicklung
├── CLAUDE.md             # diese Datei
└── .venv/                # virtuelle Umgebung (nicht eingecheckt)
```

Module liegen flach unter `backend/` und importieren sich absolut (z. B.
`import service`); uvicorn läuft mit `main:app` aus `backend/`, daher ist das
Verzeichnis auf dem `sys.path`.

## Architektur

**Layered Architecture**: Router/Controller (HTTP, `routers/`) → Service
(`service.py`, Buchungslogik & Doppelbuchungsschutz) → Repository (`repository.py`,
SQL) → SQLite (`database.py`). Pydantic-Schemas (`schemas.py`) an der API-Grenze.

**Doppelbuchungsschutz** (Qualitätsziel #1 „Zuverlässigkeit", arc42 Kap. 10): In
`service.erstelle_buchung` laufen Überschneidungsprüfung und Insert atomar in einer
`BEGIN IMMEDIATE`-Transaktion, zusätzlich durch ein prozessweites Lock serialisiert.
Bei Kollision → HTTP 409.

## Wichtige Dateien

- `main.py` — FastAPI-App `app`, CORS, Lifespan, Router-Registrierung, `GET /api/hello`
- `service.py` — Geschäftslogik inkl. `DoppelbuchungError`
- `schemas.py` — `BuchungAnfrage`, `Buchung`, `Verfuegbarkeit`, `Belegung`
- `auth.py` — `nutzer_id`-Dependency (Basic-Auth ohne Passwort)
- `requirements.txt` / `requirements-dev.txt` — Runtime- / Dev-Deps

## Endpunkte

| Methode | Pfad | Auth | Story | Zweck |
|---|---|---|---|---|
| GET | `/api/hello` | – | – | Smoke-Test |
| GET | `/api/verfuegbarkeit?raum_id=&datum=&von=&bis=` | – | CLVN-010 | Verfügbarkeit eines Raums prüfen |
| GET | `/api/belegungen?standort_id=&datum=` | – | CLVN-010 | Belegte Zeitfenster aller Räume (Trefferliste) |
| POST | `/api/buchungen` | Basic | CLVN-019 | Buchung absenden (409 bei Doppelbuchung) |
| GET | `/api/buchungen` | Basic | CLVN-023 | Eigene Buchungen auflisten |

## Wichtige Bash-Commands

```bash
# venv aktivieren
source backend/.venv/bin/activate

# Abhängigkeiten installieren (Runtime + Dev)
pip install -r backend/requirements.txt -r backend/requirements-dev.txt

# Dev-Server starten (Reload, auf allen Interfaces, Port 8000)
cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Smoke-Test
curl http://localhost:8000/api/hello        # -> "Hello World!"

# Formatieren (Ruff)
backend/.venv/bin/ruff format backend/       # formatieren
backend/.venv/bin/ruff format --check backend/   # nur prüfen, ohne zu ändern
```

> Hinweis: Bei Write/Edit von `.py`-Dateien formatiert ein PostToolUse-Hook
> (`.claude/settings.json`) die Datei automatisch mit `ruff format`.

## Code Smells (worauf achten)

- **Business-Logik im Endpoint**: Buchungslogik nicht direkt in die Route schreiben,
  sondern in eine Service-Schicht auslagern (Testbarkeit, Wiederverwendung).
- **`allow_origins=["*"]`** in `main.py` ist nur für die Trainings-/Dev-Umgebung
  akzeptabel — für Produktion auf konkrete Origins einschränken.
- **Fehlende Typannotationen / Pydantic-Modelle** an der API-Grenze.
- **Fehlende Tests** (kein pytest) — bei wachsender Logik nachziehen.
- **Hartkodierte Werte** (Ports, URLs) statt Konfiguration über Env-Variablen.

## Run Configurations

- **Port**: 8000 (`--host 0.0.0.0` wegen Container/Proxy)
- **Reload**: `--reload` im Dev-Betrieb
- **Proxy**: In der Trainings-Umgebung läuft alles hinter dem Crucible-/VS-Code-Proxy
  (`VSCODE_PROXY_URI`, Unterpfad `…/proxy/<port>/`). Client-seitig **relativ** fetchen,
  nicht absolut — siehe `.claude/rules/betrieb-hinter-proxy.md`.

## Sonstiges

- `GET /api/hello` ist der Smoke-Test der Front-/Backend-Verbindung (liefert `Hello World!`).
- CORS ist offen, damit das **Vite-Frontend** (eigener Origin, Port **5173**) die API
  per Browser ansprechen kann.
- Conventional Commits einhalten (siehe `.claude/rules/commits.md`).
