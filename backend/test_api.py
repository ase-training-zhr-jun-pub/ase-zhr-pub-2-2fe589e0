"""Integrationstests für den API-Layer des Booking-Service.

Testet den vollen Weg Router → Service → Repository → SQLite über HTTP,
indem FastAPI's TestClient gegen ``main.app`` eingesetzt wird. Der TestClient
wird als Context-Manager genutzt, damit der Lifespan (init_db + seed_if_empty)
sauber durchläuft.

Abgedeckte Endpunkte:
- GET /api/hello
- GET /api/verfuegbarkeit
- GET /api/belegungen
- POST /api/buchungen (mit und ohne Auth, Doppelbuchung, ungültiger Body)
- GET  /api/buchungen (mit und ohne Auth)
"""

import base64

import pytest
from fastapi.testclient import TestClient

import database
from main import app
from seed import seed_if_empty


# ---------------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------------


def _basic_auth_header(nutzer: str = "demo") -> dict[str, str]:
    """Erzeugt den Authorization-Header für Basic-Auth ohne Passwort."""
    kodiert = base64.b64encode(f"{nutzer}:".encode()).decode()
    return {"Authorization": f"Basic {kodiert}"}


def _buchung_body(
    *,
    raum_id: str = "test-raum-1",
    standort_id: str = "test-standort-1",
    datum: str = "2026-07-15",
    von: str = "10:00",
    bis: str = "11:00",
    titel: str = "Test-Meeting",
    notiz: str | None = None,
) -> dict:
    """Erstellt einen validen POST-Body für /api/buchungen."""
    body: dict = {
        "raum_id": raum_id,
        "standort_id": standort_id,
        "datum": datum,
        "von": von,
        "bis": bis,
        "titel": titel,
    }
    if notiz is not None:
        body["notiz"] = notiz
    return body


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def client():
    """TestClient mit laufendem Lifespan (init_db + seed_if_empty)."""
    with TestClient(app) as tc:
        yield tc


@pytest.fixture(autouse=True)
def _db_zuruecksetzen(client):
    """Setzt die Buchungstabelle vor jedem Test auf den Seed-Zustand zurück.

    Die prozessweite In-Memory-Verbindung lebt über alle Tests hinweg;
    daher alle Buchungen löschen und danach neu seeden, damit jeder Test
    mit einem definierten Ausgangszustand beginnt.
    """
    conn = database.get_connection()
    conn.execute("DELETE FROM buchungen")
    seed_if_empty()
    yield


# ---------------------------------------------------------------------------
# GET /api/hello
# ---------------------------------------------------------------------------


def test_hello_liefert_200_und_text(client):
    """Smoke-Test: /api/hello antwortet mit 200 und 'Hello World!'."""
    antwort = client.get("/api/hello")
    assert antwort.status_code == 200
    assert antwort.text == "Hello World!"


# ---------------------------------------------------------------------------
# GET /api/verfuegbarkeit
# ---------------------------------------------------------------------------


def test_verfuegbarkeit_freier_raum(client):
    """Ein Raum ohne Buchung gilt als verfügbar."""
    antwort = client.get(
        "/api/verfuegbarkeit",
        params={
            "raum_id": "freier-raum",
            "datum": "2026-09-01",
            "von": "09:00",
            "bis": "10:00",
        },
    )
    assert antwort.status_code == 200
    daten = antwort.json()
    assert daten["verfuegbar"] is True
    assert daten["raum_id"] == "freier-raum"
    assert daten["von"] == "09:00"
    assert daten["bis"] == "10:00"


def test_verfuegbarkeit_belegter_raum(client):
    """Ein Raum mit überschneidender Buchung gilt als belegt."""
    # Seed enthält b-1001: koeln-rheinauhafen, 2026-06-18, 09:00–10:30
    antwort = client.get(
        "/api/verfuegbarkeit",
        params={
            "raum_id": "koeln-rheinauhafen",
            "datum": "2026-06-18",
            "von": "09:30",
            "bis": "10:00",
        },
    )
    assert antwort.status_code == 200
    assert antwort.json()["verfuegbar"] is False


def test_verfuegbarkeit_angrenzend_ist_frei(client):
    """Ein Raum gilt als frei, wenn die Anfrage direkt an eine Buchung angrenzt."""
    # Seed b-1001 endet um 10:30 — von=10:30 muss frei sein.
    antwort = client.get(
        "/api/verfuegbarkeit",
        params={
            "raum_id": "koeln-rheinauhafen",
            "datum": "2026-06-18",
            "von": "10:30",
            "bis": "11:30",
        },
    )
    assert antwort.status_code == 200
    assert antwort.json()["verfuegbar"] is True


# ---------------------------------------------------------------------------
# GET /api/belegungen
# ---------------------------------------------------------------------------


def test_belegungen_liefert_liste(client):
    """Belegungen eines Standorts an einem Datum werden als Liste zurückgegeben."""
    # Seed enthält Fremdbelegungen für Standort 'koeln' am 2026-06-17.
    antwort = client.get(
        "/api/belegungen",
        params={"standort_id": "koeln", "datum": "2026-06-17"},
    )
    assert antwort.status_code == 200
    belegungen = antwort.json()
    assert isinstance(belegungen, list)
    assert len(belegungen) >= 1
    # Jede Belegung hat raum_id, von, bis
    for b in belegungen:
        assert "raum_id" in b
        assert "von" in b
        assert "bis" in b


def test_belegungen_leerer_tag(client):
    """Für einen Tag ohne Buchungen wird eine leere Liste zurückgegeben."""
    antwort = client.get(
        "/api/belegungen",
        params={"standort_id": "koeln", "datum": "2099-01-01"},
    )
    assert antwort.status_code == 200
    assert antwort.json() == []


# ---------------------------------------------------------------------------
# POST /api/buchungen
# ---------------------------------------------------------------------------


def test_buchung_anlegen_mit_auth_liefert_201(client):
    """Valide Buchung mit Auth wird mit 201 und den Buchungsdaten bestätigt."""
    antwort = client.post(
        "/api/buchungen",
        json=_buchung_body(),
        headers=_basic_auth_header("demo"),
    )
    assert antwort.status_code == 201
    daten = antwort.json()
    assert daten["nutzer_id"] == "demo"
    assert daten["raum_id"] == "test-raum-1"
    assert daten["datum"] == "2026-07-15"
    assert daten["von"] == "10:00"
    assert daten["bis"] == "11:00"
    assert "id" in daten
    assert "erstellt_am" in daten


def test_buchung_anlegen_ohne_auth_liefert_401(client):
    """POST ohne Authorization-Header wird mit 401 abgelehnt."""
    antwort = client.post("/api/buchungen", json=_buchung_body())
    assert antwort.status_code == 401
    # WWW-Authenticate-Header muss vorhanden sein
    assert "www-authenticate" in antwort.headers
    assert antwort.headers["www-authenticate"].lower() == "basic"


def test_doppelbuchung_liefert_409(client):
    """Zweite Buchung desselben Zeitraums für denselben Raum wird mit 409 abgelehnt."""
    body = _buchung_body(
        raum_id="konflikt-raum", datum="2026-08-01", von="14:00", bis="15:00"
    )
    headers = _basic_auth_header("demo")

    erste = client.post("/api/buchungen", json=body, headers=headers)
    assert erste.status_code == 201

    zweite = client.post("/api/buchungen", json=body, headers=headers)
    assert zweite.status_code == 409


def test_buchung_ungueltig_bis_vor_von_liefert_422(client):
    """Buchungsanfrage mit bis <= von wird mit 422 abgelehnt."""
    antwort = client.post(
        "/api/buchungen",
        json=_buchung_body(von="11:00", bis="10:00"),
        headers=_basic_auth_header(),
    )
    assert antwort.status_code == 422


def test_buchung_ungueltig_gleiche_zeit_liefert_422(client):
    """Buchungsanfrage mit von == bis wird mit 422 abgelehnt."""
    antwort = client.post(
        "/api/buchungen",
        json=_buchung_body(von="10:00", bis="10:00"),
        headers=_basic_auth_header(),
    )
    assert antwort.status_code == 422


def test_buchung_ungueltig_datum_format_liefert_422(client):
    """Buchungsanfrage mit ungültigem Datumsformat wird mit 422 abgelehnt."""
    antwort = client.post(
        "/api/buchungen",
        json=_buchung_body(datum="15.07.2026"),
        headers=_basic_auth_header(),
    )
    assert antwort.status_code == 422


def test_buchung_ungueltig_datum_nicht_existent_liefert_422(client):
    """Buchungsanfrage mit nicht existentem Datum (z. B. 2026-13-01) wird abgelehnt."""
    antwort = client.post(
        "/api/buchungen",
        json=_buchung_body(datum="2026-13-01"),
        headers=_basic_auth_header(),
    )
    assert antwort.status_code == 422


# ---------------------------------------------------------------------------
# GET /api/buchungen
# ---------------------------------------------------------------------------


def test_meine_buchungen_mit_auth(client):
    """GET /api/buchungen mit Auth liefert 200 und Liste der eigenen Buchungen."""
    antwort = client.get("/api/buchungen", headers=_basic_auth_header("demo"))
    assert antwort.status_code == 200
    buchungen = antwort.json()
    assert isinstance(buchungen, list)
    # Seed enthält 4 Buchungen für den Demo-Nutzer
    assert len(buchungen) >= 1
    # Alle Buchungen gehören dem angemeldeten Nutzer
    for b in buchungen:
        assert b["nutzer_id"] == "demo"


def test_meine_buchungen_ohne_auth_liefert_401(client):
    """GET /api/buchungen ohne Authorization-Header wird mit 401 abgelehnt."""
    antwort = client.get("/api/buchungen")
    assert antwort.status_code == 401
    assert "www-authenticate" in antwort.headers


def test_meine_buchungen_nur_eigene(client):
    """Verschiedene Nutzer sehen nur ihre eigenen Buchungen."""
    # Nutzer 'demo' hat Seed-Buchungen; Nutzer 'test-nutzer' beginnt mit leerer Liste.
    antwort_test = client.get(
        "/api/buchungen", headers=_basic_auth_header("test-nutzer")
    )
    assert antwort_test.status_code == 200
    assert antwort_test.json() == []

    # Demo-Nutzer hat eigene (Seed-)Buchungen
    antwort_demo = client.get("/api/buchungen", headers=_basic_auth_header("demo"))
    assert len(antwort_demo.json()) > 0


def test_buchung_erscheint_in_meine_buchungen(client):
    """Nach erfolgreicher POST-Buchung taucht diese in GET /api/buchungen auf."""
    nutzer = "neu-nutzer"
    body = _buchung_body(raum_id="neuer-raum", datum="2026-10-01")
    headers = _basic_auth_header(nutzer)

    post_antwort = client.post("/api/buchungen", json=body, headers=headers)
    assert post_antwort.status_code == 201
    buchung_id = post_antwort.json()["id"]

    get_antwort = client.get("/api/buchungen", headers=headers)
    assert get_antwort.status_code == 200
    ids = [b["id"] for b in get_antwort.json()]
    assert buchung_id in ids
