# Future backend authorization requirements

The current role switcher is presentation-only. Search/filter controls operate on
fictional records already loaded in the browser. Neither hidden buttons, browser
filters, nor CORS provide access control. No authentication or HIPAA compliance
is implemented or implied by this refinement.

## Proposed role boundaries

| Role | Proposed allowed scope | Important exclusions |
| --- | --- | --- |
| Administrator | Center-scoped directory, assignments, scheduling, operational reports, conversion, manual invitation tracking | Operational oversight must not automatically grant unrestricted access to sensitive clinical notes; define field-level access separately |
| Counselor | Own availability and appointments; explicitly assigned clients and authorized care workflows | No center-wide directory exports, unrelated client profiles, arbitrary conversion, or administrator operations |
| Client | Own record, approved booking/onboarding tasks, appointment changes, permitted communications | No other client IDs, staff queues, self-selected counselor/admin permissions, or manual provider tracking updates |

Before real-data use, implement authenticated sessions with server-verified identity,
staff MFA, session expiry/revocation, secure recovery and appropriate CSRF defenses.
Map identity to explicit center membership, role grants, counselor assignments,
and client/guardian relationships. Never trust a role, actor, center, counselor,
or owner ID supplied by the browser without validating it.

Apply authorization independently to every read and write route, profile lookup,
history endpoint, conversion, invitation update, assignment, calendar query,
appointment change, search result, count, report, export, and notification. Deny by
default. Scope queries before searching, filtering, sorting, counting, or paginating.
Use safe field allowlists, server-side validation, bounded query/page sizes, and
stable sort tie-breakers. Tests must cover guessed IDs, unrelated counselors,
changed assignments, revoked roles, cross-center requests, guardian boundaries,
and attempts to change protected fields.

Keep lifecycle conversion, booking, intake, clinical documentation, and optional
provider adapters distinct. Validate transitions and concurrency in transactions.
Attribute authorized changes to verified actors with time, action, source, and
record reference; do not copy sensitive answers into generic logs. Separate
administrative history from protected clinical content, with explicit retention
and access policies. Audit relevant reads/exports as well as mutations according
to the center's approved policy.

Before production, complete security/privacy review, TLS and approved storage,
encrypted backups and restore tests, secret/key management, redacted telemetry,
consent/retention/deletion decisions, rate limits, monitoring, and incident response.
See [Native Scheduling Plan](NATIVE_SCHEDULING_PLAN.md) for conflict prevention,
questionnaire privacy, reminder delivery, and separately evaluated integrations.
These are future requirements, not capabilities added in this branch.
