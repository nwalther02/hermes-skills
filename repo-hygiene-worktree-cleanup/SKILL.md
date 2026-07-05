---
name: repo-hygiene-worktree-cleanup
description: Safely handles repo hygiene around helper worktrees such as `.claude/worktrees` by verifying Git worktree registration and nested cleanliness before cleanup. Use when the user asks to drop helper worktrees, clean repo-local agent folders, decide whether `.claude/worktrees` should be merged or deleted, or remove stale local worktrees.
---

# Repo Hygiene Worktree Cleanup

## Quick start

Use this for repo-local helper folders that may be real Git worktrees rather than disposable files.

## Workflow

1. Inspect the named folder on disk before deciding what it is.
2. Run `git worktree list --porcelain` from the parent repo.
3. For each nested checkout, inspect `git status --short --branch`.
4. Remove only clean registered worktrees with `git worktree remove <path>`.
5. Remove the parent helper directory only if it is empty.
6. Leave unrelated stale worktree records alone unless the user widens scope.

## Guardrails

- Do not treat `.claude/worktrees` or similar helper folders as docs or config clutter without checking Git state.
- Do not delete dirty or unregistered nested checkouts without explicit user approval.
- Keep cleanup scoped to the user-named paths.
- Report skipped paths and why they were skipped.
