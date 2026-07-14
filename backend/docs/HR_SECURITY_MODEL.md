# HR Security Model

Authentication is supplied by the API gateway. Development headers are accepted only when `NODE_ENV` is not `production` and `DEV_AUTH_ENABLED` is not `false`. Production uses trusted `X-User-Id`, `X-Role`, `X-Employee-Id`, and `X-Department-Id`; perimeter infrastructure must strip client-supplied identity headers.

RBAC is enforced by the Nest guard. ABAC is enforced in application services for self, direct team, and all-employee scopes. Denied object access is recorded in `hr_audit_events`. Compensation fields are omitted without explicit permission.

Controls include DTO allowlists, UUID parsing, Helmet, CORS policy hook, request throttling, correlation ids, generic 500 responses, optimistic locking, idempotency keys, transactional audit/outbox, and parameterized Prisma queries. Secrets are environment variables and must be managed by the deployment secret store.

Production always selects HTTP document and workflow adapters; mock adapters cannot be selected by production configuration. The local Compose `app` profile intentionally runs in development mode.
