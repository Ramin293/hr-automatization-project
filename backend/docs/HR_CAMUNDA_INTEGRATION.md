# HR Camunda Integration

HR Absence depends on `WorkflowGateway`, not Camunda SDK types. `startLeaveRequest` receives a stable business key, employee and manager references, and correlation id. It returns workflow instance id and current step, which are persisted on the leave request and audit events.

The development adapter returns deterministic references. A production adapter must authenticate service-to-service, use the idempotent business key, map timeouts to retryable integration errors, and never make Camunda the owner of leave balance or request state.

Workflow callbacks should enter a dedicated authenticated endpoint, deduplicate by callback/event id, validate the expected transition/version, and commit the state plus outbox atomically. Manual API review remains the v1 executable adapter path.
