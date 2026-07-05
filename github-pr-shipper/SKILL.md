---
name: github-pr-shipper
description: Run the user's autonomous GitHub publish loop when they say "push and commit", "commit and push", "ship this", "create PR and bring to ready to merge", or similar. Coordinates repo orientation, local main refresh from origin/main, documentation updates, validation, commit/push, PR creation or update, review-thread and CI repair, final review, and merge after green gates without routine user intervention.
---

# GitHub PR Shipper

## Operating Contract

Treat "push and commit" as authorization to finish the whole PR lifecycle: prepare the diff, update docs, validate, commit, push, open or update the PR, repair review/CI issues, revalidate, and merge when the merge gates are clean.

Do not ask for routine confirmation. Stop only for blockers: missing credentials, ambiguous repo/branch ownership, destructive cleanup, merge conflicts requiring product judgment, failing gates you cannot diagnose, or branch protection requiring a human action.

## Skill Order

Use these skills when available and relevant:

1. Repo-specific orientation skill, if one exists for the current repo.
2. `connect-github` for live PR, comments, review, and check state.
3. `pr-docs-updater` before the first commit and again after PR repair changes.
4. GitHub plugin skills such as `github:gh-address-comments`, `github:gh-fix-ci`, or `github:yeet` when the user has them installed and they match the current phase.

## Preflight

Run from the repo root:

```bash
~/.codex/skills/github-pr-shipper/scripts/preflight.sh
```

Also inspect staged, unstaged, and untracked files. Stage only files that belong to this task. Preserve unrelated user changes.

Refresh local `main` from `origin/main` without asking:

```bash
~/.codex/skills/github-pr-shipper/scripts/sync_local_main.sh
```

If currently on `main` with implementation/doc changes, first create a feature branch to preserve the work, then sync local `main`, then rebase the feature branch onto updated `main` when it applies cleanly.

## Workflow

1. **Base freshness**
   - Fetch `origin` and fast-forward local `main` to `origin/main` without asking.
   - If local `main` has diverged from `origin/main`, stop and report the exact divergence; do not reset.
   - If working changes started on stale `main`, branch first, sync `main`, then rebase the feature branch onto updated `main` only when the rebase is clean.

2. **Diff ownership**
   - Confirm the branch, base, remote, and changed files.
   - If a PR already exists for the branch, fetch its live state before deciding what to do.
   - If there are unrelated changes, leave them unstaged and mention them in the final summary.

3. **Documentation pass**
   - Run `pr-docs-updater` from the repo root.
   - Update docs that a merge-ready PR would touch: README, architecture/context, testing, roadmap/current-state, agent instructions, release notes, or PR templates.
   - Keep updates narrow and diff-grounded.

4. **Validation and self-review**
   - Run the repo's smallest meaningful validation gates, then broader gates when the change touches shared contracts, docs used by agents, build/CI config, or user-facing flows.
   - Review the full staged diff from a code-review stance before committing.
   - Fix issues found by your own review before publishing.

5. **Commit and push**
   - Commit only relevant files with a clear message.
   - Push the feature branch and set upstream.
   - Never commit feature work directly to `main`.

6. **PR create or update**
   - Create a PR into `main` unless the repo clearly targets another base.
   - If a PR already exists, update its body instead of opening a duplicate.
   - Use a substantive body with: Summary, Documentation, Validation, Review/CI Repair, and Merge Readiness.
   - Mark draft PRs ready only after docs and validation are complete.

7. **Repair loop**
   - Fetch live review comments, unresolved review threads, PR comments, and checks before deciding what remains actionable.
   - Fix actionable review feedback and CI failures, then rerun the relevant local validation.
   - Commit and push repairs.
   - Repeat until there are no actionable unresolved review/CI issues.
   - Treat thread-aware review state as authoritative over flat comment lists.
   - Resolve review conversations only after the code/docs change plainly addresses them, or when resolving is required to merge and the thread is no longer actionable.

8. **Final merge gates**
   - Re-check live PR state after the last push.
   - Merge only when the PR is non-draft, mergeable, up to date enough for branch protection, checks are green or intentionally neutral, no blocking review remains, and no actionable unresolved thread remains.
   - Use the repo's existing merge style when evident. If no convention is evident and GitHub allows it, prefer squash merge with branch deletion for single-branch feature work.
   - After merge, sync local `main` from `origin/main` again without asking so the next task starts from the merged state.

For review/CI repair commands and merge gate details, read `references/pr-repair-and-merge.md`.

## Final Response

Report the branch, commit(s), PR URL, documentation updated, validation run, review/CI repair status, and merge result. If blocked, state the exact blocker and the last verified clean gate.
