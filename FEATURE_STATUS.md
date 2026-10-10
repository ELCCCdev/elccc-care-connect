# ELCCC Care Connect — Feature Status Audit

**Audit date:** 2026-10-10  
**Scope:** Current repository and GitHub Pages build  
**Data classification:** Fictional/mock demonstration data only

> **Prototype only — no real client or medical data.** This repository is a static stakeholder demonstration. It does not implement authentication, server-side authorization, secure storage, clinical recordkeeping, production integrations, or HIPAA compliance.

## Status legend

| Status | Meaning |
| --- | --- |
| **Implemented** | Works within the browser prototype and can be exercised with mock data. This does not imply production readiness. |
| **Simulated** | Presents a believable interaction or changes in-memory UI state, but has no durable backend, identity verification, external side effect, or authoritative system of record. |
| **Planned** | Proposed for a future prototype increment but not represented by a complete current workflow. |
| **Production-blocked** | Must not be used with real client, clinical, insurance, payment, or credential data until production architecture, contracts, security controls, validation, and governance are implemented. |

## Current technical baseline

### Framework and runtime

- **Framework:** No UI framework. The deployed prototype is plain HTML, CSS, and browser JavaScript embedded in `index.html`.
- **Application model:** A single in-memory `state` object and string-template render functions replace the contents of `#root` after each interaction.
- **Persistence:** None. Reloading the page resets every selection and simulated update.
- **Backend/API/database:** None.
- **Dependencies:** No runtime or package dependencies are declared.
- **Primary source of truth:** `index.html`.
- **Parallel source trees:** None. Obsolete, unused files under `src/` were removed during the audit correction so contributors cannot accidentally edit a version that is not deployed.

### Build and local preview

- `npm run dev` starts the custom Node static server in `scripts/serve.mjs` on port `4173`.
- `npm run build` runs `scripts/build.mjs` and creates:
  - `dist/index.html`
  - `dist/404.html`
  - `dist/README.md`
  - `dist/.nojekyll`
- The build intentionally deploys the self-contained `index.html`, which is the only application source.

### Deployment

- `.github/workflows/deploy.yml` deploys `dist/` with the official GitHub Pages actions.
- Deployment runs automatically on pushes to `main`, and can also be started by manual workflow dispatch from an approved commit.
- The current static Pages deployment is appropriate only for fictional demonstration data.
- The workflow has Pages write and OIDC token permissions scoped at workflow level.

## Navigation inventory

Navigation changes according to the selected **simulated** role:

| Role | Visible navigation |
| --- | --- |
| Public | Home, Find Care, Match Quiz, Resources, Prayer, Demo Login |
| Client | Dashboard, Book / Change, Messages, Client Demo role control |
| Counselor | Workspace, Schedule, Messages, Counselor Demo role control |
| Admin | CRM, Integrations, Privacy & Security, Roadmap, Admin Demo role control |

The mobile breakpoint replaces the horizontal navigation with a hamburger-controlled menu. Role selection affects only browser UI state; it is not an authorization boundary.

## Component and screen inventory

The application is not componentized in a framework, but it has reusable render helpers and screen functions:

- **Shared UI helpers:** page headers, cards, metric cards, buttons, list rows, avatars, footer, modals, confirmations, status chips, and journey steps.
- **Public screens:** Home, Care Team, Find Care, counselor profile modal, Match Quiz, Resources, Prayer Request Center.
- **Client screens:** Dashboard, care journey tracker, intake/forms, insurance, messages, homework, billing, booking calendar.
- **Counselor screens:** Workspace, schedule, documentation assistant concept, forms/homework review, coordination, messages.
- **Admin screens:** CRM metrics, nine-stage Kanban, appointment requests, prayer requests, client cards, Integrations Center, Privacy & Security Center, Roadmap.
- **Presentation screens:** Role demo login and stakeholder Presentation Overview.

## Mock data inventory

The deployed `index.html` generates all demonstration records in memory:

- 12 fictional counselor profiles with specialties, insurance labels, availability, location, and utilization.
- 50 fictional client records distributed across nine care-journey statuses.
- 27 fictional inquiries used by the CRM pipeline.
- 100 generated resource cards.
- Static mock appointment slots, messages, forms, homework, billing entries, prayer requests, alerts, and operational metrics.

There is no separate mock-data source: all records that drive the deployed demonstration are embedded in `index.html`.

## Feature status matrix

### Public and find-care experience

| Feature | Status | Current behavior | Limitation / production requirement |
| --- | --- | --- | --- |
| Branded home page | **Implemented** | Responsive ELCCC-style landing page, stakeholder priorities, team, and prayer call-to-action. | Static content; needs governed content management for production. |
| Find Care directory | **Implemented** | Renders 12 fictional counselors with neutral initials avatars. | Filter controls are mostly illustrative; no provider directory backend. |
| Counselor profiles | **Implemented** | Modal shows specialties, insurance, faith approach, availability, and request action. | Data is fictional and not synchronized to credentialing or scheduling systems. |
| Match Quiz | **Simulated** | Displays mock preferences and a recommendation. | Recommendation is not clinical, validated, persisted, or currently recomputed from all inputs. |
| Resource library | **Implemented** | Client-side text/category filtering over 100 generated resources. | No content lifecycle, review, analytics, or accessibility governance. |
| Prayer request | **Simulated** | Form presents a confirmation and crisis notice. | No submission, restricted ministry queue, consent handling, secure storage, or emergency monitoring. |

### Simulated role navigation and boundaries

| Feature | Status | Current behavior | Limitation / production requirement |
| --- | --- | --- | --- |
| Client/Counselor/Admin demo login | **Simulated** | Role choice changes visible navigation and landing page. | No identity, password, MFA, session, or server-enforced authorization. |
| Role-specific menus | **Implemented** | Menus differ for Public, Client, Counselor, and Admin UI state. | DOM/UI hiding is not access control. |
| Client record isolation messaging | **Implemented** | UI clearly says clients cannot see unrelated clients. | Real isolation requires server-side tenant/record authorization and test coverage. |
| Counselor management | **Planned** | Counselor cards exist; admin cannot create, edit, deactivate, credential, or manage capacity. | Requires an authorized admin service and audit history. |

### Client portal

| Feature | Status | Current behavior | Limitation / production requirement |
| --- | --- | --- | --- |
| Dashboard and care journey | **Implemented** | Shows Inquiry through Active Care and mock metrics. | Static/in-memory; no authoritative status transitions. |
| Book, reschedule, cancel | **Simulated** | Selects mock counselor/type/format/date/time and shows confirmations. | No concurrency, calendar hold, scheduling rules, reminders, or EHR synchronization. |
| Intake checklist and documents | **Simulated** | Shows form states; upload control is disabled. | Secure uploads, malware scanning, signatures, versioning, retention, and access controls are absent. |
| Insurance status | **Simulated** | Shows fictional carrier, review, and responsibility estimate. | No eligibility verification, authorization, payer response, or coverage guarantee. |
| Secure messages | **Simulated** | Displays role-appropriate fictional threads and confirmation. | Messages are neither sent nor encrypted, persisted, audited, or retained. |
| Homework and alerts | **Simulated** | Shows assigned/submitted tasks and counselor-alert language. | No assignment, upload, notification delivery, or review state persistence. |
| Billing and payments | **Simulated** | Shows fictional balance, history, and demo payment confirmation. | Payment collection is production-blocked pending a compliant payment integration and server architecture. |

### Counselor workspace

| Feature | Status | Current behavior | Limitation / production requirement |
| --- | --- | --- | --- |
| Schedule, alerts, and follow-up | **Implemented** | Renders fictional appointments, missed visit, alerts, quick actions, and tasks. | No calendar, rules engine, notification delivery, or durable task state. |
| Documentation queue | **Implemented** | Shows fictional draft/missing/signed statuses. | Not a clinical record; no signing, amendment, retention, or EHR write-back. |
| AI Documentation Assistant | **Simulated** | Buttons demonstrate dictate, upload/record, draft summary, and structured note concepts. | No recording or AI processing occurs. Production use requires consent, vendor review, BAA, security, validation, provenance, and mandatory clinician approval. |
| Forms and homework review | **Simulated** | Shows fictional submitted/reviewed items. | No document service, alerts, or workflow persistence. |
| Internal coordination | **Simulated** | Shows fictional authorized staff conversations/tasks. | Requires authenticated identities, minimum-necessary access, audit logging, and record scoping. |
| External professional coordination | **Planned / Production-blocked** | Labeled “Future secure integration.” | Requires authorization/consent validation, secure exchange, identity verification, and agreements. |

### Assessment and diagnosis

| Feature | Status | Current behavior | Limitation / production requirement |
| --- | --- | --- | --- |
| Clinician-assigned assessments | **Planned** | No assessment library, assignment, completion, or scoring workflow exists. | Must be clinician-controlled with licensed instrument governance and server authorization. |
| Assessment review | **Planned** | No results review or interpretation workflow exists. | Raw responses/results require strict access, provenance, and audit controls. |
| Diagnosis workflow | **Planned / Production-blocked** | No diagnosis entry, review, history, or EHR synchronization exists. | Only authorized clinicians may create/approve diagnoses; requires server controls, audit trails, coding governance, and clinical policy. |
| Client diagnosis visibility | **Planned / policy-dependent** | Not shown. | Visibility must follow organizational policy, law, clinical judgment, and role/consent rules. |

### Admin CRM and integrations

| Feature | Status | Current behavior | Limitation / production requirement |
| --- | --- | --- | --- |
| Nine-stage care journey Kanban | **Implemented** | Renders fictional inquiries from New Inquiry through Closed. | Cards are not draggable and statuses do not persist. |
| CRM filters | **Simulated** | Counselor, service, intake, insurance, and appointment controls are visible. | Controls do not currently filter records. |
| Operational metrics | **Implemented** | Shows inquiries, assignment queue, intake rate, insurance, no-shows, utilization, and inquiry-to-visit time. | Values are hard-coded mock metrics, not computed reporting. |
| Appointment and prayer queues | **Implemented** | Renders fictional list views. | No actions, ownership, SLAs, audit history, or persistence. |
| Integration Center | **Implemented as documentation** | Shows Valant, calendar, telehealth, insurance, payment, and reminder concepts. | Every connector is explicitly “Future Integration / Demo”; no APIs are called. |
| Valant integration | **Planned / Production-blocked** | Describes possible synchronization concepts. | Requires verified API availability, contract, BAA, ownership rules, mapping, reconciliation, error handling, and security review. |
| Configurable connector management | **Planned** | No connector configuration, credentials, mapping, health status, or logs. | Secrets must never be placed in browser code or GitHub Pages. |

### Security, operations, and guidance

| Feature | Status | Current behavior | Limitation / production requirement |
| --- | --- | --- | --- |
| Privacy & Security Center | **Implemented as documentation** | Lists proposed production safeguards and says they are not implemented. | Static explanatory content is not a control. |
| Authenticated authorization and MFA | **Production-blocked** | Not implemented. | Required before real data or privileged workflows. |
| Encryption, audit logs, backup, retention | **Production-blocked** | Not implemented. | Requires managed production infrastructure and operational procedures. |
| Presentation Overview | **Implemented** | Summarizes pain points, workflows, roles, integrations, security, and questions. | Presentation content must stay aligned with implementation status. |
| User manual / guided demo | **Planned** | README has build/deploy instructions only. | Needs role-based walkthroughs, facilitator script, and feature-status callouts. |

## Production security requirements

Before any real client or clinical use, a separate production architecture must include and validate at minimum:

1. Authenticated server-side authorization for every read, write, search, download, and workflow action.
2. Role-based and relationship-based access control with deny-by-default policies and minimum-necessary access.
3. Multi-factor authentication, secure account recovery, session expiration, device/session revocation, and privileged-access protections.
4. Encryption in transit using current TLS and encryption at rest with managed key lifecycle and rotation.
5. Tamper-resistant audit logging for access, changes, exports, approvals, failed attempts, and administrative actions.
6. Formal security risk analysis, remediation tracking, recurring testing, vulnerability management, and incident response procedures.
7. Business Associate Agreements and vendor/security review where required, including EHR, cloud, telehealth, messaging, AI, payments, and support vendors.
8. Tested backups, disaster recovery, availability objectives, restoration procedures, and business continuity plans.
9. Secure hosting with environment isolation, secrets management, monitoring, alerting, patching, and change control.
10. Strong client identity verification, record separation, consent controls, data retention/deletion policies, and prohibition of cross-client visibility.
11. Secure document storage, malware scanning, download authorization, file-level auditability, and controlled sharing.
12. Clinical governance for assessments, diagnoses, documentation assistance, corrections, signatures, and record release.

## Technical debt and deployment risks

### High priority

1. **No automated test suite:** There are no unit, interaction, accessibility, visual-regression, or workflow tests.
2. **Compressed single-file implementation:** Most CSS and JavaScript functions occupy long lines, making review, merge conflict resolution, debugging, and status auditing difficult.
3. **No authorization boundary:** Role switching is entirely client-side and must never be interpreted as security.
4. **No persistence or error states:** Workflows cannot model concurrency, retries, conflicts, partial failure, or reconciliation.

### Medium priority

1. **Hard-coded dates and metrics:** Demonstration values will become stale and may be mistaken for calculated reporting.
2. **Placeholder controls:** Some visible filters and actions do not change data, which may confuse stakeholders unless status is clearly labeled.
3. **Custom static server hardening:** `scripts/serve.mjs` is for local preview only and is not suitable for internet-facing production hosting.
4. **404 duplication:** `404.html` is a copy of `index.html`; this is acceptable for the current client-side prototype but has no URL routing/state restoration.
5. **Manual deployment ref selection:** A manual workflow run can be started from a selected branch or commit; maintainers must choose an approved ref before deploying.
6. **Unpinned action SHAs:** GitHub Actions use version tags rather than commit SHAs; production supply-chain policy may require pinning.
7. **No deployment validation:** The Pages workflow builds and uploads without syntax, content, accessibility, or smoke checks.

### Deployment guardrails

- Keep all data fictional and clearly labeled.
- Do not add credentials, API keys, client exports, assessment responses, diagnosis data, insurance data, payment details, or clinical notes to the repository.
- Do not configure production APIs from browser JavaScript.
- Preserve the explicit prototype and non-HIPAA-compliance notices.
- Treat GitHub Pages as a public demonstration host, not as a clinical application platform.
