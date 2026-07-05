---
name: "fitness-pwa-repo-orient"
description: "Orient quickly in Nick Walther's fitness-pwa repository: app shape, canonical files, storage contracts, UI patterns, service-worker behavior, validation gates, and workflow traps. Use when starting coding, review, audit, debugging, UI, JavaScript, CSS, service-worker, deployment, docs-accuracy, browser, or PR work in /Users/nicksmac/Code/Projects/fitness-pwa."
type: "skill"
parameters:
  - name: task
    description: Optional task, bug, review, or file area to orient around.
    required: false
---

# Fitness PWA Repo Orient
Use this before coding, reviewing, auditing, debugging, or planning work in `/Users/nicksmac/Code/Projects/fitness-pwa`.

## First Pass

Run:

```bash
cd /Users/nicksmac/Code/Projects/fitness-pwa
pwd
git status --short --branch
git branch --show-current
rg --files
```

If implementation work starts on `main`, create a feature branch before edits. If already on a feature branch, reuse it only when the branch scope matches the task.

## Repo Shape

- Lightweight mobile-first workout logging PWA.
- Vanilla JavaScript, HTML, and CSS.
- No framework, bundler, transpiler, or TypeScript.
- `app.js`: primary state, rendering, session flow, program data, Drive sync, localStorage, timer, exercise sheet, history, export helpers.
- `app.css`: design tokens, layout, workout cards, set rows, sheets, motion, responsive behavior.
- `index.html`: app shell and some inline handlers.
- `sw.js`: network-first service worker with auth and Google Drive API bypasses.

## Guardrails

- Preserve the direct vanilla-JS architecture.
- Do not introduce frameworks, build steps, broad abstractions, or unrelated cleanup.
- Preserve localStorage keys and data shapes unless explicitly asked for a migration.
- Preserve inline handler or MVI-style patterns unless the task is specifically to refactor them.
- For UI-only requests, keep business logic, persistence, Drive sync, and data migrations untouched.
- Reuse existing CSS variables and selectors.
- Preserve mobile-first layout, safe-area handling, set-row states, bottom-sheet structure, and timer overlay behavior.
- When docs or review work may turn into implementation from a clean `main`, branch before editing.
- Verify proposed docs against the live checkout with diffs and targeted file reads.
- Treat `.claude/worktrees/` as possible linked-worktree tooling until verified with `git worktree list --porcelain`.

## Sensitive Contracts

- Storage keys include `wl3_session`, `wl3_history`, `wl3_view`, `wl3_landing_seen`, `wl3_exercises`, `wl3_rotation`, and `wl3_schema_v1`.
- `restSeconds: 0` is valid. Do not replace it with a fallback through `|| 90`; use nullish handling.
- Add Exercise depends on `EX_SHEET_STATE`, `EX_SHEET_SEARCH_INDEX`, `refreshExTypeahead()`, `submitExToSession()`, and bottom-sheet classes.
- Timer overlay depends on `STATE.timer`, `renderTimerEl()`, `extendTimer()`, `resetTimer()`, `closeTimerOverlay()`, and hiding while `#ex-sheet` has `is-open`.
- Set-row UI has active, dormant, completed, and editing states. Verify all relevant states after markup or CSS edits.

## Search Anchors

```bash
rg -n "const LS_|function render|function renderTimerEl|function extendTimer|EX_SHEET_STATE|EX_SHEET_SEARCH_INDEX|function refreshExTypeahead|function submitExToSession|CACHE_NAME" app.js sw.js
rg -n -- "--set-row-cols|set-row|bottom-sheet|timer-overlay|:root|--complete|--accent|--danger|--warning" app.css
```

## Validation Gates

- Any `app.js` edit: `node --check app.js`.
- Unit-covered behavior: `npm run test:run`.
- UI or layout behavior: run `python3 -m http.server 4173`, open `http://localhost:4173/`, inspect mobile plus desktop, and when the user asks to "show" the browser, use a visible browser path rather than only reporting a background server.
- Set-row changes: verify active, dormant, completed, and editing states.
- Add Exercise changes: verify open, filtering, selecting, add-new, close, and background layout stability.
- Timer changes: verify overlay visible, hidden while sheet is open, reset, close, extend controls, and formatting.
- Service-worker or live-visibility work: check `sw.js` `CACHE_NAME`, cache injection, and `/workout/` scope assumptions.

## PR Workflow

Before staging:

```bash
git diff --stat
git diff
```

Publish implementation work through a branch and PR:

```bash
git add <relevant-files>
git commit -m "<clear message>"
git push -u origin <branch>
gh pr create --fill
```

Stage only relevant files. Leave the PR open for human review. Do not merge unless the user explicitly asks.

## Memory Routing

Search memory before deep exploration for tasks involving landing copy density, color-only regressions, app blanking after `app.js` edits, timer overlay, set-row affordances, Add Exercise sheet, `restSeconds: 0`, workout title persistence, service-worker cache visibility, Cloudflare `/workout`, Wrangler or Node24 deploy issues, GitHub auth, docs-accuracy review, visible local-browser bring-up, `.claude/worktrees`, or PR workflow.

Use memory to route investigation, then verify against current files before answering.
