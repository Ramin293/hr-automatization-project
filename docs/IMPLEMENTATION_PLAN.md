# ERTIS OPERATIONS frontend v1.0.1

## Release intent

This branch turns the visual concept from `main` into the first operational frontend slice. It opens directly into a developer workspace and focuses on the complete secretariat intake path, shared task visibility, and workflow observability.

## Included vertical slices

1. Corporate Flow Command Center shell with responsive navigation, search, counters, theme, locale, persona and developer controls.
2. Deterministic mock repositories behind typed contracts; pages do not import fixtures.
3. Secretariat dashboard and incoming correspondence register with URL-ready routing.
4. Incoming letter registration with validation, duplicate check, repository-backed numbering and audit updates.
5. Correspondence case view with document preview, metadata, process route, participants, attachments and history.
6. Unified task inbox with claim/complete interactions.
7. Process operations overview with versions, incidents, text process paths and retry simulation.
8. Organization directory and permission-aware persona switching.

## Deliberately deferred

The visual BPMN/DMN modelers, process migration submission, rich document editing, real EDS integration, production authentication, and live Camunda/API adapters are later vertical slices. Their boundaries and routes are represented in architecture documentation, but this release does not present inactive controls as complete features.

## Verification gate

- `pnpm install`
- `pnpm typecheck`
- `pnpm test`
- `pnpm build`
- browser check at desktop and mobile widths
