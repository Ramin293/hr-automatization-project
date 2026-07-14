# ERTIS OPERATIONS HR backend

NestJS and PostgreSQL backend for the HR workspace. The current release implements employee records and the leave-request workflow behind one API gateway. It does not implement other department business modules.

## Local start

```powershell
Copy-Item .env.example .env
docker compose up -d postgres rabbitmq
pnpm install
pnpm prisma:migrate
pnpm prisma:seed
pnpm start:dev
```

OpenAPI is available at `http://localhost:3000/api/docs` and health at `http://localhost:3000/health`.

Development requests require `X-Dev-User-Id`, `X-Dev-Role`, and optionally `X-Dev-Department-Id`. These headers are rejected in production.

See [docs/HR_BACKEND_IMPLEMENTATION_PLAN.md](docs/HR_BACKEND_IMPLEMENTATION_PLAN.md) for scope and architecture.
