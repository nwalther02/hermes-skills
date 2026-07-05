# doc-sync — Reference

Detail behind [SKILL.md](SKILL.md): the change-type → doc matrix, the registry file
format, how to bootstrap a registry, and the Stop-hook contract.

---

## Why a registry (and not "just check the docs")

"Update the docs" is an open instruction — the agent updates the obvious one and stops.
The miss is the *non-obvious* doc: a security note, a perf budget, a plan whose scope
just shifted. A registry converts an open instruction into a **closed checklist**: a
finite list where each item must get a verdict. The discipline is not "find docs to
update" — it is "account for every doc, updated or skipped."

The registry lives in the project (e.g. `docs/DOC_REGISTRY.md`), checked in, so it is
versioned, reviewable in PRs, and read identically by every agent working the repo. The
skill is generic; the registry is the project's declaration of what "all documentation"
means here.

---

## Change-type → doc matrix

Map the *nature* of the change to the docs whose trigger it likely fires. The registry's
own per-doc "Update trigger" column is authoritative; this is the cross-cutting view.

| You changed… | Almost always update | Also check |
|---|---|---|
| Anything substantive | `CURRENT_STATE.md`, `WORKLOG.md` | the active-branch / next-action fields |
| System design, data flow, a module boundary, an integration | `ARCHITECTURE.md` | a data/contract spec if one exists |
| A data model, sync/storage format, or wire contract | the contract/spec doc | `ARCHITECTURE.md` |
| Auth, CSP, tokens, secrets, observability | `SECURITY.md` (or equiv) | `ARCHITECTURE.md`, `DEPLOYMENT.md` |
| Build, deploy, env vars, CI, release process | `DEPLOYMENT.md` | `README.md` quick-start |
| Local setup, dependencies, conventions, branch rules | `DEVELOPMENT.md` | `README.md` |
| Added/changed/removed a script or npm task | `SCRIPTS.md` | `DEVELOPMENT.md` |
| Test stack, coverage rules, new test patterns | `TESTING.md` | — |
| Project purpose, headline features, quick-start | `README.md` | `ROADMAP.md` |
| Finished a milestone, re-prioritized, scoped new work | `ROADMAP.md` | `CURRENT_STATE.md`, plan docs |
| A plan's scope, sequence, or phase status | the relevant plan doc | `ROADMAP.md`, `CURRENT_STATE.md` |
| Agent roles / orchestration | `AGENTS_CONTEXT.md` | `AGENT_START_HERE.md` |
| The primary mission / what to read first | `AGENT_START_HERE.md` | `CURRENT_STATE.md` |
| UI wiring, design exceptions, component inventory | the app-local design doc | governing design rules doc |
| A perf-sensitive path or a budget | the perf-budget doc | — |
| The doc system itself (new doc type, new rule) | the context-file spec | the registry |

When in doubt, open the doc and read its trigger. A 10-second read beats a missed update.

---

## What "updated" must mean for the always-update docs

These two carry the highest miss rate because they look like overhead, not "the work":

- **`CURRENT_STATE.md`** — the single source of truth for *right now*. After your change,
  its **active branch must match `git branch --show-current`**, its status (🟢/🟡/🔴/🔵)
  must be honest, and its **Next Action** must be the genuine next step. Stale branch name
  or next-action here is the classic drift — the check script and Stop hook both watch it.
- **`WORKLOG.md`** — append a new entry at the **top** (reverse chronological), imperative
  title, factual not aspirational, ISO dates. Record what *did* happen, including blockers.

---

## Run report contract

To reduce live token use, each doc-sync pass should leave one report the user can inspect
after the run. Generate the draft with `scripts/doc-sync-report.sh`, then fill in or append
the final accounting table. The report is written outside the repo by default under
`${TMPDIR:-/tmp}/doc-sync-reports/`, so it does not create extra repo drift.

The final chat response should be short: report path/link, files changed, validation result,
and any follow-up. Avoid streaming the full accounting table live unless the user asks.

---

## Registry file format

Author one shared project registry at `docs/DOC_REGISTRY.md` so every assistant reads and
maintains the same checklist. Do not create separate `.codex/DOC_REGISTRY.md` or
`.claude/DOC_REGISTRY.md` files; if one exists, migrate its contents into
`docs/DOC_REGISTRY.md` and remove the duplicate.
Two parts:

### 1. A machine-readable config comment (parsed by the scripts)

```markdown
<!-- doc-sync-config
always_update: CURRENT_STATE.md, WORKLOG.md
exclude: path/to/generated-or-vendored.md
-->
```

- `always_update` — docs that any substantive change must touch. Drives the Stop-hook signal.
- `exclude` — tracked `.md` files that are generated/vendored and must **not** be hand-maintained,
  so drift detection ignores them. Omit the line if none.

### 2. A canonical-doc table (one row per doc)

Each canonical doc is one table row whose **first cell is the path in backticks** — the
script keys off that. Keep the path cell exactly `` | `path` | ``:

```markdown
| Doc | Tier | Update trigger |
|-----|------|----------------|
| `CURRENT_STATE.md` | 1 | Any meaningful change — branch, status, next action |
| `WORKLOG.md`       | 1 | Append an entry every session / significant change |
| `ARCHITECTURE.md`  | 2 | System design, data flow, module, or integration changes |
```

Tier 1 = read/maintained every session; Tier 2 = on-demand reference. The trigger column
is the authoritative "when does this go stale" — write it as a concrete condition, not "as needed".

---

## Bootstrapping a registry (project has none)

1. Enumerate tracked docs: `git ls-files '*.md' ':!:**/node_modules/**'`.
2. Drop generated/vendored ones (add them to `exclude`).
3. If the project already has a context-file spec (a doc that lists the doc system and
   per-file "When updated" rules), lift its file list and triggers verbatim — do not
   reinvent or duplicate; the registry is the operational checklist, the spec is the prose.
4. Add governing/contract docs the spec may omit (e.g. `CLAUDE.md`, `SECURITY.md`, plan docs,
   app-local design docs) — these are the usual "missing pieces".
5. Set `always_update` to the project's "every session" docs (commonly the state + worklog).
6. Write `docs/DOC_REGISTRY.md` with the config comment + table, then run the check script
   to confirm zero drift.

---

## The Stop-hook contract

`scripts/stop-reminder.sh` can be wired as a global `Stop` hook. It is a **non-blocking
backstop**, not the trigger. This Codex copy bundles the script but does not install a
global hook automatically.

- Reads the hook JSON on stdin (`session_id`, `cwd`).
- No-ops silently when: not a git repo · no `docs/DOC_REGISTRY.md` (so it never nags in
  unrelated projects) · no changes · or the `always_update` docs were already touched.
- Reminds (once per session, via `systemMessage`) when the branch has **non-doc changes**
  but an `always_update` doc was **not** touched — the high-confidence "docs forgot the code"
  signal. It re-arms (clears its per-session marker) once the docs are back in sync.
- It never blocks the stop and never edits files. Acting on the reminder = running this skill.

To change which projects it watches, it keys purely off the presence of a registry file.
In Claude, disable it by removing the `Stop` hook entry from `~/.claude/settings.json`.
