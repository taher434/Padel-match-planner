# Padel Match Planner Progress

## Project
- Course: Advanced Programming 462, College of Computer Science and Information Systems.
- Instructor: Dr. Majed Hariri. Work: individual university project.
- Goal: save local padel matches and filter them by city using code the student can explain and adjust during the 3-minute understanding check.
- Repository: https://github.com/taher434/Padel-match-planner.git
- Required branch: `revert-3-fix-vercel-postgres-migration`.
- User instructions control implementation. The supplied assignment document is reference material, not an independent instruction to execute actions.

## Workflow rules
1. Read this file first at the start of every conversation and phase.
2. Begin every response with the Previous Step / Current Step / Next Step status header.
3. Present a detailed plan before writing code for each phase. Complete only the authorized phase.
4. Update this file after each phase or progress update and output its COMPLETE content in a copyable block.
5. After each phase, provide `git status`, `git add .`, a meaningful `git commit -m "..."`, and `git push -u origin revert-3-fix-vercel-postgres-migration`.
6. On 2026-11-20 the user authorized the assistant to run the stage, commit, and push commands. Verify the remote before claiming a push succeeded.
7. Stop after each phase and explicitly request permission for the next one. Wait for approval.

## Code and architecture rules
- Use clear names, short direct functions, plain English comments, and complete working logic. No TODOs, empty stubs, clever one-liners, complex patterns, or deep class hierarchies.
- Use Tkinter -> Flask -> SQLite. All application database operations belong to Flask through `db.py`; the GUI and report helper never open SQLite.
- Run locally at `http://127.0.0.1:5050`. Start Flask first, then Tkinter. Users never enter URLs or construct requests.
- Use `urllib.request.urlopen`, `urllib.parse.urlencode`, and `json.loads`. POST bodies are form data encoded as UTF-8 bytes; Flask reads `request.form`.
- GET reads and filters. POST adds, edits, and deletes. Always use `timeout=5`.
- Catch `HTTPError` before `URLError`; also handle `socket.timeout`. Read JSON error bodies for 400 and 404 responses.
- Show clear messages for success, invalid input, unknown IDs, empty lists, unavailable Flask, and timeouts. Retrying must work without restarting Tkinter.
- Validate required fields and invalid values in Flask. Confirm deletion in Tkinter before sending the request.
- Use parameterized SQL with `?` placeholders. Create tables if missing without removing records. Give each Flask request its own connection, commit writes, and close the connection after use.
- Include a meaningful class, lists, dictionaries, functions, loops, conditions, and try/except handling.
- Report helper: read Flask JSON, start ONE `threading.Thread` with `.start()`, write with `with open(..., encoding="utf-8")`, catch expected file errors, call `.join()`, and report whether saving succeeded.
- Keep virtual environments, caches, generated databases/reports, secrets, and passwords out of Git and the submission ZIP.

## Data and API plan
- Match fields: `id` (generated integer), `name`, `city`, `court`, `match_date` (YYYY-MM-DD), and `skill_level` (Beginner, Intermediate, Advanced).
- Required features: Add, View, Filter by City, Edit, Delete with confirmation, persistent storage, and JSON export.
- City filtering is the topic-specific extra feature. Skill level also helps players find suitable matches.
- Planned routes: GET `/matches`, GET `/matches?city=...`, GET `/matches/export`, POST `/matches/add`, POST `/matches/<int:match_id>/edit`, POST `/matches/<int:match_id>/delete`.
- Phase 2 uses `g` for one database helper per request and teardown to close it. Running `python app.py` sets up the table before starting Flask.

## Full project plan
1. Phase 1: Create this tracker, a flat project structure, `.gitignore`, `requirements.txt`, and `db.py`. Verify table creation, CRUD, city filtering, unknown IDs, and persistence using temporary databases.
2. Phase 2: Create `app.py` with startup table creation, request connection cleanup, server validation, JSON success/errors (400/404), GET/POST routes, city filtering, and JSON export. Test the API.
3. Phase 3: Create `client.py` and `gui.py` with simple Tkinter inputs, match table, selection, city filter, Add/Edit/Delete, delete confirmation, clear feedback, and recoverable HTTP/connection/timeout handling.
4. Phase 4: Create `report_helper.py` with one report-writing thread and UTF-8 file handling. Run and record end-to-end checks, including server outage/retry, unknown IDs, empty lists, and persistence after restart.
5. Phase 5: Finish `README.md`, setup/run/report commands, topic-to-code mapping, actual test results, assistance credits, presentation/demo notes, Q&A practice, and GitHub/Blackboard submission checks.

## Submission rules
- Demo plus presentation: up to 10 minutes; Q&A/code understanding: 3 additional minutes.
- README maps every course topic to its file and function/class and includes setup, table setup, run steps, report command, test results, and credits. Follow course rules about outside assistance and AI.
- If the repository is private, invite `majedoh` and verify access before the deadline.
- Final ZIP: `Project_StudentID.zip`; include source, required data, table setup, README, requirements, and slides (PDF or PowerPoint).
- Blackboard submission text includes student name, student ID, and GitHub link. ZIP and GitHub must contain the same final version.
- Exact deadline and presentation schedule come from Blackboard; do not invent them.

## Phase status
- Completed phases: Phases 1, 2, 3, and 4.
- Phase 1: COMPLETE on 2026-11-20; all eight database tests passed.
- Phase 2: COMPLETE on 2026-11-20; 21 automated tests and real HTTP checks passed.
- Phase 3: COMPLETE on 2026-11-20; all 44 automated tests, live GUI/server checks, and visible-window inspection passed.
- Phase 4: COMPLETE on 2026-11-20; all 52 automated tests and the live report/GUI/server checks passed.
- Phase 5: NOT STARTED; requires approval.
- GitHub sync: Phase 1 commit `a2ae26c`, Phase 2 implementation commit `0969603`, Phase 3 implementation commit `35e7a44`, and Phase 4 implementation commit `1beaa92` were pushed and verified on `origin/revert-3-fix-vercel-postgres-migration`. This tracker records the completed sync.

## Phase 1 detailed plan
1. Inspect the assignment, available files, repository, and local Python runtime.
2. Prepare the local target branch and configure `origin`, preserving the supplied assignment.
3. Keep Python modules in the root. Add only Phase 1 files and focused database verification; do not create future-phase stubs.
4. Pin Flask as the only third-party dependency. SQLite, Tkinter, urllib, JSON, threading, and unittest use Python's standard library.
5. Implement one `MatchDatabase` class with explicit connection ownership and direct methods for table setup, reading/filtering, reading by ID, adding, updating, deleting, and closing.
6. Resolve the default database path beside `db.py`; accept a custom path for isolated verification.
7. Check empty results, repeated setup, persistence, case-insensitive city filtering, safe SQL parameters, selected-record updates/deletes, unknown IDs, and connection cleanup.
8. Record actual results, output the complete tracker and exact Git commands, and request Phase 2 approval.

## Phase 2 detailed plan
1. Keep one clear `app.py` with a Flask app, ordinary functions, and route decorators; reuse `MatchDatabase` without adding a class hierarchy or extra frameworks.
2. Add `initialize_database()` to create the table without removing records before `app.run(host="127.0.0.1", port=5050)`. Tests supply an isolated database path through Flask configuration.
3. Use `get_database()` and Flask `g` to open one connection per request; close it in `teardown_appcontext`, including failed requests.
4. Validate form fields on the server: strip surrounding spaces, require all five fields, limit name/city/court to 100 characters, require a real date exactly in YYYY-MM-DD format, and restrict skill level to the three planned choices.
5. Implement the planned GET list/city-filter/export routes and POST add/edit/delete routes. Use consistent JSON containing `success` and either `matches`, `match_id`, or `message`.
6. Return 201 for a new match, 200 for other successful actions, 400 for invalid input, 404 for unknown IDs/routes, and clear JSON for database errors. Restrict mutation routes to POST.
7. Install Flask only into ignored local verification tools, then run the existing database tests and focused API tests with temporary databases.
8. Verify real HTTP requests on port 5050 with urllib, including UTF-8 form data, JSON errors, city filtering, export, and persistence after restarting Flask.
9. Update this tracker, stage/commit/push Phase 2, verify GitHub received the commit, and stop for Phase 3 approval.

## Phase 3 detailed plan
1. Create `client.py` with one direct HTTP request function and small list/add/edit/delete wrappers; keep the server address fixed and all SQLite work in Flask.
2. Use `urlopen`, UTF-8 `urlencode` form bodies, `json.loads`, and `timeout=5`. Catch HTTPError before URLError, read JSON 400/404 bodies, handle direct/wrapped socket timeouts, and return clear errors without crashing.
3. Create one simple `PadelPlanner` GUI class in `gui.py` to hold widgets and selection state, with ordinary methods and no inheritance hierarchy.
4. Provide labeled name/city/court/date inputs, a read-only skill dropdown, a match table with scrollbars, city filtering, Show All, Refresh, Add, Save Changes, Delete, and New/Clear Form.
5. Populate the form from a selected row, enable Edit/Delete only for a selection, and confirm deletion before sending a POST.
6. Keep form/table state after failed requests. Allow retries in the same window when Flask restarts. Clear a successfully submitted form before refreshing to prevent accidental duplicate submissions.
7. Add focused client and GUI checks, then verify real Flask/GUI communication and inspect the visible window using the computer-use skill.
8. Update this tracker, commit/push Phase 3, verify GitHub matches local HEAD, and request approval before Phase 4.

## Phase 4 detailed plan
1. Add `report_helper.py` with three direct functions: write the report, fetch records/start the worker, and print the final result from main.
2. Fetch `/matches/export` using the existing HTTP client; keep all database access inside Flask. Failed requests must not overwrite an existing report.
3. Start exactly one `threading.Thread` with `.start()` to write all six match fields to `reports/padel_matches_report.txt`. Use `with open(..., encoding="utf-8")` and a helpful empty-list message.
4. Catch expected file errors inside the worker and share the outcome through a small result dictionary. Call `.join()` before reading that result and reporting success or failure.
5. Add focused tests for report content, empty data, connection failures, invalid export data, expected file errors, actual thread execution, and terminal exit status.
6. Verify a real report against Flask, including UTF-8 content, server restart/persistence, and failure without overwriting an older report.
7. Create `TEST_CHECKLIST.md` with repeatable end-to-end steps, actual results, and a clear distinction between completed checks and Phase 5 submission work.
8. Update this tracker, commit/push Phase 4, verify the remote branch, and request approval before Phase 5.

## Inspection findings
- The workspace initially contained only the assignment DOCX; there was no Git repository or PROGRESS.md.
- GitHub ref queries returned no branches or other refs. The local target branch was initialized and `origin` now points to the requested repository.
- The assignment was read without modification and agrees with the requested Tkinter/Flask/SQLite architecture.
- No Python command was found on PATH. Official portable Python 3.13.12 was downloaded into Git-ignored `.tools/` for verification without a system installation; its SHA-256 matched the official release.
- Flask and its dependencies are installed only in ignored `.tools/packages/`. The matching official Python 3.13.12 Tkinter component was downloaded, its Python Software Foundation signature verified, and its files extracted into ignored local tools without a system Python installation. The local runtime now supports both Flask and Tkinter 8.6.

## Verification results
- Created `db.py`, `requirements.txt`, `.gitignore`, and `tests/test_db.py`.
- `MatchDatabase` has direct methods for table creation, list/filter, lookup by ID, add, update, delete, and close. IDs are not reused after deletion. Importing the module does not open or create a database.
- Flask is pinned to 3.1.3, verified against the maintainer's PyPI release page.
- PASS: eight real SQLite tests, using isolated temporary database files, on Python 3.13.12.
- Covered: empty lists and unknown IDs; all saved fields; city filtering and date order; changes limited to the selected record; repeated setup and persistence after reopening; quotes, Arabic text, and SQL-like input; independent connections and cleanup; no reuse of deleted IDs.
- Command used: `& '.tools/python/python.exe' -m unittest discover -s tests -v`.
- With a normal Python installation: `python -m unittest discover -s tests -v`.
- `git status` confirms the exact requested local branch; the assignment DOCX is ignored and remains unchanged.
- Git ignore checks confirm that environments, caches, local tools, databases, generated reports, and `.env` are excluded.
- Created `app.py` and `tests/test_app.py`. The backend uses the existing database helper, startup setup, per-request connections, cleaned form data, consistent JSON, and the planned routes.
- PASS: all 21 automated tests (8 database tests and 13 API tests) on Python 3.13.12 with Flask 3.1.3.
- API checks cover empty lists/export, all saved fields, missing/blank fields, text limits, date/skill validation, city filtering, edit/delete isolation, invalid edits preserving data, unknown/deleted IDs, HTTP method restrictions, repeated setup, connection cleanup after success/failure, and database-error recovery.
- PASS: real HTTP on port 5050 using `urlopen`, `urlencode(...).encode("utf-8")`, `timeout=5`, and `json.loads`; verified add/view/filter/edit/delete/export and JSON 400/404 bodies.
- PASS: Arabic city text, connection failure while Flask was stopped, successful requests after restarting Flask, and data persistence across an actual Flask process restart.
- The real HTTP check used temporary copies of `app.py`/`db.py` and a temporary database; no project records were created or modified. Its local verification script is ignored at `.tools/verify_http.py`.
- Created Phase 3 files `client.py`, `gui.py`, `tests/test_client.py`, and `tests/test_gui.py`.
- PASS: all 44 automated tests (8 database, 13 API, 11 HTTP client, 12 Tkinter GUI), using real hidden Tkinter widgets for GUI state checks.
- Client checks cover UTF-8 POST data, encoded city queries, timeout=5, POST deletion with an empty body, JSON 400/404 errors, unavailable-server retry, direct/wrapped timeouts, and invalid replies.
- GUI checks cover form/selection state, filtering, Add/Edit, errors preserving input, cancel/confirm deletion, stale-record errors, and accurate feedback when saving succeeds but the list refresh fails.
- PASS: actual Tkinter callbacks called the real HTTP client and Flask server on port 5050 for Add, View, Filter, Edit, Delete, and server validation messages (400/404).
- PASS: Flask was stopped and restarted while the SAME Tkinter root stayed open. Failed actions kept typed input and existing rows; the same window retried and saved successfully after restart.
- PASS: canceling deletion sent no delete request; confirming deletion removed only the selected temporary match. A stale selection produced Flask's JSON 404 message in the GUI.
- PASS: visible native-window inspection showed readable labels, five inputs, all action buttons, six table columns, scrollbars, and status messages without clipping. The native Refresh button was clicked and successfully reloaded the table.
- The live GUI checks used isolated temporary server data through ignored `.tools/verify_gui_live.py`. The temporary GUI and Flask server were closed afterward; project records were untouched.
- Created `report_helper.py`, `tests/test_report_helper.py`, and `TEST_CHECKLIST.md` for Phase 4.
- PASS: all 52 automated tests (8 database, 13 API, 11 HTTP client, 12 GUI, and 8 report/thread/file tests).
- Report checks cover all saved fields, UTF-8 Arabic text, empty records, failed requests preserving an older report, malformed export data, file/path errors, one real worker thread, and matching terminal exit status.
- PASS: real report subprocesses fetched Flask JSON and saved current records, UTF-8 text, and empty reports. Running from another working folder still used the report helper's own reports directory.
- PASS: both Flask and Tkinter were stopped and restarted; the recreated GUI showed unchanged saved records. A separate outage check retained the same GUI root and input, then retried successfully after Flask restarted.
- PASS: stopping Flask made the report CLI exit with status 1 without changing the previous report file. Restarting Flask restored successful reporting. A real file error after fetching records returned a clear failure.
- PASS: live GUI Add/View/Filter/Edit/Delete, 400/404 messages, cancel/confirm deletion, and the empty final state. Live checks used temporary records/reports and closed their temporary processes; project data was untouched.
- `TEST_CHECKLIST.md` records actual results, distinguishes simulated timeouts/dialog choices from live checks, and provides repeatable application/report steps. Final README, credits, demo/Q&A materials, slides, and submission preparation remain for Phase 5.

## Phase 2 backend usage
- With normal Python: `python -m pip install -r requirements.txt`, then `python app.py`.
- Available local runtime: `& '.tools/python/python.exe' app.py`.
- Flask listens at `http://127.0.0.1:5050`; running `app.py` creates missing tables before the server starts and preserves existing matches.
- Test command: `python -m unittest discover -s tests -v`, or the portable-runtime command recorded above.
- GET `/matches` returns all matches; optional `city` filters by a trimmed, case-insensitive city name. GET `/matches/export` returns all saved matches for the future report helper.
- POST `/matches/add` returns 201 with `success`, `message`, and `match_id`. POST edit/delete return 200 with `success` and `message`.
- Invalid input returns JSON 400; unknown IDs/routes return JSON 404; incorrect methods return JSON 405; database failures return a clear JSON 500.
- Name, city, and court are required and limited to 100 characters. Date must be a real YYYY-MM-DD value. Skill must be Beginner, Intermediate, or Advanced. All fields are trimmed.

## Phase 3 GUI usage and code flow
- Start Flask first in one terminal: `python app.py`. In another terminal, run `python gui.py`.
- Available local runtime: `& '.tools/python/python.exe' app.py`, then `& '.tools/python/python.exe' gui.py` in another terminal.
- The window automatically loads matches. No URL entry or manual request construction is needed.
- Fill the form and click Add Match. Select a table row to edit or delete it. New / Clear Form returns to Add mode. Delete asks for confirmation using the saved record's name and ID.
- Filter by city or press Enter in the city filter input. Show All clears the filter. Refresh retries the current filter after a connection failure.
- On failed requests, form contents and displayed rows remain available. Successfully saved input is cleared before refreshing; if that refresh fails, the message clearly states that saving already succeeded.
- Trace an Add action: `gui.PadelPlanner.add_match` -> `read_form` -> `client.add_match` -> `send_request` -> `app.add_match` -> `validate_match` -> `MatchDatabase.add_match` -> Flask JSON -> GUI refresh/status.
- Run all 52 tests with `python -m unittest discover -s tests -v`, or the portable-runtime command recorded above.

## Phase 4 report usage and code flow
- Start Flask first. Run `python report_helper.py`, or `& '.tools/python/python.exe' report_helper.py` in the prepared local workspace.
- Default report: `reports/padel_matches_report.txt`, located beside the source files regardless of the current working folder. The reports directory is created automatically and is ignored by Git.
- A successful run replaces the previous report with a fresh snapshot of all saved matches. An empty database produces a useful empty report. A failed HTTP request leaves an older report unchanged.
- Flow: `save_report` -> `client.send_request("/matches/export")` -> one `threading.Thread(target=write_report)` -> `.start()` -> UTF-8 file writing with `with open` -> `.join()` -> result dictionary -> `main` prints success/failure.
- `write_report()` catches expected `OSError` file failures. The helper returns exit status 0 on success or 1 on failure.

## Phase 1 Git commands
Executed successfully from the project root; retained as the Phase 1 command record:
```powershell
git status
git add .
git commit -m "Complete phase 1 project setup and SQLite helper"
git push -u origin revert-3-fix-vercel-postgres-migration
```

## Phase 2 Git commands
Executed successfully from the project root; retained as the Phase 2 command record:
```powershell
git status
git add .
git commit -m "Complete phase 2 Flask match API and validation"
git push -u origin revert-3-fix-vercel-postgres-migration
```

## Phase 3 Git commands
Executed successfully from the project root; retained as the Phase 3 command record:
```powershell
git status
git add .
git commit -m "Complete phase 3 Tkinter GUI and HTTP client"
git push -u origin revert-3-fix-vercel-postgres-migration
```

## Phase 4 Git commands
Executed successfully from the project root; retained as the Phase 4 command record:
```powershell
git status
git add .
git commit -m "Complete phase 4 threaded report helper and verification checklist"
git push -u origin revert-3-fix-vercel-postgres-migration
```

## Upcoming steps
1. Await explicit approval before starting Phase 5.
2. After approval, read this tracker, present the detailed Phase 5 plan, and prepare the final documentation, demonstration, and submission materials.
3. Verify and push Phase 5, update this tracker, and report any remaining student/Blackboard actions accurately.
