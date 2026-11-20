# Padel Match Planner Verification Checklist

Phase 4 verification completed on 2026-11-20 using Windows, Python 3.13.12, Flask 3.1.3, and Tkinter 8.6.

## Recorded results

All 52 automated tests passed. The real HTTP and GUI integration checks used a temporary database and temporary report files. They left project records and reports unchanged and stopped their temporary processes afterward.

| Area | Tests | Result | Evidence |
| --- | ---: | --- | --- |
| SQLite helper | 8 | PASS | `tests/test_db.py` |
| Flask API | 13 | PASS | `tests/test_app.py` |
| HTTP client | 11 | PASS | `tests/test_client.py` |
| Tkinter state and callbacks | 12 | PASS | `tests/test_gui.py` |
| Report, threads, and files | 8 | PASS | `tests/test_report_helper.py` |

Run the automated suite from the project root:

```powershell
python -m unittest discover -s tests -v
```

In the prepared local workspace, the equivalent command is:

```powershell
& '.tools/python/python.exe' -m unittest discover -s tests -v
```

The suite creates its own temporary databases and does not require a running Flask server. The GUI tests construct real hidden Tkinter widgets. Message dialogs and network failures are simulated where needed for deterministic checks.

## Live integration results

The Phase 4 live check used real HTTP on `127.0.0.1:5050`, real hidden Tkinter widgets and callbacks, and separate Flask/report processes. It simulated dialog choices for cancel/confirm deletion. The Phase 3 visible-window check also confirmed readable layout and a working native Refresh button.

| Scenario | Observed result |
| --- | --- |
| Empty database | GUI showed an empty list; report contained `Total saved matches: 0` and `No saved matches.` |
| Add and view | Two matches submitted by GUI callbacks appeared in the table and Flask export. |
| City filter | Filtering by the Arabic city name returned only its matching record. |
| Edit isolation | Editing one court changed only the selected match. |
| Required field | A blank name produced Flask's 400 message in the GUI. |
| Unknown ID | Deleting a record through another HTTP request made the stale GUI edit show `Match not found.` (404). |
| Delete confirmation | Cancel kept the record; confirm removed only the selected record. |
| Restart both programs | Flask and Tkinter were both stopped and recreated; saved records remained. |
| Stop Flask | GUI requests failed clearly and preserved typed input and displayed rows. |
| Restart Flask | The same remaining GUI root retried and saved successfully. |
| UTF-8 report | The report contained both records, all six fields, and correctly encoded Arabic text. |
| Report working directory | Running the helper from another folder still saved beside its own source under `reports/`. |
| Report while Flask stopped | Helper exited with status 1 and left the previous report bytes unchanged. |
| File failure | Writing to a directory returned a clear failure instead of an unhandled thread error. |
| Fresh snapshot | A later report reflected edited/deleted records and the current count. |
| Empty final state | After deleting the temporary records, the GUI and report both showed an empty result. |

The local integration scripts are in ignored `.tools/`; the manual steps below can be repeated from a normal checkout.

## Repeat the application checks

Use a separate test copy with a fresh database for this sequence. Install Python with Tkinter and the dependency in `requirements.txt`:

```powershell
python -m pip install -r requirements.txt
```

1. Start `python app.py` in the first terminal. Start `python gui.py` in a second terminal. Table setup runs automatically when Flask starts.
2. Confirm the initial empty-list message. Add an Evening doubles match in Riyadh and a Weekend rally match in Jeddah, with a court, a valid YYYY-MM-DD date, and a skill level.
3. Confirm both rows appear. Filter by ` riyadh `, including spaces and lowercase letters. Confirm only Riyadh appears, then click Show All.
4. Select the Riyadh row, change its court, and click Save Changes. Confirm the Jeddah record keeps its previous values.
5. Try a blank required field and the impossible date `2026-02-30`. Confirm clear errors and that previously saved values remain unchanged. API tests also cover invalid skill values and the 100-character text limits.
6. Select a row and click Delete Match. Cancel once and confirm it remains. Repeat and confirm deletion; check that the other row remains.
7. To repeat the stale-ID case, open a second GUI window and select the same existing row in both. Delete it in one window, then try Save Changes in the other. Expect `Match not found.`; Refresh removes the stale row.
8. Type a new match without saving it. Stop Flask with Ctrl+C in its terminal, then try Add Match or Refresh. Confirm a clear connection message and retained input/rows. Start Flask again and retry in the same GUI window.
9. Save a match, close the GUI, and stop Flask. Restart Flask and then the GUI. Confirm the saved match remains.

Direct and wrapped socket timeouts are checked in `tests/test_client.py`. They are simulated tests; the live stop/start checks exercise actual connection failures and recovery.

## Repeat the report checks

Keep Flask running. The report helper can run separately from the GUI:

```powershell
python report_helper.py
```

In the prepared local workspace:

```powershell
& '.tools/python/python.exe' report_helper.py
```

1. Expect a success message and exit status 0. Open `reports/padel_matches_report.txt` as UTF-8 text.
2. Check the total, ID, name, city, court, date, and skill level against the saved matches. The report includes all saved matches.
3. Use Arabic text in a city/name and confirm it remains readable in the report.
4. Edit or delete a test record, run the helper again, and check that the latest report reflects the current saved records. Each successful run replaces the previous report snapshot.
5. Stop Flask and run the helper. Expect a failure message and exit status 1. Confirm an existing report was left unchanged.
6. Restart Flask and rerun the helper. Expect success without changes to the script.
7. Run `tests/test_report_helper.py` through the suite above for actual file/path failures, the empty report, and verification that exactly one real worker thread is created for a successful fetch.

## Explain the threading code

- `save_report()` asks Flask's `/matches/export` route for records through `client.send_request()`.
- It creates one `threading.Thread`, with `write_report()` as its target, and calls `.start()`.
- The worker opens the file with `with open(..., encoding="utf-8")`. It catches `OSError` and records success or failure in a shared dictionary.
- `.join()` waits for the worker to finish before the main thread reads that dictionary.
- `main()` prints the result and returns status 0 for success or 1 for failure.

## Phase 5 clean setup verification

PASS on 2026-11-20: the staged source was exported to a clean folder, a normal Python 3.13.12 virtual environment was created, and only `requirements.txt` was installed. All 52 tests passed in that environment.

PASS: the documented `app.py` and `gui.py` entry points started using that environment. The copied GUI added, filtered, and deleted a test match through the copied backend, and `report_helper.py` saved the expected UTF-8 report. Verification confirmed imports came from the clean copy/environment. Its processes were stopped afterward.

## Final submission status

- [x] Follow the README setup from a clean copy with Python/Tkinter and run all 52 tests.
- [x] Finish the course-topic mapping, assistance credits, demo notes, and Q&A guide.
- [x] Prepare and visually inspect all seven PDF slides with student details.
- [x] Send the private-repository invitation to `majedoh`; it is pending acceptance.
- [x] Include the supplied student name and ID in the submission materials.
- [ ] Build and compare the final ZIP with the pushed Git commit.
- [ ] Confirm the instructor accepted the invitation.
- [ ] Confirm the Blackboard deadline/presentation schedule, upload the ZIP and text, and check the submission receipt.
