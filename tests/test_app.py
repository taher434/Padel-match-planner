"""Verify Flask routes using real, temporary SQLite databases."""

import sqlite3
import tempfile
import unittest
from pathlib import Path

from app import app, get_database, initialize_database


class FlaskApiTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.previous_path = app.config["DATABASE_PATH"]
        self.previous_testing = app.config["TESTING"]
        app.config["DATABASE_PATH"] = Path(self.folder.name) / "api_matches.db"
        app.config["TESTING"] = True
        initialize_database()
        self.client = app.test_client()
        self.values = {
            "name": "Evening match",
            "city": "Riyadh",
            "court": "Court 1",
            "match_date": "2026-12-01",
            "skill_level": "Beginner",
        }

    def tearDown(self):
        app.config["DATABASE_PATH"] = self.previous_path
        app.config["TESTING"] = self.previous_testing
        self.folder.cleanup()

    def test_empty_list_and_export(self):
        for url in ["/matches", "/matches?city=Riyadh", "/matches/export"]:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.get_json(), {"success": True, "matches": []})

    def test_add_and_list_cleaned_form_values(self):
        self.values["name"] = "  Evening match  "
        self.values["city"] = "  Riyadh  "
        response = self.client.post("/matches/add", data=self.values)
        self.assertEqual(response.status_code, 201)
        result = response.get_json()
        self.assertTrue(result["success"])
        self.assertIsInstance(result["match_id"], int)
        expected = self.values.copy()
        expected["name"] = "Evening match"
        expected["city"] = "Riyadh"
        expected["id"] = result["match_id"]
        self.assertEqual(self.client.get("/matches").get_json()["matches"], [expected])

    def test_missing_and_blank_fields_return_400_without_saving(self):
        for field in self.values:
            for invalid_value in [None, "   "]:
                with self.subTest(field=field, value=invalid_value):
                    invalid = self.values.copy()
                    if invalid_value is None:
                        del invalid[field]
                    else:
                        invalid[field] = invalid_value
                    response = self.client.post("/matches/add", data=invalid)
                    self.assertEqual(response.status_code, 400)
                    self.assertFalse(response.get_json()["success"])
                    self.assertIn("required", response.get_json()["message"])
        self.assertEqual(self.client.get("/matches").get_json()["matches"], [])

    def test_invalid_dates_are_rejected(self):
        for invalid_date in ["2026-02-30", "2026-2-1", "20261201", "2026-W01-1"]:
            with self.subTest(date=invalid_date):
                self.values["match_date"] = invalid_date
                response = self.client.post("/matches/add", data=self.values)
                self.assertEqual(response.status_code, 400)
                self.assertIn("YYYY-MM-DD", response.get_json()["message"])
        self.assertEqual(self.client.get("/matches").get_json()["matches"], [])

    def test_text_limits_and_skill_level(self):
        for field in ["name", "city", "court", "skill_level"]:
            with self.subTest(field=field):
                invalid = self.values.copy()
                invalid[field] = "x" * 101
                response = self.client.post("/matches/add", data=invalid)
                self.assertEqual(response.status_code, 400)
                self.assertFalse(response.get_json()["success"])
        self.values["name"] = "x" * 100
        self.values["city"] = "y" * 100
        self.values["court"] = "z" * 100
        self.values["match_date"] = "2028-02-29"
        self.assertEqual(self.client.post("/matches/add", data=self.values).status_code, 201)

    def test_city_filter_and_export_saved_matches(self):
        self.client.post("/matches/add", data=self.values)
        self.values["city"] = "Jeddah"
        self.client.post("/matches/add", data=self.values)
        filtered = self.client.get("/matches", query_string={"city": " riYAdh "})
        self.assertEqual(len(filtered.get_json()["matches"]), 1)
        self.assertEqual(filtered.get_json()["matches"][0]["city"], "Riyadh")
        self.assertEqual(self.client.get("/matches?city=Dammam").get_json()["matches"], [])
        exported = self.client.get("/matches/export").get_json()["matches"]
        self.assertEqual(exported, self.client.get("/matches").get_json()["matches"])
        self.assertEqual(len(exported), 2)
        too_long = self.client.get("/matches", query_string={"city": "x" * 101})
        self.assertEqual(too_long.status_code, 400)
        self.assertFalse(too_long.get_json()["success"])

    def test_edit_and_delete_preserve_other_matches(self):
        selected_id = self.client.post("/matches/add", data=self.values).get_json()["match_id"]
        self.values["name"] = "Other match"
        self.client.post("/matches/add", data=self.values)
        self.values["name"] = "Updated match"
        self.values["city"] = "Dammam"
        self.values["court"] = "Court 2"
        self.values["match_date"] = "2026-12-03"
        self.values["skill_level"] = "Advanced"
        response = self.client.post(f"/matches/{selected_id}/edit", data=self.values)
        self.assertEqual(response.status_code, 200)
        records = self.client.get("/matches").get_json()["matches"]
        expected = self.values.copy()
        expected["id"] = selected_id
        self.assertEqual(records[1], expected)
        self.assertEqual(records[0]["name"], "Other match")
        response = self.client.post(f"/matches/{selected_id}/delete")
        self.assertEqual(response.status_code, 200)
        remaining = self.client.get("/matches").get_json()["matches"]
        self.assertEqual(remaining, [records[0]])

    def test_invalid_edit_preserves_saved_values(self):
        match_id = self.client.post("/matches/add", data=self.values).get_json()["match_id"]
        before = self.client.get("/matches").get_json()["matches"]
        self.values["skill_level"] = "Expert"
        response = self.client.post(f"/matches/{match_id}/edit", data=self.values)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.client.get("/matches").get_json()["matches"], before)

    def test_unknown_and_deleted_ids_return_404(self):
        for action in ["edit", "delete"]:
            response = self.client.post(f"/matches/999/{action}", data=self.values)
            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.get_json(), {"success": False, "message": "Match not found."})
        match_id = self.client.post("/matches/add", data=self.values).get_json()["match_id"]
        self.client.post(f"/matches/{match_id}/delete")
        response = self.client.post(f"/matches/{match_id}/edit", data=self.values)
        self.assertEqual(response.status_code, 404)

    def test_unknown_routes_and_wrong_methods_return_json(self):
        response = self.client.get("/unknown")
        self.assertEqual(response.status_code, 404)
        self.assertFalse(response.get_json()["success"])
        for url in ["/matches/add", "/matches/1/edit", "/matches/1/delete"]:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 405)
                self.assertFalse(response.get_json()["success"])
        self.assertEqual(self.client.get("/matches").get_json()["matches"], [])

    def test_repeated_setup_preserves_saved_matches(self):
        self.client.post("/matches/add", data=self.values)
        before = self.client.get("/matches").get_json()["matches"]
        initialize_database()
        self.assertEqual(self.client.get("/matches").get_json()["matches"], before)

    def test_one_connection_per_request_and_cleanup_after_errors(self):
        with app.test_request_context("/matches"):
            first_database = get_database()
            self.assertIs(first_database, get_database())
        with self.assertRaises(sqlite3.ProgrammingError):
            first_database.get_matches()
        with self.assertRaisesRegex(ValueError, "Simulated request failure"):
            with app.test_request_context("/matches"):
                second_database = get_database()
                self.assertIsNot(first_database, second_database)
                raise ValueError("Simulated request failure")
        with self.assertRaises(sqlite3.ProgrammingError):
            second_database.get_matches()

    def test_database_error_returns_json_and_requests_can_recover(self):
        valid_path = app.config["DATABASE_PATH"]
        app.config["DATABASE_PATH"] = Path(self.folder.name) / "missing" / "matches.db"
        try:
            with self.assertLogs(app.logger, level="ERROR"):
                response = self.client.get("/matches")
            self.assertEqual(response.status_code, 500)
            self.assertEqual(response.get_json(), {
                "success": False,
                "message": "Database is unavailable. Please try again.",
            })
        finally:
            app.config["DATABASE_PATH"] = valid_path
        self.assertEqual(self.client.get("/matches").status_code, 200)


if __name__ == "__main__":
    unittest.main()
