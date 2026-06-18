"""Edge-Case: BuchungAnfrage mit identischer Start- und Endzeit wird abgelehnt."""

import pytest
from pydantic import ValidationError

from schemas import BuchungAnfrage


def test_buchung_von_gleich_bis_abgelehnt():
    """von == bis ergibt ein Nullzeitfenster; der model_validator muss ValidationError werfen."""
    with pytest.raises(ValidationError) as exc:
        BuchungAnfrage(
            raum_id="raum-1",
            standort_id="standort-1",
            datum="2026-06-18",
            von="09:00",
            bis="09:00",
            titel="Test-Meeting",
        )
    assert "bis muss nach von liegen" in str(exc.value)
