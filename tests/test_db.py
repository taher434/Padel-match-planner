"""Check real SQLite behavior without changing the application's database.

Run from the project root: python -m unittest discover -s tests -v
"""

import sqlite3
import tempfile
import unittest
from pathlib import Path

from db import MatchDatabase


class MatchDatabaseTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.database_path = Path(self.folder.name) / "test_matches.db"
        self.database = MatchDatabase(self.database_path)
        self.database.create_table()

    def tearDown(self):
        self.database.close()
        self.folder.cleanup()

    def test_empty_database_and_unknown_ids(self):
        self.assertEqual(self.database.get_matches(), [])
        self.assertIsNone(self.database.get_match(999))
        self.assertFalse(
            self.database.update_match(
                999, "Evening match", "Riyadh", "Court 1", "2026-12-01", "Beginner"
            )
        )
        self.assertFalse(self.database.delete_match(999))
        self.assertEqual(self.database.get_matches(), [])

    def test_add_and_read_all_fields(self):
        match_id = self.database.add_match(
            "Evening match", "Riyadh", "Court 1", "2026-12-01", "Beginner"
        )
        expected = {
            "id": match_id,
            "name": "Evening match",
            "city": "Riyadh",
            "court": "Court 1",
            "match_date": "2026-12-01",
            "skill_level": "Beginner",
        }
        self.assertIsInstance(match_id, int)
        self.assertEqual(self.database.get_match(match_id), expected)
        self.assertEqual(self.database.get_matches(), [expected])

    def test_city_filter_and_date_order(self):
        later_id = self.database.add_match(
            "Later match", "Riyadh", "Court 1", "2026-12-03", "Beginner"
        )
        earlier_id = self.database.add_match(
            "Earlier match", "Riyadh", "Court 2", "2026-12-01", "Advanced"
        )
        self.database.add_match(
            "Other city", "Jeddah", "Court 3", "2026-12-02", "Intermediate"
        )
        filtered = self.database.get_matches("riYAdh")
        self.assertEqual(len(filtered), 2)
        self.assertEqual(filtered[0]["id"], earlier_id)
        self.assertEqual(filtered[1]["id"], later_id)
        self.assertEqual(self.database.get_matches("Dammam"), [])
        self.assertEqual(len(self.database.get_matches()), 3)

    def test_update_and_delete_only_change_selected_record(self):
        selected_id = self.database.add_match(
            "Selected match", "Riyadh", "Court 1", "2026-12-01", "Beginner"
        )
        other_id = self.database.add_match(
            "Other match", "Jeddah", "Court 2", "2026-12-02", "Intermediate"
        )
        other_before = self.database.get_match(other_id)
        updated = self.database.update_match(
            selected_id, "Updated match", "Dammam", "Court 3", "2026-12-04", "Advanced"
        )
        self.assertTrue(updated)
        self.assertEqual(
            self.database.get_match(selected_id),
            {
                "id": selected_id,
                "name": "Updated match",
                "city": "Dammam",
                "court": "Court 3",
                "match_date": "2026-12-04",
                "skill_level": "Advanced",
            },
        )
        self.assertEqual(self.database.get_match(other_id), other_before)
        self.assertTrue(self.database.delete_match(selected_id))
        self.assertIsNone(self.database.get_match(selected_id))
        self.assertEqual(self.database.get_matches(), [other_before])
        self.assertFalse(self.database.delete_match(selected_id))

    def test_setup_preserves_data_after_reopening(self):
        match_id = self.database.add_match(
            "Saved match", "Riyadh", "Court 1", "2026-12-01", "Beginner"
        )
        self.database.create_table()
        self.database.close()
        self.database = MatchDatabase(self.database_path)
        self.database.create_table()
        self.assertEqual(self.database.get_match(match_id)["name"], "Saved match")

    def test_parameters_preserve_quotes_unicode_and_sql_like_text(self):
        name = "Players' match'); DROP TABLE matches; --"
        city = "الرياض"
        match_id = self.database.add_match(
            name, city, "Court 1", "2026-12-01", "Beginner"
        )
        self.assertEqual(self.database.get_match(match_id)["name"], name)
        self.assertEqual(self.database.get_matches(city)[0]["id"], match_id)
        self.assertEqual(self.database.get_matches("' OR 1=1 --"), [])
        self.assertIsNone(self.database.get_match("1 OR 1=1"))
        self.assertFalse(self.database.delete_match("1 OR 1=1"))
        self.assertEqual(len(self.database.get_matches()), 1)

    def test_connections_are_independent_and_close_cleanly(self):
        other_database = MatchDatabase(self.database_path)
        try:
            self.assertIsNot(self.database.connection, other_database.connection)
            match_id = self.database.add_match(
                "Shared match", "Riyadh", "Court 1", "2026-12-01", "Beginner"
            )
            self.assertIsNotNone(other_database.get_match(match_id))
        finally:
            other_database.close()
        with self.assertRaises(sqlite3.ProgrammingError):
            other_database.get_matches()

    def test_deleted_id_is_not_reused_for_a_new_match(self):
        deleted_id = self.database.add_match(
            "Old match", "Riyadh", "Court 1", "2026-12-01", "Beginner"
        )
        self.database.delete_match(deleted_id)
        new_id = self.database.add_match(
            "New match", "Riyadh", "Court 2", "2026-12-02", "Beginner"
        )
        # An old GUI selection must not accidentally refer to a different match.
        self.assertGreater(new_id, deleted_id)
        self.assertIsNone(self.database.get_match(deleted_id))


if __name__ == "__main__":
    unittest.main()
