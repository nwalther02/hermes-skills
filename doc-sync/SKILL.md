---
name: doc-sync
description: Synchronize project documentation with a change before it is brought to close. Walks a checked-in per-project doc registry and forces an explicit "updated (what)" or "skipped (why)" decision for EVERY canonical doc, so pieces stop getting missed. Use when wrapping up a change, before committing, before opening or finalizing a PR, when the user says "update the docs", "doc sync", "sync the docs", "bring this to close", or when a Stop-hook reminder reports un-synced docs. Also use to add a doc registry to a project that lacks one.
---

# doc-sync

Treat documentation like the PR itself: a change is not "done" until every doc that
should reflect it has been updated **or explicitly cleared**. The failure mode this
skill exists to kill is the *silent omission* — a doc that nobody decided about. Here,
silence is a bug. Every canonical doc gets an explicit verdict.

## When to run

- Before committing a substantive change, and before opening or finalizing a PR.
- When the user asks to "update the docs", "sync docs", or "bring this to close".
- When a Stop-hook reminder fires saying docs look un-synced.
- Skip for truly trivial changes (typo, comment, formatting) — but say that you skipped and why.

## Workflow

1. **Get the facts (deterministic).** Run the check script from the project root:
   ```bash
   bash ~/.codex/skills/doc-sync/scripts/doc-sync-check.sh
   ```
   It reports: the registry it found, files changed on this branch (code vs docs),
   which registry docs were touched, which were **not**, the always-update docs status,
   and any **registry drift** (docs on disk missing from the registry, or vice-versa).
   If it reports *no registry*, go to [REFERENCE.md](REFERENCE.md) → "Bootstrapping a registry".

2. **Decide every untouched doc.** For each registry doc the script lists as *not touched*,
   consult its trigger in the registry (and the change-type matrix in [REFERENCE.md](REFERENCE.md)).
   Either edit it now, or record a one-line reason it needs no change. No doc may be left unaddressed.

3. **Always-update docs are mandatory.** `CURRENT_STATE.md` and `WORKLOG.md` (per the
   registry's `always_update` set) must reflect this change unless it was trivial. Verify
   `CURRENT_STATE.md`'s active branch, status, and next action match reality; append a
   `WORKLOG.md` entry. These are the two most-missed docs.

4. **Reconcile drift.** If the script flags a doc on disk that is not in the registry,
   add a row for it (path + tier + update trigger). If it flags a registry doc missing on
   disk, fix or remove the row. The registry must end the pass matching reality.

5. **Integrity check.** No broken cross-doc links; no content duplicated across docs
   (link to the single source of truth instead — see the project's no-duplication rule).

6. **Write one reviewable run report.** Keep live chat updates short. At the end, write a
   single report with affected files, the diff/changes, validation output, and the final
   accounting table:
   ```bash
   bash ~/.codex/skills/doc-sync/scripts/doc-sync-report.sh
   ```
   Append or fill in the "Accounting table" section before finalizing. The final chat reply
   should link the report and summarize only the few important outcomes.

## Output: the run report

Always close the pass with a report file. It must include:

- repo/branch/head context
- affected files and what changed
- diff stat plus the relevant diff
- validation/doc-sync check output
- the accounting table below, one row per canonical doc, no exceptions

```
| Doc | Verdict | Detail |
|-----|---------|--------|
| CURRENT_STATE.md | ✅ updated | active branch, status, next action |
| WORKLOG.md | ✅ updated | appended entry for this change |
| ARCHITECTURE.md | ⏭️ skipped | no system-design / data-flow change |
| docs/SECURITY.md | ⏭️ skipped | no auth/CSP/token change |
| ... | ... | ... |
```

✅ updated · ⏭️ skipped (with reason) · ⚠️ needs follow-up (out of scope — note it). Every
registry doc appears. An absent doc is the failure this skill prevents.

## The registry

The canonical doc list + per-doc update triggers live in one shared project registry:
`docs/DOC_REGISTRY.md`. Do not create assistant-specific registry files. The shared registry
keeps the checklist version-controlled, reviewable, honored by every agent
(Claude/Codex/Gemini), and self-healing via step 4. To create one for a new project, see
[REFERENCE.md](REFERENCE.md).

## Notes

- This skill **finds and updates** docs; it does not invent a doc system. It builds on the
  project's existing context-file spec when one exists.
- This Codex copy bundles `scripts/stop-reminder.sh` for parity with Claude-style hook
  setups, but it is not automatically wired as a global hook.
- The Stop-hook reminder is a backstop, not the trigger — run this at wrap-up regardless.
- Detail on the change-type → doc matrix, registry format, and the hook is in [REFERENCE.md](REFERENCE.md).
