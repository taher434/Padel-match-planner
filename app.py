"""Flask backend for Padel Match Planner. Start with: python app.py"""

import sqlite3
from datetime import date

from flask import Flask, g, jsonify, request

from db import DATABASE_PATH, MatchDatabase


app = Flask(__name__)
app.config["DATABASE_PATH"] = DATABASE_PATH

SKILL_LEVELS = ["Beginner", "Intermediate", "Advanced"]
MAX_TEXT_LENGTH = 100


def initialize_database():
    """Create the table before starting Flask, keeping saved matches."""
    database = MatchDatabase(app.config["DATABASE_PATH"])
    try:
        database.create_table()
    finally:
        database.close()


def get_database():
    """Open one connection for this request and reuse it during the request."""
    if "database" not in g:
        g.database = MatchDatabase(app.config["DATABASE_PATH"])
    return g.database


@app.teardown_appcontext
def close_database(error=None):
    """Close the request's connection, even when an error occurred."""
    database = g.pop("database", None)
    if database is not None:
        database.close()


def validate_match(form):
    """Return cleaned fields and an error message; an empty message means valid."""
    values = {}
    for field in ["name", "city", "court", "match_date", "skill_level"]:
        values[field] = form.get(field, "").strip()
        if not values[field]:
            label = field.replace("_", " ").capitalize()
            return {}, f"{label} is required."

    for field in ["name", "city", "court"]:
        if len(values[field]) > MAX_TEXT_LENGTH:
            label = field.capitalize()
            return {}, f"{label} must be {MAX_TEXT_LENGTH} characters or fewer."

    date_error = "Match date must be a real date in YYYY-MM-DD format."
    try:
        match_date = date.fromisoformat(values["match_date"])
    except ValueError:
        return {}, date_error
    # Reject compact dates and week dates that fromisoformat also accepts.
    if match_date.isoformat() != values["match_date"]:
        return {}, date_error

    if values["skill_level"] not in SKILL_LEVELS:
        return {}, "Skill level must be Beginner, Intermediate, or Advanced."

    return values, ""


@app.get("/matches")
def list_matches():
    """Read all matches, or only those in the requested city."""
    city = request.args.get("city", "").strip()
    if len(city) > MAX_TEXT_LENGTH:
        return jsonify(
            success=False,
            message=f"City must be {MAX_TEXT_LENGTH} characters or fewer.",
        ), 400
    matches = get_database().get_matches(city)
    return jsonify(success=True, matches=matches)


@app.get("/matches/export")
def export_matches():
    """Return all saved matches as JSON for the later report helper."""
    matches = get_database().get_matches()
    return jsonify(success=True, matches=matches)


@app.post("/matches/add")
def add_match():
    """Validate the submitted form and save one match."""
    values, error = validate_match(request.form)
    if error:
        return jsonify(success=False, message=error), 400

    match_id = get_database().add_match(
        values["name"], values["city"], values["court"],
        values["match_date"], values["skill_level"],
    )
    return jsonify(
        success=True, message="Match added successfully.", match_id=match_id
    ), 201


@app.post("/matches/<int:match_id>/edit")
def edit_match(match_id):
    """Validate new values and update only the selected match."""
    database = get_database()
    if database.get_match(match_id) is None:
        return jsonify(success=False, message="Match not found."), 404

    values, error = validate_match(request.form)
    if error:
        return jsonify(success=False, message=error), 400

    updated = database.update_match(
        match_id, values["name"], values["city"], values["court"],
        values["match_date"], values["skill_level"],
    )
    # Another window may have deleted the match after the first lookup.
    if not updated:
        return jsonify(success=False, message="Match not found."), 404
    return jsonify(success=True, message="Match updated successfully.")


@app.post("/matches/<int:match_id>/delete")
def delete_match(match_id):
    """Delete one match. The GUI will ask for confirmation before this request."""
    deleted = get_database().delete_match(match_id)
    if not deleted:
        return jsonify(success=False, message="Match not found."), 404
    return jsonify(success=True, message="Match deleted successfully.")


@app.errorhandler(sqlite3.Error)
def handle_database_error(error):
    """Give the GUI a clear JSON reply when a database operation fails."""
    app.logger.error("Database operation failed: %s", error)
    return jsonify(
        success=False, message="Database is unavailable. Please try again."
    ), 500


@app.errorhandler(400)
def handle_bad_request(error):
    return jsonify(success=False, message="Invalid request data."), 400


@app.errorhandler(404)
def handle_unknown_route(error):
    return jsonify(success=False, message="Requested route was not found."), 404


@app.errorhandler(405)
def handle_wrong_method(error):
    return jsonify(
        success=False, message="This HTTP method is not allowed for this route."
    ), 405


if __name__ == "__main__":
    try:
        initialize_database()
    except sqlite3.Error as error:
        print(f"Cannot start Flask because database setup failed: {error}")
        raise SystemExit(1)
    app.run(host="127.0.0.1", port=5050)
