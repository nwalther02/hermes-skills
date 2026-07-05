---
name: nix-studio-repo-orient
description: Orient Codex or Claude Code quickly in the nix-studio repository with live-state checks, doc routing, code-map exploration, and validation gates. Use when starting coding, review, planning, debugging, PR, sync/data-spine, UI, auth/security, or validation work in /Users/nicksmac/Code/Projects/nix-studio.
---

# Nix Studio Repo Orient

## Purpose

Use this skill to make the first minutes in `nix-studio` cheap and accurate: confirm live repo state, read the right source-of-truth docs, map code before opening large files, and choose the smallest validation gate that proves the work.

## First Pass

Run the bundled script before editing. Resolve `scripts/quick-context.sh` relative to this `SKILL.md`:

```bash
scripts/quick-context.sh /Users/nicksmac/Code/Projects/nix-studio
```

If the bundled script is unavailable, run:

```bash
pwd
git status --short --branch
git branch --show-current
rg --files
```

For implementation work, never edit on `main`. Create a feature branch such as `feat/phase3-short-description` or reuse an existing task branch only when its scope matches. If `CURRENT_STATE.md` disagrees with `git branch --show-current`, report the drift and trust live git for branch state.

## Minimal Context Load

Read only the dispatch set first:

1. `AGENT_START_HERE.md`
2. `CURRENT_STATE.md`
3. The last 3-5 entries in `WORKLOG.md`
4. `CLAUDE.md`

Then route by task. Use `references/task-routing.md` for doc and code surfaces, `references/repo-map.md` for the package map, and `references/validation-gates.md` for commands.

## Code Exploration

Prefer maps over full-file reads.

For Claude Code with `claude-mem` smart-explore, use:

```text
smart_search(query="<topic>", path="./apps or ./packages")
smart_outline(file_path="<file>")
smart_unfold(file_path="<file>", symbol_name="<symbol>")
```

For Codex, use targeted shell search plus the bundled outline script. Resolve `scripts/symbol-outline.mjs` relative to this `SKILL.md`:

```bash
rg -n "<topic|symbol>" apps packages docs
node scripts/symbol-outline.mjs <file-or-dir>
sed -n '<start>,<end>p' <file>
```

For code files over roughly 100 lines, outline or search first and open only the relevant symbol, test, route, reducer, or schema slice.

## Guardrails

- Preserve the monorepo boundaries: apps may import packages; `@nix/domain` stays platform-free.
- Treat `docs/plans/01-phase3-data-spine-contract.md` as authoritative for data-spine and sync work.
- Treat `CLAUDE.md` and `apps/web/DESIGN.md` as binding for UI work; Earth Power has no design latitude.
- Keep domain language aligned with `CONTEXT.md`: Account, Workspace, Member, Space, Server-readable, Opaque (Vault), Conflict, Reconcile, Revision.
- Update context docs when substantive work changes repo state: usually `CURRENT_STATE.md` and `WORKLOG.md`; check `docs/DOC_REGISTRY.md`.
- Stage only task-relevant files and use a PR-based workflow into `main`.

## Reference Routing

- Repo/package map: `references/repo-map.md`
- Task-specific docs and code surfaces: `references/task-routing.md`
- Validation commands: `references/validation-gates.md`
- Token-efficient search recipes: `references/context-queries.md`
