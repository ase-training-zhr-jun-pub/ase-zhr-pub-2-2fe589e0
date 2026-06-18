"""Unit-Tests für die Basic-Auth-Dependency (auth.py).

Testet direkt die Funktion nutzer_id() mit verschiedenen Authorization-Headern,
ohne FastAPI-Routing-Layer.
"""

import base64

import pytest
from fastapi import HTTPException

from auth import nutzer_id


def _basic(name: str, passwort: str = "") -> str:
    """Erzeugt einen gültigen Authorization: Basic Header-Wert."""
    kodiert = base64.b64encode(f"{name}:{passwort}".encode()).decode()
    return f"Basic {kodiert}"


# ---------------------------------------------------------------------------
# Erfolgreiche Authentifizierung
# ---------------------------------------------------------------------------


class TestNutzerIdErfolgreich:
    def test_einfacher_nutzername(self):
        assert nutzer_id(_basic("alice")) == "alice"

    def test_nutzername_mit_leerzeichen_am_rand(self):
        # Leerzeichen werden via strip() entfernt
        kodiert = base64.b64encode(b"  bob  :").decode()
        assert nutzer_id(f"Basic {kodiert}") == "bob"

    def test_nutzername_ist_nutzer_id(self):
        assert nutzer_id(_basic("demo")) == "demo"

    def test_nutzername_mit_passwort_ignoriert_passwort(self):
        # Passwort wird bewusst nicht geprüft
        assert nutzer_id(_basic("alice", "geheim123")) == "alice"

    def test_nutzername_mit_doppelpunkt_im_passwort(self):
        # Nur erster Doppelpunkt trennt Name von Passwort
        assert nutzer_id(_basic("alice", "pass:wort")) == "alice"

    def test_nutzername_mit_sonderzeichen(self):
        assert nutzer_id(_basic("alice@example.com")) == "alice@example.com"

    def test_nutzername_mit_bindestrich(self):
        assert nutzer_id(_basic("max-mustermann")) == "max-mustermann"


# ---------------------------------------------------------------------------
# Fehlende oder ungültige Header
# ---------------------------------------------------------------------------


class TestNutzerIdFehlerFaelle:
    def test_kein_header_wirft_401(self):
        with pytest.raises(HTTPException) as exc_info:
            nutzer_id(None)
        assert exc_info.value.status_code == 401

    def test_leerer_string_wirft_401(self):
        with pytest.raises(HTTPException) as exc_info:
            nutzer_id("")
        assert exc_info.value.status_code == 401

    def test_bearer_token_wirft_401(self):
        with pytest.raises(HTTPException) as exc_info:
            nutzer_id("Bearer abc123")
        assert exc_info.value.status_code == 401

    def test_kein_basic_praefix_wirft_401(self):
        kodiert = base64.b64encode(b"alice:").decode()
        with pytest.raises(HTTPException) as exc_info:
            nutzer_id(kodiert)  # kein "Basic "-Präfix
        assert exc_info.value.status_code == 401

    def test_ungueltige_base64_wirft_401(self):
        with pytest.raises(HTTPException) as exc_info:
            nutzer_id("Basic !!!ungueltig!!!")
        assert exc_info.value.status_code == 401

    def test_leerer_nutzername_wirft_401(self):
        # ":passwort" → name ist ""
        kodiert = base64.b64encode(b":passwort").decode()
        with pytest.raises(HTTPException) as exc_info:
            nutzer_id(f"Basic {kodiert}")
        assert exc_info.value.status_code == 401

    def test_nur_doppelpunkt_wirft_401(self):
        kodiert = base64.b64encode(b":").decode()
        with pytest.raises(HTTPException) as exc_info:
            nutzer_id(f"Basic {kodiert}")
        assert exc_info.value.status_code == 401

    def test_www_authenticate_header_in_antwort(self):
        with pytest.raises(HTTPException) as exc_info:
            nutzer_id(None)
        assert exc_info.value.headers.get("WWW-Authenticate") == "Basic"

    def test_nur_leerzeichen_als_nutzername_wirft_401(self):
        # "   :" → nach strip() leerer Name
        kodiert = base64.b64encode(b"   :").decode()
        with pytest.raises(HTTPException) as exc_info:
            nutzer_id(f"Basic {kodiert}")
        assert exc_info.value.status_code == 401
