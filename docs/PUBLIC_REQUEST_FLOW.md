# Counseling request and intake direction

This branch adds a guided **appointment-preference request**, not live booking.
It is a local, synthetic-data-only development environment, without secure sign-in
or backend role authorization. It is not HIPAA-ready. Do not enter real personal,
patient, or clinical information. Public GitHub Pages is not connected to this backend.

## Review locally on a Mac

From your existing repository folder (commit or stash any personal edits first):

```bash
git fetch origin
git switch codex/elccc-public-preference-request
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Use Python 3.9 or newer. Leave that Terminal open. In a second Terminal, change to
this same repository's root folder and run:

```bash
python3 -m http.server 5500 --bind 127.0.0.1
```

Open **http://127.0.0.1:5500** and hard refresh Chrome with Command Shift R.
The frontend must use port 5500; local CORS allows only localhost/127.0.0.1 on
that port. A refused connection means the relevant server is not running.
Do not expose either server to the internet or a shared network.

1. Choose **Explore Services or Request Care**, then **Request Counseling**.
2. Enter **Test Alex River**, **alex@example.com**, **202-555-0100**. These are
   synthetic values. There is no existing-client selector and no CRM lookup.
3. Select counseling type and session format, then optionally a counselor.
4. Choose a future preferred date and a broad time period. Eastern Time is shown;
   there are no available slots or reservations. Use Back to review your choices.
5. Review, confirm synthetic details, and submit. The confirmation displays the
   actual saved inquiry UUID. It does not promise an appointment, contact from
   staff, an email, or intake paperwork.
6. Close the confirmation, select **Switch Role → Administrator → Continue**,
   then **Clients → Prospective Clients**. Search for the inquiry UUID or name,
   open its profile, and review **Request details**, **Onboarding checklist**, and
   **Activity history**. Changing the perspective is not secure authentication.
7. Update invitation tracking independently if desired. Confirm **Convert to Client**;
   the same record moves to Established Clients with its original details/history.
8. Refresh the page. Use Switch Role to reopen Established Clients. Stop Uvicorn
   with Control C and rerun the same command; the record remains saved. Do not
   delete the SQLite file or change `ELCCC_DB_PATH` during this check.

The default database is `backend/data/inquiries.sqlite3`, ignored by Git. The
migration adds a table; it does not replace existing inquiry or management rows.
Old records show their available information without inventing missing contact data.

## Functional boundaries

| Capability | Current behavior |
| --- | --- |
| Contact and counseling preference entry | Guided form, server validation, persisted synthetic contacts/preferences |
| Inquiry identity | Server-generated UUID; no matching by name; separate requests may have identical names |
| Retry protection | Per-submission UUID key; same request returns original inquiry; changed content with the same key returns 409 |
| Client directory | Saved inquiries, search/filter/sort, recorded Last Activity, profile navigation |
| Client conversion | Confirmation, transactional duplicate prevention, original ID/date/history/preferences preserved |
| Portal invitation tracking | Persistent manual Not Sent/Sent/Activated tracking; no invitation or account verification |
| Counselor assignment | Existing page-session workflow; preferred counselor is not an assignment |
| Intake checklist and progress | Derived saved/session/planned statuses; session activities reset on reload |
| Appointments and care journey | Existing session-only simulations preserved; not actual booking or clinical care |
| Sending paperwork, communications, reminders | Not implemented; no messages sent |
| Live availability, calendar conflicts, secure portal | Not implemented |
| Valant, Calendly, MYIO | No connection; separate evaluation, no assumed calendar/API access |

Public flow uses `POST /api/preference-requests` with the supported original
inquiry fields plus `email`, `phone`, `session_format`, optional
`preferred_counselor_id`, `preferred_date`, `preferred_time`, `time_zone`, and
`request_key`. The original `/api/inquiries` routes and schemas remain compatible.
Management responses include optional `preferences`. Records created through the
older route do not gain fabricated contact data. Preference details stay under the
same inquiry UUID through conversion. No appointment row is created by submission.

The backend accepts only names starting with `Test` and a first/last name,
example.com/org/net email addresses, and reserved North American 555-0100–0199
phone numbers for this new route. This reduces accidental ordinary contact entry;
it is **not identity verification, authentication, or a comprehensive privacy
control**. Existing local APIs remain development-only and must not receive real data.
Nothing entered here is suitable for real patient care.

## Normal workspace and testing workspace

Normal services pages omit historical metrics and archive navigation. Counselor
profiles do not present reference availability as actual openings. Client and
counselor workspaces show current session records; persisted inquiry management
remains in Admin CRM. Session-only care activity is not restored after reload.

For regression testing of the pre-existing historical profiles and simulations,
open **http://127.0.0.1:5500/?tools=1**. This explicitly enables Reference Profiles,
archived scheduling fixtures, development scheduling notes, and historical charts.
It is a testing view of the same application, not a second project or security
boundary. Use a separate SQLite path for automated tests; never copy production data.

## Streamlined future workflow

Keep the inquiry UUID as the source identity, with a stable client identity linked
on conversion. Contact corrections should update the shared record with audit
history, not create another intake copy. Staff should see one profile with:

- Request review: New / Reviewing / Follow-up needed / Ready.
- Counselor assignment: Unassigned / Offered / Assigned.
- Paperwork: Not sent / Sent / In progress / Complete / Needs correction.
- Appointment: Preference received / Awaiting availability / Confirmed / Changed / Cancelled.
- Invitation: independent Not Sent / Sent / Activated, with verified activation only
  after an authenticated portal exists.
- Outstanding tasks: owner, due date, next action, and auditable completion.

These are the proposed durable statuses, not new live services in this branch.

Implement in this order:

1. Authenticate staff and clients; enforce server-side role and record ownership on
   every operation. Add audit trails, secure sessions, least privilege and recovery.
2. Complete privacy/security review, deployment hardening, encryption/key management,
   backups/recovery, retention/deletion, access monitoring and vendor/BAA evaluation.
   Require a HIPAA readiness review before any real patient-data collection.
3. Persist assignment, intake task state and approved non-sensitive administrative
   intake fields on the same client record. Add staff follow-up queues and concurrency
   controls before enabling questionnaires or document upload.
4. Implement appointment types/durations, counselor availability, IANA time zones,
   transactional calendar conflict prevention and idempotent reservations. Only then
   expose real slots, confirmation, cancellation and rescheduling.
5. Add consent-aware delivery for paperwork/reminders with delivery status and
   failures, then evaluate optional Valant/MYIO connections separately.

## Checks

```bash
cd backend
source .venv/bin/activate
python -m unittest discover -s tests -v
cd ..
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

Browser checks need Playwright and a Chromium install in the interpreter running
the script (`python -m pip install playwright && python -m playwright install chromium`).
The Python checks use Playwright’s downloaded browser on macOS; `CHROMIUM_PATH`
can override its executable. Stop your
local servers first: these checks use ports 5500/5501/8000 and disposable databases.

```bash
BACKEND_PYTHON="$PWD/backend/.venv/bin/python" python scripts/check-public-request.py
BACKEND_PYTHON="$PWD/backend/.venv/bin/python" python scripts/check-backend-integration.py
```

Browser checks cover guided input/review/back, synthetic validation, failed saves,
retry protection, responsive widths, CRM search/profile, conversion, invitation
tracking, refresh and backend restart, plus existing Phase 2/3 regression workflows.
