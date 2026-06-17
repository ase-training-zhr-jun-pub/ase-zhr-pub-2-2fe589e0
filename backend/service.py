"""Service-Schicht: Buchungslogik, Verfügbarkeit, Doppelbuchungsschutz.

Kapselt die Geschäftsregeln und hält sie aus den Routern (HTTP) heraus
(Testbarkeit, Wiederverwendung). Kernregel ist der serverseitige
Doppelbuchungsschutz (Qualitätsziel #1 „Zuverlässigkeit", arc42 Kap. 10).
"""

import uuid
from datetime import datetime, timezone

import repository
from database import get_connection, get_lock
from schemas import Belegung, Buchung, BuchungAnfrage


class DoppelbuchungError(Exception):
    """Der Raum ist im gewünschten Zeitraum bereits belegt."""


def ist_verfuegbar(raum_id: str, datum: str, von: str, bis: str) -> bool:
    """Prüft, ob ein Raum im Zeitraum frei ist (CLVN-010)."""
    conn = get_connection()
    with get_lock():
        treffer = repository.ueberschneidende(conn, raum_id, datum, von, bis)
    return len(treffer) == 0


def belegungen(standort_id: str, datum: str) -> list[Belegung]:
    """Belegte Zeitfenster aller Räume eines Standorts an einem Datum."""
    conn = get_connection()
    with get_lock():
        return repository.belegungen(conn, standort_id, datum)


def meine_buchungen(nutzer_id: str) -> list[Buchung]:
    """Alle Buchungen des Nutzers, chronologisch (CLVN-023)."""
    conn = get_connection()
    with get_lock():
        return repository.liste_fuer_nutzer(conn, nutzer_id)


def erstelle_buchung(nutzer_id: str, anfrage: BuchungAnfrage) -> Buchung:
    """Legt eine Buchung verbindlich an (CLVN-019).

    Prüfung auf Überschneidung und Einfügen laufen atomar in einer
    ``BEGIN IMMEDIATE``-Transaktion, zusätzlich durch ein prozessweites Lock
    serialisiert. Damit kann selbst bei zwei zeitgleichen Anfragen für denselben
    Raum nur eine gewinnen — die zweite erhält ``DoppelbuchungError``.

    Raises:
        DoppelbuchungError: wenn der Zeitraum bereits (teilweise) belegt ist.
    """
    conn = get_connection()
    buchung = Buchung(
        id=str(uuid.uuid4()),
        nutzer_id=nutzer_id,
        raum_id=anfrage.raum_id,
        standort_id=anfrage.standort_id,
        datum=anfrage.datum,
        von=anfrage.von,
        bis=anfrage.bis,
        titel=anfrage.titel,
        notiz=anfrage.notiz,
        erstellt_am=datetime.now(timezone.utc).isoformat(),
    )

    with get_lock():
        try:
            conn.execute("BEGIN IMMEDIATE")
            if repository.ueberschneidende(
                conn, buchung.raum_id, buchung.datum, buchung.von, buchung.bis
            ):
                conn.rollback()
                raise DoppelbuchungError(
                    "Der Raum ist im gewählten Zeitraum bereits belegt."
                )
            repository.insert(conn, buchung)
            conn.commit()
        except DoppelbuchungError:
            raise
        except Exception:
            conn.rollback()
            raise

    return buchung
