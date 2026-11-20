"""HTTP requests used by the Tkinter window. No database access belongs here."""

import json
import socket
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen


BASE_URL = "http://127.0.0.1:5050"
CONNECTION_MESSAGE = "Cannot connect to the server. Start Flask, then try again."
TIMEOUT_MESSAGE = "The server took too long to respond. Please try again."
REPLY_MESSAGE = "The server returned an invalid reply. Please try again."


def read_reply(reply):
    """Read Flask's UTF-8 JSON and check that it is a result dictionary."""
    result = json.loads(reply.read().decode("utf-8"))
    if not isinstance(result, dict) or not isinstance(result.get("success"), bool):
        return {"success": False, "message": REPLY_MESSAGE}
    return result


def send_request(path, values=None):
    """Use GET without values, or POST with form values; return a result dict."""
    body = None
    if values is not None:
        # Even an empty dictionary becomes bytes, so deletion uses POST.
        body = urlencode(values).encode("utf-8")

    try:
        with urlopen(BASE_URL + path, data=body, timeout=5) as reply:
            return read_reply(reply)
    except HTTPError as error:
        # HTTPError is a kind of URLError, so it must be caught first.
        try:
            with error:
                return read_reply(error)
        except (json.JSONDecodeError, UnicodeDecodeError, OSError):
            return {
                "success": False,
                "message": f"The server rejected the request (HTTP {error.code}).",
            }
    except URLError as error:
        # Some connection timeouts are wrapped inside URLError.
        if isinstance(error.reason, socket.timeout):
            return {"success": False, "message": TIMEOUT_MESSAGE}
        return {"success": False, "message": CONNECTION_MESSAGE}
    except socket.timeout:
        return {"success": False, "message": TIMEOUT_MESSAGE}
    except (json.JSONDecodeError, UnicodeDecodeError):
        return {"success": False, "message": REPLY_MESSAGE}
    except OSError:
        return {"success": False, "message": CONNECTION_MESSAGE}


def get_matches(city=""):
    """Read matches, optionally filtering by a safely encoded city name."""
    path = "/matches"
    city = city.strip()
    if city:
        path += "?" + urlencode({"city": city})
    return send_request(path)


def add_match(values):
    return send_request("/matches/add", values)


def update_match(match_id, values):
    return send_request(f"/matches/{match_id}/edit", values)


def delete_match(match_id):
    return send_request(f"/matches/{match_id}/delete", {})
