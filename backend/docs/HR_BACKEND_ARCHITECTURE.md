# HR Backend Architecture

## Decision

The first release is one deployable NestJS API with bounded modules, not a distributed system. `hr-core` owns employee and staffing rules. `hr-absence` owns leave balances, requests, and approval transitions. PostgreSQL is the system of record; Prisma transactions protect aggregate changes.

Shared platform capabilities are ports: document creation, workflow execution, audit publication, and event delivery. Development uses deterministic adapters. Production adapters must call the existing platform services and must not create parallel document, task, audit, or Camunda stores.

## Request flow

`HTTP -> correlation/auth/rate limit -> controller -> application service -> repository/integration ports -> PostgreSQL/outbox`.

The outbox is committed with domain state. The publisher sends `PENDING` rows to the durable RabbitMQ topic exchange and marks confirmed messages `PUBLISHED`; consumers must deduplicate by event id. Failed messages retry up to ten times and then move to `FAILED` for operational recovery.

## Deferred modules

Recruitment, lifecycle, development, and worker self-service beyond absence are deferred until their first end-to-end use case is selected. They intentionally have no empty controllers or tables.
