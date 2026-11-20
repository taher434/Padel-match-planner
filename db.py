"""SQLite operations for the Flask server.

Each Flask request will create its own MatchDatabase and close it afterward.
The Tkinter GUI and report helper must use HTTP instead of importing this file.
"""

import sqlite3
from pathlib import Path


# Keep the database beside this file, even when Flask runs from another folder.
DATABASE_PATH = Path(__file__).resolve().parent / "padel_matches.db"


class MatchDatabase:
    """Hold one SQLite connection and the operations for saved matches."""

    def __init__(self, database_path=DATABASE_PATH):
        self.connection = sqlite3.connect(database_path)
        # Named columns make it easy to convert each row into a dictionary.
        self.connection.row_factory = sqlite3.Row

    def create_table(self):
        """Create the matches table if needed, keeping existing records."""
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                city TEXT NOT NULL,
                court TEXT NOT NULL,
                match_date TEXT NOT NULL,
                skill_level TEXT NOT NULL
            )
            """
        )
        self.connection.commit()

    def get_matches(self, city=""):
        """Return a list of match dictionaries, optionally filtered by city."""
        if city:
            cursor = self.connection.execute(
                """
                SELECT * FROM matches
                WHERE city = ? COLLATE NOCASE
                ORDER BY match_date, id
                """,
                (city,),
            )
        else:
            cursor = self.connection.execute(
                "SELECT * FROM matches ORDER BY match_date, id"
            )

        matches = []
        for row in cursor.fetchall():
            matches.append(dict(row))
        return matches

    def get_match(self, match_id):
        """Return one match dictionary, or None if the ID does not exist."""
        cursor = self.connection.execute(
            "SELECT * FROM matches WHERE id = ?", (match_id,)
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return dict(row)

    def add_match(self, name, city, court, match_date, skill_level):
        """Save a match and return its new ID. Flask validates the fields."""
        cursor = self.connection.execute(
            """
            INSERT INTO matches (name, city, court, match_date, skill_level)
            VALUES (?, ?, ?, ?, ?)
            """,
            (name, city, court, match_date, skill_level),
        )
        self.connection.commit()
        return cursor.lastrowid

    def update_match(self, match_id, name, city, court, match_date, skill_level):
        """Update only the chosen match; return False for an unknown ID."""
        cursor = self.connection.execute(
            """
            UPDATE matches
            SET name = ?, city = ?, court = ?, match_date = ?, skill_level = ?
            WHERE id = ?
            """,
            (name, city, court, match_date, skill_level, match_id),
        )
        self.connection.commit()
        return cursor.rowcount > 0

    def delete_match(self, match_id):
        """Delete only the chosen match; return False for an unknown ID."""
        cursor = self.connection.execute(
            "DELETE FROM matches WHERE id = ?", (match_id,)
        )
        self.connection.commit()
        return cursor.rowcount > 0

    def close(self):
        """Close this connection. Flask will call this after the request."""
        self.connection.close()
