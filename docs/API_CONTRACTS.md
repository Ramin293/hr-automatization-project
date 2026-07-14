# API contracts

All production calls use `/api/v1` through `VITE_API_BASE_URL`. Core correspondence endpoints are `GET/POST /correspondence/incoming`, `GET/PATCH /correspondence/incoming/:id`, `POST /:id/register`, and `POST /:id/send-for-resolution`.

Tasks expose list, detail, claim, complete, delegate, extend and escalate commands. Workflows expose definitions, versions, instances, validation, testing, publishing and incidents. Registry and signature commands are separate service capabilities exposed by the BFF.

API DTOs must be validated and mapped into domain models. Network, validation, permission, conflict and timeout failures map to stable frontend errors.
