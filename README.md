# ELCCC Care Connect

## Current phase: dedicated profiles and counselor assignments

Use branch `codex/elccc-counselor-profile-pages`. Client names, row double-click,
and View/Open profile open a separate tab with a stable inquiry UUID URL. Established
clients can be assigned/reassigned/unassigned with confirmation; assignments and history
persist. Counselor dashboards show backend-scoped caseloads and read-only profiles.

Saved records now require **local staff access**; role selection alone is insufficient.
Use `python -m app.staff` in the backend folder to display your generated local test keys.
Use `python3 scripts/serve-local.py` from the root for port 5500; do not serve the whole
repository with `python -m http.server`. The preview server blocks backend/database files.
See [Mac setup, walkthrough, access limits and tests](docs/COUNSELOR_PROFILE_PAGES.md).
Synthetic data only. Local staff sessions are not production-ready authentication;
no real patient collection, live scheduling or external integrations are enabled.
The older phase notes below describe historical branch behavior.


ELCCC Client Portal, Counselor Workspace, and Administrative CRM stakeholder prototype built as a dependency-free, single-file `index.html` application using mock data only.

## Local preview

```bash
npm run dev
```

Open:

```text
http://localhost:4173/
```

## Static build

```bash
npm run build
```

The build output is written to `dist/` and is ready for static hosting.

## GitHub Pages deployment

This repository includes a GitHub Actions workflow at `.github/workflows/deploy.yml` that builds `dist/` and deploys it to GitHub Pages.

To publish publicly from GitHub:

1. Push this branch to GitHub.
2. In GitHub, open **Settings → Pages**.
3. Under **Build and deployment**, set **Source** to **GitHub Actions**.
4. Open the **Actions** tab.
5. Run **Deploy static prototype to GitHub Pages** manually, or push to `main`/`work`.
6. After the workflow finishes, open the URL shown in the workflow summary. It will usually be:

```text
https://<github-username>.github.io/<repository-name>/
```

All data displayed in the prototype is mock/demo data. The app includes the disclaimer: “Prototype only — no real client or medical data.”


## Version 2: connected fictional onboarding

The deployed entry point remains `index.html`; `src/` contains the original reference modules and is not part of the static build. Existing branding, directory and filters, match quiz, resources, dashboards, profiles, demo role chooser, and presentation brief are retained. GitHub Pages configuration and build scripts are unchanged.

1. Choose **Start Demo Counseling Request** on Home, or request a booking from an existing counselor profile.
2. Select a fictional client and submit. Names are preset; no contact details or personal information are collected.
3. Open **Admin CRM**. In **Interactive Demo Onboarding**, review and mark the request contacted, assign an available counselor, then confirm a date and time.
4. Open **Counselor Dashboard** and select the assigned demo counselor to see the referral and appointment.
5. Open **Client Portal** and select the fictional request to see its status, counselor, and confirmed appointment.

The shared in-memory request collection also feeds CRM pipeline counts, appointment requests, and connected dashboard metrics. Legacy sample panels remain demonstration fixtures. New requests remain separate from existing sample client profiles. Navigation and Home are available across roles without authentication. Refreshing the page resets all new requests; no storage, network submission, medical records, authentication, or production integrations are added. Appointment times are labeled Eastern Time. Past dates and duplicate demo counselor slots are rejected; this is not a real availability service.

### Validation

Run `node scripts/check-workflow.mjs` and `npm run build`.

The dependency-free functionality check executes the actual inline application script with a lightweight DOM/event harness. It covers request submission, review, assignment, scheduling, shared role views, counselor filtering, past-date rejection, slot conflicts, existing views, and profile/role/presentation modals. The static build creates matching index/404 outputs and `.nojekyll`.

The original Version 2 checks used a lightweight DOM harness; the responsive update below adds real Chromium checks. No real data or production services are exercised.

## Responsive usability update

Navigation now follows normal document flow, with a collapsible menu at widths up to 1100px. Home and workflow role links remain visible. Containers, dashboard metrics, cards, CRM columns, tables, and forms adapt to their available width rather than requiring browser zoom changes. Headings and spacing are smaller, touch controls have a minimum 44px height, and dialog content scrolls within the viewport. The app retains all existing fictional records and workflow logic.

Keyboard support includes a skip-to-content link, visible focus indicators, current-page markers, announced menu expansion, Escape to close menus/dialogs, dialog names, focus containment, background inertness, and focus restoration. Role selection remains a demo without authentication.

### Browser validation

With the dev server running, run `node scripts/check-responsive.mjs`. This optional QA script requires Playwright in the test environment and Chromium at `/usr/bin/chromium` (override with `CHROMIUM_PATH`). The application remains dependency-free. Set `PROTOTYPE_URL` to test another local preview URL.

Verified in headless Chromium at 100% zoom: 320, 375, 390, 480, 640, 768, 1024, 1280, 1440, and 1920px widths. All seven views, expanded navigation, and five dialog types were checked for horizontal overflow. Browser controls exercised the complete fictional request, admin review, counselor assignment, appointment scheduling, counselor visibility, and updated client status at mobile width. Menu expansion/Escape and dialog keyboard focus trapping passed, without JavaScript errors. Mobile and laptop Admin screenshots were visually inspected. The existing workflow harness, static build, and whitespace checks also pass.

Testing limitations: Firefox, Safari/iOS, real touchscreen devices, on-screen keyboards, screen readers, high contrast modes, and an exhaustive WCAG audit were not tested. Viewport emulation does not substitute for those devices. New requests remain session-only, and refresh intentionally resets them. No deployment was run. The GitHub Pages workflow and build script are unchanged; the review branch is outside the existing `main`/`work` deployment triggers.

## Phase 2: interactive counselor workspace and client portal

The selected fictional client now controls the Client Portal greeting, appointment details, intake, homework, and confirmations. Existing sample clients and newly submitted requests retain separate in-memory activity records. Counselor selection filters assigned clients, schedules, workspace tasks, and rescheduling information. Sample appointment dates are retained as fixtures rather than replaced with invented live bookings.

Counselors can open an assigned client's detailed workspace, assign preset homework with an optional future due date, review submitted homework, and complete or reopen a follow-up reminder. Clients submit preset sample intake answers and sample homework completion. Reschedule requests appear in the Admin CRM and assigned counselor's workspace; approval changes the shared appointment, while decline leaves it unchanged. Pending requests never replace the confirmed appointment. Approval rejects conflicting demo counselor slots.

All actions are fictional and session-only. Refresh resets homework, intake, reminders, requests, and new appointments. There are no uploads, free-text clinical responses, authentication, medical records, external messages, or production integrations. Demo role selectors are presentation controls, not access security.

### Manual testing

1. Open Home, start a demo request for **Jordan Demo**, and submit it. In Admin CRM, mark it contacted, assign **Rachel Kim**, and schedule a future date at **09:00**.
2. Open Counselor Dashboard, select **Rachel Kim**, and choose **Jordan Demo · demo-1** under **Assigned fictional client**. Verify the matching appointment, care status, pending intake, and follow-up reminder. You can also open a workspace using its **Open Workspace** button.
3. Assign **Sample reflection exercise**, optionally choosing a future due date. Complete the reminder and confirm it changes to Completed; reopen it to test the reverse action.
4. Open Client Portal and select **Jordan Demo · demo-1**. Confirm that the greeting and appointment match this client. Choose a preferred sample session and the sample orientation response, then submit intake. Submit the assigned sample homework.
5. Return to Jordan's counselor workspace. Verify intake is submitted and homework status is Submitted. Choose **Mark Homework Reviewed**; confirm the client then sees Reviewed.
6. In Jordan's Client Portal, request a different future date/time. Verify Pending is shown and the current appointment is unchanged. Check the assigned counselor's workspace and Admin CRM for the same request.
7. In Admin CRM, approve it. Verify both client and counselor show the new appointment and Approved status. Submit another request and decline it; verify the confirmed appointment remains unchanged.
8. Submit a request for **Taylor Example**. Switch between Jordan and Taylor in the portal and confirm their greeting, intake, homework, appointment, and confirmations remain separate. Switch counselors and verify Jordan is absent from unrelated counselor workspaces.
9. Try approving a reschedule that conflicts with another appointment for the same counselor: approval should be blocked. Try past dates and incomplete intake selections. Check narrow mobile widths, keyboard navigation, role links, and Home.
10. Refresh and confirm session data resets while the original fictional fixtures remain available.

### Automated checks and limits

Run `node scripts/check-workflow.mjs`, `node scripts/check-workspace.mjs`, and `npm run build`. With the preview server and test-environment Playwright/Chromium available, run `node scripts/check-responsive.mjs`.

The workspace harness covers assignment/submission/review, intake, reminder completion, reschedule approval/decline, client identity, per-client and counselor separation, and invalid dates. Browser checks retain the original viewport/onboarding coverage and add the complete mobile intake/homework/rescheduling flow plus populated Client/Counselor/Admin layouts. Browser coverage remains Chromium only; Safari/iOS, Firefox, real devices, screen readers, and a full accessibility audit remain unverified. GitHub Pages configuration and the static build script are unchanged. Review only: do not automatically merge or deploy.

## Phase 3: identity, appointment changes, and care activities

Client Portal identity and every care panel use one selected record. The greeting and selectors now explicitly identify **Connected demo request** versus **Sample fixture**, including the record ID. A newly created Taylor Example request does not inherit Taylor Hayes' sample counselor, appointment, intake, or homework. Existing fixtures remain intact, and each record has separate activity state. Counselor selectors expose only clients assigned to that counselor. These selectors are demo controls, not real access security.

Activities now include exercises, reflection questions, reading, and worksheets. Counselors choose a mock template, optionally customize a fictional title/instructions, and optionally set a due date. Clients may enter a fictional text response or submit sample completion without a response. Counselors see the submitted response and mark it Reviewed. Text is bounded and escaped when rendered; no uploads, records, or external messages are created. Do not enter real personal or medical information.

Rescheduling supports an optional preset fictional reason. A requested slot is Pending, never confirmed before admin approval. Approval checks date/time validity and same-counselor slot conflicts and updates the shared confirmed appointment. Decline retains the old appointment. Optional cancellation requests follow the same admin review pattern: approval removes the appointment while retaining counselor assignment and care activities; decline retains it. Only one appointment-change request may be pending per client. After an approved cancellation, a connected request returns to Assigned so Admin CRM can schedule it again.

### Complete Phase 3 walkthrough

1. From Home, submit a request for **Taylor Example**. Select **Track in Client Portal** and verify the greeting, record ID, Connected request label, counseling type, unassigned counselor, and New status. Switch to the **Taylor Hayes** sample fixture and confirm its original details are different. Switch back to Taylor Example.
2. In Admin CRM, review and mark the connected request Contacted, assign Rachel Kim, and schedule a future date at 09:00. Verify the identical confirmed appointment in Client Portal and Rachel's Counselor Dashboard. Open this exact request under Assigned fictional client.
3. In the counselor workspace, select each mock activity type (reflection, exercise, reading, worksheet). Optionally enter a fictional title and instructions and a future due date. Assign the activity. Verify only this client's portal shows it, including its instructions, due date, and Assigned status.
4. In the selected client's portal, complete the sample intake and enter a response such as “In this fictional scenario, I practiced the sample routine.” Submit homework, verify Submitted, then mark it Reviewed in the counselor workspace. Verify Reviewed and the same response in the portal. Repeat an activity with no response to try sample completion.
5. Request a different future date/time, with or without a preset reason. Verify the requested slot is labeled Pending and the old appointment remains confirmed in all roles. Approve in Admin CRM and confirm the new slot in client, counselor, and admin views.
6. Submit another reschedule and decline it. Confirm Declined and the existing confirmed slot is unchanged. Schedule another fictional client with Rachel at a different slot; request that occupied slot from the first client. Approval must be rejected without changing the appointment.
7. Submit a cancellation request. Verify Pending while the original appointment remains confirmed. Decline once and confirm the appointment remains. Request again and approve; verify Cancelled/no confirmed appointment across roles, while activities and counselor assignment remain. Admin can schedule the connected request again from its Assigned stage.
8. Switch to a different client and counselor. Verify greeting, appointment, activity responses, completion/review state, and request outcomes stay with the correct record. Repeat at mobile widths and with keyboard navigation. Home and role navigation remain available.
9. Refresh the page. All connected requests and activity changes reset; original sample fixtures remain. Separate tabs do not share state.

### Phase 3 checks and limitations

Run `node scripts/check-workflow.mjs`, `node scripts/check-workspace.mjs`, `npm run build`, and, with the dev server running, `node scripts/check-responsive.mjs` in a Playwright/Chromium test environment. Workspace regression checks include client/counselor isolation, reschedule approval/decline/conflicts, custom activity instructions, escaped text responses, submission/review, optional reasons, and cancellation approval/decline. Browser checks exercise the same actions through mobile controls and retain viewport/layout and onboarding regression coverage.

State is JavaScript memory within one browser page. Refresh or closing the page discards it; there is no storage, sync, authentication, clinical record system, messaging, or external integration. Request panels retain the latest outcome of each change type, not an audit history. Original sample appointment fixtures have dates without exact time slots; conflict detection covers explicit appointments scheduled in this demo. Dates/times are labeled Eastern Time and slots are simplified mock choices, not real availability. Safari/iOS, Firefox, physical devices, screen readers, and a full accessibility audit remain unverified. GitHub Pages configuration and the static build script are unchanged. This phase is submitted for PR review without deployment or automatic merging.

## Phase 4: operational and fictional clinical experience

Phase 4 builds on all earlier workflows. Friendly **Referral** and **Sample profile** labels replace technical identifiers in visible content; internal IDs remain unchanged for state and event handling. Switching from the selected client's portal into Counselor Dashboard opens that assigned client, and switching back preserves that context. Original sample records remain separate.

### Appointments and daily operations

Admin CRM has **Appointment Approval Routing**: Administrator managed, Counselor managed, or Configure per client. New reschedule and cancellation requests snapshot their approver (and assigned counselor), original appointment, and request events. Routing changes apply to future requests only. Both admin and assigned counselor can view requests, but only the snapshotted approver can approve, decline, or propose a rescheduling alternative. The client must accept an alternative, after which the approver must finalize it; the original appointment stays confirmed until final approval. Decline retains the original. Appointment snapshots and request events are available under **Appointment & request history**; notifications are scoped to the client.

Counselor **Daily Operations** includes an interactive date agenda, appointment detail buttons, assigned-client task links, request decisions, and simulated availability. Sessions are 60 minutes. Configurable 09:00–17:00, morning, or afternoon hours and an optional 11:00–12:00 hold apply to new bookings and change approvals. Overlapping intervals for the same counselor are rejected, including different start times such as 09:00 and 09:30. Already confirmed appointments are retained if hours are changed. Historical sample dates have unspecified times and cannot participate in precise overlap checks. Hours apply every demo day; there is no real calendar, timezone conversion service, reservation system, or live availability.

Counselors can still assign/review homework and complete/reopen reminders, and now provide fictional feedback. Submitted homework and screening review count as outstanding tasks. Clients see only their selected record's activities, clinician-authored plan, request decisions, and sample notifications.

### Fictional assessments and documentation

The assigned counselor can switch between **Authorized clinician demo** and **Care coordinator demo — read only**. Only the authorized clinician mode can assign/review screening, author diagnosis documentation, and assign treatment-goal homework for that assigned client. Client and admin roles cannot edit diagnosis documentation. These are simulated UI/action checks, not production authentication or authorization.

Two original, invented three-item screenings use preset responses (0, 1, or 2). The demo score is their sum (0–6), without validated thresholds or diagnostic interpretation. No proprietary assessment instrument is reproduced. Submission, scoring, and review **never create, populate, or confirm a diagnosis**. Diagnosis documentation is a separate manual clinician action requiring a fictional rationale, treatment goal, follow-up plan, and acknowledgement. Illustrative ICD-10-CM examples are Z63.0 (relationship problem context) and F43.21 (adjustment disorder with depressed mood); no code recommendation or real clinical service is provided. Provisional/Confirmed are explicitly clinician-selected mock states. Related homework is assigned separately and stays scoped to the client.

### Integration Center and Demo Tour

Primary navigation now includes **Integration Center** and **Demo Tour**. Integration cards cover EHR/practice management (Valant as an illustrative candidate), telehealth (Doxy.me/Zoom as illustrative candidates), calendar/scheduling, billing/insurance, and messaging/reminders. Each shows purpose, proposed data flow, fictional-only configuration, simulation enable/disable status, and a sync preview. **None is connected**. Daily cadence is a configuration illustration, not a running job. No credentials are requested; no API requests, real records, reminders, meeting links, or eligibility checks are sent.

The Tour links a logical referral → intake coordination → daily operations → client activities → clinical review → appointment decisions/follow-up → integration roadmap sequence. It does not overwrite existing state or silently create client records.

### Stakeholder walkthrough

1. Open Demo Tour, then Home. Submit Jordan Demo or Taylor Example. In Admin CRM mark contacted, assign Rachel Kim, and schedule a future date at 09:00. Verify identity and appointment in Client Portal and the assigned counselor workspace.
2. Choose **Counselor managed** approval routing. In the selected Client Portal request a different date at 11:00. Admin sees the request but has no final decision buttons; Rachel's Daily Operations shows the assigned approver and controls.
3. Rachel proposes a valid alternative date at 14:00. The client accepts it. Verify the old appointment remains confirmed until Rachel approves; then all roles show the new appointment. Expand history to see original/requested slots and proposal, acceptance, and final decision events.
4. Switch routing to **Configure per client**, save Administrator for this client, and submit a cancellation. Confirm Rachel can view but not finalize. Decline as admin and verify the confirmed appointment remains. Repeat with approval to remove it; schedule again from Assigned if desired. Try a conflicting or unavailable slot and confirm it is rejected without replacing the appointment.
5. In Daily Operations set the agenda date to a scheduled date and open its appointment details. Configure morning-only availability or the mock hold. Open Tasks, complete/reopen a reminder, and review homework. Changes are visible in the client's record.
6. In the counselor workspace's clinical panel choose Authorized clinician demo and assign a fictional wellbeing check. In Client Portal complete its three preset questions. Verify the sample sum and **no diagnosis documentation**. Review the screening as clinician; still no diagnosis should be generated.
7. Switch to Care coordinator mode and verify diagnosis edit controls disappear. Return to Authorized clinician, manually enter a fictional rationale, goal, follow-up, and acknowledgement. Save Provisional, then explicitly select Confirmed and save again. Verify client plan visibility and that another client/counselor cannot edit or see this client's details.
8. Assign goal-related homework. Submit a fictional response as the client. Add fictional feedback as counselor; verify Reviewed and matching feedback in the portal. Review sample notifications and request history.
9. In Integration Center save mock configuration, enable/disable simulation, and preview each of the five cards. Every status/preview must clearly say not connected/zero records sent. Return through Home and role links, test a narrow viewport and keyboard navigation, then refresh to demonstrate session reset.

### Checks, limitations, and future production requirements

Run `node scripts/check-workflow.mjs`, `node scripts/check-workspace.mjs`, `node scripts/check-operations.mjs`, and `npm run build`. With the local dev server and test-environment Playwright/Chromium available, also run `node scripts/check-responsive.mjs` and `node scripts/check-operations-browser.mjs`.

Tests cover original workflows, approver snapshots/restrictions, alternatives, appointment history, overlap/availability conflicts, client isolation, clinician-only documentation, screening/diagnosis separation, feedback, and integration previews. Browser checks exercise the stakeholder sequence and responsive views, and verify that integration interactions issue no external requests. Coverage remains Chromium; Safari/iOS, Firefox, real touch devices, screen readers, full WCAG compliance, and clinical validity are not verified.

All state is in one page's JavaScript memory and resets on reload; separate tabs do not share it. Unsaved form drafts may be lost when changing views. History is an in-session demonstration, not a durable or tamper-resistant audit trail. No real patient data, PHI storage, authentication, clinical services, or external integrations are introduced. The existing GitHub Pages workflow and build script are unchanged; this feature branch does not trigger deployment.

A production project would separately require server-enforced identity and role permissions, consent and privacy design, secured data storage and retention, audited change history, concurrent appointment reservations, real availability/timezone rules, clinician-reviewed/licensed assessments and coding processes, approved vendor contracts and credential handling, reliable notification delivery, and cross-browser/accessibility/security verification. Those capabilities are intentionally not implemented in this prototype.

## Presentation readiness polish

The Admin CRM now starts with **Overview**, followed by separate **Appointment Requests**, **Care Journey**, **Prayer Requests**, **Client Profiles**, **Approval Settings**, and **Sample Reports** work areas. Overview totals are calculated from their stated sources: session referrals and confirmed session appointments are separate from historical sample profiles. Pending decisions span fictional profiles; prayer follow-up counts include both historical and session queues. Historical chart data is illustrative, not live operational performance. Historical sample appointment dates are not counted as upcoming counselor appointments.

### Stakeholder walkthrough

1. Open **Demo Tour** from the main navigation. Use the Home/Client/Admin/Counselor role links throughout; they are simulated roles, not sign-in.
2. From **Find a Counselor**, submit a preset fictional counseling request. Choose **Switch to Administrator Demo**. Under **Appointment Requests**, mark it contacted, assign a counselor, and schedule a future appointment. Alternatively, use **Create Fictional Referral** on a historical referral example to create an independent session copy; the archive remains unchanged.
3. Return to **Overview** to verify the session referral and confirmed appointment counts. Historical center examples are available in the expandable activity area and **Sample Reports**.
4. In **Client Profiles**, choose a fictional profile, expand its details, and complete an administrative follow-up. The feedback names that profile; switching profiles keeps follow-up state separate. Open its assigned counselor workspace when available.
5. In **Approval Settings**, choose admin, counselor, or configured routing. In Client Portal request a reschedule or cancellation. Open **Appointment Requests** or the assigned counselor's daily operations to approve, decline, or propose an alternative. An alternative requires client acceptance and approver finalization. Confirm the original appointment stays intact until approval and inspect request history afterward. Overlapping slots and simulated unavailable hours remain rejected.
6. In Counselor Dashboard, select the assigned client. Use the section links to jump to daily operations, homework, **Assessment & Screening**, or **Diagnosis & Treatment Planning**. Assign homework and an invented screening activity; complete them in the selected Client Portal and review them as the counselor.
7. Screening scores never populate diagnosis documentation. In the separate treatment-planning section, only the simulated authorized clinician can manually author fictional documentation. Switch the workspace permission to care coordinator to demonstrate read-only restrictions. No diagnosis is generated or automatically assigned.
8. In Admin **Prayer Requests**, submit a preset fictional prayer request, mark it prayed, and complete fictional follow-up. The queue and overview follow-up total update; no message is sent. Public prayer submission uses the same queue and only offers fictional presets.
9. In **Integration Center**, inspect the plain-English purpose of each proposed connection, optionally expand technical information, save demo settings, enable a simulation, and preview it. Every connection remains explicitly **not connected** and sends **zero records**.
10. Refresh the page to demonstrate that session-created referrals, prayers, follow-ups, assignments, and decisions reset. No browser storage or external service persists them.

### Validation

Run `npm run build`, then these Node regression checks:

```sh
node scripts/check-workflow.mjs
node scripts/check-workspace.mjs
node scripts/check-operations.mjs
node scripts/check-presentation.mjs
```

With `npm run dev` running and Playwright plus Chromium available in the test environment:

```sh
node scripts/check-responsive.mjs
node scripts/check-operations-browser.mjs
node scripts/check-presentation-browser.mjs
```

Browser checks cover ten widths from 320 to 1920 pixels, existing role pages and dialogs, keyboard modal behavior, complete mobile onboarding/homework/appointment flows, clinical permissions, integration previews, prayer/profile actions, and all seven Admin areas at six widths. New presentation checks verify source-specific metrics, historical copies, isolated follow-ups, separate screening/planning, and tour navigation.

### Remaining limitations

This is a fictional presentation prototype. Permissions are client-side simulation controls and provide no security boundary. Date availability, reporting, scoring, diagnoses, feedback, and administrative follow-up are mock examples; they are not clinical services or validated instruments. Use fictional text only. Browser state lasts only in the current page, does not synchronize across tabs/devices, and resets on reload. There are no real connections, credentials, uploads, messages, insurance checks, payments, authentication, or protected health information storage. Static GitHub Pages configuration is unchanged.

Automated browser validation uses local headless Chromium and simulated viewport sizes. Safari, Firefox, physical devices, screen-reader announcements, and stakeholder usability sessions require separate manual review. Future production use would require secure authentication and authorization, consent and privacy controls, protected storage, audit trails, clinical governance, validated/licensed assessments, accessibility review, and separately approved integrations.

## Role-based welcome and demo navigation

The prototype starts on a welcome screen with **I'm a Client**, **I'm a Counselor**, and **I'm an Administrator**. Each choice opens the existing role dashboard. **Explore Services or Request Care** opens the public counseling pages without selecting a dashboard role or signing in. Home returns to the welcome screen; Explore Services retains the original public experience.

Navigation follows the selected presentation perspective:

- Client: Client Portal, public counseling services, match quiz, resources, and the client-relevant tour steps. No Admin CRM, Integration Center, administrative reports, or counselor caseload links.
- Counselor: Counselor Dashboard, public services/resources, and relevant tour steps. Administrator-only approval settings and integrations remain in the administrator perspective.
- Administrator: Admin CRM, Integration Center, administrative sections, public pages, and the complete stakeholder tour. Tour steps that open another role explicitly identify the perspective switch.

**Switch Demo Role** stays visible in the header, including when the mobile navigation is collapsed. Choose a role and continue; the current fictional session is retained. These controls provide presentation scoping only, not authentication, authorization, privacy, or security guarantees. Existing clinician and appointment approval checks remain simulated workflow rules.

Client Portal displays a stable fictional reference next to the selected client's name. Taylor Hayes's historical sample reference is **ELCCC-10024**; session referrals use a separate **ELCCC-20001** series. IDs identify fictional records and are not login credentials. Switching clients updates the name, reference, appointment, intake, and activities together. Session references and state reset on reload.

### Updated entry walkthrough

1. Start with **Explore Services or Request Care** or **I'm a Client**. Use a preset fictional care request.
2. After submission, **Track in Client Portal** opens the client perspective. **Switch to Administrator Demo** is an explicit presenter shortcut to the appointment review workflow.
3. Mark contacted, assign a counselor, and schedule. Use **Switch Demo Role** to preview the assigned counselor and client perspectives; use the same selectors and activities described above.
4. Switch to Administrator before opening approval settings, reports, or integration simulations. Continue the existing rescheduling, cancellation, homework, prayer, and clinical walkthroughs through their appropriate perspectives.
5. Return Home to inspect the **New Client Journey**: inquiry, intake, counselor assignment, scheduling, and ongoing care. The same explanation is available on the public services page.

All prior workflows remain available. Cross-role workflow navigation now uses explicit role switching instead of showing every dashboard link to every user. Public services no longer expose administrator dashboard shortcuts outside the administrator perspective. Existing prototype warnings and static GitHub Pages configuration remain unchanged.

Additional regression checks:

```sh
node scripts/check-roles.mjs
node scripts/check-roles-browser.mjs
```

Role checks cover welcome choices, navigation/tour scoping, visitor exploration, reference-ID isolation, session preservation, complete cross-role onboarding, keyboard switching, and six widths from 320 to 1920 pixels. The existing responsive suite now also includes the welcome screen (ten pages at ten widths) and updated role-dialog focus trapping. Browser testing remains local headless Chromium; Safari, Firefox, physical devices, screen-reader review, and the live Pages site were not tested. All data is fictional and lives only in page memory; no real credentials, clinical data, backend, or integrations were added.


## Phase 2: local persistent counseling inquiries

The Request Counseling form connects to the Phase 1 FastAPI backend **only** when
opened at `http://127.0.0.1:5500` or `http://localhost:5500`. Public GitHub Pages
and other origins retain the existing static fictional scenarios without calling
the backend. No deployment changes are included.

This is a local, fictional-data development prototype. Never enter real client
or patient information. There is no authentication, authorization, or HIPAA
compliance. CORS permits only those two local frontend origins; it is not an
access-control boundary.

### Start locally on a Mac

Use two Terminal windows. Select branch `codex/elccc-backend-phase-2` in your
existing clone first (`git fetch origin`, then `git switch codex/elccc-backend-phase-2`).

In Terminal 1, from the repository's `backend/` directory (Python 3.9+):

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

In Terminal 2, from the repository root:

```bash
python3 -m http.server 5500 --bind 127.0.0.1
```

If Live Server is already serving the repository at port 5500, keep using it
instead of starting another frontend server. Leave both servers running. Open
**http://127.0.0.1:5500**. Restart the backend after pulling the CORS changes.

### Create and review a persistent fictional inquiry

1. Choose **Explore Services or Request Care**, then **Find a Counselor**.
   Choose an available counselor's **Request Counseling** button.
2. Choose a preset fictional client, support pathway, session format, and contact
   preference. Check the fictional-data confirmation and click **Submit Fictional
   Request** once.
3. Wait for **Saved to the local development database** and its inquiry UUID.
   Failed requests show an error and do not create a pretend successful referral.
4. Click **Switch to Administrator Demo**, or switch demo role to Administrator,
   then open **Appointment Requests**. The **Saved fictional inquiries** section
   loads SQLite records, including the three Phase 1 samples and your new inquiry.
5. Refresh the browser. Select Administrator and Appointment Requests again. The
   inquiry and its UUID remain. **Refresh saved inquiries** retrieves current
   records, including inquiries created through `/demo` or another browser tab.
6. Stop/restart the backend with the same database and refresh the inquiry list.
   Saved inquiries still remain; records are stored at `backend/data/inquiries.sqlite3`.

Only these supported fields are sent:

| Frontend field | Backend field / mapping |
| --- | --- |
| Preset fictional client | `fictional_client_name` |
| Anxiety or Grief pathway | `category: individual` |
| Marriage pathway | `category: couples` |
| Children pathway | `category: family` |
| Contact preference selector | `preferred_contact_method: email` or `phone` |
| Required fictional-data checkbox | `fictional_data_only: true` |

Preferred counselor and session format are **not sent** to the backend. UUID,
initial status `new`, and timestamp are assigned by the server. Existing review,
assignment, scheduling, care activities, and historical scenarios remain session
simulations; their changes do not update SQLite inquiry statuses. Reloading the
page resets those simulated activities while keeping the saved inquiry list.

If the backend is unavailable, start it and retry. If a POST times out, check the
saved list before resubmitting: the server may have saved it before the response
was lost. GET failures keep previously loaded rows and label them potentially
stale. This phase has no automatic retries or persistent scheduling.

### Tests

Backend tests (from `backend/`, with the virtual environment active):

```bash
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
```

Frontend regression checks (from the repository root, with Node installed):

```bash
node scripts/check-workflow.mjs
node scripts/check-workspace.mjs
node scripts/check-operations.mjs
node scripts/check-presentation.mjs
node scripts/check-roles.mjs
```

Optional end-to-end browser check: stop servers using ports 5500, 5501, and 8000.
From the repository root, use a Python environment with the backend test dependencies:

```bash
python -m pip install -r backend/requirements-dev.txt playwright
python -m playwright install chromium
python scripts/check-backend-integration.py
```

The script starts local frontend/backend servers with a disposable SQLite file
and shuts them down afterward. It checks exact payload mapping, CORS, Admin
retrieval, refresh/restart persistence, backend/network error handling, and static
origin isolation. It does not touch your demonstration database.


## Phase 3: prospective clients, conversion, and invitation tracking

Phase 3 adds **Prospective Clients** and **Established Clients** to Admin CRM.
It builds on Phase 2 and uses the same SQLite file. Original inquiry IDs, UTC
creation timestamps, and original inquiry statuses remain unchanged. Backend
startup creates additive management/history tables automatically; do not delete
your existing database. Existing fictional inquiries start as prospective clients
with MYIO tracking **Not Sent**.

### Exact Mac setup commands

Stop the previous backend with Control+C. In Terminal 1, from your existing
`elccc-care-connect` repository root:

```bash
git fetch origin
git switch codex/elccc-backend-phase-3
git pull --ff-only origin codex/elccc-backend-phase-3
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Python 3.9+ is supported. If Git reports uncommitted local edits, preserve them
before switching; do not discard them. Keep this terminal running.

In Terminal 2, from the repository root:

```bash
python3 -m http.server 5500 --bind 127.0.0.1
```

If Live Server is already running on port 5500, use that server instead. Open
**http://127.0.0.1:5500** in Chrome. Use localhost port 5500 only; the public
GitHub Pages version does not call this local backend.

### Walkthrough

1. Submit a preset fictional Request Counseling as in Phase 2, or use the three
   fictional sample inquiries already in the database.
2. Choose **I'm an Administrator** (or Switch Demo Role → Administrator), then
   **Prospective Clients**. Open a fictional profile to review the stored inquiry
   ID, category, contact preference, creation date, and available history. No
   clinical intake fields or real contact details have been added.
3. Choose **Sent** in **MYIO invitation tracking (simulated)** and click **Save
   invitation tracking** while the record is still prospective. The change is
   saved locally and appears in history. No invitation is sent.
4. Click **Convert to Client**. Choose **Cancel Conversion** to leave it unchanged,
   or **Confirm Conversion** to save the conversion. Only confirmed conversions
   persist. The page switches to Established Clients, where the same inquiry ID
   and creation date are retained. It no longer appears in active Prospective Clients.
5. Open the established profile and change invitation tracking to **Activated**.
   This is a manual demonstration status; no MYIO account is verified. Invitation
   tracking can also be changed back to **Not Sent**, independently of conversion.
6. Refresh Chrome, choose Administrator again, and reopen Established Clients.
   Conversion, invitation status, and history remain saved. Stop/restart the backend
   using the same command and database; **Refresh client lists** shows the same record.

The new lists include loading, empty, and error feedback. Refresh updates both
lists and the open profile. Failed writes never display a successful conversion.
After an ambiguous timeout, refresh before retrying. Concurrent/duplicate
conversions return 409 and never create another conversion event or client.

### API and storage

| Method | Route | Purpose |
| --- | --- | --- |
| GET | `/api/prospective-clients` | Inquiries without a conversion |
| GET | `/api/clients` | Established fictional clients |
| GET | `/api/inquiries/{inquiry_id}/management` | Stored profile and available history |
| POST | `/api/inquiries/{inquiry_id}/convert` | Confirmed conversion: `{"confirmed": true}` |
| POST | `/api/inquiries/{inquiry_id}/portal-status` | Tracking update: `{"portal_status": "Sent"}` |

Invitation statuses are exactly `Not Sent`, `Sent`, and `Activated`. Duplicate
unchanged status updates do not add duplicate history events. Conversion uses a
SQLite transaction and the unique original inquiry ID. No duplicate client row
is created. The original inquiry endpoints and Phase 2 request schema are unchanged;
`GET /api/inquiries` still includes all original inquiries, even converted ones.
History includes the original inquiry's creation and subsequent management changes;
there is no invented historical intake or staff identity.

The ELCCC conversion lifecycle and portal tracking are separate from provider
integrations. A future authorized integration can build on this API without
making conversion depend on MYIO. No Valant, Calendly, MYIO, email, or invitation
service is called. No credentials are collected.

### Verification and limits

From `backend/`, with the virtual environment active:

```bash
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
```

The suite includes Phase 2 tests plus conversion, confirmation, competing/duplicate
conversions, legacy SQLite preservation, history, independent invitation updates,
and restart persistence. The optional browser command documented in Phase 2,
`python scripts/check-backend-integration.py`, now also exercises Phase 3 navigation,
confirmation/cancellation, profile review, invitation tracking, error states,
and persistence after page refresh and an actual backend process restart.

All information must be fictional. There is no authentication, authorization,
HIPAA compliance, external portal activation, or real staff audit attribution.
Conversion is one-way in this prototype. Assignment, appointments, care activities,
and historical Client Profiles remain unrelated session simulations; conversion
moves records between the new persistent sections, not into those mock profiles.
No deployment or merge is performed by these setup commands.


## Phase 3.5: frontend refinement

Use branch **codex/elccc-frontend-phase-3-5** to review the refined interface.
From your existing repository root on a Mac:

```bash
git fetch origin
git switch codex/elccc-frontend-phase-3-5
git pull --ff-only origin codex/elccc-frontend-phase-3-5
cd backend
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

In a second Terminal, from the repository root:

```bash
python3 -m http.server 5500 --bind 127.0.0.1
```

Use your existing Live Server instead if port 5500 is already serving the project.
Open **http://127.0.0.1:5500** and hard refresh with **Command+Shift+R**.
Stop the previous backend before starting another one. The existing database is
reused; do not delete or reset it. No backend code, schema, routes, or dependencies
change in this phase.

Admin CRM now has five main areas: **Overview, Clients, Appointments, Care Journey,
and Reports**. Within **Clients**, choose **Prospective Clients**, **Established
Clients**, or **Sample Profiles**. Prayer Requests remain available from Overview.
Approval Settings is hidden, including its former panel route; the routing
implementation and existing behavior remain available for future development.

Open a prospective profile, save its MYIO invitation tracking, and use **Convert
to Client → Confirm Conversion**. The established profile keeps the same inquiry
reference and history. Open **Original inquiry details** to inspect the original
UTC timestamp and status. Invitation tracking and conversion remain independent.
Client and Counselor section links are shorter and preserve their original section
anchors and forms. Shared button, spacing, and responsive styles retain the ELCCC
palette and branding.

The top notice still requires fictional data. **About this demonstration** in the
footer explains authentication/security limitations and disconnected integrations.
The portal tracking form explicitly states that no invitations are sent or account
activation verified. Appointment and care activities remain session simulations.
This prototype is not HIPAA-ready; use no real client or patient information.

Verification:

```bash
# From backend/, with the virtual environment active
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v

# From the repository root
node scripts/check-refinement.mjs
node scripts/check-workflow.mjs
node scripts/check-workspace.mjs
node scripts/check-operations.mjs
node scripts/check-presentation.mjs
node scripts/check-roles.mjs
```

The existing browser integration command also checks grouped navigation, conversion,
independent invitation tracking, history, and refresh/restart persistence. Its
setup is documented above. Hidden routing settings are seeded directly in browser
regression fixtures, while the retained implementation is checked separately; no
hidden settings are exposed to users. No deployment or merge is included.

## Native scheduling and intake direction

ELCCC Care Connect is planning an ELCCC-native booking and intake experience,
potentially replacing Calendly rather than embedding it. The [review and phased
implementation plan](docs/NATIVE_SCHEDULING_PLAN.md) distinguishes persistent
features from session simulations and covers appointment types, availability,
time zones, intake, confirmations, changes, reminders, identity, conflict prevention,
privacy, and a controlled cutover. Valant/MYIO evaluation remains separate.

Review branch `codex/elccc-native-scheduling-plan` using the same local commands
as Phase 3.5 after `git fetch origin` and `git switch codex/elccc-native-scheduling-plan`.
Open Admin CRM → Appointments → **Scheduling and intake direction**, or Client
Workspace → Intake → **Future native intake**. Both notes are expandable to keep
the working interface compact. The calendar preview now describes native booking
with optional synchronization. No live scheduling, new intake collection, database
migration, external connection, notification delivery, deployment, or merge is added.

## Admin CRM directory and appointments refinement

Review branch **codex/elccc-admin-crm-refinement**, based on the native scheduling
planning branch. No backend or database changes are required.

From your existing repository root:

```bash
git fetch origin
git switch codex/elccc-admin-crm-refinement
cd backend
source .venv/bin/activate
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

In a second Terminal, from the repository root:

```bash
python3 -m http.server 5500 --bind 127.0.0.1
```

Use your existing Live Server if port 5500 is occupied. Stop the old backend before
starting another. Open http://127.0.0.1:5500 and hard refresh with Command+Shift+R.
Keep your existing SQLite file; do not reset it.

### Review Clients

- Open Administrator → Clients → Prospective Clients or Established Clients.
- Search by fictional name or inquiry reference. Try Name A–Z/Z–A, activity dates,
  newest inquiry, and client-status sorting. Combine counselor, category, and
  onboarding filters. The onboarding filter uses manual MYIO invitation statuses.
- Client status can switch between prospective, established, or all records.
  Clear filters restores the current section. Filters remain while you open/close
  a profile and navigate between client sections, until page refresh.
- Open a profile, update invitation tracking, and confirm conversion. The original
  inquiry ID/history remains. Activity history is chronological.

Directory assignment and intake details come from an explicitly linked session
referral (`inquiryId`), never from a name match. They are labeled as session-only
and reset on refresh. Where no assignment/intake exists, the profile says Not
assigned/Not collected. These fields are not fabricated or written to SQLite.
Last activity uses valid timestamps in recorded management history plus explicitly
linked session notifications; inquiry/appointment dates are not inferred as activity.
Records with no valid events show **No activity recorded**; permanent history and session progress remain distinct.

Search, sorting, and filtering run over the loaded fictional dataset in the browser.
They are functional, but not server-side pagination/search or access controls.
Future backend authorization is documented [separately](docs/FUTURE_AUTHORIZATION.md).

### Review Appointments

- Open Appointments for compact session listings. Use search, counselor, date,
  simulated appointment type, status, source, and sorting controls together.
- Session appointments are the default. Choose Historical examples or All examples
  to inspect archived sample dates; they are not upcoming real appointments.
- Switch to Calendar preview, select a month, and click a date to filter the list.
  Counts honor the other filters. Displayed times remain Eastern Time; this is not
  a live scheduling engine. Unscheduled referrals have no calendar date.
- Review appointment opens its current summary and available change history.
  Existing referral review, assignment, scheduling, rescheduling, cancellation,
  and care controls remain below the compact workspace.
- Saved inquiry archive, Historical Referral Samples, and Development notes are
  expandable. The native scheduling plan remains available without occupying the
  main workspace. No bookings, reminders, invitations, or external messages are sent.

Only inquiry, conversion, and manual invitation tracking are persistent. Reports,
care journeys, and unrelated demo features remain available. No Valant/MYIO
connection, authentication, real patient data, or HIPAA compliance is introduced.

### Checks

Run the existing backend suite and frontend checks from earlier sections. Also run:

```bash
node scripts/check-crm-directory.mjs
```

The browser integration check now tests client search, sorting, combined filters,
status navigation, conversion, and tracking. The operations browser check tests
appointment search/filters, calendar selection, review, and existing care workflows.
All browser fixtures use fictional data and disposable databases.


## Sortable directory columns

Branch `codex/elccc-sortable-column-headers` adds clickable **Name**, **Status**,
and **Last Activity** headers to the client directory. The appointment list has
**Name**, **Date**, and **Status** headers. An arrow shows the current direction;
click the active header again to reverse it. Choosing another header or using the
sort dropdown updates the same sort state without clearing search or filters.
Last Activity starts newest-first when selected from another column. Missing
activity stays last in either direction.

Last Activity uses only valid event timestamps from stored inquiry/management
history and explicitly linked session notifications. Backend history includes the
recorded inquiry creation event. No appointment date or inferred creation fallback
is used, and no activity dates are generated. Unknown activity displays **No activity
recorded**. Appointment Date remains a separate scheduling column.

Use the existing local setup after `git fetch origin` and
`git switch codex/elccc-sortable-column-headers`; hard refresh Chrome. Try a column
header twice, then change the dropdown and verify its arrow updates. Search and
filter results should remain scoped. Sort buttons support keyboard activation and
expose their direction through `aria-sort`. Backend, database, scheduling, and
integration behavior are unchanged.

## Intake and onboarding refinement

Branch **codex/elccc-intake-onboarding-refinement** uses professional interface
labels such as Submit Request, Switch Role, Open Profile, Intake Checklist, and
Portal Invitation Status. A development-environment banner, test-record badges,
and concise capability notes remain. These labels do not enable production services.

The saved client profile now includes a derived **Onboarding checklist** covering
inquiry, conversion, counselor assignment, intake, questionnaire availability,
appointments, portal tracking and communications. Saved versus session-only steps
are distinguished. Where a referral is linked by inquiry ID, **Open intake checklist**
and **Review assignment and appointments** reuse that record rather than asking
for another inquiry. Test intake status carries forward across conversion within
that page session; it is not yet stored in SQLite. Unavailable questionnaires and
communications cannot be marked complete.

The [intake/onboarding review and implementation plan](docs/INTAKE_ONBOARDING_PLAN.md)
explains persistent versus session-only features, a proposed durable checklist/task
model, and phased priorities for authentication, server authorization, secure data
handling, persistent intake, administrative workflows and native scheduling. Valant
calendar/API access is not assumed and remains a separate evaluation.

To review with your existing local servers:

```bash
git fetch origin
git switch codex/elccc-intake-onboarding-refinement
```

Restart the backend only if needed, keep the frontend at port 5500, and hard refresh
Chrome. Submit a test inquiry, open Clients → Prospective Clients → Open profile,
review its checklist, complete the linked intake checklist, then confirm conversion.
The checklist and original inquiry reference remain associated. Reloading retains
saved inquiry/conversion/portal state but clears session-only progress as documented.
Do not enter real personal or clinical information. No backend schema, request
schema, authentication, live scheduling, messaging or integration is added.

Run the existing backend/frontend suites plus `node scripts/check-onboarding.mjs`.
Browser checks use the updated visible labels while retaining their behavioral
assertions for search, sorting, filters, intake, conversion, tracking and persistence.

## Guided public counseling request

The public **Request Counseling** button now opens contact → counseling preferences
→ optional counselor → preferred date/time → review → saved-reference confirmation.
There is no existing-client dropdown. This is an appointment-preference request,
not live scheduling. Only synthetic test contact details are accepted; no real
personal or clinical information is permitted.

Use branch `codex/elccc-public-preference-request`. See the
[local Mac walkthrough and capability/implementation plan](docs/PUBLIC_REQUEST_FLOW.md)
for exact setup commands, test values, CRM conversion/persistence checks, automated
checks, and security prerequisites. Saved contact/preferences remain under the
original inquiry UUID when converted. Existing backend routes remain compatible.

Normal pages omit historical archive navigation and development planning panels.
The retained historical/testing workspace is explicitly available at `?tools=1`.
No authentication, real booking, paperwork delivery or external integration is added.

## Client directory actions

Branch `codex/elccc-client-record-actions` adds clickable client names, row
double-click/Enter shortcuts, **View**, **Edit**, and confirmed **Delete** actions
in both Prospective and Established Clients, keeping **Open profile** available.
Delete archives the record; it never permanently removes inquiry or client history.
Use **Record visibility → Archived records → Restore** to recover it.

Edits and archive state persist in SQLite across refresh/restart. Cancel discards
unsaved changes. The original inquiry stays unchanged; the CRM shows the current
profile with its original reference and activity. Conflicting edits return a clear
error. Synthetic data only; authentication and external integrations are unchanged.
See the [Mac setup and review checklist](docs/CLIENT_RECORD_ACTIONS.md) for exact
commands, editable fields, persistence boundaries, API details, and automated checks.
