"""Edge-Case: Uhrzeit 24:00 wird von BuchungAnfrage abgelehnt.

ZEIT_MUSTER erlaubt nur 00:00–23:59 (^([01]\\d|2[0-3]):[0-5]\\d$);
die Stunde 24 liegt außerhalb des Musters 2[0-3] und muss einen
ValidationError auslösen.
"""

import pytest
from pydantic import ValidationError

from schemas import BuchungAnfrage


def test_von_24_uhr_abgelehnt():
    """Uhrzeit 24:00 ist ungültig — ZEIT_MUSTER lässt nur 00:00–23:59 zu."""
    with pytest.raises(ValidationError):
        BuchungAnfrage(
            raum_id="raum-1",
            standort_id="standort-1",
            datum="2026-06-18",
            von="24:00",
            bis="23:00",
            titel="Test-Meeting",
        )
