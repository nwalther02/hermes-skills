---
name: handoff-doc-pr-repair
description: Repairs stale handoff documentation in PRs by grounding review threads in real repo paths and marking historical rollout instructions clearly. Use when the user asks to review PR comments, fix stale docs, resolve handoff-doc comments, or update imported project docs before merge.
---

# Handoff Doc PR Repair

## Quick start

Use this when PR feedback says docs point to stale files, dead-end a future agent, or make historical rollout work look active.

## Workflow

1. Fetch live PR review-thread state first; flat comments may miss unresolved threads.
2. Confirm the actual checkout path, branch, and PR target before editing.
3. Read the referenced docs and verify every named file path against the repo.
4. Make the smallest doc change that fixes the actionable thread.
5. Mark historical rollout plans as historical when they are no longer the live handoff.
6. Redirect active handoff guidance to the current source-of-truth docs.
7. Run relevant doc or repo validation.
8. Commit and push only the scoped repair.
9. Resolve the review thread only after the fix is visible in the final diff or pushed PR.

## Guardrails

- Keep clean-start repos narrowly scoped unless the user explicitly broadens them.
- Do not revive completed rollout instructions as current work.
- Do not resolve review threads based on intent; resolve them based on visible code or doc changes.
