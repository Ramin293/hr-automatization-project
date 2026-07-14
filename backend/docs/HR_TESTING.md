# HR Testing

The test pyramid for this backend is:

1. Unit tests for validation, idempotency, ABAC, transitions, and compensation redaction using port mocks.
2. HTTP tests for middleware, guards, DTO rejection, response/error shape, and OpenAPI reachability.
3. PostgreSQL integration tests for constraints, transactions, optimistic locking, audit, and outbox.
4. Contract tests for document/workflow adapters and RabbitMQ event schemas.

Run `pnpm lint`, `pnpm typecheck`, `pnpm test`, `pnpm test:e2e`, and `pnpm build`. CI should start PostgreSQL, apply migrations from an empty database, seed only when a scenario needs reference data, and never share a database between parallel jobs.

Before production, add Testcontainers suites for concurrent leave approvals and balance races, production adapter contract tests, failure injection for timeouts, and an authorization matrix test for every route.
