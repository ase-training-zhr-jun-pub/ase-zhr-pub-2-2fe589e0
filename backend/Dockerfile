# Backend (Booking-Service) — FastAPI/uvicorn, Python 3.13
# Build-Kontext ist das backend/-Verzeichnis.
FROM python:3.13-slim

WORKDIR /app

# Runtime-Abhängigkeiten zuerst installieren (Docker-Layer-Caching:
# ändert sich der Code, müssen die Pakete nicht neu installiert werden).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Anwendungscode kopieren (Tests/DB/venv via .dockerignore ausgeschlossen).
COPY . .

# Port des uvicorn-Servers (siehe backend/CLAUDE.md, Run Configurations).
EXPOSE 8000

# Im Container auf allen Interfaces lauschen; das Schema wird beim Start per
# Lifespan (init_db + seed) angelegt. Die SQLite-Datei liegt unter /app
# (CALVIN_DB_PATH überschreibbar).
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
