"""Fetch saved matches from Flask and write a report using one worker thread."""

import threading
from pathlib import Path

import client


REPORT_PATH = Path(__file__).resolve().parent / "reports" / "padel_matches_report.txt"


def write_report(matches, output_path, result):
    """Write UTF-8 text in the worker and record whether saving succeeded."""
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as report:
            report.write("Padel Match Planner Report\n")
            report.write(f"Total saved matches: {len(matches)}\n\n")
            if not matches:
                report.write("No saved matches.\n")
            for match in matches:
                report.write(f"ID: {match['id']}\n")
                report.write(f"Name: {match['name']}\n")
                report.write(f"City: {match['city']}\n")
                report.write(f"Court: {match['court']}\n")
                report.write(f"Date: {match['match_date']}\n")
                report.write(f"Skill level: {match['skill_level']}\n\n")
        result["success"] = True
        result["message"] = f"Report saved successfully: {output_path}"
    except OSError as error:
        result["success"] = False
        result["message"] = f"Could not save report: {error}"


def save_report(output_path=REPORT_PATH):
    """Fetch records, start one writer thread, and wait for its result."""
    response = client.send_request("/matches/export")
    if not response["success"]:
        return {"success": False, "message": "Report was not saved. " + response["message"]}

    matches = response.get("matches")
    if not isinstance(matches, list):
        return {"success": False, "message": "Report was not saved. Invalid match data received."}

    output_path = Path(output_path)
    result = {"success": False, "message": "Report was not saved."}
    worker = threading.Thread(target=write_report, args=(matches, output_path, result))
    worker.start()
    # join waits until the worker finishes, so the result below is ready.
    worker.join()
    return result


def main():
    result = save_report()
    print(result["message"])
    if result["success"]:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
