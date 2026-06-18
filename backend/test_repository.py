"""Unit-Tests für die Repository-Schicht (repository.py).

Direkte SQL-Tests gegen eine frische In-Memory-SQLite-DB (ohne Service-Schicht).
"""

import sqlite3

import pytest

import repository
from database import init_db
from schemas import Buchung

# Fester Zeitstempel für alle Test-Buchungen
_TS = "2026-01-01T00:00:00+00:00"


@pytest.fixture
def conn():
    """Frische In-Memory-DB mit Buchungen-Schema für jeden Test."""
    c = sqlite3.connect(":memory:", isolation_level=None)
    c.row_factory = sqlite3.Row
    c.execute(
        """
        CREATE TABLE buchungen (
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
    c.execute("CREATE INDEX idx_buchungen_raum_datum ON buchungen (raum_id, datum)")
    return c


def _buchung(
    id="b-001",
    nutzer_id="alice",
    raum_id="koeln-dom",
    standort_id="koeln",
    datum="2026-07-01",
    von="09:00",
    bis="10:00",
    titel="Test-Meeting",
    notiz=None,
) -> Buchung:
    return Buchung(
        id=id,
        nutzer_id=nutzer_id,
        raum_id=raum_id,
        standort_id=standort_id,
        datum=datum,
        von=von,
        bis=bis,
        titel=titel,
        notiz=notiz,
        erstellt_am=_TS,
    )


# ---------------------------------------------------------------------------
# insert + anzahl
# ---------------------------------------------------------------------------


class TestInsertUndAnzahl:
    def test_leere_db_anzahl_null(self, conn):
        assert repository.anzahl(conn) == 0

    def test_eine_buchung_eingefuegt(self, conn):
        repository.insert(conn, _buchung())
        assert repository.anzahl(conn) == 1

    def test_mehrere_buchungen_eingefuegt(self, conn):
        repository.insert(conn, _buchung(id="b-001"))
        repository.insert(conn, _buchung(id="b-002"))
        repository.insert(conn, _buchung(id="b-003"))
        assert repository.anzahl(conn) == 3

    def test_doppelte_id_wirft_fehler(self, conn):
        repository.insert(conn, _buchung(id="b-dup"))
        with pytest.raises(Exception):
            repository.insert(conn, _buchung(id="b-dup"))

    def test_notiz_none_gespeichert(self, conn):
        repository.insert(conn, _buchung(notiz=None))
        row = conn.execute("SELECT notiz FROM buchungen WHERE id = 'b-001'").fetchone()
        assert row["notiz"] is None

    def test_notiz_mit_wert_gespeichert(self, conn):
        repository.insert(conn, _buchung(notiz="Hinweis"))
        row = conn.execute("SELECT notiz FROM buchungen WHERE id = 'b-001'").fetchone()
        assert row["notiz"] == "Hinweis"


# ---------------------------------------------------------------------------
# liste_fuer_nutzer
# ---------------------------------------------------------------------------


class TestListeFuerNutzer:
    def test_leere_liste_ohne_buchungen(self, conn):
        result = repository.liste_fuer_nutzer(conn, "alice")
        assert result == []

    def test_gibt_buchungen_des_nutzers_zurueck(self, conn):
        repository.insert(conn, _buchung(id="b-001", nutzer_id="alice"))
        result = repository.liste_fuer_nutzer(conn, "alice")
        assert len(result) == 1
        assert result[0].nutzer_id == "alice"

    def test_gibt_nicht_buchungen_anderer_zurueck(self, conn):
        repository.insert(conn, _buchung(id="b-001", nutzer_id="bob"))
        result = repository.liste_fuer_nutzer(conn, "alice")
        assert result == []

    def test_chronologische_sortierung_nach_datum_von(self, conn):
        repository.insert(conn, _buchung(id="b-003", datum="2026-07-03", von="09:00"))
        repository.insert(conn, _buchung(id="b-001", datum="2026-07-01", von="14:00"))
        repository.insert(conn, _buchung(id="b-002", datum="2026-07-01", von="09:00"))
        result = repository.liste_fuer_nutzer(conn, "alice")
        assert [b.id for b in result] == ["b-002", "b-001", "b-003"]

    def test_nur_eigene_buchungen_bei_mehreren_nutzern(self, conn):
        repository.insert(conn, _buchung(id="b-a1", nutzer_id="alice"))
        repository.insert(conn, _buchung(id="b-b1", nutzer_id="bob"))
        repository.insert(
            conn, _buchung(id="b-a2", nutzer_id="alice", datum="2026-07-02")
        )
        result = repository.liste_fuer_nutzer(conn, "alice")
        assert len(result) == 2
        assert all(b.nutzer_id == "alice" for b in result)

    def test_gibt_buchung_objekte_zurueck(self, conn):
        repository.insert(conn, _buchung())
        result = repository.liste_fuer_nutzer(conn, "alice")
        assert isinstance(result[0], Buchung)


# ---------------------------------------------------------------------------
# belegungen
# ---------------------------------------------------------------------------


class TestBelegungen:
    def test_keine_belegungen_leere_db(self, conn):
        result = repository.belegungen(conn, "koeln", "2026-07-01")
        assert result == []

    def test_belegung_eines_raums(self, conn):
        repository.insert(conn, _buchung(standort_id="koeln", datum="2026-07-01"))
        result = repository.belegungen(conn, "koeln", "2026-07-01")
        assert len(result) == 1
        assert result[0].raum_id == "koeln-dom"
        assert result[0].von == "09:00"
        assert result[0].bis == "10:00"

    def test_anderer_standort_nicht_enthalten(self, conn):
        repository.insert(conn, _buchung(standort_id="berlin", datum="2026-07-01"))
        result = repository.belegungen(conn, "koeln", "2026-07-01")
        assert result == []

    def test_anderes_datum_nicht_enthalten(self, conn):
        repository.insert(conn, _buchung(standort_id="koeln", datum="2026-07-02"))
        result = repository.belegungen(conn, "koeln", "2026-07-01")
        assert result == []

    def test_mehrere_raeume_eines_standorts(self, conn):
        repository.insert(
            conn, _buchung(id="b-1", raum_id="koeln-dom", standort_id="koeln")
        )
        repository.insert(
            conn, _buchung(id="b-2", raum_id="koeln-flora", standort_id="koeln")
        )
        result = repository.belegungen(conn, "koeln", "2026-07-01")
        assert len(result) == 2
        raum_ids = {b.raum_id for b in result}
        assert "koeln-dom" in raum_ids
        assert "koeln-flora" in raum_ids

    def test_sortierung_nach_raum_von(self, conn):
        repository.insert(
            conn,
            _buchung(
                id="b-2", raum_id="b-raum", von="10:00", bis="11:00", standort_id="s"
            ),
        )
        repository.insert(
            conn,
            _buchung(
                id="b-1", raum_id="a-raum", von="09:00", bis="10:00", standort_id="s"
            ),
        )
        result = repository.belegungen(conn, "s", "2026-07-01")
        assert result[0].raum_id == "a-raum"
        assert result[1].raum_id == "b-raum"


# ---------------------------------------------------------------------------
# ueberschneidende
# ---------------------------------------------------------------------------


class TestUeberschneidende:
    def test_keine_buchungen_kein_treffer(self, conn):
        result = repository.ueberschneidende(
            conn, "koeln-dom", "2026-07-01", "09:00", "10:00"
        )
        assert result == []

    def test_identisches_intervall_ueberschneidet(self, conn):
        repository.insert(conn, _buchung(von="09:00", bis="10:00"))
        result = repository.ueberschneidende(
            conn, "koeln-dom", "2026-07-01", "09:00", "10:00"
        )
        assert len(result) == 1

    def test_teilweise_ueberlappung_von_vorne(self, conn):
        # Bestehend: 09:00–10:00 | Neu: 08:30–09:30 → Überschneidung
        repository.insert(conn, _buchung(von="09:00", bis="10:00"))
        result = repository.ueberschneidende(
            conn, "koeln-dom", "2026-07-01", "08:30", "09:30"
        )
        assert len(result) == 1

    def test_teilweise_ueberlappung_von_hinten(self, conn):
        # Bestehend: 09:00–10:00 | Neu: 09:30–10:30 → Überschneidung
        repository.insert(conn, _buchung(von="09:00", bis="10:00"))
        result = repository.ueberschneidende(
            conn, "koeln-dom", "2026-07-01", "09:30", "10:30"
        )
        assert len(result) == 1

    def test_neues_intervall_enthaelt_bestehendes(self, conn):
        # Bestehend: 10:00–11:00 | Neu: 09:00–12:00 → Überschneidung
        repository.insert(conn, _buchung(von="10:00", bis="11:00"))
        result = repository.ueberschneidende(
            conn, "koeln-dom", "2026-07-01", "09:00", "12:00"
        )
        assert len(result) == 1

    def test_bestehendes_enthaelt_neues_intervall(self, conn):
        # Bestehend: 08:00–18:00 | Neu: 10:00–12:00 → Überschneidung
        repository.insert(conn, _buchung(von="08:00", bis="18:00"))
        result = repository.ueberschneidende(
            conn, "koeln-dom", "2026-07-01", "10:00", "12:00"
        )
        assert len(result) == 1

    def test_direkt_angrenzend_kein_ueberschneiden(self, conn):
        # Bestehend: 09:00–10:00 | Neu: 10:00–11:00 → kein Overlap (Randfall)
        repository.insert(conn, _buchung(von="09:00", bis="10:00"))
        result = repository.ueberschneidende(
            conn, "koeln-dom", "2026-07-01", "10:00", "11:00"
        )
        assert result == []

    def test_vor_bestehendem_kein_ueberschneiden(self, conn):
        # Bestehend: 10:00–11:00 | Neu: 08:00–09:00 → kein Overlap
        repository.insert(conn, _buchung(von="10:00", bis="11:00"))
        result = repository.ueberschneidende(
            conn, "koeln-dom", "2026-07-01", "08:00", "09:00"
        )
        assert result == []

    def test_anderer_raum_kein_treffer(self, conn):
        repository.insert(conn, _buchung(raum_id="koeln-dom"))
        result = repository.ueberschneidende(
            conn, "koeln-flora", "2026-07-01", "09:00", "10:00"
        )
        assert result == []

    def test_anderes_datum_kein_treffer(self, conn):
        repository.insert(conn, _buchung(datum="2026-07-02"))
        result = repository.ueberschneidende(
            conn, "koeln-dom", "2026-07-01", "09:00", "10:00"
        )
        assert result == []

    def test_mehrere_ueberschneidungen_gefunden(self, conn):
        repository.insert(conn, _buchung(id="b-001", von="09:00", bis="10:00"))
        repository.insert(conn, _buchung(id="b-002", von="09:30", bis="10:30"))
        # Neues Intervall überschneidet beide
        result = repository.ueberschneidende(
            conn, "koeln-dom", "2026-07-01", "09:15", "10:15"
        )
        assert len(result) == 2
