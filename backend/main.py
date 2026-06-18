"""Booking-Service — FastAPI-Backend für Calvin.

Stellt die REST-API des Booking-Service bereit: Verfügbarkeitsprüfung (CLVN-010),
Raumbuchung absenden (CLVN-019) und Buchungsübersicht (CLVN-023). Die Ressourcen-
Stammdaten (Standorte/Räume) liegen in der SPA (ADR-002); der Service arbeitet
ausschließlich mit den IDs.

Schichten: Router/Controller (HTTP) → Service (Buchungslogik, Doppelbuchungs-
schutz) → Repository (SQLite). Auth per Basic-Auth ohne Passwort (ADR-003).
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

from database import init_db
from routers import buchungen, verfuegbarkeit
from seed import seed_if_empty


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialisiert Schema und Seed-Daten beim Start."""
    init_db()
    seed_if_empty()
    yield


app = FastAPI(title="Calvin Booking-Service", lifespan=lifespan)

# CORS — das Frontend (Vite, anderer Port/Origin, ggf. hinter dem Crucible-
# Proxy) muss die API per Browser ansprechen dürfen. Für die Trainings-/
# Entwicklungsumgebung erlauben wir alle Origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(verfuegbarkeit.router)
app.include_router(buchungen.router)


@app.get("/api/hello", response_class=PlainTextResponse)
def hello() -> str:
    """Smoke-Test-Endpunkt für die Front-/Backend-Verbindung."""
    return "Hello World!"
