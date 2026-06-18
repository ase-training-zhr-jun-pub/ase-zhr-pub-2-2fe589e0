"""Edge-Case-Test: Meetingtitel mit maximaler Länge (200 Zeichen) wird akzeptiert."""

from schemas import BuchungAnfrage


def test_titel_maximallaenge_akzeptiert():
    """BuchungAnfrage akzeptiert einen Meetingtitel mit exakt 200 Zeichen (max_length=200)."""
    anfrage = BuchungAnfrage(
        raum_id="raum-1",
        standort_id="standort-1",
        datum="2026-06-20",
        von="09:00",
        bis="10:00",
        titel="x" * 200,
    )
    assert len(anfrage.titel) == 200
