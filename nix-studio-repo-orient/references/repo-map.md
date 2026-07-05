# nix-studio Repo Map

Use this as an orientation map, not as a replacement for live code or current docs.

## Identity

`nix-studio` is a pnpm monorepo for a multi-device, cloud-backed, offline-capable productivity app. It combines object-based knowledge, rich text, visual annotation, tasks, sync, auth, and eventually AI/MCP surfaces.

## Top-Level Dispatch Files

- `AGENT_START_HERE.md` - session entrypoint and current required reading.
- `CURRENT_STATE.md` - live status, active branch expectation, current mission, next action.
- `WORKLOG.md` - recent factual changes and decisions; read the newest entries first.
- `CLAUDE.md` - governing rules, especially PR workflow and Earth Power UI constraints.
- `CONTEXT.md` - domain glossary and preferred terms.
- `docs/DOC_REGISTRY.md` - docs that must be checked before closing substantive work.

## Apps

- `apps/web` - React 19 + Vite + TypeScript UI.
  - Auth: `apps/web/src/auth/`
  - App shell: `apps/web/src/App.tsx`, `apps/web/src/main.tsx`
  - Earth Power primitives: `apps/web/src/components/ui/earth-power/`
  - Tokens/styles: `apps/web/src/styles/earth-power/`, `apps/web/src/index.css`
  - Visual/a11y tests: `apps/web/tests/`
  - Design rules: `apps/web/DESIGN.md`
- `apps/api` - Cloudflare Workers + Hono API.
  - App wiring/routes: `apps/api/src/app.ts`, `apps/api/src/index.ts`
  - Auth/security/logging: `apps/api/src/auth.ts`, `security.ts`, `logger.ts`
  - Store/sync/device surfaces: `apps/api/src/store.ts`, `devices.ts`
  - D1 migrations: `apps/api/migrations/`
  - API and harness tests: `apps/api/test/`

## Packages

- `packages/domain` - platform-free domain contracts and pure logic.
  - Sync/data primitives: `changelog.ts`, `hlc.ts`, `ids.ts`, `seq.ts`, `canonical.ts`, `payload-hash.ts`, `records.ts`, `ports.ts`
  - Tests live beside source as `*.test.ts`
- `packages/metadata` - metadata and opaque/crypto-adjacent helpers.
- `packages/canvas-contract` - renderer-neutral canvas and annotation contracts.

## Plans And Contracts

- `docs/plans/00-master-plan.md` - roadmap and phase scope.
- `docs/plans/01-phase3-data-spine-contract.md` - authoritative Phase 3 data-spine contract.
- `docs/plans/02-phase2-3-reconciliation.md` - R&D recommendations folded into the plan.
- `docs/plans/03-phase3-execution-plan.md` - Phase 3 PR ladder and fixture sequencing.
- `docs/plans/04-phase3-pr3.2-sync-api-plan.md` - sync API/apply-engine execution plan when present.
- `docs/SECURITY.md` - CSP, auth, token, PWA, and observability rules.
- `docs/OPAQUE-CONTRACT.md` - opaque record contract.
- `docs/PERF-BUDGETS.md` - performance budgets.
- `docs/adr/` - accepted architecture decisions; supersede instead of rewriting accepted ADRs.

## External Source Repos

Read these only when a task explicitly depends on copied behavior:

- `/Users/nicksmac/Code/Projects/nix-kanban-tool` - kanban, Dexie/local-first, board/views, TipTap, scheduling, ordering references.
- `/Users/nicksmac/Code/Projects/nix-markup-tool/nix-markup-tool` - visual annotation, Konva adapter, asset/editor references.
- `/Users/nicksmac/Code/Projects/fitness-pwa` - Google auth and Cloudflare/Hono auth source.
- `/Users/nicksmac/Code/Projects/earth-power-design-system` - canonical UI design system.

## Boundary Rules

- `@nix/domain` must not import React, DOM, Konva, Hono, Cloudflare, Wrangler, or browser-only APIs.
- Apps may import packages; package-to-package imports must follow the repo's boundary checks.
- Konva belongs behind UI/canvas adapters, not in domain contracts.
- Auth/session JWTs remain in memory; do not persist session tokens.
- Workspace is the data partition boundary. Avoid calling it tenant or space.
