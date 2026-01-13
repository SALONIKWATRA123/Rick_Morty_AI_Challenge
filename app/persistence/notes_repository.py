"""SQLite notes repository (placeholder).

Uses the DB file at rick_morty_ai/db/notes.db.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

DB_PATH = "db/notes.db"


class NotesRepository:

    def __init__(self):
        self._create_table()

    def _create_table(self):
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS character_notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    character_id INT,
                    note TEXT,
                    created_at TEXT
                )
            """)

    def add_note(self, character_id, note):
        note = (note or "").strip()[:100]
        if not note:
            return
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                "INSERT INTO character_notes VALUES (NULL, ?, ?, ?)",
                (character_id, note, datetime.utcnow().isoformat())
            )

    def get_notes(self, character_id, limit: int = 3):
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute(
                "SELECT note, created_at FROM character_notes WHERE character_id = ? ORDER BY id DESC LIMIT ?",
                (character_id, limit)
            )
            return cursor.fetchall()
