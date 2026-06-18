"""Datenzugriffsschicht (Repository) für Buchungen.

Reines SQL gegen die SQLite-Verbindung; keine Geschäftslogik. Die Transaktions-
steuerung (Doppelbuchungsschutz) liegt in der Service-Schicht.
"""

import sqlite3

from schemas import Belegung, Buchung

_SPALTEN_LISTE = (
    "id",
    "nutzer_id",
    "raum_id",
    "standort_id",
    "datum",
    "von",
    "bis",
    "titel",
    "notiz",
    "erstellt_am",
)
_SPALTEN = ", ".join(_SPALTEN_LISTE)
_PLATZHALTER = ", ".join("?" for _ in _SPALTEN_LISTE)


def _row_to_buchung(row: sqlite3.Row) -> Buchung:
    return Buchung(**{key: row[key] for key in row.keys()})


def liste_fuer_nutzer(conn: sqlite3.Connection, nutzer_id: str) -> list[Buchung]:
    """Alle Buchungen eines Nutzers, chronologisch (Datum, Startzeit)."""
    rows = conn.execute(
        f"SELECT {_SPALTEN} FROM buchungen WHERE nutzer_id = ? ORDER BY datum, von",
        (nutzer_id,),
    ).fetchall()
    return [_row_to_buchung(row) for row in rows]


def belegungen(
    conn: sqlite3.Connection, standort_id: str, datum: str
) -> list[Belegung]:
    """Belegte Zeitfenster aller Räume eines Standorts an einem Datum."""
    rows = conn.execute(
        "SELECT raum_id, von, bis FROM buchungen "
        "WHERE standort_id = ? AND datum = ? ORDER BY raum_id, von",
        (standort_id, datum),
    ).fetchall()
    return [Belegung(raum_id=r["raum_id"], von=r["von"], bis=r["bis"]) for r in rows]


def ueberschneidende(
    conn: sqlite3.Connection, raum_id: str, datum: str, von: str, bis: str
) -> list[sqlite3.Row]:
    """Bestehende Buchungen desselben Raums, die das Intervall überschneiden.

    Zwei Intervalle [von, bis) überschneiden sich, wenn ``a.von < b.bis`` und
    ``b.von < a.bis``. Zeit-Strings "HH:MM" vergleichen sich lexikografisch korrekt.
    """
    return conn.execute(
        "SELECT id FROM buchungen "
        "WHERE raum_id = ? AND datum = ? AND von < ? AND ? < bis",
        (raum_id, datum, bis, von),
    ).fetchall()


def insert(conn: sqlite3.Connection, buchung: Buchung) -> None:
    """Fügt eine Buchung ein (ohne Commit — die Transaktion steuert der Aufrufer).

    Spaltenliste, Platzhalter und Werte werden alle aus ``_SPALTEN_LISTE``
    abgeleitet; eine neue Spalte muss daher nur dort (und im Schema/Modell)
    ergänzt werden.
    """
    conn.execute(
        f"INSERT INTO buchungen ({_SPALTEN}) VALUES ({_PLATZHALTER})",
        tuple(getattr(buchung, spalte) for spalte in _SPALTEN_LISTE),
    )


def anzahl(conn: sqlite3.Connection) -> int:
    """Gesamtzahl der Buchungen (für den Seed-Check)."""
    return conn.execute("SELECT COUNT(*) AS n FROM buchungen").fetchone()["n"]
