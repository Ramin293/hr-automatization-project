# HR Database Schema

The source of truth is `prisma/schema.prisma`; SQL is versioned under `prisma/migrations`.

Core tables: `hr_departments`, `hr_positions`, `hr_staffing_positions`, `hr_employees`. Absence tables: `hr_leave_balances`, `hr_leave_requests`. Reliability tables: `hr_audit_events`, `hr_outbox_events`.

Important constraints include unique employee number/email/staffing assignment, unique yearly balance per employee/type, and unique leave idempotency key. Foreign keys preserve organization and manager relationships. Indexes cover employee status/department/manager, leave status/period, audit correlation, and outbox polling.

Monetary and day values use PostgreSQL decimal types. Dates that represent business days use `date`; timestamps use UTC. Optimistic `version` columns protect approval and balance updates.
