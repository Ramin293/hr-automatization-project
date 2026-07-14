# HR Domain Model

## HR Core

- Employee is assigned to one department, position, and optional unique staffing position.
- An employee can read self; a manager can read direct reports; HR can read all.
- Salary is field-filtered unless the caller has `hr.compensation.read`.
- Creating an employee and occupying a vacant staffing position is atomic.

Employee status supports `DRAFT`, `PRE_HIRE`, `ACTIVE`, leave states, suspension, termination, and archive. The first API creates `ACTIVE` employees only.

## Absence

The implemented path is `MANAGER_REVIEW -> HR_REVIEW -> APPROVED`, with rejection possible at either review. Approval uses request and balance versions to reject stale decisions. Annual leave is constrained to one calendar year in v1; cross-year requests are split by the caller.

Invariants: active employee, valid substitute, no self-substitution, no overlapping active request, sufficient balance, maximum 60 calendar days, and one result per idempotency key.
