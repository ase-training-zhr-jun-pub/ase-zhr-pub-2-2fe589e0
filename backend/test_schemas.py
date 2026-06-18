"""Unit-Tests für die Pydantic-Schemas (schemas.py).

Prüft Validierungsregeln: Zeitformat, Datumsformat, bis > von, Feldgrenzen.
"""

import pytest
from pydantic import ValidationError

from schemas import Belegung, Buchung, BuchungAnfrage, Verfuegbarkeit


# ---------------------------------------------------------------------------
# BuchungAnfrage — gültige Anfragen
# ---------------------------------------------------------------------------


def _minimale_anfrage(**overrides) -> dict:
    """Liefert einen validen BuchungAnfrage-Dict (mit optionalen Overrides)."""
    base = {
        "raum_id": "koeln-dom",
        "standort_id": "koeln",
        "datum": "2026-07-01",
        "von": "09:00",
        "bis": "10:00",
        "titel": "Meeting",
        "notiz": None,
    }
    base.update(overrides)
    return base


class TestBuchungAnfrageGueltig:
    def test_minimale_pflichtfelder_akzeptiert(self):
        anfrage = BuchungAnfrage(**_minimale_anfrage())
        assert anfrage.raum_id == "koeln-dom"
        assert anfrage.von == "09:00"
        assert anfrage.bis == "10:00"

    def test_notiz_optional_fehlt(self):
        daten = _minimale_anfrage()
        del daten["notiz"]
        anfrage = BuchungAnfrage(**daten)
        assert anfrage.notiz is None

    def test_notiz_mit_wert(self):
        anfrage = BuchungAnfrage(**_minimale_anfrage(notiz="Wichtiger Hinweis"))
        assert anfrage.notiz == "Wichtiger Hinweis"

    def test_mitternacht_als_von(self):
        anfrage = BuchungAnfrage(**_minimale_anfrage(von="00:00", bis="01:00"))
        assert anfrage.von == "00:00"

    def test_spaete_uhrzeit_23_59(self):
        anfrage = BuchungAnfrage(**_minimale_anfrage(von="22:00", bis="23:59"))
        assert anfrage.bis == "23:59"


# ---------------------------------------------------------------------------
# BuchungAnfrage — Zeitformat-Validierung
# ---------------------------------------------------------------------------


class TestBuchungAnfrageZeitformat:
    @pytest.mark.parametrize("von", ["9:00", "09:0", "09:60", "24:00", "25:00", "abc"])
    def test_ungueltige_von_uhrzeit_abgelehnt(self, von):
        with pytest.raises(ValidationError):
            BuchungAnfrage(**_minimale_anfrage(von=von, bis="10:00"))

    @pytest.mark.parametrize("bis", ["10:61", "24:00", "10:0", "1000"])
    def test_ungueltige_bis_uhrzeit_abgelehnt(self, bis):
        with pytest.raises(ValidationError):
            BuchungAnfrage(**_minimale_anfrage(bis=bis))

    def test_bis_gleich_von_abgelehnt(self):
        with pytest.raises(ValidationError, match="bis muss nach von liegen"):
            BuchungAnfrage(**_minimale_anfrage(von="10:00", bis="10:00"))

    def test_bis_vor_von_abgelehnt(self):
        with pytest.raises(ValidationError, match="bis muss nach von liegen"):
            BuchungAnfrage(**_minimale_anfrage(von="11:00", bis="10:00"))


# ---------------------------------------------------------------------------
# BuchungAnfrage — Datumsformat-Validierung
# ---------------------------------------------------------------------------


class TestBuchungAnfrageDatum:
    @pytest.mark.parametrize("datum", ["2026-13-01", "2026-00-01", "2026-02-30"])
    def test_ungueltige_kalendertermine_abgelehnt(self, datum):
        with pytest.raises(ValidationError):
            BuchungAnfrage(**_minimale_anfrage(datum=datum))

    @pytest.mark.parametrize("datum", ["01-07-2026", "2026/07/01", "20260701", "abc"])
    def test_falsches_datumsformat_abgelehnt(self, datum):
        with pytest.raises(ValidationError):
            BuchungAnfrage(**_minimale_anfrage(datum=datum))

    def test_schaltjahr_29_feb_akzeptiert(self):
        anfrage = BuchungAnfrage(**_minimale_anfrage(datum="2024-02-29"))
        assert anfrage.datum == "2024-02-29"

    def test_kein_schaltjahr_29_feb_abgelehnt(self):
        with pytest.raises(ValidationError):
            BuchungAnfrage(**_minimale_anfrage(datum="2025-02-29"))


# ---------------------------------------------------------------------------
# BuchungAnfrage — Textfeld-Validierung
# ---------------------------------------------------------------------------


class TestBuchungAnfrageTitel:
    def test_leerer_titel_abgelehnt(self):
        with pytest.raises(ValidationError):
            BuchungAnfrage(**_minimale_anfrage(titel=""))

    def test_titel_200_zeichen_akzeptiert(self):
        anfrage = BuchungAnfrage(**_minimale_anfrage(titel="x" * 200))
        assert len(anfrage.titel) == 200

    def test_titel_201_zeichen_abgelehnt(self):
        with pytest.raises(ValidationError):
            BuchungAnfrage(**_minimale_anfrage(titel="x" * 201))

    def test_notiz_2000_zeichen_akzeptiert(self):
        anfrage = BuchungAnfrage(**_minimale_anfrage(notiz="y" * 2000))
        assert len(anfrage.notiz) == 2000

    def test_notiz_2001_zeichen_abgelehnt(self):
        with pytest.raises(ValidationError):
            BuchungAnfrage(**_minimale_anfrage(notiz="y" * 2001))

    def test_leere_raum_id_abgelehnt(self):
        with pytest.raises(ValidationError):
            BuchungAnfrage(**_minimale_anfrage(raum_id=""))

    def test_leere_standort_id_abgelehnt(self):
        with pytest.raises(ValidationError):
            BuchungAnfrage(**_minimale_anfrage(standort_id=""))


# ---------------------------------------------------------------------------
# Buchung (Response-Modell)
# ---------------------------------------------------------------------------


class TestBuchungModell:
    def test_buchung_vollstaendig(self):
        b = Buchung(
            id="b-001",
            nutzer_id="alice",
            raum_id="koeln-dom",
            standort_id="koeln",
            datum="2026-07-01",
            von="09:00",
            bis="10:00",
            titel="Test",
            notiz=None,
            erstellt_am="2026-06-01T08:00:00+00:00",
        )
        assert b.id == "b-001"
        assert b.nutzer_id == "alice"

    def test_buchung_notiz_optional(self):
        b = Buchung(
            id="b-002",
            nutzer_id="bob",
            raum_id="r1",
            standort_id="s1",
            datum="2026-07-01",
            von="10:00",
            bis="11:00",
            titel="Ohne Notiz",
            erstellt_am="2026-01-01T00:00:00+00:00",
        )
        assert b.notiz is None


# ---------------------------------------------------------------------------
# Verfuegbarkeit
# ---------------------------------------------------------------------------


class TestVerfuegbarkeit:
    def test_verfuegbar_true(self):
        v = Verfuegbarkeit(
            raum_id="r1", datum="2026-07-01", von="09:00", bis="10:00", verfuegbar=True
        )
        assert v.verfuegbar is True

    def test_verfuegbar_false(self):
        v = Verfuegbarkeit(
            raum_id="r1", datum="2026-07-01", von="09:00", bis="10:00", verfuegbar=False
        )
        assert v.verfuegbar is False


# ---------------------------------------------------------------------------
# Belegung
# ---------------------------------------------------------------------------


class TestBelegung:
    def test_belegung_felder(self):
        b = Belegung(raum_id="koeln-dom", von="09:00", bis="12:00")
        assert b.raum_id == "koeln-dom"
        assert b.von == "09:00"
        assert b.bis == "12:00"
