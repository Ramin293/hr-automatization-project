# HR Automatization Project

Monorepo for the ERTIS OPERATIONS corporate document management and workflow automation platform.

## Structure

- `frontend/` - React, TypeScript and Vite application with deterministic mock repositories.
- `backend/` - reserved backend service boundary for the future API Gateway/BFF and domain services.

## Frontend

```powershell
cd frontend
pnpm install
pnpm dev
```

The frontend opens at `http://localhost:5173` by default. Detailed architecture and release scope are documented in `frontend/docs/`.

## Backend

Backend implementation has not started yet. Its folder documents the intended security and integration boundaries without committing placeholder production code.
