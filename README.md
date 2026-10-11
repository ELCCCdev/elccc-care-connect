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
