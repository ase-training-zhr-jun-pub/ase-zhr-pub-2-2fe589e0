"""Edge-Case: Meetingtitel mit 201 Zeichen wird abgelehnt (max_length=200)."""

import pytest
from pydantic import ValidationError

from schemas import BuchungAnfrage


def test_titel_201_zeichen_abgelehnt():
    """BuchungAnfrage lehnt einen Titel mit 201 Zeichen ab (max_length=200)."""
    with pytest.raises(ValidationError):
        BuchungAnfrage(
            raum_id="raum-1",
            standort_id="standort-1",
            datum="2026-06-18",
            von="09:00",
            bis="10:00",
            titel="x" * 201,
        )
