"""Tests der Service-Schicht — Fokus: Doppelbuchungsschutz (Qualitätsziel #1).

Die kritische ``erstelle_buchung``-Logik (atomare ``BEGIN IMMEDIATE``-Transaktion
+ Überschneidungsprüfung) darf bei Refactorings nicht still brechen. Läuft gegen
eine In-Memory-DB (siehe ``conftest.py``).
"""

import pytest

import database
import service
from schemas import BuchungAnfrage


@pytest.fixture(autouse=True)
def _frische_db():
    """Schema sicherstellen und Tabelle vor jedem Test leeren.

    Die prozessweite Verbindung lebt über alle Tests hinweg, daher zwischen den
    Tests die Daten zurücksetzen.
    """
    database.init_db()
    # Läuft bewusst im Autocommit-Modus (isolation_level=None): ein einzelnes,
    # sofort wirksames DELETE genügt zum Zurücksetzen — keine Transaktion nötig.
    database.get_connection().execute("DELETE FROM buchungen")
    yield


def _anfrage(von="09:00", bis="10:00", raum_id="raum-1") -> BuchungAnfrage:
    return BuchungAnfrage(
        raum_id=raum_id,
        standort_id="standort-1",
        datum="2026-06-18",
        von=von,
        bis=bis,
        titel="Test-Meeting",
    )


def test_buchung_anlegen_und_abrufen():
    buchung = service.erstelle_buchung("nutzer-a", _anfrage())
    assert buchung.id
    meine = service.meine_buchungen("nutzer-a")
    assert [b.id for b in meine] == [buchung.id]


def test_doppelbuchung_wird_abgelehnt():
    service.erstelle_buchung("nutzer-a", _anfrage("09:00", "10:00"))
    with pytest.raises(service.DoppelbuchungError):
        service.erstelle_buchung("nutzer-b", _anfrage("09:30", "10:30"))
    # Es darf nur die erste Buchung existieren.
    assert len(service.meine_buchungen("nutzer-b")) == 0


def test_angrenzende_buchung_erlaubt():
    # Halboffenes Intervall [von, bis): 10:00 grenzt direkt an, überschneidet nicht.
    service.erstelle_buchung("nutzer-a", _anfrage("09:00", "10:00"))
    zweite = service.erstelle_buchung("nutzer-b", _anfrage("10:00", "11:00"))
    assert zweite.id


def test_rollback_blockiert_folgebuchung_nicht():
    service.erstelle_buchung("nutzer-a", _anfrage("09:00", "10:00"))
    with pytest.raises(service.DoppelbuchungError):
        service.erstelle_buchung("nutzer-b", _anfrage("09:30", "10:30"))
    # Nach dem Rollback ist die Verbindung intakt: anderer Raum bleibt buchbar.
    ok = service.erstelle_buchung(
        "nutzer-b", _anfrage("09:30", "10:30", raum_id="raum-2")
    )
    assert ok.id


def test_ist_verfuegbar_spiegelt_belegung():
    assert service.ist_verfuegbar("raum-x", "2026-06-18", "09:00", "10:00") is True
    service.erstelle_buchung("nutzer-a", _anfrage(raum_id="raum-x"))
    assert service.ist_verfuegbar("raum-x", "2026-06-18", "09:30", "10:30") is False
