"""Edge-Case: BuchungAnfrage ohne notiz-Feld ist gültig (notiz=None)."""

from schemas import BuchungAnfrage


def test_buchung_ohne_notiz_ist_gueltig():
    """BuchungAnfrage ohne notiz-Feld ist gültig; notiz ist None (Default)."""
    anfrage = BuchungAnfrage(
        raum_id="raum-1",
        standort_id="standort-1",
        datum="2026-06-18",
        von="09:00",
        bis="10:00",
        titel="Test-Meeting",
    )
    assert anfrage.notiz is None
