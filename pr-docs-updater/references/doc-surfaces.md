# Documentation Surface Routing

Use this reference after `scan_pr_docs.py` identifies candidate docs, or when a diff clearly affects a known project surface.

## Common Surfaces

- `AGENTS.md`: repo-specific agent workflow, branch rules, validation gates, hard contracts, and traps future agents must know before editing.
- `CLAUDE.md`: Claude-specific equivalent when the repo uses it. Keep format differences intact.
- `docs/AGENTS_CONTEXT.md`: compact repo orientation, invariants, and current architecture for future agents.
- `agents/CURRENT_STATE.md`: current phase, just-finished work, next step, known blockers, and validation status.
- `README.md`: user/developer setup, visible behavior, commands, and feature overview.
- `docs/ARCHITECTURE.md` or `architecture.md`: module boundaries, data contracts, persistence, sync, deployment shape, or major flow changes.
- `docs/TESTING.md`, `docs/testing/**`: new test commands, changed smoke gates, skipped coverage, CI/local validation workflow.
- `docs/ROADMAP.md`, `ROADMAP.md`, `docs/plans/**`: phase completion, sequencing changes, deferred work, or next implementation slice.
- `docs/adr/**`: architectural decisions that introduce or reverse a long-lived constraint.
- `.github/pull_request_template.md`, `.github/workflows/**`: PR checklist, CI, labels, automation, or required merge gates.
- `CHANGELOG.md`, release notes: user-visible behavior that should be announced for a release.

## Routing Heuristics

- Changed setup scripts, package scripts, Docker, Wrangler, deployment config, or CI workflows usually require README/testing/deployment docs.
- Changed persistence, migrations, schemas, cache names, storage keys, or sync rules usually require architecture/context/agent docs.
- Changed UI behavior, routes, keyboard behavior, accessibility, or product copy usually require README/feature docs and sometimes screenshots or design guardrails.
- Changed validation commands or new regression tests usually require testing docs or agent validation gates.
- Changed phase completion or a PR that unblocks the next task usually requires current-state/roadmap docs.
- Changed security/auth/share/permissions behavior usually requires architecture/security docs plus agent warnings about owner boundaries.

## Token-Saving Inspection Pattern

Use line-targeted commands before opening full docs:

```bash
rg -n "term|symbol|feature" AGENTS.md docs agents README.md
sed -n '40,95p' docs/ARCHITECTURE.md
git diff --unified=0 -- docs/ARCHITECTURE.md
```

When the first search finds nothing, search changed path stems and nearby domain words. Example: a diff touching `syncDriveState` should search `sync`, `Drive`, `state`, `persistence`, and the edited file path stem.
