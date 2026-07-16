# Module 2: workflow, documents, recruitment, hiring and termination

## Delivered scope

Module 2 is implemented inside the existing FastAPI modular monolith and reuses Module 1 identity,
database-authoritative authorization, organization structure, staffing slots, employees,
assignments, audit log, and transactional outbox. It does not change or depend on the frontend.

The implementation contains 41 new relational PostgreSQL tables and migration `0004`. Business
records use UUID identifiers, organization ownership, foreign keys, useful indexes, optimistic
revisions where records are mutable, and UTC timestamps for instants.

## Workflow runtime

Process definitions have immutable published versions. A running instance stores the exact route
snapshot, form-version IDs, context and definition-version ID used at start, so later configuration
changes cannot alter an in-flight process.

Supported behavior:

- draft, review, return, validation, publication, comparison and cloning of route versions;
- sequential and parallel tasks with `all` or `any` completion and required approver counts;
- safe declarative transition conditions (`and`, `or`, comparisons, membership and existence);
- process initiator, explicit user, subject employee, permission/functional-role holder, signing
  authority and commission-member actor rules;
- idempotent decisions, optimistic concurrency, required reasons for return/reject/cancel;
- authorized delegation-backed task reassignment;
- persistent `configuration_error`, audit entry and stable `PROCESS_ACTOR_UNRESOLVED` response when
  an actor cannot be resolved;
- immutable process history and safe transactional workflow events.

No custom Python, SQL, expression evaluation, or user-provided executable code is accepted.

## Versioned forms and checklists

Form definitions support published versions and fields with code, label, type, required flag,
declarative validation rules, reference source, visibility/editability data, confidentiality,
ordering and help text. Submissions are validated and stored against the exact published version
captured in the process snapshot. Submission content is redacted from audit state.

Document checklist items bind required document types to a business entity and prevent hiring or
termination completion until mandatory items are validated. Initial form/checklist configuration
is included in the deterministic seed.

## Documents

The documents module provides document types, templates and immutable template versions, document
records and immutable content versions, checklists, signatures, registration and employee
acknowledgements. Uploads are streamed, filename/path-safe, MIME-limited, size-limited and hashed.
Storage is behind local and S3 adapters. Failed metadata persistence removes an unreferenced object.

Generation uses a deliberately limited local UTF-8 scalar-placeholder adapter. Binary DOCX/PDF
rendering belongs behind a future document-rendering adapter. Manual signature confirmation is
available only in development and is explicitly marked `manualConfirmation`; production requires
a real signature integration. Signature and acknowledgement status remain distinguishable.

## Recruitment and formal hiring

The implemented route is:

1. A scoped unit actor creates a request against an authoritative unit, position and optional
   vacant staffing slot.
2. HR checks completeness; staffing/finance confirms position, capacity and conditions.
3. HR creates and publishes a vacancy through an internal or recorded manual external channel.
4. A consented candidate and application are recorded. Protected email, phone and identity values
   are Fernet-encrypted and never returned by generic views, audit or outbox.
5. Screening, interview participants and one immutable evaluation per evaluator are recorded.
6. A configured commission records conflict declarations and can decide only with quorum.
7. An offer is sent and explicitly accepted or declined.
8. A separate hiring case validates mandatory documents and onboarding tasks, locks staffing
   capacity, prevents duplicate employee numbers, creates Person/Employee/Assignment atomically,
   fills the vacancy and emits `employeeHired`.

Expired candidate records can be anonymized only after retention expiry and only when no active
application exists. Personal fields are removed, consent becomes withdrawn, and the safe event
contains only the candidate ID.

## Termination and offboarding

Termination initiation validates the employee's actual primary assignment and unit scope.
Employee-request, mutual-agreement, employer-initiative and contract-expiry reasons are seeded;
configured reasons can require a legal review. HR/legal/signature decisions, order registration,
future scheduling, return/reject paths and cancellation are explicit.

Future termination sets assignment status to `scheduled_end` but keeps employment and access
active. Final completion is blocked until the effective date, a mandatory validated document and
completed/authorized-waived handover, asset return, access revocation and settlement tasks exist.
Secondary assignments require an explicit `end` or `retain` plan. Completion ends only scheduled
assignments and changes employee status atomically. Cancellation before the effective date restores
scheduled assignments and cancels pending tasks; cancellation after legal effect is rejected.

Exit-interview restricted notes are excluded from generic views and audit. IAM, payroll and asset
system confirmations remain externally verifiable tasks until real adapters are connected.

## Security and observability

Every route checks a stable permission and authoritative organization/resource ownership. Unit
scope is derived from stored assignments and access scopes rather than request names. Cross-org IDs
are returned as not found or a stable scope/access error to prevent IDOR disclosure.

All material decisions append redacted audit events. Domain events are written in the same database
transaction through the existing outbox and contain identifiers/status only—never CVs, contacts,
identity data, compensation or restricted notes.

## Primary API groups

- `/api/v1/workflow`: route administration, instances, tasks, history, versioned forms/submissions;
- `/api/v1/documents`: types, templates, records, upload/download/generation, signatures,
  registration, acknowledgements and checklists;
- `/api/v1/recruitment`: requests, reviews, vacancies/publications, candidates/applications,
  interviews/evaluations, commissions, offers, hiring and onboarding;
- `/api/v1/terminations`: initiation, decisions, order registration, tasks, scheduling, completion
  and cancellation.

Swagger UI and the generated OpenAPI document are the authoritative field-level API contract.

## Operations

Apply and verify the PostgreSQL schema:

```powershell
alembic upgrade head
alembic current
alembic check
python -m app.seed
```

Run quality gates:

```powershell
pytest
pytest -m integration
ruff check app tests migrations
ruff format --check app tests migrations
mypy app
python -m app.open_api --check
```

The seed may be run repeatedly. It uses deterministic IDs and conflict-safe inserts for Module 1
and Module 2 reference/configuration data.
