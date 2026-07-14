# HR API Contracts

Base path: `/api/v1/hr`. OpenAPI UI: `/api/docs`.

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/overview` | HR counters |
| GET/POST | `/employees` | search or create employees |
| GET | `/employees/:id` | self/team/all profile read |
| GET/POST | `/leave-requests` | scoped list or idempotent submission |
| GET | `/leave-requests/:id` | scoped detail |
| POST | `/leave-requests/:id/review` | manager or HR decision |

Write validation rejects unknown fields. Leave submission requires `Idempotency-Key`. Review body contains `stage`, `decision`, and current `version`. Errors use `{ error: { code, message, details }, correlationId, path, timestamp }`.

Development identity headers are `X-Dev-User-Id`, `X-Dev-Role`, `X-Dev-Employee-Id`, and `X-Dev-Department-Id`. Production ignores them and expects trusted gateway headers without `Dev`.
