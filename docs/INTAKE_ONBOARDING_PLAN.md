# Intake and onboarding: shared record direction

This refinement improves the test interface and makes available onboarding progress
visible. It does not enable production intake, authentication, real bookings,
communications, or patient-data collection. The public frontend remains a test
experience; only the approved local frontend uses the development backend.

## Reviewed workflows and current boundaries

| Workflow | Current state | Meaning in the refined interface |
| --- | --- | --- |
| Initial inquiry | Persistent local SQLite record with UUID, test name, category, contact preference, creation time | Received; details are reused read-only in the profile |
| Client conversion | Persistent confirmed transition with original inquiry ID and history | Prospective or Established; not proof that intake or booking is complete |
| Counselor assignment | Session-only referral workflow | Show assigned counselor only through an explicit inquiry-ID link; never infer one by name |
| Intake checklist | Preset time preference and orientation response in browser state | Not started or Submitted, labeled Session only; not a secure clinical questionnaire |
| Appointments and changes | Session-only scheduling, approval, conflict checks, cancellation/rescheduling and history | Selected time is not a live reservation; session state resets on refresh |
| Portal invitation | Persistent manual Not Sent/Sent/Activated tracking | Tracked state only; no invitation delivery or account verification |
| Communications/reminders | In-page notices and follow-up task toggles | No external delivery; not a functioning messaging service |
| Clinical exercises | Existing test-only screening/planning/homework controls | Not validated clinical instruments, production records or live care services |
| Authentication/permissions | Role presentation and mock checks only | No authenticated user or secure record boundary |

The existing inquiry request schema is unchanged. No real email/phone fields,
clinical intake questions, uploads, or live integrations are added. Test record
names/IDs are preserved; record badges and the environment indicator distinguish
this environment from real center records. Stored history is not rewritten when
its wording is shortened for display.

## Unified journey

1. **Receive inquiry.** Create the canonical inquiry once and show its reference.
   Carry its category and contact preference into the profile without re-entry.
2. **Review and follow up.** The administrator sees outstanding items on the same
   profile. Missing information should become a targeted task, not another inquiry.
3. **Assign counselor.** Persist an explicit association to the canonical record in
   a later phase. The current session link is `inquiryId`; duplicate names do not
   authorize matching or merging.
4. **Complete intake.** Reuse confirmed inquiry values in a versioned intake record.
   Ask only for genuinely missing, approved information. Client edits should update
   an authorized version of the shared record, not fork another client profile.
5. **Review booking readiness.** Keep appointment requirements and clinical intake
   requirements separate. A checklist is not proof of a calendar reservation.
6. **Convert when appropriate.** Conversion retains the original inquiry, intake,
   assignments, invitations and history. Center policy determines timing; conversion
   must not be required for invitation tracking or automatically caused by booking.
7. **Continue care and follow-up.** Authorized client, counselor and administrator
   views reference the same record through scoped APIs. Communications and tasks
   attach to that reference and reveal only permitted information.

In this branch, linked session referrals can open the existing intake checklist or
assignment/appointment workspace directly from the saved profile. Intake status
carries forward across conversion during that session. It does **not** persist
through a page refresh. An inquiry loaded without a session link does not create
or guess a duplicate referral; secure persistent intake is clearly unavailable.

## Checklist design

The current read-only checklist derives status from existing saved data or explicit
session relationships. It does not let someone mark unavailable features complete.

| Item | Current statuses/evidence | Future administrative requirement |
| --- | --- | --- |
| Inquiry | Received: stored inquiry | Confirm contact/consent requirements using approved secure fields |
| Client record | Prospective/Established: conversion state | Review owner and next action; conversion remains independent |
| Assignment | Counselor name/Not assigned; Session only | Persistent counselor ID, effective dates, assignment authorization |
| Intake checklist | Not started/Submitted; Session only | Draft, submitted, needs clarification, reviewed; versioned templates/responses |
| Secure questionnaire | Not available | Explicit approval, authentication, consent, access controls and protected storage first |
| Appointment | Not scheduled/Time selected/Cancelled; Session only | Persistent appointment ID with actual booking state and policy snapshot |
| Portal invitation | Not recorded or tracked Sent/Activated | Keep manual tracking separate from verified provider delivery/activation |
| Communications | Not connected | Approved consent/channel preferences and audited, reliable delivery later |

The items-to-review count reflects currently identifiable missing assignment, checklist,
appointment, and invitation-tracking items. Unimplemented secure questionnaires and
communications stay visibly unavailable; they are not counted as completed. This
is guidance, not a clinical readiness decision or production booking gate.

Future tasks should have a responsible staff member, due date, required/optional
flag, status (Not started, In progress, Awaiting client, Needs review, Complete,
Not applicable), supporting evidence and an audit trail. Completion needs a
server-validated event, not a browser checkbox. Distinguish administrative review
from clinical review and limit who may see each answer/task.

## Proposed persistent model and API boundaries

Keep the original inquiry/client relationship as the canonical reference. Add
separate, linked resources for assignments, intake cases, questionnaire versions,
response revisions, consent receipts, appointments and administrative tasks. Do
not replace the existing inquiry or clone all its fields into disconnected records.
Create explicit field ownership and conflict/version rules for corrections.

Return a minimal onboarding summary (step, state, evidence reference, updated time,
next action) to authorized directories; retrieve protected answers separately.
Share the same service across staff and personal portals. Writes must include
revision/idempotency safeguards and server-verified actor attribution. Preserve
history across conversion and reject unrelated record access. Search, sorting and
filtering must be applied within authorized scopes before pagination/counting.

No such intake APIs/tables are implemented in this branch. The current checklist
is a truthful view of existing capabilities, not a persistent task engine.

## Prioritized implementation phases

### 1. Identity and secure foundation

Implement verified identity, secure sessions, recovery, staff MFA, revocation and
server-enforced center/role/record permissions. Administrators need operational
scope, counselors need assignment-based access, and clients need their own scoped
record access; guardian/delegation rules require explicit design. Do not trust the
role switcher or client-supplied ownership IDs. See
[Future Authorization](FUTURE_AUTHORIZATION.md).

Before real-data use, complete data minimization and privacy review, approved
hosting/storage, TLS, encryption/backups, secrets management, redacted logs, audit,
retention/deletion, consent, restore testing and incident response. None of these
steps alone establishes HIPAA compliance. Remain test-only until a separately
approved readiness review and pilot.

### 2. Persistent administrative onboarding

Start with fictional data: persist assignments, intake-case status and staff tasks
linked to the original inquiry. Reuse inquiry fields and preserve existing conversion
and invitation behavior. Add transactional updates, optimistic versions, actor
history, and deterministic migrations that do not reset records. Test duplicate
names, concurrent edits, refresh/restart, assignment changes and conversion with
unfinished intake. Do not require conversion to begin onboarding.

### 3. Authenticated, versioned intake

Add approved nonclinical questions first, draft/resume, required/optional fields,
consent receipts and administrative review. Ask only for missing information and
show who can see it. Historical submissions retain their questionnaire version.
Sensitive clinical collection requires separate approval, access controls and
retention policy; do not enable it through the public test demo. Test denial of
cross-client/cross-counselor access and sensitive-data exclusion from logs/URLs.

### 4. Administrative workflow and native scheduling

Connect persistent checklist readiness to authorized task queues and the native
scheduling work described in [Native Scheduling Plan](NATIVE_SCHEDULING_PLAN.md).
Add server-generated availability, transactional overlap prevention, time-zone/DST
handling, cancellations/rescheduling and durable booking confirmations before
claiming live scheduling. Calendar dates must never stand in for recorded activity.
Keep conversion, portal tracking, intake submission and booking separate events.

### 5. Communications and controlled rollout

Only after approval, add consent-aware communications and reliable reminder jobs
with delivery states, retries, cancellation and audit. Protect content and use
short-lived authenticated links. Pilot a limited workflow with staff acceptance,
monitoring, restore/rollback and operational ownership before public launch.

## Valant and MYIO evaluation stays separate

Identify intended system-of-record responsibilities, contractual/privacy terms,
actual licensed access, supported APIs, calendar capabilities, identifiers, scopes,
rate limits, webhooks and failure behavior with the center/vendors. No Valant
calendar/API access is assumed. Do not make native intake or conversion depend on
an unverified integration. Manual portal tracking does not establish provider state.

## Verification for this refinement

Preserve directory search, filters, sort dropdowns and column toggles; record
conversion and invitation history; appointment views; role navigation; and test
intake/scheduling/care controls. Tests check explicit ID-only links and checklist
carry-forward across conversion, unavailable states, no false completion, and the
continued development/security indicators. Existing backend tests remain unchanged.
