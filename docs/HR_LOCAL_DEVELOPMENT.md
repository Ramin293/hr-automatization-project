# HR Local Development

Frontend:

```powershell
cd frontend
pnpm install
pnpm dev --host 127.0.0.1 --port 5174
```

Open `http://localhost:5174/hr` and switch the development persona to **HR специалист**. Add Employee is available at `/hr/hiring/add-employee` and uses browser-only mock references/localStorage.

Validation:

```powershell
pnpm lint
pnpm test
pnpm build
```

Backend local setup and Prisma commands are documented in `backend/README.md`. Do not add Hiring migrations, endpoints or seed records.
