"""Booking-Service — FastAPI-Backend für Calvin.

Minimaler Einstieg (Übung 2): ein /api/hello-Endpunkt als Smoke-Test der
Front-/Backend-Verbindung. CORS ist für das Vite-Frontend geöffnet.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

app = FastAPI(title="Calvin Booking-Service")

# CORS — das Frontend (Vite, anderer Port/Origin, ggf. hinter dem Crucible-
# Proxy) muss die API per Browser ansprechen dürfen. Für die Trainings-/
# Entwicklungsumgebung erlauben wir alle Origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/hello", response_class=PlainTextResponse)
def hello() -> str:
    """Smoke-Test-Endpunkt für die Front-/Backend-Verbindung."""
    return "Hello World!"
