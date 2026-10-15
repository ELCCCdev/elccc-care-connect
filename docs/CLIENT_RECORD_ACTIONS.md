# Client list actions and safe record management

Branch: `codex/elccc-client-record-actions`.

This remains a local development prototype for synthetic test records only.
Role selection is not authentication or authorization. No real patient information,
live scheduling, external invitations, or new integrations are enabled.

## Run locally on your Mac

Stop the running backend with **Control C** first. From your existing repository
folder, commit or stash any personal edits, then run:

```bash
git fetch origin
git switch codex/elccc-client-record-actions
cd backend
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

If you do not yet have a virtual environment, run `python3 -m venv .venv` before
activating it. Python 3.9 or newer is supported; dependencies are unchanged.
Leave this Terminal running. Open another Terminal in the repository root:

```bash
python3 -m http.server 5500 --bind 127.0.0.1
```

Visit **http://127.0.0.1:5500**, hard refresh with **Command Shift R**, and select
**I'm an Administrator → Clients → Prospective Clients**. You can also use
**Switch Role → Administrator → Continue to Administrator** from another view.

Keep the same database path as your previous work. The default is
`backend/data/inquiries.sqlite3`; no database reset is necessary. The migration
adds `client_record_state`, leaving existing inquiries, preferences, conversion,
invitation tracking, and history in place. Databases are not committed to Git.

## Review checklist

Use an existing synthetic record, or create one using **Request Counseling**
with `Test Alex River`, `alex@example.com`, and `202-555-0100`.

1. In either client list, single-click the name, double-click the name or plain row
   area, or use **View** / **Open profile**. All open the same saved profile.
2. Press Tab to focus a name or either view button and press Enter/Space. A row
   itself also supports Enter. Double-clicking is optional; all actions work with
   a single click or tap.
3. Select **Edit**. Change the synthetic name to `Test Alex Updated`, counseling
   category, contact preference, or inquiry review status. Records with saved
   contact preferences also allow synthetic email and phone corrections.
4. Select **Cancel**, the close control, or Escape. The draft is discarded and
   the prior profile/list, search, and filters remain unchanged. No server write
   or activity is created by cancellation.
5. Reopen Edit, change the fields, and select **Save Changes**. The current profile,
   directory search/sort results, and activity history update. Expand **Original
   inquiry details** to see the unchanged original values and reference.
6. Select **Delete**. This action means **archive**, for both prospective and
   established clients. Nothing changes until you check the confirmation box
   and select **Confirm Archive**. Cancel leaves the record untouched.
7. The record disappears from Active records. Change **Record visibility** to
   **Archived records**, open it, and review its preserved details/history.
   Archived records are read-only. **Restore** requires its own confirmation and
   returns the record to its original prospective/established list.
8. Convert a prospective test record using the existing confirmed conversion.
   Repeat View/Edit/Delete/Restore in Established Clients. Original inquiry ID,
   creation date, preferences, conversion, invitation tracking, and activity remain.
9. Refresh the browser, then stop/restart Uvicorn using the same command/database.
   Reopen the appropriate list and visibility filter. Edits and archive state remain.
   Filters and open dialogs are page-session preferences, not saved client data.

Try invalid contact data such as an ordinary email domain: the backend rejects it
and keeps the form open with an error. Do not enter actual personal information.
If another view changes a record after Edit opens, Save returns a conflict rather
than overwriting it. Cancel and reopen to fetch the latest version. On a network
failure the form retains the draft and does not show success; verify the profile
before retrying if the response was uncertain.

## Scope and persistence

- Current editable fields: synthetic name, counseling category, preferred contact
  method, inquiry review status (`new`, `reviewing`, `closed`), and existing
  synthetic contact email/phone. A new name must start with `Test` and include a
  first and last name. Existing legacy synthetic names may be kept unchanged.
- Inquiry review status is independent of client conversion. Conversion, counselor
  assignment, invitation tracking, and appointments keep their existing controls.
- Existing inquiry APIs and backend `/demo` expose the original immutable inquiry.
  CRM management APIs expose the current edited profile plus `original_inquiry`.
- A separate SQLite table stores current edits, archive timestamp, and revision.
  Every actual edit, archive, restore, conversion, and invitation change advances
  the revision. No-change saves do not invent history or update Last Activity.
- Edits append timestamped activity entries listing changed fields. Existing
  entries are not replaced. Archive and restore append their own actual events.
- No hard-delete endpoint is added. Archive removes directory visibility without
  cancelling appointments or removing linked care history. Existing session-only
  appointment/intake/assignment simulations stay session-only and reset on refresh.
- Older records without contact preferences do not receive invented contact data.
- These remain unauthenticated local development APIs. Revision checks and frontend
  role selection are not access control. Server-side authentication, record-level
  authorization, secure deployment/storage and privacy readiness are prerequisites
  for any real client data.

## Backend additions

All routes use the existing local CORS configuration; no new HTTP method is required.

| Route | Request / behavior |
| --- | --- |
| `POST /api/inquiries/{id}/edit` | Original editable inquiry fields, `status`, `fictional_data_only: true`, `expected_revision`; optional existing contact `email`/`phone` |
| `POST /api/inquiries/{id}/archive` | `confirmed: true`, `expected_revision`; reversible soft removal |
| `POST /api/inquiries/{id}/restore` | `confirmed: true`, `expected_revision`; restores original lifecycle |
| `GET /api/prospective-clients?include_archived=true` | Includes archived prospective records for local visibility filtering |
| `GET /api/clients?include_archived=true` | Includes archived established records |

Without `include_archived`, both directory endpoints return active records only.
Management responses add `original_inquiry`, `revision`, and `archived_at`.
Stale revisions or changes to archived records return 409. Invalid fields return
422, missing records return 404, and database errors return 503. Updates and their
history are committed in the same transaction. Archived clients cannot be edited,
converted, or have invitation status changed until restored.

## Automated checks

Backend, from the backend folder with the virtual environment active:

```bash
python -m unittest discover -s tests -v
```

From the repository root:

```bash
node scripts/check-workflow.mjs
node scripts/check-workspace.mjs
node scripts/check-operations.mjs
node scripts/check-presentation.mjs
node scripts/check-roles.mjs
node scripts/check-refinement.mjs
node scripts/check-crm-directory.mjs
node scripts/check-onboarding.mjs
npm run build
```

Browser checks need Playwright and Chromium in the interpreter running them:
`python -m pip install playwright` and `python -m playwright install chromium`.
Stop your own servers first; these scripts use ports 5500/5501/8000 and disposable
SQLite databases. `BACKEND_PYTHON` selects the installed backend interpreter.

```bash
BACKEND_PYTHON="$PWD/backend/.venv/bin/python" python scripts/check-client-actions.py
BACKEND_PYTHON="$PWD/backend/.venv/bin/python" python scripts/check-public-request.py
BACKEND_PYTHON="$PWD/backend/.venv/bin/python" python scripts/check-backend-integration.py
```

The record-action browser check exercises both lists, all entry points, keyboard
access, Cancel/Escape, validated editing, failed saves, conflicting versions,
confirmation, archive/restore, four screen widths, and actual backend restart.
Existing tests continue to cover inquiry creation, conversion, invitation tracking,
search/filter/sort, appointment workflows, care journeys, and role navigation.
