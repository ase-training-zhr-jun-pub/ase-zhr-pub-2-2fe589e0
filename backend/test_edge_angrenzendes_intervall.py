"""Edge-Case: direkt angrenzendes Zeitfenster ist kein Buchungskonflikt.

Halboffene Intervalle [von, bis): Ein neues Fenster, dessen Start exakt mit dem
Ende einer bestehenden Buchung zusammenfällt (Ende == Start), darf NICHT als
Konflikt gewertet werden.
"""

import sqlite3

import pytest

import database
import repository
from schemas import Buchung

_TS = "2026-01-01T00:00:00+00:00"


@pytest.fixture()
def conn():
    """Frische In-Memory-Verbindung mit initialisiertem Schema für jeden Test."""
    database.init_db()
    c = database.get_connection()
    c.execute("DELETE FROM buchungen")
    return c


def _buchung(**overrides) -> Buchung:
    defaults = dict(
        id="b-test-1",
        nutzer_id="nutzer-a",
        raum_id="raum-x",
        standort_id="standort-1",
        datum="2026-06-18",
        von="09:00",
        bis="10:00",
        titel="Test",
        notiz=None,
        erstellt_am=_TS,
    )
    defaults.update(overrides)
    return Buchung(**defaults)


def _insert(conn, **overrides) -> Buchung:
    b = _buchung(**overrides)
    repository.insert(conn, b)
    return b


def test_direkt_angrenzend_kein_konflikt(conn):
    """Buchung raum_x 09:00-10:00 vorhanden; neues Fenster 10:00-11:00 → kein Konflikt.

    Halboffene Intervalle [von, bis): Ende der bestehenden Buchung == Start des neuen
    Fensters → keine Überschneidung.
    """
    _insert(conn, id="b-1", raum_id="raum-x", von="09:00", bis="10:00")
    treffer = repository.ueberschneidende(
        conn, "raum-x", "2026-06-18", "10:00", "11:00"
    )
    assert treffer == []
