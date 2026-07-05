---
name: "fitness-pwa-repo-orient"
description: "Orient an agent quickly in Nick Walther's fitness-pwa repository: app shape, canonical files, storage contracts, UI patterns, service-worker behavior, validation gates, and workflow traps. Use when starting any coding, review, audit, debugging, UI, JavaScript, CSS, service-worker, deployment, or PR task in /Users/nicksmac/Code/Projects/fitness-pwa."
---

# Fitness PWA Repo Orient

## Purpose

Use this skill to reduce rediscovery work in `fitness-pwa`. It should make the first five minutes of a task boring: confirm the repo state, identify the right files, preserve existing architecture, and choose the smallest useful validation gate.

## First Pass

Run or inspect these before editing:

```bash
pwd
git status --short --branch
git branch --show-current
rg --files
```

If the task is implementation work and the current branch is `main`, create a feature branch before edits. If the branch is already task-specific, reuse it only when the scope matches.

## Repo Shape

This is a lightweight, local-first workout logging PWA:

- Vanilla JavaScript, HTML, and CSS.
- No framework, bundler, transpiler, or TypeScript.
- `app.js` owns most state, rendering, Drive sync, exercise registry, timer behavior, and UI handlers.
- `app.css` owns the design token contract, layout, workout rows, sheets, and motion.
- `index.html` is the app shell and contains some inline handlers.
- `sw.js` is network-first and bypasses auth plus Google Drive API traffic.

For the fuller file map, read `references/repo-map.md`.

## Guardrails

- Preserve the direct vanilla-JS architecture. Do not introduce a framework or broad abstraction.
- Preserve storage keys and data shapes unless the user explicitly asks for a migration.
- Keep inline MVI-style handlers and existing helper patterns unless the task is specifically to refactor them.
- For UI-only requests, keep business logic, persistence, Drive sync, and data migrations untouched.
- Reuse existing CSS variables and selectors. Avoid hard-coded colors when a token exists.
- Preserve mobile-first layout, safe-area handling, set-row states, bottom-sheet structure, and timer overlay behavior.
- Do not clean up unrelated code while touching nearby code.
- When a docs/review task may turn into implementation from a clean `main`, branch before editing.
- When reviewing proposed docs, verify claims against the live checkout with diffs and targeted file reads.
- Treat `.claude/worktrees/` as possible linked-worktree tooling, not app source, until verified with `git worktree list --porcelain`.

## Task Routing

- `app.js` behavior: inspect the surrounding function and related storage/render call sites before editing.
- `app.css` UI: inspect token definitions and the relevant component state selectors before editing.
- Set rows: verify active, dormant, completed, and editing states.
- Add Exercise sheet: preserve `EX_SHEET_STATE`, `EX_SHEET_SEARCH_INDEX`, `refreshExTypeahead()`, `submitExToSession()`, and bottom-sheet class contracts.
- Timer overlay: check `STATE.timer`, `renderTimerEl()`, `extendTimer()`, `closeTimerOverlay()`, `resetTimer()`, and `#ex-sheet.is-open`.
- Service worker/live visibility: check `sw.js` `CACHE_NAME`, generated deployment cache injection, and `/workout/` scope assumptions.
- Deployment/Cloudflare: inspect `wrangler.toml`, `wrangler.jsonc`, `cloudflare/`, `_headers`, and `docs/deployment/`.

## Validation

Choose the smallest gate that proves the change:

- After editing `app.js`: `node --check app.js`.
- For unit-covered behavior: `npm test -- --run` or `npm run test:run`.
- For UI/layout behavior: run a local static server and inspect mobile plus desktop render; when the user asks to "show" the browser, use a visible browser path rather than only reporting a background server.
- For workflow PR tasks: inspect diff, stage only relevant files, commit, push, create PR, and do not merge.

For detailed gates, read `references/validation-gates.md`.

## Memory Routing

If the task resembles prior work, search memory before deep repo exploration. Useful triggers include landing copy density, color-only regressions, timer overlay, set-row affordances, Add Exercise sheet, service-worker cache visibility, Cloudflare `/workout`, and PR publish blockers.

For exact keywords, read `references/memory-keywords.md`.
