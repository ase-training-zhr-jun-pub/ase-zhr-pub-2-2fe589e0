"""Zusätzliche Edge-Case-Tests der Basic-Auth-Dependency (auth.py).

Ergänzt test_auth.py um Grenzfälle: Whitespace im Namen, "Basic" ohne Wert,
Passwort wird ignoriert, Sonderzeichen im Namen.
"""

import base64

import pytest
from fastapi import HTTPException, status

from auth import nutzer_id


def _basic(roh: str) -> str:
    return "Basic " + base64.b64encode(roh.encode()).decode()


# ---------------------------------------------------------------------------
# Passwort wird ignoriert (ADR-003)
# ---------------------------------------------------------------------------


def test_passwort_wird_ignoriert_beliebiger_wert():
    """Beliebiges Passwort nach dem Doppelpunkt wird ignoriert."""
    assert nutzer_id(_basic("alice:geheimesPasswort123")) == "alice"


def test_passwort_leer_nach_doppelpunkt():
    """Leeres Passwort (nur Doppelpunkt) ist gültig — nur Name zählt."""
    assert nutzer_id(_basic("bob:")) == "bob"


def test_kein_doppelpunkt_im_wert():
    """Kein Doppelpunkt: der gesamte dekodierte Wert ist der Name."""
    assert nutzer_id(_basic("nurdername")) == "nurdername"


# ---------------------------------------------------------------------------
# Whitespace im Nutzernamen
# ---------------------------------------------------------------------------


def test_whitespace_um_namen_wird_getrimmt():
    """Führender/nachfolgender Whitespace im Namen wird per strip() entfernt."""
    # roh = "  alice  :" → name = "  alice  ".strip() = "alice"
    assert nutzer_id(_basic("  alice  :")) == "alice"


def test_nur_whitespace_als_name_abgelehnt():
    """Name, der nur aus Leerzeichen besteht, wird nach strip() leer → 401."""
    with pytest.raises(HTTPException) as exc:
        nutzer_id(_basic("   :passwort"))
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc.value.headers["WWW-Authenticate"] == "Basic"


# ---------------------------------------------------------------------------
# "Basic" ohne Wert / Sonderfälle im Header-Format
# ---------------------------------------------------------------------------


def test_basic_ohne_token_abgelehnt():
    """ "Basic" allein (kein Base64-Teil) wird abgelehnt."""
    with pytest.raises(HTTPException) as exc:
        nutzer_id("Basic ")
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED


def test_basic_gross_kleinschreibung_abgelehnt():
    """ "basic" (Kleinschreibung) passt nicht auf 'Basic ' → 401."""
    with pytest.raises(HTTPException) as exc:
        nutzer_id("basic " + base64.b64encode(b"demo:").decode())
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED


def test_leerer_string_als_header_abgelehnt():
    """Leerer String wird wie fehlender Header behandelt."""
    with pytest.raises(HTTPException) as exc:
        nutzer_id("")
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED


def test_sonderzeichen_im_nutzernamen_erlaubt():
    """Namen mit Sonderzeichen (z. B. E-Mail-Adresse) sind gültig."""
    assert nutzer_id(_basic("alice@example.com:")) == "alice@example.com"
