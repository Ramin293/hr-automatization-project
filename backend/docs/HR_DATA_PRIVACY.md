# HR Data Privacy

HR data is confidential. API responses are data-minimized by role; compensation is removed for callers without permission. Logs contain route metadata and identifiers needed for tracing, but must not contain salaries, comments, phone numbers, or document contents.

Audit records retain actor, action, reason, correlation, workflow reference, and minimal changes. Retention periods, legal holds, employee export, and erasure must be defined with legal/compliance before production. Erasure should anonymize eligible personal fields while preserving legally required audit evidence.

Production requires encryption in transit, encrypted database/backups, least-privilege database users, secret rotation, restricted backup restore access, and alerting on repeated denied reads. Seed data is synthetic and must never be mixed with production.
