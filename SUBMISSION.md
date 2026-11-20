# Padel Match Planner Submission

## Student and course

- Student: Taher Ramzi Taher Farhan Almaghrebi
- Student ID: 451000573
- Course: Advanced Programming 462
- College: College of Computer Science and Information Systems
- Instructor: Dr. Majed Hariri
- Project: Padel Match Planner
- Final source branch: `revert-3-fix-vercel-postgres-migration`
- GitHub source: https://github.com/taher434/Padel-match-planner/tree/revert-3-fix-vercel-postgres-migration

## Blackboard upload

Upload **Project_451000573.zip**. The prepared file is in the local `submission/` folder.

Copy this text into the Blackboard submission text field:

```text
Project: Padel Match Planner
Course: Advanced Programming 462
Student name: Taher Ramzi Taher Farhan Almaghrebi
Student ID: 451000573
GitHub: https://github.com/taher434/Padel-match-planner/tree/revert-3-fix-vercel-postgres-migration
```

The exact deadline and presentation schedule must be checked on Blackboard. Uploading the ZIP and confirming Blackboard's submission receipt are student actions.

## Instructor access

The repository was verified as private on 2026-11-20. A collaborator invitation was sent to GitHub user `majedoh` and verified as pending acceptance. The instructor must accept it before collaborator access is active.

Before the deadline, check GitHub repository Settings, Collaborators, and confirm that `majedoh` has accepted and can access the submission branch. A pending invitation is not confirmed access.

## What is in the ZIP

- All application source: `app.py`, `db.py`, `client.py`, `gui.py`, and `report_helper.py`.
- Table setup in `db.py`, called automatically when `app.py` starts.
- `requirements.txt`, README, tests, verification checklist, progress tracker, demo/Q&A guide, and this submission guide.
- The seven-slide PDF: `output/pdf/Padel_Match_Planner_451000573.pdf`.
- Git ignore rules.

No sample database is required. The application creates its database and table automatically. Environments, caches, Git internals, local tooling, generated reports/databases, private configuration, and the ZIP output folder are excluded.

## How the ZIP matches GitHub

The ZIP is created with Git archive from the final committed and pushed source. It contains that commit's tracked file bytes, including the presentation PDF. Its Git archive comment records the source commit.

To rebuild after committing and pushing any later edits, run from the project root:

```powershell
git status
git push -u origin revert-3-fix-vercel-postgres-migration
New-Item -ItemType Directory -Path submission -Force | Out-Null
git -c core.autocrlf=false archive --format=zip --output=submission/Project_451000573.zip HEAD
git rev-parse HEAD
```

Git archive uses the committed version. The one-command `core.autocrlf=false` setting preserves the exact stored file bytes on Windows. Commit later edits before rebuilding. The ZIP is kept outside Git to avoid including an archive inside itself.

## Final student actions

- [ ] Check the Blackboard deadline and presentation schedule.
- [ ] Confirm the instructor accepted the private repository invitation.
- [ ] Review the code, rehearse the demo, and practice a small code change using `DEMO_GUIDE.md`.
- [ ] Follow the course policy on outside/AI assistance; assistance is disclosed in the README and slides.
- [ ] Upload `Project_451000573.zip` with the submission text above and confirm the Blackboard receipt.

The presentation/demo must fit within 10 minutes. The Q&A and code-understanding check allow 3 additional minutes.
