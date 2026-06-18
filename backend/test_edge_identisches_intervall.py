"""Edge-Case: Exakt identisches Zeitintervall wird als Konflikt erkannt."""

import database
import repository
from schemas import Buchung

_TS = "2026-01-01T00:00:00+00:00"


def setup_function():
    database.init_db()
    conn = database.get_connection()
    conn.execute("DELETE FROM buchungen")
    conn.commit()


def test_identisches_intervall_ist_konflikt():
    """ueberschneidende() erkennt ein exakt identisches Zeitintervall als Konflikt."""
    conn = database.get_connection()
    buchung = Buchung(
        id="b-edge-1",
        nutzer_id="nutzer-a",
        raum_id="raum-x",
        standort_id="standort-1",
        datum="2026-06-18",
        von="09:00",
        bis="10:00",
        titel="Edge Test",
        notiz=None,
        erstellt_am=_TS,
    )
    repository.insert(conn, buchung)

    treffer = repository.ueberschneidende(
        conn, "raum-x", "2026-06-18", "09:00", "10:00"
    )
    assert len(treffer) >= 1
