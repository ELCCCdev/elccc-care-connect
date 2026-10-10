# ELCCC Care Connect — V2 Implementation Plan

**Plan type:** Incremental stakeholder-demonstration roadmap  
**Constraint:** Mock data only; no real patient/client data, credentials, or production integrations  
**Current host:** Public static GitHub Pages prototype

> V2 remains a demonstration prototype. It must not claim HIPAA compliance, must not be used for clinical operations, and must continue to display: **“Prototype only — no real client or medical data.”**

## Prioritization principles

1. Preserve the working single-file GitHub Pages deployment while validating workflows.
2. Make status visible: every feature should be labeled **Implemented**, **Simulated**, **Planned**, or **Production-blocked**.
3. Demonstrate role boundaries before adding deeper clinical workflows.
4. Keep clients isolated from every unrelated client and administrative directory, even in mock navigation.
5. Put clinician review and approval ahead of automation for assessment, diagnosis, and documentation concepts.
6. Design integrations around explicit systems of record, idempotency, reconciliation, and failure handling—not only “connect” buttons.
7. Move to production architecture only after security risk analysis, vendor/BAA review, policy definition, and workflow validation.

## Delivery sequence

| Priority | Workstream | Prototype outcome | Primary dependency |
| --- | --- | --- | --- |
| P0 | 1. Simulated role-based navigation and counselor management | Clear role journeys and admin-managed fictional counselor roster | Role/permission matrix |
| P0 | 4. Referral, intake, assignment, and scheduling | One coherent mock journey from referral to first appointment | Workstream 1 roles; status model |
| P1 | 2. Clinician-controlled assessment and diagnosis | Safe demonstration of clinician ownership, review, and approval | Workstream 1 authorization model; clinical policy decisions |
| P1 | 3. Admin Integration Center | Configurable mock connector catalog and Valant concept mapping | Systems-of-record discovery; Workstream 4 canonical IDs/statuses |
| P2 | 5. User manual and guided demo | Repeatable role-based stakeholder walkthrough | Stable screens and labels from Workstreams 1–4 |

Workstreams can overlap in design, but acceptance should follow this order to avoid documenting or integrating unstable workflows.

---

## Workstream 1 — Simulated role-based navigation and counselor management

### Objective

Make role behavior explicit and consistent while adding a fictional counselor-management experience. The prototype will simulate permissions but will continue to state that real authorization is not implemented.

### Status target

- Role selector and role-specific navigation: advance from **Simulated** to **Implemented in prototype / still production-blocked for authorization**.
- Counselor directory management: advance from **Planned** to **Simulated**.

### Screens

1. **Demo Role Launcher**
   - Client Demo
   - Counselor Demo
   - Admin Demo
   - Visible reminder that role switching is not authentication
2. **Role Home / Navigation Shell**
   - Role badge
   - “Exit role demo” action
   - Role-specific primary and secondary navigation
3. **Admin → Counselor Management**
   - Fictional counselor roster
   - Counselor detail drawer/modal
   - Availability, services, locations, insurance labels, populations, and accepting-new-client state
   - Capacity/utilization display
4. **Counselor → My Profile & Availability**
   - Preview public profile
   - Edit simulated availability and service preferences
   - Mark mock profile changes “Awaiting admin review”
5. **Admin → Counselor Change Review**
   - Pending profile/availability changes
   - Approve/reject simulated changes

### User actions

- Select, switch, and exit a demo role.
- See only navigation appropriate to the selected role.
- Admin creates, edits, activates/deactivates, and previews a fictional counselor record in memory.
- Admin assigns services, locations, insurance labels, capacity, and availability.
- Counselor proposes fictional profile and availability changes.
- Admin approves or rejects a simulated change with a mock audit entry.

### Data models

```text
DemoUser
- id
- displayName
- role: client | counselor | admin
- active

CounselorProfile
- id
- displayName
- credentials[]
- roleTitle
- specialties[]
- populations[]
- serviceIds[]
- insuranceLabels[]
- locationIds[]
- telehealthAvailable
- acceptingNewClients
- publicBio
- faithIntegrationApproach
- profileStatus: draft | pending_review | published | inactive

AvailabilityRule
- id
- counselorId
- locationId
- appointmentTypeId
- dayOfWeek
- startTime
- endTime
- effectiveDateRange
- status

MockAuditEvent
- id
- actorRole
- action
- entityType
- entityId
- timestamp
- beforeSummary
- afterSummary
```

### Acceptance criteria

1. Selecting a role immediately updates menus and the role landing page.
2. Client navigation contains no counselor directory of clients, admin queues, or counselor documentation.
3. Counselor navigation exposes only a fictional assigned caseload, not the full CRM roster.
4. Admin can add/edit/deactivate a fictional counselor during the browser session.
5. Counselor changes appear in an admin review queue before simulated publication.
6. Reloading resets all edits and displays a clear “mock/in-memory” notice.
7. Automated smoke checks render every role route without a JavaScript error.

### Security considerations

- UI visibility is not authorization; production must enforce role and relationship checks server-side on every request.
- Use deny-by-default and minimum-necessary access.
- Counselor profile administration and availability changes require authenticated identities, MFA for privileged users, audit logging, and change history in production.
- Never store credentials, passwords, access tokens, or real provider records in static JavaScript.
- Test that client roles cannot query, infer, or enumerate unrelated client identifiers.

### Dependencies

- Approved role/permission matrix.
- Definition of counselor profile ownership and admin approval policy.
- Decision on whether Valant or another system owns provider and availability data.
- Stable service, location, appointment-type, and insurance-label taxonomies.

---

## Workstream 2 — Clinician-controlled assessment and diagnosis workflow

### Objective

Demonstrate a workflow in which authorized clinicians—not clients, admins, or automation—control assessment assignment, interpretation, diagnosis entry, and approval. No real instruments, responses, scores, or diagnoses will be used.

### Status target

- Assessment assignment/review: **Planned → Simulated**.
- Diagnosis workflow: **Planned / Production-blocked → Simulated with explicit clinician approval gates**.
- AI suggestions: remain **Production-blocked** and excluded unless separately governed.

### Screens

1. **Counselor → Assessment Library**
   - Fictional/general assessment templates only
   - Intended population, purpose, status, and mock licensing note
2. **Counselor → Assign Assessment**
   - Select assigned fictional client
   - Due date, instructions, visibility, and reminder settings
3. **Client → Assigned Assessments**
   - Only assessments assigned to the logged-in fictional client
   - Start/continue/submit mock response flow
   - Crisis and “not monitored” guidance where appropriate
4. **Counselor → Assessment Results Review**
   - Mock completion state and score band
   - Interpretation notes
   - “Reviewed by clinician” gate
5. **Counselor → Diagnosis Workspace**
   - Add fictional diagnostic impression/code
   - Evidence/source summary
   - Status: draft, reviewed, approved, amended, inactive
   - Effective dates and history
6. **Client Visibility Preview**
   - Policy-controlled demonstration of what a client might see
   - Default to hidden until organizational policy is decided

### User actions

- Counselor assigns a fictional assessment to an assigned fictional client.
- Client completes mock questions and submits.
- Counselor reviews results and records interpretation.
- Counselor creates a draft fictional diagnosis, reviews it, and explicitly approves it.
- Counselor amends rather than overwrites a previously approved entry.
- Admin may configure workflow labels but cannot diagnose or approve clinical content.
- Prototype shows blocked actions when attempted from the wrong role.

### Data models

```text
AssessmentDefinition
- id
- name
- version
- purpose
- population
- licensingStatus
- active

AssessmentAssignment
- id
- clientId
- definitionId
- assignedByClinicianId
- assignedAt
- dueAt
- status
- clientVisibility

AssessmentSubmission
- id
- assignmentId
- submittedAt
- mockScore
- mockSeverityBand
- responseVersion

AssessmentReview
- id
- submissionId
- clinicianId
- reviewedAt
- interpretation
- status

DiagnosisRecord
- id
- clientId
- codeSystem
- code
- displayLabel
- status: draft | approved | amended | inactive
- enteredByClinicianId
- approvedByClinicianId
- effectiveAt
- supportingSourceIds[]
- priorVersionId
```

### Acceptance criteria

1. Only the counselor role can assign, interpret, approve, amend, or inactivate a diagnosis in the demonstration.
2. Client role sees only its own assigned mock assessments.
3. Admin role cannot enter or approve diagnosis content.
4. Submitted assessment state is immutable in the UI; corrections create a new version.
5. A diagnosis cannot become “Approved” without an explicit counselor confirmation step.
6. The screen states that scores do not diagnose and that clinical judgment is required.
7. No real assessment text, copyrighted instrument, client response, diagnosis, or clinical data is committed to the repository.

### Security considerations

- Assessment responses and diagnoses are highly sensitive and production-blocked without authenticated server-side authorization, encryption, auditing, secure storage, retention policy, and backups.
- Verify clinician-client assignment before every access.
- Separate administrative workflow metadata from clinical content permissions.
- Log assignment, submission, view, interpretation, approval, amendment, export, and disclosure.
- Validate assessment licensing and permitted electronic use.
- Define break-glass access, amendment policy, client access policy, and record-release workflow.
- If future AI is considered, require approved use cases, BAA/vendor review, data minimization, provenance, human review, monitoring, and prohibition on autonomous diagnosis.

### Dependencies

- Workstream 1 role and relationship model.
- Clinical leadership approval of assessment and diagnosis policies.
- Assessment licensing review.
- Decision on the production system of record and Valant capabilities.
- Legal/privacy review of client visibility and consent.

---

## Workstream 3 — Admin Integration Center with Valant and configurable future connectors

### Objective

Turn the current static integration cards into a configurable **mock** integration catalog that demonstrates ownership, mappings, status, sync direction, health, and reconciliation without storing credentials or calling external services.

### Status target

- Integration catalog: **Implemented as documentation → Simulated**.
- Valant and all external connectors: remain **Planned / Production-blocked**.

### Screens

1. **Admin → Integration Catalog**
   - Valant EHR
   - Calendar / Scheduling
   - HIPAA-capable Telehealth
   - Insurance Verification
   - Payments
   - Email/SMS Reminders
   - “Add Future Connector” mock action
2. **Connector Detail**
   - Status: Demo, Planned, Configuration Draft, Production-blocked
   - Owner and system-of-record designation
   - Sync direction and frequency concept
   - Entity/field mapping preview
3. **Valant Concept Mapping**
   - Patient/client synchronization
   - Appointment synchronization
   - Counselor availability
   - Charges/billing status
   - Intake/status updates
4. **Mock Sync Monitor**
   - Last fictional run
   - Mock successful, warning, and failed records
   - Retry/reconciliation concept
5. **Connector Configuration Draft**
   - Non-secret labels and mock endpoints only
   - Explicit warning not to enter credentials

### User actions

- Add, edit, enable, or disable a fictional connector configuration in memory.
- Choose a proposed system of record for each entity.
- Configure fictional sync direction and mapping labels.
- Run a mock synchronization and inspect fabricated results.
- Resolve a fictional conflict by selecting the authoritative value.
- Export a non-sensitive mapping summary for stakeholder review.

### Data models

```text
ConnectorDefinition
- id
- name
- category
- vendor
- status: demo | planned | configuration_draft | production_blocked
- capabilities[]

ConnectorConfiguration
- id
- connectorDefinitionId
- enabledInDemo
- ownerRole
- environmentLabel
- syncMode
- scheduleLabel
- containsSecrets: false

EntityMapping
- id
- connectorConfigurationId
- localEntity
- externalEntity
- systemOfRecord
- direction: inbound | outbound | bidirectional
- fieldMappings[]

MockSyncRun
- id
- connectorConfigurationId
- startedAt
- finishedAt
- status
- createdCount
- updatedCount
- skippedCount
- errorCount

MockSyncIssue
- id
- syncRunId
- entityType
- fictionalRecordRef
- issueType
- resolutionStatus
```

### Acceptance criteria

1. Every connector displays “Demo,” “Planned,” or “Production-blocked”; none display “Connected” or imply live synchronization.
2. Valant concepts include all five requested synchronization areas.
3. No secret, credential, token, real endpoint, or client data can be entered or persisted.
4. Mock sync runs produce clearly fictional records and deterministic outcomes.
5. A mapping explicitly names the proposed system of record and sync direction.
6. Conflict/retry/reconciliation states are represented.
7. Connector configuration resets on reload.

### Security considerations

- Production credentials belong in a managed secrets service, never browser code, logs, source control, or GitHub Pages.
- Validate vendor contracts, API access, security posture, data flows, least-privilege scopes, BAAs where required, retention, and incident responsibilities.
- Use authenticated backend integration workers, replay protection, idempotency keys, rate limits, encryption, monitoring, and audit logs.
- Minimize synchronized fields and maintain consent/authorization context.
- Design safe failure handling so a partial sync cannot silently corrupt care status, appointments, billing, or identity links.

### Dependencies

- Vendor/API discovery, especially verified Valant capabilities and contractual access.
- Canonical identifiers and status models from Workstream 4.
- Counselor availability ownership decision from Workstream 1.
- Data-flow diagrams and security risk analysis.
- Vendor management, legal, privacy, and BAA review.

---

## Workstream 4 — End-to-end referral, intake, assignment, and scheduling workflow

### Objective

Make the highest-value care-coordination journey demonstrable from a public referral through intake, insurance review, counselor assignment, appointment scheduling, active care, follow-up, and closure.

### Status target

- Current CRM and booking fragments: **Implemented/Simulated → coherent end-to-end Simulated workflow**.
- Notifications, eligibility, calendar, and EHR changes remain **Production-blocked**.

### Screens

1. **Public → Request Care / Referral Form**
   - Self, parent/guardian, professional referral, or other source
   - Minimal fictional contact and service preferences
2. **Client → Inquiry Confirmation**
   - Reference number and next steps
   - Invitation to continue mock intake
3. **Client → Intake Wizard**
   - Demographics/contact mockup
   - Communication preferences
   - Forms/documents checklist
   - Insurance information/status
   - Consent and guardian concepts
4. **Admin → Intake Work Queue**
   - Missing items, owner, age/SLA, contact attempts, and blockers
5. **Admin → Insurance Review Queue**
   - Pending, needs information, approved, not verified, self-pay discussion
6. **Admin → Counselor Assignment Workspace**
   - Specialty, population, location, format, insurance, availability, and capacity matching factors
   - Match rationale and admin override
7. **Client/Admin → Scheduling**
   - Available fictional slots
   - Hold, request, confirmation, reschedule, cancellation, and waitlist concepts
8. **Admin → Care Journey Kanban**
   - New Inquiry, Contacted, Intake Started, Insurance Review, Counselor Assigned, Scheduled, Active, Follow-Up, Closed
9. **Role Notifications**
   - Client next-step reminders
   - Counselor new-assignment and submission alerts
   - Admin overdue work alerts

### User actions

- Submit a fictional inquiry and receive a mock reference.
- Continue a multi-step mock intake and observe checklist progress.
- Upload action remains disabled or uses generated placeholder metadata only.
- Admin records fictional contact attempts, requests missing information, and advances valid stages.
- Admin reviews mock insurance status.
- Admin compares counselor matches and assigns a fictional counselor.
- Client requests a fictional slot; admin/counselor confirms it.
- Client reschedules or requests cancellation.
- Missed appointment creates a follow-up task.
- Closure requires a mock reason and records a simulated audit event.

### Data models

```text
Referral
- id
- sourceType
- createdAt
- serviceNeed
- preferredLocationId
- preferredFormat
- preferredContactMethod
- status

IntakeCase
- id
- referralId
- fictionalClientId
- ownerUserId
- checklistItems[]
- completionPercent
- status
- blockers[]

ContactAttempt
- id
- intakeCaseId
- channel
- outcome
- attemptedAt
- actorId

InsuranceReview
- id
- intakeCaseId
- fictionalPayerLabel
- status
- requestedAt
- reviewedAt
- authorizationLabel
- notesSummary

CounselorMatch
- id
- intakeCaseId
- counselorId
- score
- factors[]
- availabilitySnapshot
- capacitySnapshot
- status

Assignment
- id
- intakeCaseId
- counselorId
- assignedByUserId
- assignedAt
- status
- rationale

Appointment
- id
- assignmentId
- appointmentTypeId
- locationId
- format
- startsAt
- endsAt
- status
- source
- priorAppointmentId

WorkflowEvent
- id
- entityType
- entityId
- eventType
- fromStatus
- toStatus
- actorRole
- occurredAt
```

### Acceptance criteria

1. A new fictional referral can proceed through every care-journey stage without editing source data.
2. Invalid stage jumps are blocked or require an explicit admin override reason.
3. Intake progress and blockers are visible to the client and authorized staff in role-appropriate language.
4. Counselor recommendations show match factors and current fictional capacity; final assignment remains an admin action.
5. Booking prevents selection of a visibly unavailable mock slot during the session.
6. Rescheduling retains a link to the prior appointment; cancellation and no-show create follow-up states.
7. Every role sees only its authorized mock subset.
8. Reloading clears all session changes and displays the prototype limitation.

### Security considerations

- Collect the minimum necessary information at each step.
- Production referral/intake links require identity verification, CSRF protection, bot/rate protection, secure sessions, validation, and safe error handling.
- Server authorization must verify role, organization, assignment, care relationship, guardian authority, and consent before access.
- Insurance data, documents, and scheduling details require encryption, audit logs, controlled retention, and secure deletion.
- Notifications must avoid sensitive content and honor communication consent/preferences.
- Calendar and EHR integrations require idempotent operations and reconciliation to avoid duplicate or lost appointments.

### Dependencies

- Workstream 1 roles, counselor roster, availability, services, and capacity.
- Approved care-journey status definitions and transition rules.
- Intake ownership and escalation/SLA policy.
- Insurance workflow discovery.
- System-of-record decisions and future connector design from Workstream 3.

---

## Workstream 5 — Plain-English user manual and guided demo

### Objective

Create a repeatable, non-technical walkthrough for stakeholders and future usability sessions. The guide must explain what works, what is simulated, what is planned, and what is production-blocked.

### Status target

- User manual / guided demo: **Planned → Implemented documentation**.
- In-app guided tour: **Planned → Simulated**, after Workstreams 1–4 stabilize.

### Screens and documents

1. **`USER_MANUAL.md`**
   - What the prototype is and is not
   - How to run locally
   - How to select each role
   - Plain-English walkthrough by role
   - Reset/reload behavior
   - Status legend and known limitations
2. **`GUIDED_DEMO.md`**
   - 15–20 minute facilitator script
   - Suggested role order
   - Talking points and discovery questions
3. **In-app “Start Guided Demo”**
   - Step counter
   - Role/screen instructions
   - Next, Back, Skip, Exit
   - No automatic data submission
4. **Feature Status Drawer**
   - Implemented, Simulated, Planned, Production-blocked labels
5. **Feedback Capture Template**
   - Workflow, pain point, expected outcome, severity, role, follow-up owner
   - Download/copy only; no production submission

### User actions

- Follow a public-to-client-to-counselor-to-admin demonstration.
- See an explanation before each simulated or blocked action.
- Open feature status from any guided step.
- Exit and restart the tour.
- Copy a mock feedback template without sending data.
- Use a facilitator checklist to record stakeholder observations outside the application.

### Data models

```text
DemoGuide
- id
- title
- audience
- estimatedMinutes
- steps[]

DemoStep
- id
- role
- route
- targetLabel
- title
- plainEnglishInstruction
- talkingPoints[]
- featureStatus
- nextStepId
- previousStepId

FeatureStatusDefinition
- featureId
- label
- status
- limitation
- productionDependency

FeedbackPrompt
- id
- role
- question
- category
```

### Acceptance criteria

1. A first-time stakeholder can launch and complete each role walkthrough without developer assistance.
2. Every guided step names its status and data limitation.
3. The guide never instructs users to enter real data or credentials.
4. The client walkthrough never navigates through a client directory.
5. The counselor walkthrough includes clinician review responsibilities for documentation, assessment, and diagnosis concepts.
6. The admin walkthrough includes the CRM, Integration Center, Privacy & Security Center, and roadmap.
7. Documentation and in-app labels use matching terminology.

### Security considerations

- Do not include screenshots or examples containing real client, provider, credential, endpoint, or account data.
- Clearly distinguish security architecture proposals from implemented controls.
- Do not use analytics or feedback tools that collect personal data without review and consent.
- Keep demo reset behavior obvious so shared devices do not retain misleading state.

### Dependencies

- Stable navigation and status labels from Workstream 1.
- Stable end-to-end journey from Workstream 4.
- Assessment/diagnosis guardrails from Workstream 2.
- Final connector terminology from Workstream 3.
- Stakeholder review for language, training order, and discovery prompts.

---

## Cross-workstream production requirements

These requirements are **production-blocked** and are not satisfied by the GitHub Pages prototype:

### Identity and access

- Authenticated server-side authorization on every operation.
- Role-based and relationship-based access controls with deny-by-default policies.
- Multi-factor authentication for workforce users and appropriate client authentication.
- Secure account recovery, session timeout, revocation, privileged-access review, and minimum-necessary access.

### Data protection

- Encryption in transit and at rest with managed keys and rotation.
- Secure, isolated storage for records and documents.
- Secrets management outside source control and browser code.
- Data minimization, retention schedules, secure deletion, export controls, and client-record separation.

### Accountability and resilience

- Tamper-resistant audit logging and monitoring.
- Security risk analysis, vulnerability management, penetration testing, and remediation governance.
- Incident response and breach procedures.
- Tested backups, disaster recovery, availability targets, and restoration exercises.
- Secure hosting, environment separation, configuration/change management, and operational alerting.

### Vendor and clinical governance

- Business Associate Agreements where required.
- Vendor security and privacy review.
- Verified Valant and other integration contracts/capabilities.
- Clinical governance for assessments, diagnoses, documentation, AI assistance, signatures, amendments, and record release.
- Formal policies for consent, guardian access, outside-professional communication, and client-visible information.

## Definition of done for V2 planning

V2 planning is complete when:

1. `FEATURE_STATUS.md` accurately reflects the deployed prototype.
2. Stakeholders approve the role matrix and nine-stage workflow vocabulary.
3. Each workstream has a named owner, discovery participants, and decision log.
4. Systems of record and integration unknowns are documented.
5. Assessment/diagnosis governance questions are assigned to clinical leadership.
6. Production security requirements are accepted as separate implementation work—not inferred from prototype visuals.
7. No real data, credentials, or production API configuration is added to this repository.

