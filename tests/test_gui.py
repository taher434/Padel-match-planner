"""Check real Tkinter widgets and callbacks without showing modal dialogs."""

import tkinter as tk
import unittest
from unittest.mock import patch

from gui import PadelPlanner


class PlannerGuiTests(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.planner = PadelPlanner(self.root)
        self.match = {
            "id": 7,
            "name": "Evening match",
            "city": "Riyadh",
            "court": "Court 1",
            "match_date": "2026-12-01",
            "skill_level": "Beginner",
        }
        self.get_patcher = patch("gui.client.get_matches")
        self.get_matches = self.get_patcher.start()
        self.get_matches.return_value = {"success": True, "matches": []}
        self.error_patcher = patch("gui.messagebox.showerror")
        self.show_error = self.error_patcher.start()
        self.confirm_patcher = patch("gui.messagebox.askyesno", return_value=False)
        self.confirm = self.confirm_patcher.start()

    def tearDown(self):
        self.root.destroy()
        self.confirm_patcher.stop()
        self.error_patcher.stop()
        self.get_patcher.stop()

    def select_saved_match(self):
        self.get_matches.return_value = {"success": True, "matches": [self.match]}
        self.planner.refresh_matches()
        self.planner.table.selection_set("7")
        self.planner.select_match()

    def fill_form(self):
        for field in self.planner.fields:
            self.planner.fields[field].set(self.match[field])

    def test_empty_list_has_clear_feedback_and_disabled_edit_buttons(self):
        self.assertTrue(self.planner.refresh_matches())
        self.assertEqual(self.planner.table.get_children(), ())
        self.assertIn("No matches found", self.planner.status.get())
        self.assertEqual(str(self.planner.edit_button["state"]), "disabled")
        self.assertEqual(str(self.planner.delete_button["state"]), "disabled")

    def test_selection_fills_form_and_clear_restores_new_match_mode(self):
        self.select_saved_match()
        self.assertEqual(self.planner.selected_id, 7)
        self.assertEqual(self.planner.fields["name"].get(), "Evening match")
        self.assertEqual(str(self.planner.add_button["state"]), "disabled")
        self.assertEqual(str(self.planner.edit_button["state"]), "normal")
        self.planner.clear_form()
        self.assertIsNone(self.planner.selected_id)
        self.assertEqual(self.planner.fields["name"].get(), "")
        self.assertEqual(str(self.planner.add_button["state"]), "normal")

    def test_filter_and_show_all_use_the_city_input(self):
        self.planner.city_filter.set("  Riyadh  ")
        self.planner.filter_matches()
        self.get_matches.assert_called_with("Riyadh")
        self.assertIn("City filter: Riyadh", self.planner.status.get())
        self.planner.show_all()
        self.get_matches.assert_called_with("")
        self.assertEqual(self.planner.city_filter.get(), "")

    @patch("gui.client.add_match")
    def test_add_sends_form_and_shows_success(self, add_match):
        self.fill_form()
        add_match.return_value = {"success": True, "message": "Match added successfully."}
        self.planner.add_match()
        expected = self.match.copy()
        del expected["id"]
        add_match.assert_called_once_with(expected)
        self.assertEqual(self.planner.fields["name"].get(), "")
        self.assertIn("Match added successfully", self.planner.status.get())

    @patch("gui.client.add_match")
    def test_invalid_add_keeps_form_and_displays_flask_message(self, add_match):
        self.fill_form()
        add_match.return_value = {"success": False, "message": "Name is required."}
        self.planner.add_match()
        self.assertEqual(self.planner.fields["name"].get(), self.match["name"])
        self.show_error.assert_called_once()
        self.assertEqual(self.planner.status.get(), "Name is required.")
        self.get_matches.assert_not_called()

    @patch("gui.client.update_match")
    def test_edit_uses_selected_record_id(self, update_match):
        self.select_saved_match()
        self.planner.fields["court"].set("Court 2")
        update_match.return_value = {"success": True, "message": "Match updated successfully."}
        self.planner.edit_match()
        arguments = update_match.call_args.args
        self.assertEqual(arguments[0], 7)
        self.assertEqual(arguments[1]["court"], "Court 2")
        self.assertIn("Match updated successfully", self.planner.status.get())

    @patch("gui.client.delete_match")
    @patch("gui.client.update_match")
    def test_missing_selection_does_not_send_edit_or_delete(self, update_match, delete_match):
        self.planner.edit_match()
        self.planner.delete_match()
        update_match.assert_not_called()
        delete_match.assert_not_called()
        self.confirm.assert_not_called()
        self.assertEqual(self.show_error.call_count, 2)

    @patch("gui.client.delete_match")
    def test_cancelled_delete_sends_no_request(self, delete_match):
        self.select_saved_match()
        self.planner.fields["name"].set("Unsaved name")
        self.planner.delete_match()
        delete_match.assert_not_called()
        self.assertIn("Evening match", self.confirm.call_args.args[1])
        self.assertNotIn("Unsaved name", self.confirm.call_args.args[1])
        self.assertEqual(self.planner.selected_id, 7)

    @patch("gui.client.delete_match")
    def test_confirmed_delete_sends_selected_id_and_clears_selection(self, delete_match):
        self.select_saved_match()
        self.confirm.return_value = True
        delete_match.return_value = {"success": True, "message": "Match deleted successfully."}
        self.get_matches.return_value = {"success": True, "matches": []}
        self.planner.delete_match()
        delete_match.assert_called_once_with(7)
        self.assertIsNone(self.planner.selected_id)
        self.assertEqual(self.planner.table.get_children(), ())
        self.assertIn("Match deleted successfully", self.planner.status.get())

    def test_failed_refresh_preserves_form_and_rows_then_same_window_recovers(self):
        self.select_saved_match()
        self.planner.fields["court"].set("Unsaved court")
        self.get_matches.return_value = {"success": False, "message": "Cannot connect to the server."}
        self.assertFalse(self.planner.refresh_matches())
        self.assertEqual(self.planner.table.get_children(), ("7",))
        self.assertEqual(self.planner.fields["court"].get(), "Unsaved court")
        self.assertEqual(self.planner.selected_id, 7)
        self.get_matches.return_value = {"success": True, "matches": [self.match]}
        self.assertTrue(self.planner.refresh_matches())
        self.assertEqual(self.planner.table.get_children(), ("7",))
        self.assertEqual(self.planner.root, self.root)

    @patch("gui.client.update_match")
    def test_stale_selection_shows_404_message_without_losing_form(self, update_match):
        self.select_saved_match()
        update_match.return_value = {"success": False, "message": "Match not found."}
        self.planner.edit_match()
        self.assertEqual(self.planner.status.get(), "Match not found.")
        self.assertEqual(self.planner.fields["name"].get(), "Evening match")

    @patch("gui.client.add_match")
    def test_saved_match_followed_by_refresh_failure_is_not_reported_as_unsaved(self, add_match):
        self.fill_form()
        add_match.return_value = {"success": True, "message": "Match added successfully."}
        self.get_matches.return_value = {"success": False, "message": "Cannot connect to the server."}
        self.planner.add_match()
        self.assertEqual(self.planner.fields["name"].get(), "")
        self.assertIn("Match added successfully", self.planner.status.get())
        self.assertIn("list could not refresh", self.planner.status.get())


if __name__ == "__main__":
    unittest.main()
