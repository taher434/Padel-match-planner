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
- Phase 2 will use `g` for one database helper per request and teardown to close it. Table setup runs when Flask starts.

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
- Completed phases: Phase 1.
- Phase 1: COMPLETE on 2026-11-20; all eight database tests passed.
- Phase 2: APPROVED by the user; starts after the Phase 1 push succeeds.
- Phases 3-5: NOT STARTED; require approval before each phase.
- GitHub sync: Phase 1 is ready to commit and push; assistant execution is authorized.

## Phase 1 detailed plan
1. Inspect the assignment, available files, repository, and local Python runtime.
2. Prepare the local target branch and configure `origin`, preserving the supplied assignment.
3. Keep Python modules in the root. Add only Phase 1 files and focused database verification; do not create future-phase stubs.
4. Pin Flask as the only third-party dependency. SQLite, Tkinter, urllib, JSON, threading, and unittest use Python's standard library.
5. Implement one `MatchDatabase` class with explicit connection ownership and direct methods for table setup, reading/filtering, reading by ID, adding, updating, deleting, and closing.
6. Resolve the default database path beside `db.py`; accept a custom path for isolated verification.
7. Check empty results, repeated setup, persistence, case-insensitive city filtering, safe SQL parameters, selected-record updates/deletes, unknown IDs, and connection cleanup.
8. Record actual results, output the complete tracker and exact Git commands, and request Phase 2 approval.

## Inspection findings
- The workspace initially contained only the assignment DOCX; there was no Git repository or PROGRESS.md.
- GitHub ref queries returned no branches or other refs. The local target branch was initialized and `origin` now points to the requested repository.
- The assignment was read without modification and agrees with the requested Tkinter/Flask/SQLite architecture.
- No Python command was found on PATH. Official portable Python 3.13.12 was downloaded into Git-ignored `.tools/` for verification without a system installation; its SHA-256 matched the official release.
- This portable runtime is a local verification tool. A full Python installation with pip and Tkinter is still needed for the later application phases.

## Verification results
- Created `db.py`, `requirements.txt`, `.gitignore`, and `tests/test_db.py`.
- `MatchDatabase` has direct methods for table creation, list/filter, lookup by ID, add, update, delete, and close. IDs are not reused after deletion. Importing the module does not open or create a database.
- Flask is pinned to 3.1.3, verified against the maintainer's PyPI release page.
- PASS: eight real SQLite tests, using isolated temporary database files, on Python 3.13.12.
- Covered: empty lists and unknown IDs; all saved fields; city filtering and date order; changes limited to the selected record; repeated setup and persistence after reopening; quotes, Arabic text, and SQL-like input; independent connections and cleanup; no reuse of deleted IDs.
- Command used: `& '.tools/python/python.exe' -m unittest discover -s tests -v`.
- With a normal Python installation: `python -m unittest discover -s tests -v`.
- `git status` confirms the exact requested local branch and the expected new files; the assignment DOCX is ignored and remains unchanged.
- Git ignore checks confirm that environments, caches, local tools, databases, generated reports, and `.env` are excluded.
- Flask routes, server validation, GUI behavior, and report output are not implemented or tested yet; they belong to later phases.

## Phase 1 Git commands
Run from the project root; the assistant is authorized to execute these commands:
```powershell
git status
git add .
git commit -m "Complete phase 1 project setup and SQLite helper"
git push -u origin revert-3-fix-vercel-postgres-migration
```

## Upcoming steps
1. Commit and push Phase 1 using the commands above, then verify the remote branch.
2. Phase 2 is approved. Present its detailed plan and implement only the Flask backend after the Phase 1 push succeeds.
3. Verify and push Phase 2, update this tracker, and request approval before Phase 3.
