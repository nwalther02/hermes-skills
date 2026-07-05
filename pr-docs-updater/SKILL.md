---
name: pr-docs-updater
description: Update project documentation from PR-ready code changes with minimal context. Use when preparing, reviewing, or repairing a GitHub PR/branch and documentation may need to reflect new behavior, architecture, workflow, validation, roadmap/current-state, or agent instructions; especially when the user wants token-efficient doc checks, diff-first doc audits, or all project/agent docs kept current before merge.
---

# PR Docs Updater

## Purpose

Use this skill to keep project and agent-facing documentation aligned with the newest PR work while spending as few tokens as possible. Prefer changed hunks, symbol searches, and targeted section reads over full-file reading.

## Workflow

1. Confirm the checkout and branch:

```bash
pwd
git status --short --branch
git branch --show-current
```

If the task is implementation/doc editing and the current branch is `main`, create a PR branch before edits unless the user explicitly says not to. If the workspace is not a Git repo, stop and ask where the repo or PR branch lives.

2. Run the scanner from the repo root:

```bash
python3 ~/.codex/skills/pr-docs-updater/scripts/scan_pr_docs.py
```

Use `--base <ref>` when the PR targets something other than `origin/main`.

3. Inspect only the focused evidence:

```bash
git diff --unified=0 --find-renames <base>...HEAD -- <changed-file>
rg -n "<term1>|<term2>|<term3>" <candidate-doc>
sed -n '<start>,<end>p' <candidate-doc>
```

Read entire docs only when targeted evidence is insufficient, the file is small, or the document is the authoritative current-state surface.

4. Update docs that a merge-ready PR would reasonably touch:

- User-facing behavior: `README.md`, feature docs, usage docs, release notes.
- Architecture/contracts/data shape: architecture docs, ADRs, context docs, schemas.
- Tests/CI/deploy/local workflow: testing strategy, deployment docs, workflow docs.
- Agent continuity: `AGENTS.md`, `CLAUDE.md`, `docs/AGENTS_CONTEXT.md`, `agents/CURRENT_STATE.md`, repo-orientation docs.
- Roadmap/phase status: roadmap, current-state, plan docs that route the next agent.

For detailed doc-surface routing, read `references/doc-surfaces.md`.

5. Verify the documentation patch:

```bash
git diff --check
git diff --stat
git diff -- <edited-docs>
```

If the PR has no doc impact, say so explicitly and cite the diff scan basis. Do not claim docs are current unless you inspected the PR diff and candidate documentation surfaces.

## Editing Rules

- Keep docs updates scoped to the PR behavior, not a broad rewrite.
- Preserve existing terminology and file naming exactly, including filename case.
- Update agent-facing docs when the change affects future coding, validation, branching, release, or repo-orientation behavior.
- Prefer adding one precise bullet, section sentence, or status update over restating the whole design.
- Do not bury stale status. Move completed phase notes to done/current wording and make the next action obvious.
- Before final response, ensure every edited doc is included in `git diff --stat` and no unrelated generated artifacts were staged.
