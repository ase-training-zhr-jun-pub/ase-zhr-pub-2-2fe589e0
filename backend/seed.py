"""Initiale Beispieldaten für den Prototyp.

Spiegelt die Buchungen aus den SPA-Mock-Daten (``frontend/src/lib/mock-data.ts``)
wider, damit sich Verfügbarkeitsprüfung und „Meine Buchungen" konsistent
verhalten. Die eigenen Buchungen gehören dem Demo-Nutzer ``demo`` (= Basic-Auth-
Name der SPA); Fremdbelegungen laufen unter ``andere`` und dienen nur der
Verfügbarkeitsprüfung.

Hinweis: Im Prototyp ist „heute" der 2026-06-17.
"""

import repository
from database import get_connection
from schemas import Buchung

# Fester Zeitstempel für reproduzierbare Seeds.
_SEED_TS = "2026-06-01T08:00:00+00:00"

DEMO_NUTZER = "demo"

_SEED_BUCHUNGEN: list[Buchung] = [
    # --- Eigene Buchungen des Demo-Nutzers (Meine Buchungen, CLVN-023) ---
    Buchung(
        id="b-1001",
        nutzer_id=DEMO_NUTZER,
        raum_id="koeln-rheinauhafen",
        standort_id="koeln",
        datum="2026-06-18",
        von="09:00",
        bis="10:30",
        titel="Sprint Planning Team Phoenix",
        notiz="Bitte Whiteboard vorbereiten.",
        erstellt_am=_SEED_TS,
    ),
    Buchung(
        id="b-1002",
        nutzer_id=DEMO_NUTZER,
        raum_id="berlin-tempelhof",
        standort_id="berlin",
        datum="2026-06-24",
        von="14:00",
        bis="15:00",
        titel="Kunden-Sync ACME",
        notiz=None,
        erstellt_am=_SEED_TS,
    ),
    Buchung(
        id="b-1003",
        nutzer_id=DEMO_NUTZER,
        raum_id="koeln-dom",
        standort_id="koeln",
        datum="2026-07-02",
        von="10:00",
        bis="16:00",
        titel="Architektur-Workshop",
        notiz="Ganztägig, Catering bestellt.",
        erstellt_am=_SEED_TS,
    ),
    # Vergangene eigene Buchung (für die Unterscheidung kommend/vergangen)
    Buchung(
        id="b-0900",
        nutzer_id=DEMO_NUTZER,
        raum_id="koeln-hohenzollern",
        standort_id="koeln",
        datum="2026-06-03",
        von="10:00",
        bis="11:00",
        titel="1:1 mit Teamlead",
        notiz=None,
        erstellt_am=_SEED_TS,
    ),
    # --- Fremdbelegungen (nur für die Verfügbarkeitsprüfung relevant) ---
    Buchung(
        id="b-2001",
        nutzer_id="andere",
        raum_id="koeln-flora",
        standort_id="koeln",
        datum="2026-06-17",
        von="09:00",
        bis="12:00",
        titel="Belegt",
        notiz=None,
        erstellt_am=_SEED_TS,
    ),
    Buchung(
        id="b-2002",
        nutzer_id="andere",
        raum_id="berlin-brandenburger-tor",
        standort_id="berlin",
        datum="2026-06-17",
        von="13:00",
        bis="18:00",
        titel="Belegt",
        notiz=None,
        erstellt_am=_SEED_TS,
    ),
    Buchung(
        id="b-2003",
        nutzer_id="andere",
        raum_id="muenchen-isar",
        standort_id="muenchen",
        datum="2026-06-17",
        von="08:00",
        bis="18:00",
        titel="Belegt",
        notiz=None,
        erstellt_am=_SEED_TS,
    ),
]


def seed_if_empty() -> None:
    """Befüllt die DB mit Beispieldaten, falls sie noch leer ist."""
    conn = get_connection()
    if repository.anzahl(conn) > 0:
        return
    # Explizite Transaktion: Die Verbindung läuft mit isolation_level=None
    # (Autocommit), daher die Seeds atomar in eine Transaktion klammern.
    conn.execute("BEGIN")
    try:
        for buchung in _SEED_BUCHUNGEN:
            repository.insert(conn, buchung)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
