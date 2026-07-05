---
name: branch-to-pr-gate
description: Checks whether a branch can become a GitHub PR and opens or explains the gate based on live divergence. Use when the user provides a branch URL/name and asks to open a PR, create a PR from a branch, or diagnose "no commits between base and head".
---

# Branch To PR Gate

## Quick start

Treat a provided branch URL or branch name as the source of truth. Verify live divergence before promising that a PR can be opened.

## Workflow

1. Parse the repo, branch, and intended base from the URL or prompt.
2. Use GitHub connector tools first for live compare/PR state when available.
3. If connector tools are unavailable, fetch the remote branch and compare refs locally.
4. If the branch is ahead of base, create or prepare the PR as requested.
5. If the branch is identical to base, explain that there is no PR to open and ask the user to push the intended commits.
6. If local refs disagree with GitHub, fetch and compare again before reporting.

## Guardrails

- Do not ask the user to restate repo/branch context when the URL already contains it.
- Do not open a PR from a branch with zero commits ahead of base.
- For coding projects, respect branch-based workflow and avoid committing feature work directly to `main`.
- Keep the check quick unless the branch actually has content to review or ship.
