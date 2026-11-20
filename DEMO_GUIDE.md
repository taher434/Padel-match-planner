# Padel Match Planner Demo and Code Understanding Guide

- Student: Taher Ramzi Taher Farhan Almaghrebi
- Student ID: 451000573
- Course: Advanced Programming 462
- Instructor: Dr. Majed Hariri

## Prepare the demonstration

Open the project in your editor. Keep `gui.py`, `client.py`, `app.py`, `db.py`, and `report_helper.py` easy to find. Start Flask, then Tkinter, using the README commands. Keep a third terminal ready for the report helper and open GitHub's commit history for the required branch.

Practice in a separate test copy so your demonstration uses known records. Use two matches with different cities, such as Riyadh and Jeddah. Prepare a valid date, an impossible date such as `2026-02-30`, and one record you can delete during the demonstration.

## Presentation and live demo within 10 minutes

| Time | Action | Main explanation |
| --- | --- | --- |
| 0:00-0:30 | Show the title slide and introduce the project. | Save local padel matches and find them by city. |
| 0:30-1:00 | Explain the useful fields and city filter. | Players can choose a city, court, date, and suitable skill level. |
| 1:00-2:00 | Show the architecture slide. | Tkinter sends HTTP to Flask; Flask validates and uses SQLite; JSON returns the result. |
| 2:00-3:00 | Add a Riyadh match and a Jeddah match. | Users work entirely in the GUI. SQLite generates each ID. |
| 3:00-3:45 | Filter Riyadh, then click Show All. | GET reads records; the city query is encoded safely. |
| 3:45-4:30 | Edit one court and show the other row is unchanged. | The real selected ID identifies the record to update. |
| 4:30-5:15 | Try a missing name or invalid date, then correct it. | Flask returns JSON 400; the GUI keeps the entered values. |
| 5:15-6:00 | Cancel deletion once, then confirm it. | Confirmation happens before a POST delete request. |
| 6:00-7:00 | Stop Flask, try Refresh, restart Flask, and retry in the same GUI. | HTTP errors and connection failures are handled without closing the window. |
| 7:00-8:00 | Run the report helper and open the UTF-8 report. | One worker writes all saved records; the main thread waits with join. |
| 8:00-9:00 | Trace Add in the source and show the helper class/query. | Explain form values, validation, SQL parameters, commit, and JSON. |
| 9:00-9:30 | Show start/join and with open in the report helper. | The thread demonstrates course topics; this small task is not a speed test. |
| 9:30-10:00 | Show test evidence and GitHub commits, then finish. | 52 automated tests passed, with separate real integration checks and disclosed assistance. |

If a step runs long, shorten your explanation and move on. Keep the Q&A separate from the 10-minute presentation/demo.

## Trace one Add action

1. `gui.py: PadelPlanner.add_match()` calls `read_form()` to build a dictionary of five strings.
2. `client.py: add_match()` calls `send_request('/matches/add', values)`.
3. `send_request()` runs `urlencode(values).encode('utf-8')`. Passing these bytes as `data` to `urlopen` sends POST.
4. `app.py: add_match()` reads `request.form`. `validate_match()` trims values and checks required fields, lengths, date, and skill level.
5. `get_database()` opens a helper for this request and stores it in Flask `g`.
6. `db.py: MatchDatabase.add_match()` executes an INSERT with `?` parameters, commits, and returns the generated ID.
7. Flask replies with JSON 201. The client decodes the reply with `json.loads`.
8. The GUI clears the successfully saved form, requests the current list, and shows a success message. Flask teardown closes the connection.

## Three-minute understanding practice

Rehearse a 60-second Add trace, a 60-second database/error explanation, and a 60-second report explanation or small change. Answer in your own words while pointing to the relevant function.

| Question | Short explanation to practice | Code location |
| --- | --- | --- |
| Why use an ID? | Names can repeat. A generated ID selects exactly one saved record. | `db.py: create_table`; `gui.py: select_match` |
| What does the class do? | `MatchDatabase` owns one connection and groups the related database operations. | `db.py: MatchDatabase` |
| Why SQL placeholders? | Query values stay separate from SQL instructions, including quotes and SQL-like input. | `db.py: add_match`, `update_match`, `delete_match` |
| Why commit? | A successful write must be saved before the connection closes. | `db.py: add_match` |
| Does table setup erase data? | CREATE TABLE IF NOT EXISTS creates only a missing table. | `db.py: create_table` |
| Why a connection per request? | Each request gets its own connection; teardown closes it even after an error. | `app.py: get_database`, `close_database` |
| Why validate in Flask? | The server checks every submitted request, including requests from outside the GUI. | `app.py: validate_match` |
| What is GET versus POST here? | GET reads/filter records; POST adds, edits, or deletes. Bytes supplied as data make urlopen send POST. | `client.py: send_request` |
| Why catch HTTPError first? | It is a subclass of URLError. The specific handler reads Flask's JSON 400/404 body. | `client.py: send_request` |
| What if Flask stops? | The client returns a clear failure dictionary. The GUI retains its state and can retry later. | `client.py: send_request`; `gui.py: refresh_matches` |
| What collections are used? | Records are a list of dictionaries. The GUI also maps row IDs to match dictionaries. | `db.py: get_matches`; `gui.py: refresh_matches` |
| What does start do? | It begins the worker's execution separately from the main thread. | `report_helper.py: save_report` |
| What does join do? | It waits until the worker finishes, so the result dictionary is ready to read. | `report_helper.py: save_report` |
| How does the worker report success? | It updates a shared dictionary after writing or after catching OSError. The main thread reads it after join. | `report_helper.py: write_report`, `save_report` |
| Why use with open? | The context manager closes the file when the block ends, including on an exception. UTF-8 preserves Arabic text. | `report_helper.py: write_report` |
| Why use a thread for a small report? | It demonstrates threads and files. It is not intended to make this small task faster. | `report_helper.py` |

## Small changes to rehearse

Make practice changes in a test copy and run the relevant tests afterward.

1. Change a button label in `gui.py: build_form()` and show the new label.
2. Change `MAX_TEXT_LENGTH` in `app.py`, then demonstrate a value above the new limit. Explain that boundary tests using 100/101 also need to match a permanent limit change.
3. Add a skill level by updating both Flask's `SKILL_LEVELS` and the GUI combobox values. Also update the validation message and affected documentation/tests.
4. Change the report heading in `report_helper.py: write_report()` and regenerate the file.
5. Change the empty-list message in `gui.py: refresh_matches()` without changing how requests are sent.

## Keep the explanation accurate

The server uses SQLite, not a remote database service. The GUI sends requests automatically. Timeout behavior has automated simulated checks, while real stop/start checks verified connection recovery. Assistance from OpenAI Codex is disclosed in the README and slides. Review the core code before presenting and follow the course's assistance policy.
