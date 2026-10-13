# ELCCC Care Connect — Phase 1 local backend

**DEVELOPMENT PROTOTYPE — FICTIONAL DATA ONLY.** This is not HIPAA-ready or suitable
for real patient information. It has no authentication or authorization. Never
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

Eight tests use disposable databases: demo/health responses, create/list/retrieve
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
