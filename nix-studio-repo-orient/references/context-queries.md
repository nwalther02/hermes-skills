# Context Queries

Use these recipes to avoid reading whole files before you know where the work lives.

## Claude Code With claude-mem smart-explore

Prefer the smart-explore ladder:

```text
smart_search(query="<concept>", path="./apps", max_results=15)
smart_outline(file_path="<file>")
smart_unfold(file_path="<file>", symbol_name="<symbol>")
```

Good starting queries:

- Sync/store: `appendOps`, `listChangelogSince`, `ChangeLogOp`, `workspace_id`, `seq`, `protocolVersion`
- Device enrollment: `challenge`, `enroll`, `P-256`, `public_key`, `pending`
- Domain contracts: `RecordKind`, `payloadHash`, `canonical`, `HLC`, `deterministic`
- Auth: `requireAccount`, `requireSession`, `machine token`, `singleFlight`, `AuthProvider`
- Security: `documentCsp`, `redact`, `CORS`, `JWT_SECRET`, `opaque`
- UI: `Button`, `ThemeToggle`, `SignInScreen`, `Showcase`, `data-theme`
- Canvas: `AnnotationElement`, `Asset`, `Canvas`, `Konva`

Use Markdown smart-outline/unfold for long docs. Expand only the section that governs the task.

## Codex Shell Search

Start broad but cheap:

```bash
rg -n "<concept|symbol>" apps packages docs
rg -n "TODO|FIXME|HACK|unsafe|dangerouslySetInnerHTML" apps packages docs
```

Map files before reading:

```bash
node scripts/symbol-outline.mjs apps/api/src/store.ts
node scripts/symbol-outline.mjs packages/domain/src
```

Then read tight slices:

```bash
sed -n '120,220p' apps/api/src/store.ts
sed -n '1,180p' packages/domain/src/changelog.ts
```

## Useful File Discovery

```bash
rg --files apps/api/test packages/domain/src apps/web/src/auth
rg --files docs docs/plans docs/adr
rg --files apps/web/src/components/ui/earth-power apps/web/src/styles/earth-power
```

## Cross-Boundary Sweeps

```bash
rg -n "react|react-dom|hono|cloudflare|wrangler|konva|window\\.|document\\." packages/domain packages/metadata packages/canvas-contract
rg -n "JWT_SECRET|localStorage|sessionStorage|dangerouslySetInnerHTML|unsafe-inline|unsafe-eval" apps packages docs
rg -n "account_sub|workspace_id|Workspace|tenant|Space" apps/api packages/domain docs
```

Treat sweep results as leads, not conclusions. Read the surrounding code before changing it.
