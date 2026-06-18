"""Unit-Tests für die Seed-Logik (seed.py).

Prüft Idempotenz, Anzahl der Seed-Datensätze und Nutzer-Zuordnung.
"""

import pytest

import repository
import seed
from database import get_connection, init_db


@pytest.fixture(autouse=True)
def frische_db():
    """Schema initialisieren und Tabelle vor jedem Test leeren."""
    conn = get_connection()
    init_db()
    conn.execute("DELETE FROM buchungen")
    conn.commit()
    yield
    conn.execute("DELETE FROM buchungen")
    conn.commit()


class TestSeedIfEmpty:
    def test_befuellt_leere_db(self):
        conn = get_connection()
        seed.seed_if_empty()
        assert repository.anzahl(conn) > 0

    def test_seed_exakte_anzahl(self):
        conn = get_connection()
        seed.seed_if_empty()
        # Es gibt genau 7 Seed-Buchungen (4 demo + 3 andere)
        assert repository.anzahl(conn) == len(seed._SEED_BUCHUNGEN)

    def test_idempotenz_zweifacher_aufruf(self):
        conn = get_connection()
        seed.seed_if_empty()
        anzahl_nach_erstem = repository.anzahl(conn)
        seed.seed_if_empty()
        # Zweiter Aufruf ändert nichts
        assert repository.anzahl(conn) == anzahl_nach_erstem

    def test_idempotenz_dreifacher_aufruf(self):
        conn = get_connection()
        seed.seed_if_empty()
        seed.seed_if_empty()
        seed.seed_if_empty()
        assert repository.anzahl(conn) == len(seed._SEED_BUCHUNGEN)

    def test_nicht_leer_wird_nicht_ueberschrieben(self):
        """seed_if_empty() darf bei nicht-leerer DB nichts tun."""
        conn = get_connection()
        seed.seed_if_empty()
        # Manuelle Löschung einer Buchung
        conn.execute("DELETE FROM buchungen WHERE id = 'b-1001'")
        conn.commit()
        anzahl_nach_loeschung = repository.anzahl(conn)
        # Erneuter Seed: da DB nicht leer, wird nichts eingefügt
        seed.seed_if_empty()
        assert repository.anzahl(conn) == anzahl_nach_loeschung

    def test_demo_nutzer_buchungen_vorhanden(self):
        conn = get_connection()
        seed.seed_if_empty()
        demo_buchungen = repository.liste_fuer_nutzer(conn, seed.DEMO_NUTZER)
        assert len(demo_buchungen) > 0

    def test_demo_nutzer_ist_demo(self):
        assert seed.DEMO_NUTZER == "demo"

    def test_seed_buchungen_haben_unterschiedliche_ids(self):
        ids = [b.id for b in seed._SEED_BUCHUNGEN]
        assert len(ids) == len(set(ids)), "Alle Seed-IDs müssen eindeutig sein"

    def test_seed_buchungen_haben_gueltiges_zeitformat(self):
        import re

        zeitformat = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")
        for b in seed._SEED_BUCHUNGEN:
            assert zeitformat.match(b.von), f"{b.id}: von='{b.von}' ungültig"
            assert zeitformat.match(b.bis), f"{b.id}: bis='{b.bis}' ungültig"

    def test_seed_buchungen_bis_nach_von(self):
        for b in seed._SEED_BUCHUNGEN:
            assert b.bis > b.von, f"{b.id}: bis muss nach von liegen"

    def test_fremdbelegungen_nutzer_andere(self):
        andere = [b for b in seed._SEED_BUCHUNGEN if b.nutzer_id == "andere"]
        assert len(andere) >= 1
