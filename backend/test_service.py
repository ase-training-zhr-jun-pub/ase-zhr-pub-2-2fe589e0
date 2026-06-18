"""Unit-Tests für die Service-Schicht (service.py).

Nutzt die In-Memory-DB aus conftest.py. Jeder Test bekommt eine frische DB
durch das autouse-Fixture, das die Tabelle nach jedem Test leert.
"""

import pytest

import repository
import service
from database import get_connection, init_db
from schemas import BuchungAnfrage, Buchung


@pytest.fixture(autouse=True)
def frische_db():
    """Initialisiert das Schema und leert die Tabelle vor jedem Test."""
    conn = get_connection()
    init_db()
    conn.execute("DELETE FROM buchungen")
    conn.commit()
    yield
    conn.execute("DELETE FROM buchungen")
    conn.commit()


def _anfrage(**overrides) -> BuchungAnfrage:
    """Liefert eine valide BuchungAnfrage (mit optionalen Overrides)."""
    base = {
        "raum_id": "koeln-dom",
        "standort_id": "koeln",
        "datum": "2026-07-01",
        "von": "09:00",
        "bis": "10:00",
        "titel": "Test-Meeting",
        "notiz": None,
    }
    base.update(overrides)
    return BuchungAnfrage(**base)


# ---------------------------------------------------------------------------
# erstelle_buchung — Erfolgsfall
# ---------------------------------------------------------------------------


class TestErstelleBuchung:
    def test_buchung_wird_zurueckgegeben(self):
        buchung = service.erstelle_buchung("alice", _anfrage())
        assert isinstance(buchung, Buchung)
        assert buchung.nutzer_id == "alice"
        assert buchung.raum_id == "koeln-dom"
        assert buchung.von == "09:00"
        assert buchung.bis == "10:00"

    def test_buchung_hat_uuid_als_id(self):
        buchung = service.erstelle_buchung("alice", _anfrage())
        # UUID: 8-4-4-4-12 Hex-Zeichen
        assert len(buchung.id) == 36
        assert buchung.id.count("-") == 4

    def test_buchung_in_db_gespeichert(self):
        conn = get_connection()
        service.erstelle_buchung("alice", _anfrage())
        assert repository.anzahl(conn) == 1

    def test_zwei_buchungen_verschiedener_raeume_gleichzeitig(self):
        service.erstelle_buchung("alice", _anfrage(raum_id="koeln-dom"))
        service.erstelle_buchung("bob", _anfrage(raum_id="koeln-flora"))
        assert repository.anzahl(get_connection()) == 2

    def test_buchung_am_naechsten_tag_nach_voll_belegtem_tag(self):
        service.erstelle_buchung("alice", _anfrage(datum="2026-07-01"))
        # Gleiche Zeit, anderes Datum → kein Konflikt
        buchung = service.erstelle_buchung("alice", _anfrage(datum="2026-07-02"))
        assert buchung.datum == "2026-07-02"

    def test_angrenzende_buchung_nach_bestehender_erlaubt(self):
        service.erstelle_buchung("alice", _anfrage(von="09:00", bis="10:00"))
        # 10:00–11:00 grenzt an aber überschneidet nicht → erlaubt
        buchung = service.erstelle_buchung("alice", _anfrage(von="10:00", bis="11:00"))
        assert buchung.von == "10:00"

    def test_angrenzende_buchung_vor_bestehender_erlaubt(self):
        service.erstelle_buchung("alice", _anfrage(von="10:00", bis="11:00"))
        buchung = service.erstelle_buchung("alice", _anfrage(von="09:00", bis="10:00"))
        assert buchung.bis == "10:00"

    def test_erstellt_am_wird_gesetzt(self):
        buchung = service.erstelle_buchung("alice", _anfrage())
        assert buchung.erstellt_am is not None
        assert len(buchung.erstellt_am) > 0

    def test_notiz_wird_uebernommen(self):
        buchung = service.erstelle_buchung("alice", _anfrage(notiz="Hinweis"))
        assert buchung.notiz == "Hinweis"

    def test_notiz_none_bleibt_none(self):
        buchung = service.erstelle_buchung("alice", _anfrage(notiz=None))
        assert buchung.notiz is None


# ---------------------------------------------------------------------------
# erstelle_buchung — Doppelbuchungsschutz
# ---------------------------------------------------------------------------


class TestDoppelbuchungsschutz:
    def test_identischer_zeitraum_wirft_doppelbuchung_error(self):
        service.erstelle_buchung("alice", _anfrage(von="09:00", bis="10:00"))
        with pytest.raises(service.DoppelbuchungError):
            service.erstelle_buchung("bob", _anfrage(von="09:00", bis="10:00"))

    def test_ueberlappung_am_anfang_wirft_doppelbuchung_error(self):
        service.erstelle_buchung("alice", _anfrage(von="09:00", bis="10:00"))
        with pytest.raises(service.DoppelbuchungError):
            service.erstelle_buchung("bob", _anfrage(von="08:30", bis="09:30"))

    def test_ueberlappung_am_ende_wirft_doppelbuchung_error(self):
        service.erstelle_buchung("alice", _anfrage(von="09:00", bis="10:00"))
        with pytest.raises(service.DoppelbuchungError):
            service.erstelle_buchung("bob", _anfrage(von="09:30", bis="10:30"))

    def test_umschliessende_buchung_wirft_doppelbuchung_error(self):
        service.erstelle_buchung("alice", _anfrage(von="10:00", bis="11:00"))
        with pytest.raises(service.DoppelbuchungError):
            service.erstelle_buchung("bob", _anfrage(von="09:00", bis="12:00"))

    def test_doppelbuchung_rollt_transaktion_zurueck(self):
        """Nach fehlgeschlagener Buchung darf keine neue Buchung in der DB sein."""
        conn = get_connection()
        service.erstelle_buchung("alice", _anfrage(von="09:00", bis="10:00"))
        assert repository.anzahl(conn) == 1
        with pytest.raises(service.DoppelbuchungError):
            service.erstelle_buchung("bob", _anfrage(von="09:00", bis="10:00"))
        # Anzahl unverändert — kein Rollback-Restleichen
        assert repository.anzahl(conn) == 1

    def test_doppelbuchung_nur_fuer_selben_raum(self):
        """Dieselbe Zeit in einem anderen Raum ist kein Fehler."""
        service.erstelle_buchung(
            "alice", _anfrage(raum_id="koeln-dom", von="09:00", bis="10:00")
        )
        # Anderer Raum → kein Konflikt
        buchung = service.erstelle_buchung(
            "bob", _anfrage(raum_id="koeln-flora", von="09:00", bis="10:00")
        )
        assert buchung.raum_id == "koeln-flora"

    def test_doppelbuchung_nur_fuer_selbes_datum(self):
        """Gleiche Zeit, aber anderes Datum → kein Fehler."""
        service.erstelle_buchung(
            "alice", _anfrage(datum="2026-07-01", von="09:00", bis="10:00")
        )
        buchung = service.erstelle_buchung(
            "bob", _anfrage(datum="2026-07-02", von="09:00", bis="10:00")
        )
        assert buchung.datum == "2026-07-02"


# ---------------------------------------------------------------------------
# ist_verfuegbar
# ---------------------------------------------------------------------------


class TestIstVerfuegbar:
    def test_leere_db_immer_verfuegbar(self):
        assert (
            service.ist_verfuegbar("koeln-dom", "2026-07-01", "09:00", "10:00") is True
        )

    def test_nach_buchung_nicht_mehr_verfuegbar(self):
        service.erstelle_buchung("alice", _anfrage(von="09:00", bis="10:00"))
        assert (
            service.ist_verfuegbar("koeln-dom", "2026-07-01", "09:00", "10:00") is False
        )

    def test_anderer_raum_weiterhin_verfuegbar(self):
        service.erstelle_buchung("alice", _anfrage(raum_id="koeln-dom"))
        assert (
            service.ist_verfuegbar("koeln-flora", "2026-07-01", "09:00", "10:00")
            is True
        )

    def test_angrenzend_nach_buchung_verfuegbar(self):
        service.erstelle_buchung("alice", _anfrage(von="09:00", bis="10:00"))
        assert (
            service.ist_verfuegbar("koeln-dom", "2026-07-01", "10:00", "11:00") is True
        )

    def test_angrenzend_vor_buchung_verfuegbar(self):
        service.erstelle_buchung("alice", _anfrage(von="10:00", bis="11:00"))
        assert (
            service.ist_verfuegbar("koeln-dom", "2026-07-01", "09:00", "10:00") is True
        )

    def test_teilueberlappung_nicht_verfuegbar(self):
        service.erstelle_buchung("alice", _anfrage(von="09:00", bis="11:00"))
        assert (
            service.ist_verfuegbar("koeln-dom", "2026-07-01", "10:00", "12:00") is False
        )


# ---------------------------------------------------------------------------
# belegungen
# ---------------------------------------------------------------------------


class TestBelegungen:
    def test_leere_db_keine_belegungen(self):
        result = service.belegungen("koeln", "2026-07-01")
        assert result == []

    def test_belegung_nach_buchung_sichtbar(self):
        service.erstelle_buchung(
            "alice", _anfrage(standort_id="koeln", datum="2026-07-01")
        )
        result = service.belegungen("koeln", "2026-07-01")
        assert len(result) == 1
        assert result[0].raum_id == "koeln-dom"

    def test_anderer_standort_nicht_sichtbar(self):
        service.erstelle_buchung(
            "alice", _anfrage(standort_id="berlin", datum="2026-07-01")
        )
        result = service.belegungen("koeln", "2026-07-01")
        assert result == []

    def test_anderes_datum_nicht_sichtbar(self):
        service.erstelle_buchung(
            "alice", _anfrage(standort_id="koeln", datum="2026-07-02")
        )
        result = service.belegungen("koeln", "2026-07-01")
        assert result == []


# ---------------------------------------------------------------------------
# meine_buchungen
# ---------------------------------------------------------------------------


class TestMeineBuchungen:
    def test_keine_buchungen_leere_liste(self):
        result = service.meine_buchungen("alice")
        assert result == []

    def test_eigene_buchungen_zurueck(self):
        service.erstelle_buchung("alice", _anfrage())
        result = service.meine_buchungen("alice")
        assert len(result) == 1
        assert result[0].nutzer_id == "alice"

    def test_fremde_buchungen_nicht_enthalten(self):
        service.erstelle_buchung("bob", _anfrage())
        result = service.meine_buchungen("alice")
        assert result == []

    def test_mehrere_eigene_buchungen_chronologisch(self):
        service.erstelle_buchung("alice", _anfrage(datum="2026-07-03", von="09:00"))
        service.erstelle_buchung(
            "alice",
            _anfrage(datum="2026-07-01", von="14:00", bis="15:00", raum_id="r2"),
        )
        service.erstelle_buchung(
            "alice", _anfrage(datum="2026-07-01", von="09:00", raum_id="r3")
        )
        result = service.meine_buchungen("alice")
        assert result[0].datum == "2026-07-01"
        assert result[0].von == "09:00"
        assert result[1].datum == "2026-07-01"
        assert result[1].von == "14:00"
        assert result[2].datum == "2026-07-03"
