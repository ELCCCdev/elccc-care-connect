# ELCCC Care Connect — Feature Status Audit

**Audit baseline:** preserved application from merged PR #1 (`411d2d3`)  
**Audit date:** 2026-10-10  
**Data classification:** fictional/mock demonstration data only

> **Prototype only — no real client or medical data.** This public static prototype does not implement authentication, server-side authorization, secure storage, production integrations, or HIPAA compliance.

## Status legend

| Status | Meaning |
| --- | --- |
| **Implemented** | Renders and works in the browser with mock data. This does not mean production-ready. |
| **Simulated** | Changes browser-only state or displays a confirmation without persistence or external effects. |
| **Planned** | Included in the V2 plan but not present as a working current workflow. |
| **Production-blocked** | Must not process real client, clinical, payment, insurance, or credential data without production architecture and controls. |

## Current technical baseline

- The live artifact is the self-contained root `index.html`, using embedded HTML, CSS, JavaScript, and mock data.
- `scripts/build.mjs` copies `index.html` unchanged to `dist/index.html` and `dist/404.html`; it also copies `README.md` and adds `.nojekyll`.
- `scripts/serve.mjs` provides local static preview on port `4173`.
- `src/app.js`, `src/mockData.js`, and `src/styles.css` are an older parallel implementation. They are retained to preserve the existing repository but are not referenced by the root page or copied by the build.
- There is no framework, dependency, backend, API, database, durable persistence, or real identity provider.
- The Pages workflow deploys `dist/` on pushes to `main` or `work`, and through manual dispatch.

## Current navigation and screens

The header exposes the same navigation to every visitor: **Home, Find a Counselor, Match Quiz, Resources, Client Portal, Counselor, and Admin CRM**. The Login modal offers Client, Counselor, and Admin demo choices and routes to the selected dashboard, but it does not change access rights or create an authenticated session.

Current screens and overlays include:

- Landing page, care-team section, prayer request form, and executive presentation modal.
- Counselor directory, neutral initials avatars, counselor profiles, match quiz, and appointment-request modal.
- Searchable/filterable resources library generated from mock records.
- Client dashboard, appointments, forms/messages placeholders, recommended resources, and mock client profile.
- Counselor dashboard with assigned clients, schedule, referrals, and follow-up lists.
- Admin CRM with metrics, four-stage lead pipeline, appointment requests, prayer requests, client directory, charts, lead management, and counselor utilization.

## Mock data inventory

The deployed `index.html` contains 12 fictional counselors, 50 fictional clients, 25 appointment requests, 10 prayer requests, 100 generated resources, monthly appointment totals, lead sources, and specialty-demand data. The parallel `src/mockData.js` contains a separate mock-data implementation and must not be assumed to drive the deployed page.

## Feature status

### Public and find-care experience

| Feature | Status | Current behavior | Limitation |
| --- | --- | --- | --- |
| Landing page and branding | **Implemented** | Responsive ELCCC-style landing page, care-team cards, prayer call-to-action, and presentation-quality sections. | Static content; no content management workflow. |
| Counselor directory/profile | **Implemented** | Specialty filtering and modal profiles for 12 fictional counselors. | No provider-directory, credentialing, or availability service. |
| Counselor match quiz | **Simulated** | Recommends a fictional counselor from browser-only preferences. | Not diagnostic, validated, persisted, or clinically governed. |
| Appointment request | **Simulated** | Modal accepts demo form values and shows an in-browser confirmation. | No request is stored, transmitted, scheduled, or synchronized. |
| Resources | **Implemented** | Client-side search/category filtering over 100 generated cards. | No editorial, clinical-review, analytics, or publishing workflow. |
| Prayer request | **Placeholder** | Form is displayed. | Submit has no processing workflow, persistence, restricted queue, or emergency monitoring. |

### Role and portal experiences

| Feature | Status | Current behavior | Limitation |
| --- | --- | --- | --- |
| Demo role selector | **Simulated** | Client, Counselor, and Admin choices route to dashboard views. | All views remain reachable from public navigation; this is not authorization. |
| Role-specific navigation | **Planned** | Not implemented. | Requires simulated navigation first and authenticated server authorization for production. |
| Client portal | **Implemented / Placeholder** | Shows mock metrics, appointment, care summary, forms/messages task list, resources, and own profile modal. | No intake workflow, secure messaging, documents, billing, notifications, or persistence. |
| Counselor dashboard | **Implemented / Placeholder** | Shows assigned clients, schedule, referrals, and follow-up tracking. | No task actions, documentation workflow, alerts, calendar, or durable state. |
| Client isolation | **Production-blocked** | The demo selects one fictional client for the portal. | Real isolation requires authenticated server-side relationship checks on every operation. |

### Admin CRM and reporting

| Feature | Status | Current behavior | Limitation |
| --- | --- | --- | --- |
| Admin metrics and charts | **Implemented** | Displays hard-coded/generated leads, active clients, appointments, prayer volume, utilization, and charts. | Values are mock presentation data, not authoritative analytics. |
| Referral pipeline | **Implemented / Placeholder** | Four static columns: New, Contacted, Assigned, and Scheduled. | Cards do not move and changes do not persist; V2 proposes a nine-stage workflow. |
| Appointment/prayer management | **Implemented / Placeholder** | Lists fictional requests with illustrative action buttons. | Buttons have no workflow, ownership, audit history, notifications, or persistence. |
| Client profiles | **Implemented** | Admin can open fictional client summary modals. | No search authorization, record service, audit log, or clinical record. |
| Search and filters | **Partial** | Counselor and resource filtering work; broader CRM search/filtering is absent. | V2 requires defined filters and server-side authorization. |
| Counselor management | **Planned** | Counselor data is hard-coded and read-only. | Requires authorized create/edit/deactivate/capacity workflows and audit history. |

### Planned V2 workflows

| Feature | Status | Production requirement |
| --- | --- | --- |
| Clinician-controlled assessments and diagnosis | **Planned / Production-blocked** | Licensed-instrument governance, clinician-only approval, provenance, policy, audit, and secure record controls. |
| Integration Center and Valant connector | **Planned / Production-blocked** | Verified APIs, contracts/BAAs, secrets management, mapping, reconciliation, monitoring, and system-of-record decisions. |
| End-to-end referral, intake, assignment, scheduling | **Planned** | Canonical data model, durable backend, authorization, concurrency, notifications, and integration boundaries. |
| User manual and guided demo | **Planned** | Stable workflows, role walkthroughs, facilitator script, and explicit status labels. |
| Secure messaging, documents, payments, telehealth | **Planned / Production-blocked** | Approved vendors, identity, encryption, retention, consent, audit, and operational controls. |

## Production security requirements

Before any real client or clinical use, a separate production implementation must include at minimum:

1. Authenticated server-side authorization for every read, write, search, download, approval, and administrative action.
2. Deny-by-default role- and relationship-based access control, minimum-necessary access, and strict separation of unrelated client records.
3. Multi-factor authentication, secure recovery, session expiration/revocation, and privileged-access controls.
4. Encryption in transit and at rest with managed keys and rotation.
5. Tamper-resistant audit logging for access, changes, exports, approvals, failures, and administration.
6. Formal risk analysis, remediation, vulnerability management, incident response, and recurring security testing.
7. Business Associate Agreements and security review for applicable hosting, EHR, telehealth, messaging, AI, payment, and support vendors.
8. Tested backups, restoration, disaster recovery, business continuity, and availability objectives.
9. Secure hosting, isolated environments, secrets management, monitoring, alerting, patching, and controlled releases.
10. Identity verification, consent controls, retention/deletion policy, secure document storage, malware scanning, and controlled release of records.
11. Clinical governance for assessments, diagnoses, documentation, signatures, amendments, and AI-assisted drafts.

## Technical debt and deployment risks

### High priority

1. **Two implementations:** the deployed single-file page and unused `src/` implementation can diverge or lead contributors to edit the wrong source.
2. **No automated tests:** no unit, interaction, accessibility, or visual-regression suite protects the application.
3. **Compressed embedded source:** large portions of CSS and JavaScript are difficult to review and maintain.
4. **No authorization or persistence:** browser role selection and UI state are not security controls or workflow records.
5. **Public host:** GitHub Pages must never receive real client, clinical, insurance, payment, or credential data.

### Deployment-specific

1. Pushes to either `main` or `work` can deploy to the same Pages environment.
2. The workflow has no syntax, browser smoke, accessibility, or content-safety gate before deployment.
3. Actions use version tags rather than immutable commit SHAs.
4. `404.html` duplicates the application, which is acceptable for this static prototype but is not real route restoration.
5. The custom server is for local preview only, not production hosting.

## Guardrails

- Keep every person and record fictional and preserve the visible prototype disclaimer.
- Do not commit credentials, secrets, exports, clinical notes, diagnoses, assessment responses, insurance details, or payment data.
- Do not configure production APIs or secrets in browser JavaScript.
- Do not describe the prototype as secure, authenticated, production-ready, or HIPAA compliant.
