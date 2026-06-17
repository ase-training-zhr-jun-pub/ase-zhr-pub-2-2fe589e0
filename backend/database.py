"""SQLite-Anbindung für den Booking-Service.

Dateibasierte SQLite-DB (siehe [ADR-001]/[ADR-004]). Eine prozessweite
Verbindung, durch ein Lock serialisiert — das erlaubt den ``BEGIN IMMEDIATE``-
Transaktionsschutz gegen Doppelbuchungen (Qualitätsziel #1 „Zuverlässigkeit")
auch bei FastAPIs Ausführung von sync-Endpunkten im Threadpool.

Persistenz/Schema bewusst minimal gehalten (Prototyp-Scope, ADR-002: der Service
arbeitet nur mit den Ressourcen-IDs aus den SPA-Mock-Daten).
"""

import os
import sqlite3
import threading
from pathlib import Path

# Pfad über Env-Variable konfigurierbar (Tests nutzen eine eigene/temporäre DB),
# Fallback auf eine Datei neben diesem Modul.
DB_PATH = os.environ.get("CALVIN_DB_PATH", str(Path(__file__).parent / "calvin.db"))

_conn = sqlite3.connect(DB_PATH, check_same_thread=False)
_conn.row_factory = sqlite3.Row
_lock = threading.Lock()


def get_connection() -> sqlite3.Connection:
    """Liefert die prozessweite SQLite-Verbindung."""
    return _conn


def get_lock() -> threading.Lock:
    """Lock zur Serialisierung von Schreibzugriffen (Doppelbuchungsschutz)."""
    return _lock


def init_db() -> None:
    """Legt das Schema an (idempotent)."""
    _conn.execute(
        """
        CREATE TABLE IF NOT EXISTS buchungen (
            id           TEXT PRIMARY KEY,
            nutzer_id    TEXT NOT NULL,
            raum_id      TEXT NOT NULL,
            standort_id  TEXT NOT NULL,
            datum        TEXT NOT NULL,
            von          TEXT NOT NULL,
            bis          TEXT NOT NULL,
            titel        TEXT NOT NULL,
            notiz        TEXT,
            erstellt_am  TEXT NOT NULL
        )
        """
    )
    # Beschleunigt Verfügbarkeits-/Belegungsabfragen (Raum + Datum).
    _conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_buchungen_raum_datum "
        "ON buchungen (raum_id, datum)"
    )
    _conn.commit()
