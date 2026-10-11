# ELCCC Care Connect

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
