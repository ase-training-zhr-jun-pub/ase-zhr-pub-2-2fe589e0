# Booking-Service (Backend)

FastAPI-Backend für Calvin.

## Entwicklung

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Der Smoke-Test-Endpunkt liefert unter `GET /api/hello` den Text `Hello World!`.

> Hinweis: Die Technologie-Entscheidung hierzu hält ADR-002 fest
> (FastAPI statt des ursprünglich in ADR-001 vorgesehenen Swift/Vapor).
