# ELCCC Care Connect — Phase 1 local backend

**Current branch:** `codex/elccc-counselor-profile-pages`. Saved record reads now require
local staff access. Run `python -m app.staff` to display your generated test keys; the
frontend signs in using an HttpOnly cookie. Use the [current Mac walkthrough](../docs/COUNSELOR_PROFILE_PAGES.md)
and the restricted frontend server, not the older whole-repository preview command.


**DEVELOPMENT PROTOTYPE — FICTIONAL DATA ONLY.** This is not HIPAA-ready or suitable
for real patient information. It uses local test staff sessions and server-side role/record checks, not production-ready authentication. Never
enter real names, contact details, clinical information, or patient records. Do
not expose it publicly or connect the GitHub Pages frontend to it.

This separate FastAPI/SQLite backend preserves the existing frontend design,
branding, navigation, and Pages deployment. No billing, telehealth, diagnosis,
or external service integrations are included. Phase 2 connects the local frontend
inquiry form and Admin inquiry list only.

## Start and open the demo

You need Python **3.9 or newer**, Git, and a terminal. SQLite comes with Python;
you do not need a database server.

The dependency pins support Python 3.9, including macOS Python 3.9.6. Pydantic
2 is required by the models; pip selects transitive dependencies compatible with
your Python version. If updating an existing installation, activate its virtual
environment and rerun `python -m pip install -r requirements.txt` before starting
the server.

1. Clone the repository (or use your existing clone) and select the branch:

   ```bash
   git clone https://github.com/ELCCCdev/elccc-care-connect.git
   cd elccc-care-connect
   git switch codex/elccc-backend-phase-1
   cd backend
   ```

2. Create a virtual environment:

   ```bash
   python -m venv .venv
   ```

   Use `python3` instead if that is your computer's Python command.
   Activate on macOS/Linux:

   ```bash
   source .venv/bin/activate
   ```

   Or on Windows PowerShell:

   ```powershell
   .venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, use `.venv\Scripts\python.exe` instead of
   `python` in the following commands without activating.

3. Install dependencies and start the server **from backend/**:

   ```bash
   python -m pip install -r requirements.txt
   python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
   ```

4. Leave the terminal running and open **http://127.0.0.1:8000/demo**.
   The DEVELOPMENT DEMO page displays three explicitly fictional samples.
   API documentation: http://127.0.0.1:8000/docs.
   Health check: http://127.0.0.1:8000/health.

Keep the loopback host shown above. Do not use `--host 0.0.0.0`, public hosting,
or a public tunnel. CORS permits only `http://127.0.0.1:5500` and `http://localhost:5500` for GET/POST
and the Content-Type header, without credentials. Public frontend origins are
not allowed. CORS is a browser policy, not authentication or access control. Local
isolation and fictional-data acknowledgment are not security or compliance
controls that prevent someone from entering real information.

## Verify persistence

1. Enter a made-up name such as **Demo Robin Orchard**, choose an interest and
   contact preference, and check the fictional-data confirmation.
2. Click **Save fictional inquiry**. It appears with a UUID, status `new`, and
   creation time.
3. Refresh the browser page. The inquiry remains.
4. Stop the server with **Ctrl+C** and restart it using the same command.
5. Reopen `/demo`. The inquiry remains, and the samples are not duplicated.

The SQLite file is created automatically at `backend/data/inquiries.sqlite3`.
The default location is relative to the backend code, so it stays the same across
server restarts. Successful writes are committed, and connections are closed
per operation. Samples are seeded only once per database.

Database files, `data/`, `.venv/`, Python caches, and `.env` files are ignored by
Git. Never commit databases, credentials, or secrets. Optionally set `ELCCC_DB_PATH`
to another local database file before startup. Relative custom paths resolve
against your terminal directory. Keep all databases outside frontend/build output.

To reset the demo, stop the server and delete only `backend/data/inquiries.sqlite3`
(or your custom demo database). **This deletes all saved demo inquiries.** Samples
return on next startup.

## API and validation

| Method | Path | Result |
| --- | --- | --- |
| GET | `/health` | App and database readiness; 503 on database failure |
| POST | `/api/inquiries` | Create an inquiry; 201 on success |
| GET | `/api/inquiries` | List saved inquiries, newest first |
| GET | `/api/inquiries/{inquiry_id}` | Retrieve a UUID; 404 if missing |
| GET | `/demo` | Independent backend browser demo |

Create request example (try it through `/docs`):

```json
{
  "fictional_client_name": "Demo Robin Orchard",
  "category": "couples",
  "preferred_contact_method": "email",
  "fictional_data_only": true
}
```

Names are trimmed and must be 2–80 characters. Categories: `individual`, `couples`,
`family`, `general`. Contact preferences: `email`, `phone`; no actual email or
phone field is accepted. Fictional-data confirmation is required. Unknown fields
are rejected. The server assigns UUIDs, status `new`, and UTC timestamps.
Samples illustrate `new`, `reviewing`, and `closed`; status updates are outside
Phase 1. Invalid inputs/malformed UUIDs return 422 with readable field errors;
missing records return 404; database errors return 503. Writes use parameterized
SQL, and the page renders names as text rather than HTML.

## Automated tests

From `backend/`, with the virtual environment active:

```bash
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
```

The Phase 2 tests use disposable databases: demo/health responses, create/list/retrieve
and metadata, restart persistence without duplicate samples, validation/malformed
JSON, missing/invalid IDs, SQL-like input and whitespace, database errors, and allowed/disallowed local CORS origins. Tests do not change your demo database.

## Troubleshooting

- **Module not found:** activate your environment, install requirements, and run
  from `backend/`.
- **Port in use:** stop the previous server or use `--port 8001`, then open
  http://127.0.0.1:8001/demo.
- **Database unavailable/startup failure:** ensure the directory is writable and
  `ELCCC_DB_PATH` points to a file, not a directory. Do not delete saved data to
  fix permissions.
- **Browser cannot connect:** keep the terminal running and match the command's
  host/port. A cloud workspace's loopback URL is not your laptop's URL; clone and
  run locally to view this private demo.

## Files

- `app/main.py`: routes, validation, SQLite storage, fictional sample seeding.
- `app/demo.html`: independent browser demo.
- `tests/test_backend.py`: standard-library unittest suite.
- `requirements.txt`: runtime dependencies; `requirements-dev.txt`: test dependency.
- `data/`: generated SQLite database, ignored by Git.

The Phase 2 frontend integration is documented in the root README. The GitHub
Pages deployment configuration remains unchanged, and the static build does not
publish this backend or its data. Public Pages retains the static mock behavior.


## Phase 3 management

See the root README's Phase 3 section for Mac setup and the Admin workflow.
Startup adds `inquiry_management` and `inquiry_history` tables in the existing
SQLite database without changing original inquiries. The original inquiry APIs
remain unchanged. New management APIs list prospective/established clients,
retrieve profiles, confirm conversions, and update MYIO demonstration tracking.
Conversion and invitation statuses are independent and persist across restarts.
No invitations are sent or external accounts checked. The new tests cover
conversion, duplicate/competing requests, history, independent invitation tracking,
legacy database preservation, and restart persistence. All data is fictional.

### Synthetic appointment-preference requests

`POST /api/preference-requests` adds a guided contact/preference submission while
preserving the original inquiry API. It accepts the original required inquiry fields
plus `email`, `phone`, `session_format` (Telehealth/In-person/No preference), optional
`preferred_counselor_id`, `preferred_date` (today or later), `preferred_time`
(Morning/Afternoon/Evening/No preference), `time_zone` (America/New_York), and a UUID
`request_key`. Unknown fields are rejected. Synthetic-only name/email/phone rules
are enforced server-side; see the [walkthrough](../docs/PUBLIC_REQUEST_FLOW.md).

A new additive `preference_requests` table links details to the existing inquiry
UUID. Management responses expose optional `preferences`; older inquiries have none.
An identical retry with the same request key returns HTTP 200 and the original ID;
a different payload with that key returns 409. A new submission returns 201. Name
is never an identity key. Conversion retains these details and existing history.
No appointment, invitation, intake document, or message is created or sent.
Python 3.9+ and existing dependencies remain supported; no new dependency is needed.

### Client profile editing and reversible archiving

The `client_record_state` additive table stores current profile edits, revision,
and archive timestamp separately from the original inquiry. Management responses
add `original_inquiry`, `revision`, and `archived_at` while retaining existing fields.
POST `/api/inquiries/{id}/edit` requires editable original inquiry fields, `status`,
`fictional_data_only: true`, and `expected_revision`. Existing synthetic contact
email/phone can also be corrected. Original inquiry endpoints remain immutable.

POST `/api/inquiries/{id}/archive` and `/restore` each require `confirmed: true`
and `expected_revision`. These are reversible operations; there is no permanent
delete endpoint. The prospective/established list routes omit archived records by
default; `?include_archived=true` includes them. Edits/archive/restore and existing
conversion/invitation changes advance the revision. Stale writes return 409;
archived clients must be restored before editing/conversion/invitation updates.
All actual changes append history in the same transaction. No data reset or new
dependency is required. See [local review instructions](../docs/CLIENT_RECORD_ACTIONS.md).

### Persistent counselor assignment and scoped profiles

Additive `counselors` and `client_assignments` tables store eligibility and the current
assignment. POST `/api/inquiries/{id}/assignment` requires an administrator session,
`confirmed: true`, `expected_revision`, and explicit `counselor_id` (or null to remove).
Only active established clients and active counselors accepting assignments are allowed.
Updates and timestamped history are atomic; counselor preferences are never assignments.
Management responses add `assigned_counselor_id` and `assignment_updated_at`.

GET `/api/counselors/{id}/clients` returns scoped clients and counts; counselors can
read only their own active established caseload. Broad client/inquiry lists and all
management mutations require administrator access; single-record reads also support
the assigned counselor. Public synthetic creation endpoints remain available.

Local staff login/session/logout routes live under `/api/staff`. Generated credentials
are private local files outside the frontend root; never commit or share them. Sessions
expire after eight hours and are invalidated by restart. These shared local test roles
are not real staff identities or production authentication. The current walkthrough
covers credentials, HttpOnly cookies, CORS, revision conflicts, future authorization,
production readiness and regression commands. Dependencies remain unchanged.
