"""Zusätzliche Edge-Case-Tests der Service-Schicht.

Ergänzt test_service.py um Grenzfälle, die dort nicht abgedeckt sind:
ist_verfuegbar für angrenzende/überlappende Fälle, belegungen()-Filter,
meine_buchungen-Sortierung, erstelle_buchung mit verschiedenen Räumen
und mehrere Buchungen desselben Nutzers.
"""

import pytest

import database
import service
from schemas import BuchungAnfrage


@pytest.fixture(autouse=True)
def _frische_db():
    """Schema sicherstellen und Tabelle vor jedem Test leeren."""
    database.init_db()
    database.get_connection().execute("DELETE FROM buchungen")
    yield


def _anfrage(
    von="09:00",
    bis="10:00",
    raum_id="raum-1",
    standort_id="standort-1",
    datum="2026-06-18",
    titel="Test",
    notiz=None,
) -> BuchungAnfrage:
    return BuchungAnfrage(
        raum_id=raum_id,
        standort_id=standort_id,
        datum=datum,
        von=von,
        bis=bis,
        titel=titel,
        notiz=notiz,
    )


# ---------------------------------------------------------------------------
# ist_verfuegbar — Grenzfälle
# ---------------------------------------------------------------------------


def test_ist_verfuegbar_angrenzend_danach_gilt_als_frei():
    """Neue Buchung beginnt exakt, wenn bestehende endet → verfügbar (halboffenes Intervall)."""
    service.erstelle_buchung("u", _anfrage(von="09:00", bis="10:00"))
    assert service.ist_verfuegbar("raum-1", "2026-06-18", "10:00", "11:00") is True


def test_ist_verfuegbar_angrenzend_davor_gilt_als_frei():
    """Neue Buchung endet exakt, wenn bestehende beginnt → verfügbar."""
    service.erstelle_buchung("u", _anfrage(von="10:00", bis="11:00"))
    assert service.ist_verfuegbar("raum-1", "2026-06-18", "09:00", "10:00") is True


def test_ist_verfuegbar_teilueberlappung_ist_belegt():
    """Teilüberlappung am Anfang → belegt."""
    service.erstelle_buchung("u", _anfrage(von="09:00", bis="11:00"))
    assert service.ist_verfuegbar("raum-1", "2026-06-18", "10:00", "12:00") is False


def test_ist_verfuegbar_anderes_datum_ist_frei():
    """Gleicher Raum und Zeit, anderes Datum → verfügbar."""
    service.erstelle_buchung("u", _anfrage(datum="2026-06-18"))
    assert service.ist_verfuegbar("raum-1", "2026-06-19", "09:00", "10:00") is True


def test_ist_verfuegbar_anderer_raum_ist_frei():
    """Gleiche Zeit und Datum, anderer Raum → verfügbar."""
    service.erstelle_buchung("u", _anfrage(raum_id="raum-1"))
    assert service.ist_verfuegbar("raum-2", "2026-06-18", "09:00", "10:00") is True


def test_ist_verfuegbar_ohne_buchungen_true():
    """Leere DB → jeder Raum ist verfügbar."""
    assert service.ist_verfuegbar("raum-leer", "2026-06-18", "09:00", "10:00") is True


# ---------------------------------------------------------------------------
# belegungen — Filter und Inhalt
# ---------------------------------------------------------------------------


def test_belegungen_liefert_nur_angefragten_standort():
    """belegungen() schließt andere Standorte aus."""
    service.erstelle_buchung("u", _anfrage(standort_id="s1", raum_id="r1"))
    service.erstelle_buchung(
        "u",
        _anfrage(
            standort_id="s2", raum_id="r2", datum="2026-06-18", von="09:00", bis="10:00"
        ),
    )

    bel = service.belegungen("s1", "2026-06-18")
    assert all(b.raum_id == "r1" for b in bel)
    assert len(bel) == 1


def test_belegungen_liefert_nur_angefragtes_datum():
    """belegungen() schließt andere Daten aus."""
    service.erstelle_buchung("u", _anfrage(datum="2026-06-18", standort_id="s1"))
    service.erstelle_buchung(
        "u",
        _anfrage(
            datum="2026-06-19",
            standort_id="s1",
            raum_id="raum-1",
            von="11:00",
            bis="12:00",
        ),
    )

    bel = service.belegungen("s1", "2026-06-18")
    assert len(bel) == 1


def test_belegungen_leer_wenn_kein_eintrag():
    """belegungen() gibt leere Liste zurück, wenn kein Eintrag passt."""
    bel = service.belegungen("unbekannter-standort", "2026-06-18")
    assert bel == []


# ---------------------------------------------------------------------------
# meine_buchungen — Sortierung
# ---------------------------------------------------------------------------


def test_meine_buchungen_chronologische_reihenfolge():
    """meine_buchungen() liefert Buchungen chronologisch (Datum, dann von)."""
    service.erstelle_buchung(
        "u",
        _anfrage(datum="2026-06-20", von="09:00", bis="10:00", raum_id="r1"),
    )
    service.erstelle_buchung(
        "u",
        _anfrage(datum="2026-06-18", von="14:00", bis="15:00", raum_id="r2"),
    )
    service.erstelle_buchung(
        "u",
        _anfrage(datum="2026-06-18", von="09:00", bis="10:00", raum_id="r3"),
    )

    buchungen = service.meine_buchungen("u")
    daten_von = [(b.datum, b.von) for b in buchungen]
    assert daten_von == [
        ("2026-06-18", "09:00"),
        ("2026-06-18", "14:00"),
        ("2026-06-20", "09:00"),
    ]


def test_meine_buchungen_nur_eigene_buchungen():
    """meine_buchungen() gibt nur Buchungen des angefragten Nutzers zurück."""
    service.erstelle_buchung("nutzer-a", _anfrage(raum_id="r1"))
    service.erstelle_buchung(
        "nutzer-b", _anfrage(raum_id="r2", von="11:00", bis="12:00")
    )

    buchungen_a = service.meine_buchungen("nutzer-a")
    assert len(buchungen_a) == 1
    assert buchungen_a[0].nutzer_id == "nutzer-a"


def test_meine_buchungen_leer_fuer_unbekannten_nutzer():
    """meine_buchungen() gibt leere Liste für Nutzer ohne Buchungen zurück."""
    assert service.meine_buchungen("niemand") == []


# ---------------------------------------------------------------------------
# erstelle_buchung — Grenzfälle und Rückgabewerte
# ---------------------------------------------------------------------------


def test_erstelle_buchung_setzt_nutzer_id():
    """erstelle_buchung() trägt die übergebene nutzer_id in die Buchung ein."""
    b = service.erstelle_buchung("nutzer-xyz", _anfrage())
    assert b.nutzer_id == "nutzer-xyz"


def test_erstelle_buchung_generiert_eindeutige_ids():
    """Zwei Buchungen erhalten unterschiedliche UUIDs."""
    b1 = service.erstelle_buchung("u", _anfrage(raum_id="r1"))
    b2 = service.erstelle_buchung("u", _anfrage(raum_id="r2", von="11:00", bis="12:00"))
    assert b1.id != b2.id


def test_erstelle_buchung_mit_notiz():
    """erstelle_buchung() persistiert die optionale notiz."""
    b = service.erstelle_buchung("u", _anfrage(notiz="Wichtiger Hinweis"))
    meine = service.meine_buchungen("u")
    assert meine[0].notiz == "Wichtiger Hinweis"


def test_erstelle_buchung_ohne_notiz():
    """erstelle_buchung() lässt notiz=None korrekt durch."""
    b = service.erstelle_buchung("u", _anfrage(notiz=None))
    meine = service.meine_buchungen("u")
    assert meine[0].notiz is None


def test_erstelle_buchung_angrenzend_links_erlaubt():
    """Neue Buchung endet genau dort, wo bestehende beginnt → erlaubt."""
    service.erstelle_buchung("u", _anfrage(von="10:00", bis="11:00"))
    b = service.erstelle_buchung(
        "u", _anfrage(von="09:00", bis="10:00", raum_id="raum-1")
    )
    assert b.id


def test_doppelbuchung_exakter_zeitraum_selber_raum_abgelehnt():
    """Exakt gleicher Zeitraum im selben Raum löst DoppelbuchungError aus."""
    service.erstelle_buchung("u", _anfrage(von="09:00", bis="10:00"))
    with pytest.raises(service.DoppelbuchungError):
        service.erstelle_buchung("v", _anfrage(von="09:00", bis="10:00"))


def test_doppelbuchung_rollback_db_unveraendert():
    """Nach DoppelbuchungError bleibt die DB im konsistenten Zustand."""
    service.erstelle_buchung("u", _anfrage(von="09:00", bis="10:00"))
    import repository
    import database

    anzahl_vorher = repository.anzahl(database.get_connection())

    with pytest.raises(service.DoppelbuchungError):
        service.erstelle_buchung("v", _anfrage(von="09:30", bis="10:30"))

    anzahl_nachher = repository.anzahl(database.get_connection())
    assert anzahl_vorher == anzahl_nachher


def test_erstelle_buchung_gibt_korrekte_felder_zurueck():
    """erstelle_buchung() gibt ein Buchungsobjekt mit allen Feldern zurück."""
    anfrage = _anfrage(
        raum_id="raum-abc",
        standort_id="standort-xyz",
        datum="2026-07-01",
        von="13:00",
        bis="14:00",
        titel="Wichtiges Meeting",
        notiz="Raum reservieren",
    )
    b = service.erstelle_buchung("nutzer-test", anfrage)
    assert b.raum_id == "raum-abc"
    assert b.standort_id == "standort-xyz"
    assert b.datum == "2026-07-01"
    assert b.von == "13:00"
    assert b.bis == "14:00"
    assert b.titel == "Wichtiges Meeting"
    assert b.notiz == "Raum reservieren"
    assert b.erstellt_am  # nicht leer
