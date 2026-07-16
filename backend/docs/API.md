# Module 2 API

All endpoints are under `/api/v1`. Field-level schemas and stable error envelopes are published at
`/openapi.json`; Swagger UI is at `/docs`.

- `/workflow`: definition versions, validation/publication, instances/history/tasks and versioned
  forms/submissions.
- `/documents`: types/templates/records, streaming content, generation, signatures, registration,
  acknowledgements and checklists.
- `/recruitment`: requests/reviews, vacancies/channels/publication, candidates/applications,
  screening/interviews/evaluations, commissions, offers, hiring and onboarding.
- `/terminations`: initiation/decisions, order registration, offboarding tasks, scheduling,
  completion and cancellation.

Mutations use `organizationId`; mutable resources require `revision`. Task actions require an
`idempotencyKey`. Return/reject/cancel and waivers require reasons. Authorization and organization
ownership are evaluated from stored resources; cross-organization IDs do not disclose records.
See [API contracts](API_CONTRACTS.md) and [permissions](PERMISSIONS.md).
