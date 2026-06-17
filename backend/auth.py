"""Basic-Auth-Dependency (ohne Passwort) — siehe [ADR-003].

Im Prototyp authentifiziert die SPA per ``Authorization: Basic base64(name:)``.
Der Nutzername IST die Nutzer-ID; ein Passwort wird bewusst nicht geprüft. Die
spätere Okta-Anbindung (OIDC) ersetzt diesen Mechanismus.
"""

import base64
import binascii

from fastapi import Header, HTTPException, status


def nutzer_id(authorization: str | None = Header(default=None)) -> str:
    """Ermittelt die Nutzer-ID aus dem Basic-Auth-Header.

    Raises:
        HTTPException(401): wenn der Header fehlt oder nicht dekodierbar ist.
    """
    if not authorization or not authorization.startswith("Basic "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Basic-Authentifizierung erforderlich.",
            headers={"WWW-Authenticate": "Basic"},
        )

    kodiert = authorization[len("Basic ") :]
    try:
        roh = base64.b64decode(kodiert, validate=True).decode("utf-8")
    except (binascii.Error, ValueError, UnicodeDecodeError) as fehler:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ungültiger Authorization-Header.",
        ) from fehler

    name = roh.split(":", 1)[0].strip()
    if not name:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Kein Nutzername im Authorization-Header.",
        )
    return name
