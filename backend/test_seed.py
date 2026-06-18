"""Tests der Seed-Funktion (seed.py).

Prüft, dass seed_if_empty() die DB beim ersten Aufruf befüllt und beim
zweiten Aufruf idempotent ist (keine doppelten Datensätze).
"""

import database
import repository
import seed


def _frische_db():
    """Schema sicherstellen und Tabelle leeren."""
    database.init_db()
    database.get_connection().execute("DELETE FROM buchungen")


def test_seed_befuellt_leere_db():
    """seed_if_empty() fügt Datensätze ein, wenn die Tabelle leer ist."""
    _frische_db()
    seed.seed_if_empty()
    conn = database.get_connection()
    assert repository.anzahl(conn) > 0


def test_seed_idempotent():
    """Zweiter Aufruf von seed_if_empty() fügt keine weiteren Datensätze ein."""
    _frische_db()
    seed.seed_if_empty()
    conn = database.get_connection()
    anzahl_nach_erstem = repository.anzahl(conn)

    seed.seed_if_empty()
    anzahl_nach_zweitem = repository.anzahl(conn)

    assert anzahl_nach_erstem == anzahl_nach_zweitem


def test_seed_befuellt_korrekte_anzahl():
    """seed_if_empty() legt genau die konfigurierten Seed-Buchungen an."""
    _frische_db()
    seed.seed_if_empty()
    conn = database.get_connection()
    assert repository.anzahl(conn) == len(seed._SEED_BUCHUNGEN)


def test_seed_ueberspringt_nicht_leere_db():
    """seed_if_empty() fügt nichts ein, wenn die DB bereits Buchungen enthält."""
    _frische_db()
    # Eine einzelne Buchung vorab einfügen
    from schemas import Buchung

    vorhandene = Buchung(
        id="b-vorab",
        nutzer_id="testnutzer",
        raum_id="raum-x",
        standort_id="standort-x",
        datum="2026-06-18",
        von="08:00",
        bis="09:00",
        titel="Vorab-Buchung",
        notiz=None,
        erstellt_am="2026-01-01T00:00:00+00:00",
    )
    conn = database.get_connection()
    repository.insert(conn, vorhandene)

    seed.seed_if_empty()

    # Nur die eine vorab eingefügte Buchung darf vorhanden sein
    assert repository.anzahl(conn) == 1


def test_seed_demo_nutzer_buchungen_vorhanden():
    """Nach dem Seed sind Buchungen für den Demo-Nutzer abrufbar."""
    _frische_db()
    seed.seed_if_empty()
    conn = database.get_connection()
    demo_buchungen = repository.liste_fuer_nutzer(conn, seed.DEMO_NUTZER)
    assert len(demo_buchungen) > 0
