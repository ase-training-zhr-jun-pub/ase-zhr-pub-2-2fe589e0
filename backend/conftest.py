"""Pytest-Setup für den Booking-Service.

Setzt eine isolierte In-Memory-SQLite-DB, *bevor* ``database`` importiert wird
(das Modul öffnet die Verbindung beim Import anhand von ``CALVIN_DB_PATH``).
"""

import os

os.environ.setdefault("CALVIN_DB_PATH", ":memory:")
