# HR Events Catalog

| Event | Producer | Essential payload |
| --- | --- | --- |
| `EmployeeCreated` | HR Core | employeeId, departmentId, staffingPositionId |
| `LeaveRequestSubmitted` | HR Absence | leaveRequestId, employeeId, workflowInstanceId, documentId |
| `LeaveManagerApproved` | HR Absence | leaveRequestId, employeeId, status |
| `LeaveManagerRejected` | HR Absence | leaveRequestId, employeeId, status |
| `LeaveHrApproved` | HR Absence | leaveRequestId, employeeId, status |
| `LeaveHrRejected` | HR Absence | leaveRequestId, employeeId, status |

Every outbox record has event id, aggregate identity, correlation id, creation time, status, and payload. RabbitMQ routing convention is `hr.<aggregate>.<event>` in lowercase. Consumers use the event id as the idempotency key. Payload evolution is additive within a version; breaking changes require a new event name/version.
