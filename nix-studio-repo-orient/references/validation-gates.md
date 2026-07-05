# Validation Gates

Choose the smallest gate that proves the change. Broaden when touching shared contracts, auth/security, sync, UI, or package boundaries.

## Baseline Root Gates

Run from `/Users/nicksmac/Code/Projects/nix-studio`:

```bash
pnpm typecheck
pnpm test
pnpm lint
pnpm check:boundaries
pnpm check:security-patterns
pnpm build
```

Use the full baseline before PR handoff unless the user explicitly asks for a narrower pass.

## Focused Package Gates

Web:

```bash
pnpm --filter @nix/web typecheck
pnpm --filter @nix/web test
pnpm --filter @nix/web lint
pnpm --filter @nix/web build
```

API:

```bash
pnpm --filter @nix/api typecheck
pnpm --filter @nix/api test
pnpm --filter @nix/api test:harness
pnpm --filter @nix/api check
```

Domain:

```bash
pnpm --filter @nix/domain typecheck
pnpm --filter @nix/domain test
```

Metadata or canvas contract:

```bash
pnpm --filter @nix/metadata typecheck
pnpm --filter @nix/canvas-contract typecheck
```

## UI Gates

For any visible UI change:

```bash
pnpm --filter @nix/web test:a11y
pnpm --filter @nix/web test:visual
```

Only update snapshots when the visual change is intentional:

```bash
pnpm --filter @nix/web test:visual:update
```

Also inspect light and dark states. Earth Power violations are merge blockers, not style nits.

## Auth And Security Gates

For auth, token, route, CSP, CORS, logging, or tenant/workspace isolation work:

```bash
pnpm --filter @nix/api test
pnpm check:security-patterns
pnpm --filter @nix/web test
```

Add or run negative-tenant/workspace tests when changing any account/workspace-scoped path. Confirm secrets, JWTs, opaque payloads, and editor payloads are not logged.

## Sync And Data-Spine Gates

For Phase 3 sync/store/device/schema/domain work:

```bash
pnpm --filter @nix/domain test
pnpm --filter @nix/api test
pnpm --filter @nix/api test:harness
pnpm check:boundaries
pnpm check:security-patterns
```

Prefer fixture-specific tests first while developing, then run the broader package gates before handoff.

## PR Handoff

Before commit or PR:

```bash
git status --short
git diff --check
git diff --stat
```

Stage only task-relevant files. Confirm `CURRENT_STATE.md`, `WORKLOG.md`, and any docs named in `docs/DOC_REGISTRY.md` were updated or intentionally skipped.
