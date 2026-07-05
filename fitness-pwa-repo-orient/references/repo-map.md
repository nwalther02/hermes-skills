# fitness-pwa Repo Map

Use this as an orientation map, not as a replacement for reading live code.

## Canonical Files

- `CONTEXT.md`: project identity and working style.
- `docs/architecture.md`: plain architecture summary.
- `index.html`: app shell, root buttons, bottom-sheet container, script/style wiring.
- `app.js`: primary app state, rendering, program data, session flow, Drive sync, localStorage, timer, exercise sheet, history, export helpers.
- `app.css`: token system, layout, workout cards, set rows, sheets, motion, responsive behavior.
- `sw.js`: service worker. Network-first, small precache, auth/Drive bypasses, cache cleanup by Iron Logic prefix.
- `manifest.json`: PWA metadata.
- `fitness-checks.md`: repo-specific validation notes and manual/browser checks.
- `.github/copilot-instructions.md`: tracked agent workflow and code rules.
- `.github/instructions/*.md`: targeted Copilot instructions for vanilla JS, CSS/UI, set rows, and git workflow.
- `docs/design/iron-logic-design-guardrails.json`: design guardrail artifact.
- `docs/plans/*.md`: scoped implementation plans that may be stale; verify against current code.
- `cloudflare/`, `wrangler.toml`, `wrangler.jsonc`, `_headers`: Cloudflare and deployment surface.

## Runtime Shape

- The app is intentionally simple: no framework, no build step, no TypeScript.
- State is held in `STATE` and persisted through localStorage keys such as `wl3_session`, `wl3_history`, `wl3_view`, `wl3_landing_seen`, `wl3_exercises`, `wl3_rotation`, and `wl3_schema_v1`.
- Drive sync exists, but localStorage writes are the local-first source of truth for current draft persistence.
- `render()` owns high-level screen rendering and session-active body state.
- Many UI actions use inline `onclick`/event handlers in generated HTML strings. Preserve that pattern unless the task explicitly asks for a refactor.

## Sensitive Contracts

- Exercise objects use fields such as `id`, `exerciseId`, `exerciseNameSnapshot`, `equipment`, `matchStatus`, `suggestion`, `virtualWeight`, `wasReanchored`, `name`, `targetSets`, `targetRepRange`, `notes`, `restSeconds`, `selectedRestDuration`, and `sets`.
- `restSeconds: 0` is valid and must not be overwritten by `|| 90`; use nullish handling when defaults are needed.
- Add Exercise depends on `EX_SHEET_STATE`, `EX_SHEET_SEARCH_INDEX`, `refreshExTypeahead()`, `submitExToSession()`, `exSheetBody()`, and bottom-sheet classes.
- Timer overlay depends on `STATE.timer`, `renderTimerEl()`, `extendTimer()`, `resetTimer()`, `closeTimerOverlay()`, and hiding while `#ex-sheet` has `is-open`.
- Set-row UI has active, dormant, completed, and editing states. Do not validate only one state after markup or CSS edits.

## Quick Search Anchors

```bash
rg -n "const LS_|function render|function renderTimerEl|function extendTimer|EX_SHEET_STATE|EX_SHEET_SEARCH_INDEX|function refreshExTypeahead|function submitExToSession|CACHE_NAME" app.js sw.js
rg -n "--set-row-cols|set-row|bottom-sheet|timer-overlay|:root|--complete|--accent|safe-area" app.css
```
