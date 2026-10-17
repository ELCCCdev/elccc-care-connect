# Intake, navigation, and client actions review

Review branch: `codex/elccc-intake-navigation-review`.

## What was recovered

The supplied workspace was clean on `work` at `ce57cee` (the October 11 role-navigation merge).
GitHub contained later development through `2474634` on
`codex/elccc-counselor-profile-pages`: local staff access, stable separate-tab client
profiles, persistent editing/archiving, and authorized counselor assignments. Those
changes were already committed and pushed. This review builds directly on that
commit and preserves its history. No saved Intake/header/selection-toolbar changes
were found in the supplied working tree or the latest pushed profile branch;
unsaved work from the interrupted conversation could not be recovered.

## Current selection and onboarding refinements

Client rows now contain only record information and a selection checkbox. Click a
row once to select it, again to deselect, or click another row to switch selection.
Space and Enter toggle a focused row; the checkbox supports keyboard selection.
Only the toolbar above the list offers View, Edit and Archive (or Restore for archived
records). No selection means all toolbar actions are disabled. Filtering, switching
lists, archiving, and signing out clear selection. View still opens a separate tab.

Within a profile, Intake follows Overview in navigation and page order. Its grouped
checklist begins with a saved setup progress indicator derived from the stored inquiry,
conversion, counselor assignment, and invitation-tracking fields. Session-only intake
and appointments are separate; planned questionnaires and communications are
expandable. Setup progress does not claim intake completion or portal activation.

Convert to Client is a primary action in a separate Overview card above the record
facts. Confirmation explains the move to Established Clients, preserved history,
and unchanged assignment/invitation/booking state. Saving disables repeat actions;
already-converted records show completion instead. Existing backend authorization,
serialized conversion, duplicate rejection, storage, and API routes are unchanged.

## Original review changes

- Intake follows Overview in Admin navigation. Overview has a prominent Review
  Intake shortcut. Intake lists active saved prospective and established records
  and opens the existing profile checklist in a separate tab.
- Signed-in local staff see Administrator or Counselor and Sign Out in the header,
  including with mobile navigation collapsed. Logout failure is visible; successful
  logout clears cached staff data and selections, leaves profile URLs, returns to
  welcome, and invalidates other open tabs through the existing session mechanism.
- Both client lists have a selected-client toolbar with View, Edit, and Archive.
  Click a plain row, choose its checkbox, or focus the row and press Space.
  Toolbar View retains separate-tab profiles.
  Changing filters clears selection and disables the toolbar. Archive still requires
  confirmation and remains reversible; archived records offer Restore.
- Existing counselor assignments, saved records/history, workflows, and deployment
  configuration remain intact. Intake completion remains session-only, as before.

## Test locally on a Mac

Stop the old servers with **Control+C**. Open Terminal in your existing repository
folder. Keep any personal edits safe before switching branches; do not reset or
remove your SQLite database.

```bash
git fetch origin
git switch --track origin/codex/elccc-intake-navigation-review
cd backend
```

If this local branch already exists, use `git switch codex/elccc-intake-navigation-review`.
If you do not already have a virtual environment, create it with
`python3 -m venv .venv`. Then start the backend:

```bash
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Leave that Terminal running. In a second Terminal, open the repository's `backend`
folder and display the local test access keys:

```bash
source .venv/bin/activate
python -m app.staff
cd ..
python3 scripts/serve-local.py
```

Open **http://127.0.0.1:5500** and hard refresh with **Command+Shift+R**.
Choose **I'm an Administrator**, enter the administrator test key, and choose
**Open staff workspace**. Keys stay local; do not commit or share them.
Use the existing database path; the default is `backend/data/inquiries.sqlite3`.
Use synthetic records only, such as `Test Alex River`, `alex@example.com`, and
`202-555-0100`. This is still a local development prototype.

1. Confirm **Overview → Intake → Clients** order. Choose **Review Intake**, then
   open a record's checklist. The profile opens in a separate tab.
2. In **Clients → Prospective Clients**, select a row. Use toolbar **View**,
   **Edit → Cancel**, then **Archive → Cancel**. Confirm no canceled changes save.
   Test confirmed archive and Restore on a disposable test record if desired.
3. Convert a test profile, then repeat in **Established Clients**. Confirm the
   original inquiry reference/history and counselor assignment remain.
4. Tab to the row; Space or Enter toggles selection. Tab to toolbar
   buttons and use Enter. Escape closes an edit/archive dialog. Search for a name
   that hides the selection; toolbar actions should become disabled.
5. Narrow the browser or use Chrome DevTools device mode at 375px. Staff role and
   **Sign Out** stay visible, and the toolbar wraps without horizontal scrolling.
6. Keep two profile tabs open, then **Sign Out**. The current tab returns to welcome;
   other profile tabs require staff access again. Sign back in and confirm saved
   edits/assignments remain after refresh.
7. Sign in with a counselor test key to verify that counselor's assigned caseload
   and read-only profiles. Saved assignment editing remains administrator-only.

## Automated checks

From the repository root:

```bash
for script in scripts/check-*.mjs; do
  case "$script" in *browser*|*responsive*) continue;; esac
  node "$script" || break
done
npm run build
(cd backend && source .venv/bin/activate && python -m unittest discover -s tests)
```

Browser checks require Playwright separately in the test environment. Python browser
checks create disposable databases and need free ports 5500/8000, so stop the manual
servers first. On a Mac, point `CHROMIUM_PATH` at an installed Chromium executable
(for example `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`) or use
Playwright's installed Chromium for the Python checks. See the existing profile
and backend documentation for test setup and individual commands.

Verification in this session used headless Chromium, viewport emulation, disposable
SQLite databases, and synthetic staff credentials. Safari, physical iPhones,
screen readers, and production authentication are outside this verification.
No merge or deployment was performed.

### Results for this review

Passed: 38 backend unit/API tests; all nine Node regression scripts; static build;
all four JavaScript browser suites and all four Python browser integration suites.
The responsive suite covered ten widths (320–1920px), ten pages, expanded menus,
and five dialog types. New profile checks covered Intake navigation, toolbars in
both lists, keyboard selection, canceled actions, filter isolation, visible mobile
staff controls, logout failure/success, cross-tab invalidation, saved counselor
assignments, and backend restart persistence. After the final mobile row adjustment,
the profile suite and build passed again. Directory screenshots at 375px and 1280px
were visually inspected; whitespace validation passed.

The current refinements also verify repeated click deselection, switching between
fictional records, clearing selection even when changed filters still match, list
switching, profile Intake position, conversion cancellation, duplicate conversion
rejection with unchanged history, and saved progress updates across reloads.

### Verification of the selection and onboarding refinements

The revised checks passed using only synthetic records and disposable SQLite files:
38 backend unit/API tests, nine Node regression checks, four JavaScript browser
suites, four Python browser integration suites, the static build, and whitespace
validation. Checks include selection/deselection by click and keyboard, switching
records and lists, clearing selection on filters/archive, toolbar-only actions,
separate-tab navigation, Intake position, grouped tasks, real saved progress changes
and reload persistence, canceled and duplicate conversion, preserved inquiry history,
assignment permissions, anonymous access denial, sign-out across tabs, and mobile
layouts. The directory and Intake checklist were visually inspected at mobile width.
Safari/iOS, physical touchscreen devices and screen-reader announcements still need
manual review. No authentication, backend implementation, schema, or deployment
configuration was changed.
