# Native scheduling and intake direction

ELCCC Care Connect should own its scheduling and intake experience, potentially
replacing Calendly rather than making Calendly the booking interface. Calendly is
currently part of the center's operations, but **this repository neither calls nor
embeds it**. No Calendly, Valant, or MYIO technical capabilities have been verified.

This is a product and implementation plan, not a live booking system. All current
development data must remain fictional. Do not activate real contact or sensitive
clinical intake collection in the public demo. Security and privacy readiness must
be assessed before any separately authorized real-data pilot; this prototype is
not HIPAA-ready.

## What exists today

Reviewed against the Phase 3.5 frontend and current FastAPI routes.

| Capability | Current behavior | Missing for native production use |
| --- | --- | --- |
| Initial counseling request | Local port-5500 frontend POSTs a preset fictional name, category, contact preference, and acknowledgment to SQLite | Scheduling intent, authenticated identity, verified contact and consent where appropriate |
| Prospective/established directory | Persistent lists, profile review, confirmed conversion, duplicate-conversion prevention, and management history | Server-side search/filter/pagination, record permissions, real staff audit attribution |
| Counselor assignment | Functional session demo: review referral, assign an available sample counselor, then schedule | Persistent assignments, eligibility/qualification rules, staff permissions |
| Appointment types | Counseling categories and a session-format preference are demonstrated; categories are not appointment types | Explicit consultation/follow-up types with duration, buffers, locations, eligibility, and booking policies |
| Counselor availability | Simulated standard/morning/afternoon hours and one mock daily hold | Weekly rules, dated exceptions, leave, holidays, locations, booking horizon, and trusted calendar busy data |
| Date/time selection | Future-date selection, preset Eastern Time choices, fixed 60-minute appointment simulation | Server-generated slots, client time-zone display, variable durations, DST handling, atomic reservation |
| Conflict checks | Rejects overlaps and simulated unavailable hours in current browser state | Protection across tabs, users, retries, restarts, and external calendar changes |
| Intake | Preset session-time preference and fictional orientation checklist stored in page state | Versioned questionnaires, authorized response storage, consent receipts, draft/resume, retention policies |
| Confirmation | Backend confirms inquiry saves; appointment notices and notification history are simulated | Durable booking receipt with reference, appointment details, delivery status and safe recovery |
| Cancellation/rescheduling | Functional approval, alternative-time acceptance, and history simulations; original appointment retained until final approval | Persistent state transitions, policy enforcement, concurrency handling, permission checks and audit |
| Reminders | Staff task toggles and in-page notices; nothing is sent | Reliable scheduled delivery with consent/preferences, retry/cancel rules, delivery tracking and privacy-safe content |
| MYIO invitation tracking | Persistent Not Sent/Sent/Activated labels and history, independent of conversion | No invitation delivery or account verification; provider role remains undecided |
| Calendar/Valant/MYIO | Preview-only integration cards | Authorized discovery of capabilities, contracts, identifiers, permissions, and failure behavior |

Sources: `index.html` functions `bookingModal`, `saveCounselingInquiry`,
`demoAdminPanel`, `schedulingError`, `dailyOperations`, `intakePanel`,
`finalizeChange`, `managedClientsPanel`, and reminder handlers;
`backend/app/main.py` inquiry and management routes. The backend currently has
**no appointment, availability, questionnaire, reminder-delivery, or authentication API**.
Original inquiry timestamps and conversion history persist; appointment and intake
history do not. Saved inquiry categories should not be silently repurposed as
appointment types. The current conversion transaction is not a booking-lock system.

## Proposed center experience

Keep the compact Admin areas from Phase 3.5:

- **Overview:** today's work, requests awaiting review, incomplete intake, and delivery failures.
- **Clients:** searchable Prospective and Established directories; one profile for inquiry,
  appointments, assignment, intake progress, portal tracking, and activity.
- **Appointments:** compact list/calendar switch, consultation type, counselor, status,
  location, and date filters. Default to upcoming appointments, sorted chronologically.
- **Care Journey:** explicit next steps linked to the same records, without duplicate profiles.
- **Reports:** operational counts with clear date windows, not invented clinical conclusions.

Client booking should progress through appointment type, eligible counselor or
staff matching, location/format, available date/time, minimal booking details, and
review/confirmation. Show a time-zone selector and duration beside every offered
slot and final summary. Show cancellation/rescheduling rules before confirmation.
Provide an accessible list of times alongside the calendar, keyboard navigation,
clear empty/error states, and a way to request staff assistance. Do not offer
unsupported or emergency clinical services through booking.

A completed booking should link to the existing prospective-client ID, chosen
appointment type, counselor assignment, and durable appointment reference. A
returning established client uses the same relationship rather than creating
another prospective record. Prevent duplicate records through authenticated IDs
and explicit staff reconciliation; never match people by name alone. A future
new-prospect route needs separate anti-abuse, identity, consent, and recovery design.

Staff should see the booking immediately in the client profile, counselor agenda,
and Admin queue. Conversion to established client remains a separate confirmed
center decision. Portal invitation tracking remains independent of both booking
and conversion. Rebooking, cancellation, and reminder jobs retain the original
inquiry/appointment relationship and append authorized activity history.

### Compact directories and profile information

Introduce server-side search, pagination, and filtering before directories become
large. Search only permitted identifiers/fields; apply record permissions before
searching or counting results. Prospective clients: received date, category,
assigned counselor, booking state, intake completion, invitation state. Established
clients: name/reference, counselor, next appointment, intake tasks. Offer explicit
ascending/descending sort choices with a stable ID tie-breaker. Preserve filters
when returning from a profile, display result counts, and include Clear filters.

Use concise rows and one detail panel. Keep original IDs and full timestamps in
record details. Avoid clinical details in directory previews, URLs, query logs,
notifications, and calendar event titles. Prefer structured booking preferences
over open-ended clinical text in the scheduling flow.

## Domain boundaries to preserve

The following are proposed entities, not tables added by this change:

| Boundary | Responsibility |
| --- | --- |
| Inquiry/person relationship | Original inquiry ID/date; prospect-to-client lifecycle; authorized identity matching |
| Appointment type | Name, duration, buffers, formats/locations, counselor eligibility, booking limits and cancellation policy version |
| Availability | Counselor/location time zone, weekly rules, exceptions, leave, authoritative busy periods |
| Appointment | Linked record, counselor, type, start/end UTC instants, display-zone IDs, status, policy snapshot, optimistic version |
| Assignment | Persistent counselor-to-client association with effective dates and authorization rules |
| Intake | Questionnaire/version, required/optional questions, draft/submitted state, authorized responses, consent/version receipts |
| Activity/audit | Actor, time, action, record reference, reason and source; protect logs without copying sensitive answers into them |
| Notifications | Booking-event reference, channel/consent, job state, idempotency key, delivery outcome and cancellation |
| Optional provider adapter | Provider IDs, scoped permissions, sync checkpoints and mappings; never owns the native client lifecycle |

Store concrete appointment start/end instants in UTC plus IANA time-zone identifiers
such as `America/New_York`. Author availability in the counselor/location zone,
then present slots in the client's selected zone. Avoid ambiguous strings such as
"EST" year-round. Explicitly handle nonexistent and duplicated daylight-saving
times; test transitions and cross-zone date boundaries. A future location-zone
change must not silently move an existing confirmed appointment.

## Phased implementation and release gates

### A. Define center policies and validate fictional prototypes

Agree on initial consultation types, lengths, buffers, counselor eligibility,
location/format, hours and exceptions, booking lead time/horizon, minors/guardian
handling, approval rules, cancellation/rescheduling deadlines, reminder preferences,
and which intake questions are operational versus clinical. Inventory the current
Calendly flow with authorized staff; do not assume its fields are all necessary.
Confirm accessibility needs and the staff owner for unresolved bookings.

Prototype the compact slot picker and intake progression using fictional data.
Plan native booking first, with optional external calendar sync later. Keep the
current demo controls until their replacements pass regression tests.

**Gate:** center-reviewed policies, data inventory/minimization, and a tested
fictional walkthrough. No live collection or scheduling.

### B. Establish identity, authorization, storage, and privacy foundations

Implement authenticated client and staff sessions, staff MFA, scoped server-side
roles/record access, secure recovery and session expiration, CSRF protection where
cookie sessions are used, explicit trusted origins, and rate limiting. Role-switch
buttons and CORS are not authorization. Choose an approved deployment/storage
architecture; local SQLite is not the default target for concurrent real-data use.

Before any real data: threat model and privacy review; TLS and encrypted managed
storage/backups with controlled keys; least-privilege service access; secrets
management; migration/restore procedures; redacted telemetry; retention/deletion
and consent policies; access/change audit; dependency updates and incident response.
Evaluate vendors, contractual/privacy obligations, and agreements where applicable.
Clinical response collection needs its own access, consent, retention, and review
requirements, not just a checkbox. Do not label these tasks proof of HIPAA compliance.

**Gate:** tested permission boundaries, recovery, audit, backup restoration, and
security/privacy review in an isolated environment. Still fictional data until
separately authorized for a controlled pilot.

### C. Build the native appointment core with fictional data

Add persistent appointment types, assignments, availability rules/exceptions and
server-side slot generation. Link bookings to original inquiry/client IDs. Support
internal staff booking before opening a client booking route. Test restart and
multi-user behavior, including simultaneous booking attempts.

At confirmation, revalidate eligibility, hours, buffers and conflicts inside a
database transaction. Use a database-enforced overlap strategy or serialized
per-resource reservation appropriate to the chosen production database. A unique
start time alone does not prevent partially overlapping appointments. Reserve all
required resources consistently, use expiring holds where needed, and require
idempotency keys to make retries safe. Never treat displayed free slots as reserved.

Add persistent cancellation/rescheduling and revision checks. Keep the original
reservation until a replacement is confirmed atomically; handle competing requests,
stale screens and policy deadlines. If changes need approval, retain the existing
appointment until the authorized decision is committed. Record meaningful actor
history. Booking state and the prospect/client lifecycle remain separate.

**Gate:** concurrent overlapping requests produce only one booking; buffers and
exceptions hold; duplicates/retries are safe; DST tests pass; cancellations and
reschedules survive restart without losing or double-booking an appointment.

### D. Add versioned intake and confirmed booking experience

Start with minimal nonclinical scheduling information and consent/preferences.
Add versioned questionnaire templates, required/optional fields, safe drafts,
submission receipts, and staff review status. Submitted answers retain their template
version; later edits create a revision rather than changing historical meaning.

Keep appointment confirmation separate from clinical intake completion unless
center policy explicitly requires otherwise. Show outstanding tasks without exposing
answers to unauthorized staff. Define abandoned draft expiry and deletion. Sensitive
clinical questionnaires remain disabled until their separate approval and safeguards
are complete; the public demo continues using presets only.

**Gate:** staff/client permissions, questionnaire versioning, validation, consent,
draft recovery, and booking-to-profile linkage verified with fictional scenarios.

### E. Add reliable confirmations/reminders, then optional calendar adapters

Create notification jobs from committed appointment events using an outbox or
comparable durable pattern. Notifications must not claim success before delivery
is known. Use controlled test delivery during development. Support opt-out/channel
preferences, bounded retries, idempotency, quiet-hour policy and monitoring. Cancel
or replace obsolete jobs when appointments change. Keep message/calendar titles
generic; use authenticated links for details, with no sensitive intake content.

Evaluate calendar-provider APIs and delegated scopes separately. Decide which busy
source is authoritative, how fresh it must be, and what happens on outage or uncertain
sync; stop offering affected availability when conflicts cannot be checked safely.
Native booking remains the source of truth for native appointments. Handle inbound
changes, webhook validation, deduplication, reconciliation and provider failures
without duplicating bookings. Do not claim those capabilities exist until evaluated.

**Gate:** controlled delivery tests, safe retry/cancellation, outage/reconciliation
exercises, and staff visibility into failures. No live messages without separate approval.

### F. Controlled pilot and possible Calendly replacement

Run a separately authorized, limited pilot only after readiness review. Define the
booking source of truth for each counselor/time window; do not accept independent
Calendly and native bookings into the same uncoordinated availability pool.
Plan an authorized cutover/reconciliation of future bookings, avoid duplicate
notifications, preserve references/history, and give staff a rollback procedure.
Do not import Calendly records into this fictional demo. Replace the old entry point
only after staff acceptance, accessibility checks, restore tests, monitoring and
operational ownership are established. Do not switch public links automatically.

## Valant and MYIO are a separate evaluation

Determine the intended system of record, supported APIs, licensing/access,
identity matching, scopes, intake/appointment capabilities, consent requirements,
notification ownership, audit, rate limits, webhook/security guarantees and failure
handling with the center and vendors. No capabilities are assumed here.

Keep native booking, intake, conversion, and invitation tracking usable without
Valant/MYIO. If approved later, add adapters with explicit mappings and sync status.
The existing manual MYIO labels do not mean an invitation was sent or an account
activated. They must not silently become evidence of real provider state.

## Verification for this planning change

No scheduling engine, intake fields, backend endpoints, schema changes, real data,
provider connections or notification sending are introduced. The interface adds
compact expandable direction notes in Admin Appointments and sample Intake, and
updates the calendar preview's wording to native-first. Existing controls stay live
as fictional session demos. The README links to this plan.

Run existing backend and frontend checks plus the Phase 2/3 browser integration
suite. In particular preserve inquiry submission, prospective-to-established
conversion, independent invitation tracking, session scheduling and conflict checks,
intake presets, approval decisions, cancellation/rescheduling history, reminders,
role navigation and responsive layouts. Production booking tests listed in the
release gates are future work, not capabilities demonstrated by today's tests.
