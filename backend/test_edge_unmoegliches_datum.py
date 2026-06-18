"""Edge-Case: Unmögliches Kalenderdatum wird von BuchungAnfrage abgelehnt."""

import pytest
from pydantic import ValidationError

from schemas import BuchungAnfrage


def test_datum_februar_31_abgelehnt():
    """2026-02-31 existiert nicht und muss eine ValidationError auslösen."""
    with pytest.raises(ValidationError):
        BuchungAnfrage(
            raum_id="raum-1",
            standort_id="standort-1",
            datum="2026-02-31",
            von="09:00",
            bis="10:00",
            titel="Test-Meeting",
        )
