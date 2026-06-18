"""Tests der Datenzugriffsschicht (repository.py).

Testet die SQL-Abfragen direkt gegen eine In-Memory-DB: Überschneidungslogik,
Sortierung/Filter von belegungen() und liste_fuer_nutzer(), sowie anzahl().
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
    """Hilfsfunktion: Buchungsobjekt mit sinnvollen Standardwerten."""
    defaults = dict(
        id="b-test-1",
        nutzer_id="nutzer-a",
        raum_id="raum-1",
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


# ---------------------------------------------------------------------------
# ueberschneidende() — Grenzfälle
# ---------------------------------------------------------------------------


def test_ueberschneidend_exakt_gleich(conn):
    """Exakt identisches Intervall überschneidet sich."""
    _insert(conn, id="b-1", von="09:00", bis="10:00")
    treffer = repository.ueberschneidende(
        conn, "raum-1", "2026-06-18", "09:00", "10:00"
    )
    assert len(treffer) == 1


def test_ueberschneidend_teilweise(conn):
    """Teilüberlappung (Start vor Ende der bestehenden Buchung) ist Konflikt."""
    _insert(conn, id="b-1", von="09:00", bis="11:00")
    treffer = repository.ueberschneidende(
        conn, "raum-1", "2026-06-18", "10:00", "12:00"
    )
    assert len(treffer) == 1


def test_ueberschneidend_eingeschlossen(conn):
    """Neue Buchung liegt vollständig innerhalb der bestehenden."""
    _insert(conn, id="b-1", von="09:00", bis="12:00")
    treffer = repository.ueberschneidende(
        conn, "raum-1", "2026-06-18", "10:00", "11:00"
    )
    assert len(treffer) == 1


def test_ueberschneidend_umschliessend(conn):
    """Neue Buchung umschließt die bestehende vollständig."""
    _insert(conn, id="b-1", von="10:00", bis="11:00")
    treffer = repository.ueberschneidende(
        conn, "raum-1", "2026-06-18", "09:00", "12:00"
    )
    assert len(treffer) == 1


def test_kein_konflikt_exakt_angrenzend_danach(conn):
    """Exakt angrenzend (neue beginnt, wo alte endet) = kein Konflikt.

    Das Intervall ist halbsoffen [von, bis): b.von < a.bis ist die Bedingung,
    bei bis==von ist sie falsch → kein Treffer.
    """
    _insert(conn, id="b-1", von="09:00", bis="10:00")
    treffer = repository.ueberschneidende(
        conn, "raum-1", "2026-06-18", "10:00", "11:00"
    )
    assert len(treffer) == 0


def test_kein_konflikt_exakt_angrenzend_davor(conn):
    """Exakt angrenzend (neue endet, wo alte beginnt) = kein Konflikt."""
    _insert(conn, id="b-1", von="10:00", bis="11:00")
    treffer = repository.ueberschneidende(
        conn, "raum-1", "2026-06-18", "09:00", "10:00"
    )
    assert len(treffer) == 0


def test_kein_konflikt_anderer_raum(conn):
    """Gleiche Zeit, aber anderer Raum → kein Konflikt."""
    _insert(conn, id="b-1", raum_id="raum-1", von="09:00", bis="10:00")
    treffer = repository.ueberschneidende(
        conn, "raum-2", "2026-06-18", "09:00", "10:00"
    )
    assert len(treffer) == 0


def test_kein_konflikt_anderes_datum(conn):
    """Gleiche Zeit und Raum, aber anderes Datum → kein Konflikt."""
    _insert(conn, id="b-1", datum="2026-06-18", von="09:00", bis="10:00")
    treffer = repository.ueberschneidende(
        conn, "raum-1", "2026-06-19", "09:00", "10:00"
    )
    assert len(treffer) == 0


def test_kein_konflikt_komplett_danach(conn):
    """Neue Buchung beginnt nach Ende der bestehenden."""
    _insert(conn, id="b-1", von="09:00", bis="10:00")
    treffer = repository.ueberschneidende(
        conn, "raum-1", "2026-06-18", "11:00", "12:00"
    )
    assert len(treffer) == 0


def test_kein_konflikt_komplett_davor(conn):
    """Neue Buchung endet vor Beginn der bestehenden."""
    _insert(conn, id="b-1", von="13:00", bis="14:00")
    treffer = repository.ueberschneidende(
        conn, "raum-1", "2026-06-18", "10:00", "11:00"
    )
    assert len(treffer) == 0


# ---------------------------------------------------------------------------
# belegungen() — Sortierung und Filter
# ---------------------------------------------------------------------------


def test_belegungen_sortierung_nach_raum_dann_von(conn):
    """belegungen() liefert Ergebnisse sortiert nach raum_id, dann von."""
    _insert(
        conn,
        id="b-1",
        raum_id="raum-b",
        standort_id="s1",
        datum="2026-06-18",
        von="14:00",
        bis="15:00",
    )
    _insert(
        conn,
        id="b-2",
        raum_id="raum-a",
        standort_id="s1",
        datum="2026-06-18",
        von="11:00",
        bis="12:00",
    )
    _insert(
        conn,
        id="b-3",
        raum_id="raum-a",
        standort_id="s1",
        datum="2026-06-18",
        von="09:00",
        bis="10:00",
    )

    bel = repository.belegungen(conn, "s1", "2026-06-18")
    assert [(b.raum_id, b.von) for b in bel] == [
        ("raum-a", "09:00"),
        ("raum-a", "11:00"),
        ("raum-b", "14:00"),
    ]


def test_belegungen_nur_eigener_standort(conn):
    """belegungen() liefert nur Räume des gefragten Standorts."""
    _insert(conn, id="b-1", standort_id="s1", raum_id="raum-1", datum="2026-06-18")
    _insert(conn, id="b-2", standort_id="s2", raum_id="raum-2", datum="2026-06-18")

    bel = repository.belegungen(conn, "s1", "2026-06-18")
    assert len(bel) == 1
    assert bel[0].raum_id == "raum-1"


def test_belegungen_nur_eigenes_datum(conn):
    """belegungen() liefert nur Buchungen des angefragten Datums."""
    _insert(conn, id="b-1", standort_id="s1", datum="2026-06-18")
    _insert(conn, id="b-2", standort_id="s1", datum="2026-06-19")

    bel = repository.belegungen(conn, "s1", "2026-06-18")
    assert len(bel) == 1


def test_belegungen_leer_wenn_keine_buchungen(conn):
    """belegungen() liefert leere Liste, wenn keine Buchungen vorhanden sind."""
    bel = repository.belegungen(conn, "s1", "2026-06-18")
    assert bel == []


def test_belegungen_felder_korrekt(conn):
    """belegungen() befüllt raum_id, von und bis korrekt."""
    _insert(
        conn,
        id="b-1",
        raum_id="raum-x",
        standort_id="s1",
        datum="2026-06-18",
        von="10:00",
        bis="11:30",
    )
    bel = repository.belegungen(conn, "s1", "2026-06-18")
    assert len(bel) == 1
    assert bel[0].raum_id == "raum-x"
    assert bel[0].von == "10:00"
    assert bel[0].bis == "11:30"


# ---------------------------------------------------------------------------
# liste_fuer_nutzer() — Sortierung
# ---------------------------------------------------------------------------


def test_liste_fuer_nutzer_sortierung_datum_dann_von(conn):
    """liste_fuer_nutzer() liefert chronologisch sortiert (Datum, dann Startzeit)."""
    _insert(conn, id="b-1", nutzer_id="u", datum="2026-06-20", von="09:00", bis="10:00")
    _insert(conn, id="b-2", nutzer_id="u", datum="2026-06-18", von="14:00", bis="15:00")
    _insert(conn, id="b-3", nutzer_id="u", datum="2026-06-18", von="09:00", bis="10:00")

    buchungen = repository.liste_fuer_nutzer(conn, "u")
    assert [b.id for b in buchungen] == ["b-3", "b-2", "b-1"]


def test_liste_fuer_nutzer_nur_eigene(conn):
    """liste_fuer_nutzer() gibt nur Buchungen des angefragten Nutzers zurück."""
    _insert(conn, id="b-1", nutzer_id="u1")
    _insert(conn, id="b-2", nutzer_id="u2")

    buchungen = repository.liste_fuer_nutzer(conn, "u1")
    assert len(buchungen) == 1
    assert buchungen[0].id == "b-1"


def test_liste_fuer_nutzer_leer(conn):
    """liste_fuer_nutzer() liefert leere Liste für unbekannte nutzer_id."""
    buchungen = repository.liste_fuer_nutzer(conn, "niemand")
    assert buchungen == []


# ---------------------------------------------------------------------------
# anzahl()
# ---------------------------------------------------------------------------


def test_anzahl_leer(conn):
    """anzahl() liefert 0 bei leerer Tabelle."""
    assert repository.anzahl(conn) == 0


def test_anzahl_nach_inserts(conn):
    """anzahl() zählt alle Buchungen unabhängig von Nutzer/Raum."""
    _insert(conn, id="b-1", nutzer_id="u1")
    _insert(conn, id="b-2", nutzer_id="u2")
    assert repository.anzahl(conn) == 2


# ---------------------------------------------------------------------------
# insert() — Vollständigkeit der Felder
# ---------------------------------------------------------------------------


def test_insert_alle_felder_gespeichert(conn):
    """insert() persistiert alle Felder korrekt, auch notiz=None."""
    b = _buchung(id="b-persist", notiz=None)
    repository.insert(conn, b)
    row = conn.execute("SELECT * FROM buchungen WHERE id='b-persist'").fetchone()
    assert row["nutzer_id"] == "nutzer-a"
    assert row["raum_id"] == "raum-1"
    assert row["notiz"] is None


def test_insert_mit_notiz(conn):
    """insert() persistiert notiz als Text korrekt."""
    b = _buchung(id="b-mit-notiz", notiz="Wichtiger Hinweis")
    repository.insert(conn, b)
    row = conn.execute("SELECT notiz FROM buchungen WHERE id='b-mit-notiz'").fetchone()
    assert row["notiz"] == "Wichtiger Hinweis"
