# HR backend implementation plan

## Repository audit

The repository contained a React frontend and a placeholder `backend/README.md`; there was no API gateway, database, identity provider, document service, task service, Camunda gateway, notification service, audit service, or backend test harness to extend. The frontend already defines an HR employee and leave-request contract.

## Architecture decision

The first backend release is one deployable NestJS API gateway with isolated `hr-core` and `hr-absence` modules. This is a deliberate modular-monolith starting point: it provides working business behavior without creating empty microservices. Modules own their tables through Prisma repositories and communicate with shared capabilities only through ports. The ports can later become HTTP or message-bus adapters without changing application services.

Shared capabilities represented by ports:

- Document Service: creates the corporate leave-request document and returns `documentId` and number.
- Workflow Gateway: starts the Camunda process and returns `workflowInstanceId` and current step.
- Audit Service: accepts security and business audit records; a local adapter persists immutable audit events.
- Event Bus: transactional outbox records are ready for RabbitMQ publication.
- Authentication: request context is accepted from safe development headers outside production; production requires a trusted upstream context.

## Service boundaries

- HR Core owns employees, departments, positions, staffing positions, employment metadata, and leave-balance identity.
- HR Absence owns leave requests, balance reservations/deductions, overlap checks, workflow/document references, and absence events.
- API Gateway owns HTTP routing, validation, normalized errors, correlation IDs, OpenAPI, and rate limits. It does not own HR business rules.

## First vertical slices

1. Employee directory and profile: pagination, search, status/department filters, sensitive-field projection, create employee, status validation, audit and outbox.
2. Leave request: create with idempotency key, validate employee/balance/dates/overlap/substitute, create document/workflow references, manager review, HR review, atomic balance deduction, audit and outbox.
3. Operations: PostgreSQL migration, deterministic seed, health/readiness endpoints, structured request logs, Docker Compose, OpenAPI, unit and HTTP tests.

## Data model and migrations

PostgreSQL is the system of record. Prisma models use explicit foreign keys, unique employee numbers, unique idempotency keys, workflow/document indexes, timestamps, actor fields, and optimistic `version` columns. Production schema changes are applied only by committed migrations.

## Events

The first slice publishes through the outbox: `EmployeeCreated`, `LeaveRequestSubmitted`, `LeaveManagerReviewed`, `LeaveApproved`, and `LeaveRejected`. Payloads contain identifiers and workflow context, not personal or medical data.

## Deferred slices

Recruitment, sick leave, business trips, hiring, onboarding, probation, employee changes, termination, offboarding, development, and analytics are intentionally deferred. Their boundaries and target contracts are documented, but no empty controllers are created.

## Risks and assumptions

- Real shared services do not exist yet, so local adapters return deterministic references; production adapters must be configured before deployment.
- Development identity headers are disabled when `NODE_ENV=production`.
- RabbitMQ publishing is represented by an outbox; a separate publisher worker is a follow-up slice.
- Holiday calendars are not yet available. The first leave slice counts calendar days and exposes the calculation policy explicitly.
