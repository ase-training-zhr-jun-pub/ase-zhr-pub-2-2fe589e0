"""Tests der Basic-Auth-Dependency (``auth.nutzer_id``) — ADR-003.

Prüft die Pfade der Header-Verarbeitung: gültiger Header, fehlender/falscher
Header, ungültiges Base64 und leerer Nutzername. Bei allen 401-Antworten muss
der ``WWW-Authenticate``-Header gesetzt sein (RFC 7235).
"""

import base64

import pytest
from fastapi import HTTPException, status

from auth import nutzer_id


def _basic(roh: str) -> str:
    return "Basic " + base64.b64encode(roh.encode()).decode()


def test_gueltiger_header_liefert_nutzer_id():
    assert nutzer_id(_basic("demo:")) == "demo"
    # Das Passwort hinter dem Doppelpunkt wird bewusst ignoriert (ADR-003).
    assert nutzer_id(_basic("alice:geheim")) == "alice"


def test_fehlender_header():
    with pytest.raises(HTTPException) as exc:
        nutzer_id(None)
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc.value.headers["WWW-Authenticate"] == "Basic"


def test_falsches_schema():
    with pytest.raises(HTTPException) as exc:
        nutzer_id("Bearer token")
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc.value.headers["WWW-Authenticate"] == "Basic"


def test_ungueltiges_base64():
    with pytest.raises(HTTPException) as exc:
        nutzer_id("Basic !!!kein-base64!!!")
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc.value.headers["WWW-Authenticate"] == "Basic"


def test_leerer_nutzername():
    with pytest.raises(HTTPException) as exc:
        nutzer_id(_basic(":nur-passwort"))
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc.value.headers["WWW-Authenticate"] == "Basic"
