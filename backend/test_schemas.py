"""Tests der Pydantic-Schemas (schemas.py) — Fokus: Validierungsregeln.

Prüft BuchungAnfrage auf korrekte Ablehnung ungültiger Eingaben und Akzeptanz
gültiger Randfälle. Alle Validierungen laufen rein in Python ohne DB-Zugriff.
"""

import pytest
from pydantic import ValidationError

from schemas import BuchungAnfrage


def _basis(**overrides) -> dict:
    """Liefert eine minimale, gültige BuchungAnfrage als dict (überschreibbar)."""
    defaults = {
        "raum_id": "raum-1",
        "standort_id": "standort-1",
        "datum": "2026-06-18",
        "von": "09:00",
        "bis": "10:00",
        "titel": "Test-Meeting",
    }
    defaults.update(overrides)
    return defaults


# ---------------------------------------------------------------------------
# Gültige Fälle
# ---------------------------------------------------------------------------


def test_gueltige_anfrage_akzeptiert():
    """Minimal gültige Anfrage darf nicht fehlschlagen."""
    anfrage = BuchungAnfrage(**_basis())
    assert anfrage.raum_id == "raum-1"


def test_notiz_none_erlaubt():
    """notiz ist optional und darf explizit None sein."""
    anfrage = BuchungAnfrage(**_basis(notiz=None))
    assert anfrage.notiz is None


def test_notiz_fehlt_erlaubt():
    """notiz darf im dict vollständig fehlen (Standardwert None)."""
    daten = _basis()
    daten.pop("notiz", None)
    anfrage = BuchungAnfrage(**daten)
    assert anfrage.notiz is None


def test_notiz_leer_erlaubt():
    """Leerer notiz-String liegt unter max_length=2000 und ist gültig."""
    anfrage = BuchungAnfrage(**_basis(notiz=""))
    assert anfrage.notiz == ""


def test_notiz_maxlaenge_erlaubt():
    """notiz mit genau 2000 Zeichen ist noch gültig."""
    anfrage = BuchungAnfrage(**_basis(notiz="x" * 2000))
    assert len(anfrage.notiz) == 2000


def test_titel_ein_zeichen_erlaubt():
    """titel mit genau einem Zeichen (min_length=1) ist gültig."""
    anfrage = BuchungAnfrage(**_basis(titel="X"))
    assert anfrage.titel == "X"


def test_titel_maxlaenge_erlaubt():
    """titel mit genau 200 Zeichen ist noch gültig."""
    anfrage = BuchungAnfrage(**_basis(titel="A" * 200))
    assert len(anfrage.titel) == 200


def test_mittage_von_bis():
    """von=12:00, bis=13:00 — gültige Mittagsbuchung."""
    anfrage = BuchungAnfrage(**_basis(von="12:00", bis="13:00"))
    assert anfrage.von == "12:00"


def test_tagesbeginn_bis_tagesende():
    """Grenzwerte der Uhrzeit: 00:00 bis 23:59."""
    anfrage = BuchungAnfrage(**_basis(von="00:00", bis="23:59"))
    assert anfrage.bis == "23:59"


# ---------------------------------------------------------------------------
# bis <= von wird abgelehnt
# ---------------------------------------------------------------------------


def test_bis_gleich_von_abgelehnt():
    """bis == von ergibt einen Nullraum und muss abgelehnt werden."""
    with pytest.raises(ValidationError) as exc:
        BuchungAnfrage(**_basis(von="09:00", bis="09:00"))
    assert "bis muss nach von liegen" in str(exc.value)


def test_bis_vor_von_abgelehnt():
    """bis < von ist sinnwidrig und muss abgelehnt werden."""
    with pytest.raises(ValidationError) as exc:
        BuchungAnfrage(**_basis(von="10:00", bis="09:00"))
    assert "bis muss nach von liegen" in str(exc.value)


# ---------------------------------------------------------------------------
# Ungültiges Kalenderdatum
# ---------------------------------------------------------------------------


def test_datum_februar_30_abgelehnt():
    """2026-02-30 existiert nicht und muss abgelehnt werden."""
    with pytest.raises(ValidationError) as exc:
        BuchungAnfrage(**_basis(datum="2026-02-30"))
    assert "Kalenderdatum" in str(exc.value)


def test_datum_13ter_monat_abgelehnt():
    """Monat 13 existiert nicht und muss abgelehnt werden."""
    with pytest.raises(ValidationError) as exc:
        BuchungAnfrage(**_basis(datum="2026-13-01"))
    assert "Kalenderdatum" in str(exc.value)


def test_datum_tag_00_abgelehnt():
    """Tag 00 existiert nicht und muss abgelehnt werden."""
    with pytest.raises(ValidationError) as exc:
        BuchungAnfrage(**_basis(datum="2026-06-00"))
    assert "Kalenderdatum" in str(exc.value)


# ---------------------------------------------------------------------------
# Zeit-Regex (ZEIT_MUSTER ^([01]\d|2[0-3]):[0-5]\d$)
# ---------------------------------------------------------------------------


def test_von_ungueltige_stunde_24_abgelehnt():
    """Stunde 24 liegt außerhalb des Musters [01]d|2[0-3] und wird abgelehnt."""
    with pytest.raises(ValidationError):
        BuchungAnfrage(**_basis(von="24:00", bis="25:00"))


def test_von_ungueltige_minute_60_abgelehnt():
    """Minute 60 überschreitet [0-5]d und wird abgelehnt."""
    with pytest.raises(ValidationError):
        BuchungAnfrage(**_basis(von="09:60", bis="10:00"))


def test_von_ohne_fuehrender_null_abgelehnt():
    """Einzelne Stundenzahl ohne führende Null ('9:00') passt nicht auf HH:MM."""
    with pytest.raises(ValidationError):
        BuchungAnfrage(**_basis(von="9:00", bis="10:00"))


def test_von_leerer_string_abgelehnt():
    """Leerer String entspricht nicht dem Zeitmuster."""
    with pytest.raises(ValidationError):
        BuchungAnfrage(**_basis(von="", bis="10:00"))


# ---------------------------------------------------------------------------
# Datum-Regex (DATUM_MUSTER ^\d{4}-\d{2}-\d{2}$)
# ---------------------------------------------------------------------------


def test_datum_falsches_format_abgelehnt():
    """Datum im US-Format (MM/DD/YYYY) entspricht nicht dem Muster."""
    with pytest.raises(ValidationError):
        BuchungAnfrage(**_basis(datum="06/18/2026"))


def test_datum_leerer_string_abgelehnt():
    """Leerer String entspricht nicht dem Datumsmuster."""
    with pytest.raises(ValidationError):
        BuchungAnfrage(**_basis(datum=""))


# ---------------------------------------------------------------------------
# Min-/Max-Längen
# ---------------------------------------------------------------------------


def test_titel_leer_abgelehnt():
    """Leerer Titel verletzt min_length=1."""
    with pytest.raises(ValidationError):
        BuchungAnfrage(**_basis(titel=""))


def test_titel_zu_lang_abgelehnt():
    """Titel mit 201 Zeichen überschreitet max_length=200."""
    with pytest.raises(ValidationError):
        BuchungAnfrage(**_basis(titel="A" * 201))


def test_notiz_zu_lang_abgelehnt():
    """notiz mit 2001 Zeichen überschreitet max_length=2000."""
    with pytest.raises(ValidationError):
        BuchungAnfrage(**_basis(notiz="x" * 2001))


def test_raum_id_leer_abgelehnt():
    """Leere raum_id verletzt min_length=1."""
    with pytest.raises(ValidationError):
        BuchungAnfrage(**_basis(raum_id=""))


def test_standort_id_leer_abgelehnt():
    """Leere standort_id verletzt min_length=1."""
    with pytest.raises(ValidationError):
        BuchungAnfrage(**_basis(standort_id=""))
