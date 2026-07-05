---
name: safe-filesystem-reorg
description: Plans and executes conservative machine-local file reorgs and repo doc imports with archive-first and no-overwrite safeguards. Use when the user asks to clean up home, Code, or Documents folders, move/archive project files, import loose docs into repos, or implement a no-destructive-delete reorg plan.
---

# Safe Filesystem Reorg

## Quick start

Use this skill for broad local cleanup or doc-import work where losing user files would be costly. Start by separating repo-backed changes from machine-local moves, then verify current state before moving anything.

## Workflow

1. Clarify the requested scope from the prompt and current filesystem.
2. Inventory candidate paths with read-only tools first.
3. Check for Git worktrees with `git worktree list --porcelain` before treating odd folders as disposable.
4. For Git clones, inspect status, remotes, and ahead/behind state before archiving.
5. For Git bundles, verify the bundle before moving it.
6. Prefer archive/quarantine paths plus a manifest over deletion.
7. Never overwrite an existing destination; choose a distinct archive path or stop.
8. Keep unrelated local work out of repo doc-import PRs.

## Repo Doc Imports

When loose docs need to be added to a project repo:

1. Inspect the target repo status and current branch.
2. Create a feature branch before editing.
3. Add only the requested docs or closely related routing docs.
4. Normalize obvious whitespace if validation requires it.
5. Run repo-appropriate checks such as `git diff --cached --check`.
6. Commit, push, and open a PR when the user wants the change shipped.

## Handoff

Report what moved, where the manifest/archive lives, what was left untouched, and what still needs a live decision.
