# Task Routing

Start with `AGENT_START_HERE.md`, `CURRENT_STATE.md`, recent `WORKLOG.md`, and `CLAUDE.md`. Then load only the rows that match the task.

## Phase Or Planning Work

- Read: `docs/plans/00-master-plan.md`, then the specific phase plan or contract.
- For Phase 3/data-spine: read `docs/plans/01-phase3-data-spine-contract.md`, `docs/plans/03-phase3-execution-plan.md`, and the latest numbered plan for the active PR when one exists.
- Check: `docs/adr/`, `CONTEXT.md`, `docs/DOC_REGISTRY.md`.
- Avoid: treating an older memory, chat summary, or plan draft as current until repo docs confirm it.

## Sync, Store, Op-Log, Devices, D1

- Read docs: `docs/plans/01-phase3-data-spine-contract.md`, `docs/plans/03-phase3-execution-plan.md`, `docs/SECURITY.md`.
- Inspect code: `packages/domain/src/{changelog,hlc,ids,seq,canonical,payload-hash,records,ports}.ts`, `apps/api/src/{store,devices,app,auth}.ts`, `apps/api/migrations/`.
- Inspect tests first: `packages/domain/src/*.test.ts`, `apps/api/test/sync-store.test.ts`, `apps/api/test/harness/`, related API tests.
- Claude smart-explore query examples: `appendOps`, `device enrollment`, `ChangeLogOp`, `workspace_id`, `payloadHash`, `seq`.
- Codex query examples: `rg -n "appendOps|ChangeLogOp|workspace_id|payloadHash|device" apps/api packages/domain docs/plans`.

## Auth, Machine Tokens, Security

- Read docs: `docs/SECURITY.md`, `CLAUDE.md`, relevant Phase 2 sections in `docs/plans/00-master-plan.md`.
- Inspect code: `apps/api/src/{auth,security,logger,app,store}.ts`, `apps/web/src/auth/`.
- Inspect tests: `apps/api/test/{auth,security,tenant,logger}.test.ts`, `apps/web/src/auth/*.test.ts`.
- Watch for: persisted session JWTs, secrets in config, missing redaction, weak tenant/workspace scoping, missing negative tests.

## UI Or Design System Work

- Read docs: `CLAUDE.md`, `apps/web/DESIGN.md`, and only then the relevant component files.
- If the task changes the design system source or rules, inspect `/Users/nicksmac/Code/Projects/earth-power-design-system`.
- Inspect code: `apps/web/src/components/ui/earth-power/`, `apps/web/src/styles/earth-power/`, `apps/web/src/showcase/Showcase.tsx`, target feature files.
- Inspect tests: `apps/web/tests/a11y.spec.ts`, `apps/web/tests/visual.spec.ts`.
- Watch for: raw hex, off-palette colors, gradients, blur/glass, emoji, missing focus rings, unverified light/dark states.

## Canvas, Markup, Annotation

- Read docs: `docs/plans/00-master-plan.md`, `docs/plans/01-phase3-data-spine-contract.md`, `docs/OPAQUE-CONTRACT.md` if visibility matters.
- Inspect code: `packages/canvas-contract/src/`, any future adapter under `apps/web/src/`.
- Source reference only when needed: `/Users/nicksmac/Code/Projects/nix-markup-tool/nix-markup-tool/src/editor-core`, `src/ui/CanvasAdapter.tsx`, `shared/models.ts`.
- Watch for: Konva leaking into domain, image-space coordinate drift, renderer contract mixing with record contract.

## Kanban, Tasks, Views, Rich Text

- Read docs: phase sections in `docs/plans/00-master-plan.md` and any active execution plan.
- Source reference only when needed: `/Users/nicksmac/Code/Projects/nix-kanban-tool/src/features`, `src/db/schema.ts`, `src/sync/`, `src/lib/order`, `src/features/task-detail`.
- Watch for: client-final order keys, whole-object LWW, bypassing the Phase 3 data-spine contract.

## Docs Or Agent Context Work

- Read: `docs/DOC_REGISTRY.md` and `docs/ai-context-files-spec.md`.
- Always check whether `CURRENT_STATE.md` and `WORKLOG.md` need updates.
- Update `AGENT_START_HERE.md` only when mission or first-read routing changes.
- Avoid duplicating source-of-truth content across docs; link to canonical files.
