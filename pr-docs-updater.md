---
name: "pr-docs-updater"
description: "Update project and agent documentation from PR-ready code changes with minimal context: diff-first documentation audits, focused doc checks, roadmap/current-state updates, and merge-readiness doc repair."
type: "skill"
parameters:
  - name: base_ref
    description: Optional PR base ref such as origin/main.
    required: false
  - name: task
    description: Optional branch, PR, feature, review, or documentation goal to focus the audit.
    required: false
---

# PR Docs Updater

Use this when preparing, reviewing, or repairing a PR/branch and docs may need to reflect new behavior, architecture, validation, roadmap/current-state, or agent instructions. Optimize for low tokens: inspect changed hunks, search terms, and nearby doc sections before reading whole files.

## First Pass

Run from the repo root:

```bash
pwd
git status --short --branch
git branch --show-current
```

If implementation/doc editing starts on `main`, create a PR branch before edits unless the user explicitly says not to. If the workspace is not a Git repo, ask for the repo or PR branch path.

## Diff-First Scan

Prefer the installed scanner:

```bash
python3 ~/.codex/skills/pr-docs-updater/scripts/scan_pr_docs.py
python3 ~/.codex/skills/pr-docs-updater/scripts/scan_pr_docs.py --base origin/main
```

Use the scanner output to get changed files, extracted search terms, docs already touched, likely documentation surfaces, and focused commands.

Manual fallback:

```bash
git diff --name-status --find-renames <base>...HEAD
git diff --unified=0 --find-renames <base>...HEAD -- <changed-file>
git diff --cached --name-status --find-renames
git diff --name-status --find-renames
git ls-files --others --exclude-standard
```

## Targeted Inspection

Search candidate docs with changed symbols, path stems, feature names, and nearby domain words:

```bash
rg -n "<term1>|<term2>|<term3>" AGENTS.md CLAUDE.md README.md docs agents .github
sed -n '<start>,<end>p' <candidate-doc>
```

Read whole docs only when targeted evidence is insufficient, the file is small, or the doc is an authoritative current-state surface.

## Documentation Surfaces

- `AGENTS.md`: repo-specific agent workflow, branch rules, validation gates, hard contracts, and traps future agents must know before editing.
- `CLAUDE.md`: Claude-specific repo instructions. Keep format differences intact.
- `docs/AGENTS_CONTEXT.md`: compact repo orientation, invariants, and current architecture.
- `agents/CURRENT_STATE.md`: current phase, just-finished work, next step, blockers, and validation status.
- `README.md`: user/developer setup, visible behavior, commands, and feature overview.
- `docs/ARCHITECTURE.md` or `architecture.md`: module boundaries, data contracts, persistence, sync, deployment shape, or major flow changes.
- `docs/TESTING.md`, `docs/testing/**`: test commands, smoke gates, skipped coverage, CI/local validation workflow.
- `docs/ROADMAP.md`, `ROADMAP.md`, `docs/plans/**`: phase completion, sequencing changes, deferred work, or next implementation slice.
- `docs/adr/**`: long-lived architectural decisions.
- `.github/pull_request_template.md`, `.github/workflows/**`: PR checklist, CI, labels, automation, or required merge gates.
- `CHANGELOG.md` or release notes: user-visible behavior that should be announced.

## Routing Heuristics

- Setup scripts, package scripts, Docker, Wrangler, deployment config, or CI workflows usually touch README/testing/deployment docs.
- Persistence, migrations, schemas, cache names, storage keys, or sync rules usually touch architecture/context/agent docs.
- UI behavior, routes, keyboard behavior, accessibility, or product copy usually touch README/feature docs and sometimes design guardrails.
- Validation command changes or new regression tests usually touch testing docs or agent validation gates.
- Phase completion or PRs that unblock a next task usually touch current-state/roadmap docs.
- Security/auth/share/permissions changes usually touch architecture/security docs plus agent warnings about owner boundaries.

## Editing Rules

- Keep docs scoped to the PR behavior, not a broad rewrite.
- Preserve terminology and filename case exactly.
- Update agent-facing docs when future coding, validation, branching, release, or repo-orientation behavior changes.
- Prefer one precise bullet, section sentence, or status update over restating the whole design.
- Do not bury stale status. Move completed phase notes to done/current wording and make the next action obvious.

## Verification

Before finishing:

```bash
git diff --check
git diff --stat
git diff -- <edited-docs>
```

If the PR has no doc impact, say so explicitly and cite the diff scan basis. Do not claim docs are current unless the PR diff and candidate documentation surfaces were inspected.
