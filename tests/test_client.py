"""Check the required HTTP formats and recoverable client errors."""

import io
import json
import socket
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs

import client


def json_reply(result):
    return io.BytesIO(json.dumps(result).encode("utf-8"))


class HttpClientTests(unittest.TestCase):
    @patch("client.urlopen")
    def test_get_uses_fixed_address_and_five_second_timeout(self, open_url):
        expected = {"success": True, "matches": []}
        open_url.return_value = json_reply(expected)
        self.assertEqual(client.get_matches(), expected)
        open_url.assert_called_once_with(client.BASE_URL + "/matches", data=None, timeout=5)

    @patch("client.urlopen")
    def test_post_encodes_unicode_form_values_as_bytes(self, open_url):
        open_url.return_value = json_reply({"success": True, "match_id": 7})
        values = {"name": "Players' match", "city": "الرياض"}
        self.assertTrue(client.add_match(values)["success"])
        arguments = open_url.call_args
        self.assertEqual(arguments.args[0], client.BASE_URL + "/matches/add")
        body = arguments.kwargs["data"]
        self.assertIsInstance(body, bytes)
        self.assertEqual(parse_qs(body.decode("utf-8")), {
            "name": ["Players' match"], "city": ["الرياض"],
        })
        self.assertEqual(arguments.kwargs["timeout"], 5)

    @patch("client.urlopen")
    def test_delete_uses_post_even_without_fields(self, open_url):
        open_url.return_value = json_reply({"success": True, "message": "Deleted."})
        client.delete_match(7)
        open_url.assert_called_once_with(
            client.BASE_URL + "/matches/7/delete", data=b"", timeout=5
        )

    @patch("client.urlopen")
    def test_city_filter_is_trimmed_and_url_encoded(self, open_url):
        open_url.return_value = json_reply({"success": True, "matches": []})
        client.get_matches("  Al Khobar & East  ")
        requested_url = open_url.call_args.args[0]
        query = requested_url.split("?", 1)[1]
        self.assertEqual(parse_qs(query), {"city": ["Al Khobar & East"]})
        self.assertIsNone(open_url.call_args.kwargs["data"])

    @patch("client.urlopen")
    def test_http_400_and_404_preserve_flask_json_messages(self, open_url):
        for code, message in [(400, "Name is required."), (404, "Match not found.")]:
            with self.subTest(code=code):
                expected = {"success": False, "message": message}
                open_url.side_effect = HTTPError(
                    client.BASE_URL, code, message, None, json_reply(expected)
                )
                self.assertEqual(client.update_match(7, {}), expected)

    @patch("client.urlopen")
    def test_non_json_http_error_has_a_clear_fallback(self, open_url):
        open_url.side_effect = HTTPError(
            client.BASE_URL, 500, "Server error", None, io.BytesIO(b"<html>Error</html>")
        )
        result = client.get_matches()
        self.assertFalse(result["success"])
        self.assertIn("HTTP 500", result["message"])

    @patch("client.urlopen", side_effect=socket.timeout("Too slow"))
    def test_direct_socket_timeout(self, open_url):
        self.assertEqual(client.get_matches(), {
            "success": False, "message": client.TIMEOUT_MESSAGE,
        })

    @patch("client.urlopen", side_effect=URLError(socket.timeout("Too slow")))
    def test_wrapped_socket_timeout(self, open_url):
        self.assertEqual(client.get_matches(), {
            "success": False, "message": client.TIMEOUT_MESSAGE,
        })

    @patch("client.urlopen")
    def test_connection_failures_are_returned_without_crashing(self, open_url):
        for error in [URLError("Connection refused"), ConnectionResetError("Reset")]:
            with self.subTest(error=type(error).__name__):
                open_url.side_effect = error
                self.assertEqual(client.get_matches(), {
                    "success": False, "message": client.CONNECTION_MESSAGE,
                })

    @patch("client.urlopen")
    def test_invalid_json_and_unexpected_results_are_reported(self, open_url):
        for body in [b"not JSON", b"\xff", b"[]", b'{"message": "missing success"}']:
            with self.subTest(body=body):
                open_url.return_value = io.BytesIO(body)
                self.assertEqual(client.get_matches(), {
                    "success": False, "message": client.REPLY_MESSAGE,
                })

    @patch("client.urlopen")
    def test_same_client_functions_can_retry_after_a_connection_failure(self, open_url):
        expected = {"success": True, "matches": []}
        open_url.side_effect = [URLError("Connection refused"), json_reply(expected)]
        self.assertFalse(client.get_matches()["success"])
        self.assertEqual(client.get_matches(), expected)


if __name__ == "__main__":
    unittest.main()
