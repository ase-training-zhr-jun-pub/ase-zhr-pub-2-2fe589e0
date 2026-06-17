"""Pydantic-Schemas an der API-Grenze (Request-/Response-Modelle).

Zeit-Strings im Format ``HH:MM``, Datum als ISO ``YYYY-MM-DD``. Diese Formate
lassen sich lexikografisch korrekt vergleichen (nullbasiert/zero-padded), was die
Überschneidungsprüfung in SQL vereinfacht.
"""

from pydantic import BaseModel, Field, model_validator

# 24-Stunden-Uhrzeit "HH:MM"
ZEIT_MUSTER = r"^([01]\d|2[0-3]):[0-5]\d$"
# ISO-Datum "YYYY-MM-DD"
DATUM_MUSTER = r"^\d{4}-\d{2}-\d{2}$"


class BuchungAnfrage(BaseModel):
    """Eingehende Buchungsanfrage (POST /api/buchungen).

    Die ``nutzer_id`` stammt nicht aus dem Body, sondern aus dem Auth-Header
    (siehe ``auth.py``, ADR-003).
    """

    raum_id: str = Field(min_length=1)
    standort_id: str = Field(min_length=1)
    datum: str = Field(pattern=DATUM_MUSTER)
    von: str = Field(pattern=ZEIT_MUSTER)
    bis: str = Field(pattern=ZEIT_MUSTER)
    titel: str = Field(min_length=1, max_length=200)
    notiz: str | None = Field(default=None, max_length=2000)

    @model_validator(mode="after")
    def _bis_nach_von(self) -> "BuchungAnfrage":
        if self.bis <= self.von:
            raise ValueError("bis muss nach von liegen")
        return self


class Buchung(BaseModel):
    """Persistierte Buchung (Response-Modell)."""

    id: str
    nutzer_id: str
    raum_id: str
    standort_id: str
    datum: str
    von: str
    bis: str
    titel: str
    notiz: str | None = None
    erstellt_am: str


class Verfuegbarkeit(BaseModel):
    """Ergebnis der Verfügbarkeitsprüfung (GET /api/verfuegbarkeit, CLVN-010)."""

    raum_id: str
    datum: str
    von: str
    bis: str
    verfuegbar: bool


class Belegung(BaseModel):
    """Ein belegtes Zeitfenster eines Raums (GET /api/belegungen).

    Erlaubt der Trefferliste, die Verfügbarkeit vieler Räume mit einer einzigen
    Abfrage clientseitig zu bestimmen.
    """

    raum_id: str
    von: str
    bis: str
