"""Edge-Case-Test: BuchungAnfrage lehnt einen leeren Meetingtitel ab.

Prüft, dass schemas.BuchungAnfrage mit titel="" (min_length=1 verletzt)
eine pydantic.ValidationError wirft.
"""

import pytest
from pydantic import ValidationError

from schemas import BuchungAnfrage


def test_leerer_titel_wird_abgelehnt():
    """Leerer Titel ('') verletzt min_length=1 und muss eine ValidationError auslösen."""
    with pytest.raises(ValidationError):
        BuchungAnfrage(
            raum_id="raum-1",
            standort_id="standort-1",
            datum="2026-06-18",
            von="09:00",
            bis="10:00",
            titel="",
        )
