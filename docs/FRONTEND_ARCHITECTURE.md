# Frontend architecture

The page layer talks only to repository contracts. `repositories/index.ts` selects adapters; v1.0.1 uses deterministic local adapters. TanStack Query owns server-like state, while Zustand stores only developer UI preferences. React Router provides lazy route boundaries.

The dependency direction is `page -> repository contract -> adapter -> DTO/domain mapper`. A future API adapter must validate external payloads before mapping them to domain models. Components must never call Camunda or internal microservices directly.

Primary modules are `app`, `shared`, `widgets`, `features`, `repositories`, and `mocks`. Authorization in the browser is presentation-only; the backend remains authoritative.
