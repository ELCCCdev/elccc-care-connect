# Dedicated profiles and counselor assignments

Branch: `codex/elccc-counselor-profile-pages`.

This phase provides stable, staff-protected client profile URLs, persistent counselor
assignments, and scoped caseloads. It remains a **local synthetic-data development
prototype**, not a production authentication system or HIPAA-ready application.
Do not enter real contact, patient, or clinical information.

## Run on your Mac

Stop both old servers with **Control C**. From your existing repository folder,
commit or stash any personal edits, then run in Terminal 1:

```bash
git fetch origin
git switch codex/elccc-counselor-profile-pages
cd backend
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

If `.venv` does not exist, first run `python3 -m venv .venv`. Python 3.9+ and the
existing dependencies remain supported. Leave Terminal 1 running.

In Terminal 2, change to the same repository's `backend` folder:

```bash
source .venv/bin/activate
python -m app.staff
```

This command displays generated **local test access keys** for `administrator`
and the counselor IDs (including `rachel-kim` and `melissa-smith`). Copy the key
for the account you want to test. Keep keys local; do not paste them into chat,
commit them, or put them in URLs. They are test credentials, not real staff accounts.

Then, in this Terminal, move back to the repository root and start the frontend:

```bash
cd ..
python3 scripts/serve-local.py
```

Open **http://127.0.0.1:5500**, then hard refresh Chrome with **Command Shift R**.
Use this server instead of `python -m http.server` or a server that shares the whole
repository. It serves only the application page and blocks backend files, databases,
Git metadata and credential files. `npm run dev` also now serves only the application
on loopback, at port 4173; saved-data workflows still require port 5500.

Keep the same SQLite path as your previous work. The default remains
`backend/data/inquiries.sqlite3`. No database reset or copying is needed.

## Review the administrator workflow

1. Choose **I'm an Administrator**, then enter the `administrator` local test key
   under **Local staff access → Open staff workspace**. Choosing a workspace alone
   does not grant backend access.
2. Open **Clients → Prospective Clients**. Create a synthetic inquiry first if needed
   through Request Counseling, using `Test Alex River`, `alex@example.com` and
   `202-555-0100`. Selecting a preferred counselor does not create an assignment.
3. Click a name, double-click a plain row area, or use **View / Open profile**.
   Keyboard users can Tab to a name/button and press Enter or Space; a focused row
   also opens with Enter. The profile opens in a **new browser tab**. Allow popups
   for the local site if your browser blocks new tabs.
4. The directory stays in its original tab with its search, filters and sorting.
   The profile URL is `http://127.0.0.1:5500/?client=<inquiry-UUID>`. Bookmarking or
   refreshing that URL opens the same record after staff access is verified. It
   contains no contact details or credentials.
5. Use **Overview, Contact Information, Counseling Preferences, Intake, Appointments,
   Activity History** links to navigate the sections. **Back to Clients** opens the
   appropriate directory in the current tab; the original tab remains available.
6. Edit and cancel or save as before. Original inquiry details and the UUID stay
   unchanged. The profile's activity records actual changes.
7. Convert the inquiry using the existing confirmation. In an established profile,
   choose **Assign counselor → Review Assignment Change → Confirm Assignment Change**.
   Choosing **Cancel Assignment Change** makes no change. A counselor preference
   never preselects an assignment.
8. Change to another eligible counselor or select **Not assigned** to remove the
   assignment. Each change requires confirmation and is saved with timestamped
   activity. Inactive or non-accepting counselors cannot be selected for a new
   assignment; the backend independently enforces this rule.
9. Return to the original directory tab. On focus or Refresh client lists, the
   saved assignment appears and the counselor filter uses the persistent assignment.
   Existing appointment/session simulations do not override it.
10. Try **Delete → checkbox → Confirm Archive**. Archived profiles are clearly marked
    and read-only; assignment/edit/conversion/invitation changes are blocked by the
    backend as well as the interface. **Restore** retains the original assignment,
    conversion, references and history. No permanent delete endpoint is added.

Caseload eligibility is synthetic roster data, **not verified calendar availability**.
The initial roster marks Denice Colson and Sarah Williams as not accepting assignments.
All seed counselors are active. The database has an independent active flag; tests
also exercise inactive counselors. There is no new counselor-status editing screen.

## Review counselor access

Use a Chrome Incognito window or another browser profile so its staff cookies are
separate from the administrator's session. Open
**http://127.0.0.1:5500/?workspace=counselor** and enter the `rachel-kim` test key.

- The dashboard displays that counselor's active established clients, review and
  invitation statuses, and basic caseload counts. It has loading, empty, error and
  retry states. Profile buttons open separate tabs.
- Profiles are read-only for counselors. They cannot assign, edit, convert, archive,
  restore, or change portal tracking through the backend.
- An unassigned client's URL, another counselor's client, or an archived client is
  not readable with this account. Changing a URL, selector, or frontend role does
  not grant access. Administrator sessions can preview different counselor caseloads.
- Reassignment immediately changes backend ownership. The former counselor loses
  access on the next request. Archiving removes the record from the active caseload;
  restoration retains the assignment and returns it to the caseload.

## Verify persistence and session behavior

Refresh an established profile: its UUID, assignment and history remain. Stop
Uvicorn with Control C, restart with the same command, and refresh the same profile
URL. **Reenter the local key**: backend restarts invalidate sessions, not saved data.
Assignment, original inquiry, conversion, edits and archive state remain in SQLite.

Generated keys normally persist in a private, installation-specific directory under
the operating system's temporary directory, outside the repository and frontend root.
The directory/file use private Unix permissions. If macOS clears that directory,
`python -m app.staff` generates new keys; client records are unaffected. Never commit
credential files. `ELCCC_ACCESS_PATH` can select an operator-controlled location outside
the served root; automated tests use disposable paths and synthetic keys only.

Cookies are HttpOnly, SameSite Strict and valid for at most eight hours. The browser
shares the local staff session across profile tabs; no key is stored in JavaScript
storage or the profile URL. Use **Sign out of staff access** when done. Sign-in/sign-out changes are broadcast to
other open tabs so their cached staff views are rechecked. Frontend and
backend must use a consistent hostname: prefer 127.0.0.1 for both. localhost on both
ports is supported; mixing the two hostnames does not share staff cookies.

## What is persistent, simulated, and deferred

| Feature | Current behavior |
| --- | --- |
| Inquiry, ID, conversion, edits, original details, history | SQLite, preserved |
| Profile route | Stable UUID query URL; protected data is fetched after local staff access |
| Assignment/change/removal | SQLite, confirmed, revision-checked and recorded in activity |
| Counselor eligibility | Persistent active/accepting-assignment roster flags; not a live calendar |
| Caseload and ownership | Backend scopes active established clients to their assigned counselor |
| Invitation status | Existing persistent manual tracking, no messages or account verification |
| Intake, appointments and clinical exercises | Existing page-session simulations; not durable services |
| Staff sessions | Local testing credentials and server-side role/record checks; expire/restart invalidates |
| Production identity, secure intake, scheduling, external integrations | Not implemented |

The profile Appointments section does not invent bookings. Its intake section
identifies persisted versus session-only steps. The original directory tab retains
existing session care/appointment activities. Historical counselor session testing
remains under `?tools=1` → Session workflow testing; it does not replace the persisted
caseload. Session referral actions do not save persistent counselor assignments.

Valant, Calendly and MYIO remain disconnected. No live invitations, messages,
reminders, billing or clinical collection are enabled.

## Backend and access structure

Additive tables: `counselors` and `client_assignments`; existing records are not rewritten
or inferred by name. Existing conversions receive no automatic assignment. Counselor
preferences stay in their original preference data. Assignment updates are transactional,
use the existing revision check, and append activity without replacing history.

- `POST /api/staff/login` accepts a local test key and issues a staff cookie.
- `GET /api/staff/session`, `POST /api/staff/logout` check/end the session.
- `GET /api/counselors` returns roster metadata to staff.
- `POST /api/inquiries/{id}/assignment` requires administrator access, `confirmed: true`,
  `expected_revision`, and `counselor_id` (nullable to remove). Only active established
  clients and eligible counselors are accepted.
- `GET /api/counselors/{id}/clients` returns a scoped, alphabetized caseload and count.
  Administrators may inspect any counselor; counselors may inspect only their own.
- Management responses add `assigned_counselor_id` and `assignment_updated_at`.
- All saved inquiry/profile read routes now require staff access. Broad directory
  reads and management mutations require administrator access. Counselor reads of
  individual profiles/original inquiries require active established ownership.
- Public synthetic inquiry creation and `/health` remain available without sign-in.
  Public creation returns only the submitted inquiry, not someone else's record.
- Staff API responses use `Cache-Control: no-store`. Foreign-origin writes are rejected;
  credentialed CORS is limited to the two explicit local frontend origins.

Authorization is centralized in `staff`, `administrator`, and `readable_record` backend
checks. Future identity providers should replace local-key/session issuance while
retaining tested operation/ownership rules. Do not trust frontend role selection,
headers, counselor query IDs, or a hidden button as proof of authorization.

## Production prerequisites

These keys represent shared **test roles**, not verified individual staff identities.
Sessions and login throttling are in memory in one process. Cookies are not marked
Secure because this preview is HTTP on loopback. No clinical-data security readiness
or HIPAA compliance is claimed. Keep both servers local and use synthetic records only.

Before real use: individual identity and MFA, managed account lifecycle, HTTPS/Secure
cookies, reviewed CSRF/session controls, durable distributed session/rate limiting,
least-privilege permission review, audit actor identity, access monitoring, encryption
and key management, protected backups/retention, privacy/security review and HIPAA
readiness assessment. Persist approved intake and appointment workflows only after
those foundations are reviewed. Evaluate optional Valant/MYIO integration separately.

## Tests

With the backend virtual environment active, from `backend`:

```bash
python -m unittest discover -s tests -v
```

From the repository root, run the existing eight frontend suites plus:

```bash
node scripts/check-profile-pages.mjs
npm run build
```

Browser checks require Playwright/Chromium in the Python interpreter running them:
`python -m pip install playwright` then `python -m playwright install chromium`.
Stop your own servers first: checks use ports 5500/5501/8000 and temporary databases.

```bash
BACKEND_PYTHON="$PWD/backend/.venv/bin/python" python scripts/check-counselor-profiles.py
BACKEND_PYTHON="$PWD/backend/.venv/bin/python" python scripts/check-public-request.py
BACKEND_PYTHON="$PWD/backend/.venv/bin/python" python scripts/check-backend-integration.py
BACKEND_PYTHON="$PWD/backend/.venv/bin/python" python scripts/check-client-actions.py
```

The new browser suite tests real new-tab navigation with no routing overrides,
protected direct links, section navigation, editing/cancellation, assignment lifecycle,
counselor isolation/read-only access, archive/restore, four widths and an actual backend
restart followed by reauthentication. Earlier component suites retain their inline
profile harness to continue testing the established components; they do not bypass
staff authorization. The existing four static browser suites test the retained
historical simulations and responsive navigation at port 4173 using `npm run dev`.
