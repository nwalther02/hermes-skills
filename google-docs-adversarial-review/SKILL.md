---
name: google-docs-adversarial-review
description: Performs user-specific adversarial reviews directly inside live Google Docs, with severity-ranked critique, append/edit verification, list-format cleanup, and exact link handoff. Use when the user asks to review, scrutinize, critique, red-team, or append feedback to a Google Doc or plan.
---

# Google Docs Adversarial Review

## Quick start

Use connected Google Docs or Drive tools when available. The deliverable is usually the live doc updated and verified, not just a chat summary.

## Workflow

1. Resolve the newest Google Doc URL or document target.
2. Read the current document structure before reviewing.
3. If the user says a prior version is stale, re-ground on the new doc instead of carrying assumptions forward.
4. Write findings-first critique: severity-ranked, implementation-focused, and tied to exact document claims where possible.
5. Append or insert the review into the live document when requested.
6. Re-read the inserted boundary paragraphs to verify the edit landed.
7. Clean inherited list or bullet formatting if the appended section picked up the prior list style.
8. Return the exact document link and note what was verified.

## Review Focus

Look for:

- missing source of truth;
- unowned operational steps;
- schema or artifact gaps;
- unsafe automation assumptions;
- weak rollback or recovery paths;
- mismatch between plan wording and implementation reality.

## Guardrails

- Do not praise before findings in an adversarial review.
- Do not claim the live doc was updated until readback verifies it.
- Do not rely on old doc context when the user provides a new URL.
