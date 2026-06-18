"""Router: Verfügbarkeit & Belegungen (CLVN-010).

Lesende Endpunkte ohne Auth — Verfügbarkeit ist keine personenbezogene Info.
"""

from fastapi import APIRouter, Query

import service
from schemas import Belegung, Verfuegbarkeit, DATUM_MUSTER, ZEIT_MUSTER

router = APIRouter(prefix="/api", tags=["verfuegbarkeit"])


@router.get("/verfuegbarkeit", response_model=Verfuegbarkeit)
def verfuegbarkeit_pruefen(
    raum_id: str = Query(min_length=1),
    datum: str = Query(pattern=DATUM_MUSTER),
    von: str = Query(pattern=ZEIT_MUSTER),
    bis: str = Query(pattern=ZEIT_MUSTER),
) -> Verfuegbarkeit:
    """Prüft, ob ein Raum im gewünschten Zeitraum frei ist (CLVN-010)."""
    frei = service.ist_verfuegbar(raum_id, datum, von, bis)
    return Verfuegbarkeit(
        raum_id=raum_id, datum=datum, von=von, bis=bis, verfuegbar=frei
    )


@router.get("/belegungen", response_model=list[Belegung])
def belegungen(
    standort_id: str = Query(min_length=1),
    datum: str = Query(pattern=DATUM_MUSTER),
) -> list[Belegung]:
    """Belegte Zeitfenster aller Räume eines Standorts an einem Datum.

    Erlaubt der Trefferliste, die Verfügbarkeit vieler Räume mit einer einzigen
    Abfrage zu bestimmen.
    """
    return service.belegungen(standort_id, datum)
