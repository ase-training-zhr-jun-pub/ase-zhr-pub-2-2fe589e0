"""Router: Buchungen anlegen & auflisten (CLVN-019, CLVN-023).

Beide Endpunkte sind authentifiziert; die Nutzer-ID stammt aus dem Basic-Auth-
Header (ADR-003) und wird nicht aus dem Body/Query übernommen.
"""

from fastapi import APIRouter, Depends, HTTPException, status

import service
from auth import nutzer_id
from schemas import Buchung, BuchungAnfrage

router = APIRouter(prefix="/api/buchungen", tags=["buchungen"])


@router.get("", response_model=list[Buchung])
def meine_buchungen(nutzer: str = Depends(nutzer_id)) -> list[Buchung]:
    """Buchungsübersicht des angemeldeten Nutzers (CLVN-023)."""
    return service.meine_buchungen(nutzer)


@router.post("", response_model=Buchung, status_code=status.HTTP_201_CREATED)
def buchung_anlegen(
    anfrage: BuchungAnfrage, nutzer: str = Depends(nutzer_id)
) -> Buchung:
    """Sendet eine Raumbuchung verbindlich ab (CLVN-019).

    Bei Überschneidung mit einer bestehenden Buchung antwortet der Service mit
    HTTP 409 (Conflict) — der Doppelbuchungsschutz greift serverseitig.
    """
    try:
        return service.erstelle_buchung(nutzer, anfrage)
    except service.DoppelbuchungError as fehler:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(fehler)
        ) from fehler
