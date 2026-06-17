"""Datenzugriffsschicht (Repository) für Buchungen.

Reines SQL gegen die SQLite-Verbindung; keine Geschäftslogik. Die Transaktions-
steuerung (Doppelbuchungsschutz) liegt in der Service-Schicht.
"""

import sqlite3

from schemas import Belegung, Buchung

_SPALTEN = (
    "id, nutzer_id, raum_id, standort_id, datum, von, bis, titel, notiz, erstellt_am"
)


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
    """Fügt eine Buchung ein (ohne Commit — die Transaktion steuert der Aufrufer)."""
    conn.execute(
        f"INSERT INTO buchungen ({_SPALTEN}) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            buchung.id,
            buchung.nutzer_id,
            buchung.raum_id,
            buchung.standort_id,
            buchung.datum,
            buchung.von,
            buchung.bis,
            buchung.titel,
            buchung.notiz,
            buchung.erstellt_am,
        ),
    )


def anzahl(conn: sqlite3.Connection) -> int:
    """Gesamtzahl der Buchungen (für den Seed-Check)."""
    return conn.execute("SELECT COUNT(*) AS n FROM buchungen").fetchone()["n"]
