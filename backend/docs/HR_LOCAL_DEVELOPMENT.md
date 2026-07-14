# HR Local Development

Requirements: Node 22+, pnpm 11+, and Docker.

```powershell
Copy-Item .env.example .env
docker compose up -d postgres rabbitmq
pnpm install
pnpm prisma:migrate
pnpm prisma:seed
pnpm start:dev
```

Health is at `http://localhost:3000/health`, readiness at `/health/ready`, and Swagger at `/api/docs`.

Example HR headers: `X-Dev-User-Id: local-hr`, `X-Dev-Role: HR_SPECIALIST`. Example employee headers additionally include the seeded employee UUID as `X-Dev-Employee-Id`. Set `DEV_AUTH_ENABLED=false` to exercise trusted non-dev headers. PostgreSQL is exposed on 5433 and RabbitMQ management on 15673.
