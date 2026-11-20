"""Verify UTF-8 files, real thread execution, and clear report failures."""

import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

import report_helper


class ReportHelperTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.output_path = Path(self.folder.name) / "reports" / "matches.txt"
        self.match = {
            "id": 7,
            "name": "Players' evening match",
            "city": "الرياض",
            "court": "Court 1",
            "match_date": "2026-12-01",
            "skill_level": "Beginner",
        }
        self.request_patcher = patch("report_helper.client.send_request")
        self.request = self.request_patcher.start()
        self.request.return_value = {"success": True, "matches": [self.match]}

    def tearDown(self):
        self.request_patcher.stop()
        self.folder.cleanup()

    def test_report_includes_all_fields_and_utf8_text(self):
        result = report_helper.save_report(self.output_path)
        self.assertTrue(result["success"])
        self.request.assert_called_once_with("/matches/export")
        content = self.output_path.read_text(encoding="utf-8")
        self.assertIn("Padel Match Planner Report", content)
        self.assertIn("Total saved matches: 1", content)
        for value in self.match.values():
            self.assertIn(str(value), content)
        self.assertIn("الرياض".encode("utf-8"), self.output_path.read_bytes())

    def test_empty_list_writes_a_useful_report(self):
        self.request.return_value = {"success": True, "matches": []}
        self.assertTrue(report_helper.save_report(self.output_path)["success"])
        content = self.output_path.read_text(encoding="utf-8")
        self.assertIn("Total saved matches: 0", content)
        self.assertIn("No saved matches.", content)

    @patch("report_helper.threading.Thread")
    def test_failed_request_keeps_the_previous_report_and_starts_no_thread(self, worker):
        self.output_path.parent.mkdir()
        self.output_path.write_text("Previous report", encoding="utf-8")
        self.request.return_value = {"success": False, "message": "Cannot connect to the server."}
        result = report_helper.save_report(self.output_path)
        self.assertFalse(result["success"])
        self.assertIn("Cannot connect", result["message"])
        self.assertEqual(self.output_path.read_text(encoding="utf-8"), "Previous report")
        worker.assert_not_called()

    @patch("report_helper.threading.Thread")
    def test_invalid_export_data_is_reported_without_creating_a_file(self, worker):
        self.request.return_value = {"success": True, "matches": "invalid"}
        result = report_helper.save_report(self.output_path)
        self.assertFalse(result["success"])
        self.assertIn("Invalid match data", result["message"])
        self.assertFalse(self.output_path.exists())
        worker.assert_not_called()

    def test_file_write_error_is_reported_from_the_worker(self):
        # A directory cannot be opened as a text file.
        result = report_helper.save_report(Path(self.folder.name))
        self.assertFalse(result["success"])
        self.assertIn("Could not save report", result["message"])

    def test_parent_folder_error_is_reported_from_the_worker(self):
        blocker = Path(self.folder.name) / "existing_file"
        blocker.write_text("A file, not a folder", encoding="utf-8")
        result = report_helper.save_report(blocker / "matches.txt")
        self.assertFalse(result["success"])
        self.assertIn("Could not save report", result["message"])

    def test_one_real_worker_finishes_before_save_report_returns(self):
        worker_ids = []
        original_writer = report_helper.write_report
        original_thread = threading.Thread

        def record_worker(*arguments):
            worker_ids.append(threading.get_ident())
            original_writer(*arguments)

        with patch("report_helper.write_report", side_effect=record_worker):
            with patch("report_helper.threading.Thread", wraps=original_thread) as worker:
                result = report_helper.save_report(self.output_path)
                worker.assert_called_once()
        self.assertTrue(result["success"])
        self.assertEqual(len(worker_ids), 1)
        self.assertNotEqual(worker_ids[0], threading.get_ident())
        self.assertIn("Total saved matches: 1", self.output_path.read_text(encoding="utf-8"))

    @patch("report_helper.save_report")
    @patch("builtins.print")
    def test_main_prints_the_result_and_uses_a_matching_exit_status(self, print_message, save_report):
        for success, expected_status in [(True, 0), (False, 1)]:
            with self.subTest(success=success):
                save_report.return_value = {"success": success, "message": "Report result"}
                self.assertEqual(report_helper.main(), expected_status)
                print_message.assert_called_with("Report result")


if __name__ == "__main__":
    unittest.main()
