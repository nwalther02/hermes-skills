# fitness-pwa Validation Gates

Pick evidence that matches the risk. Do not substitute a syntax check for a visual behavior change.

## Fast Gates

- Any `app.js` edit:
  ```bash
  node --check app.js
  ```
- Unit-covered behavior:
  ```bash
  npm run test:run
  ```
- Search for accidental broad color or token drift:
  ```bash
  rg -n "#[0-9A-Fa-f]{3,8}|rgb\\(|hsl\\(|oklch\\(|--complete|--accent|--danger|--warning" app.css
  ```
- Service worker visibility:
  ```bash
  rg -n "CACHE_NAME|CACHE_PREFIX|APP_SCOPE_PATH|BYPASS" sw.js scripts cloudflare .github
  ```

## Browser Gates

Use a static server for local checks:

```bash
python3 -m http.server 4173
```

Then inspect `http://localhost:4173/`.

For UI changes, verify the relevant mobile viewport first, then desktop:

- landing/auth gate when touching first-run copy or Drive sign-in.
- picker, session, history, and preview views when navigation or rendering changes.
- active, dormant, completed, and editing set rows when workout rows change.
- Add Exercise sheet open, filtering, selecting, add-new, close, and background layout stability.
- timer overlay visible, hidden while sheet is open, reset/close/extend controls, and background formatting.

## PR Gates

Before staging:

```bash
git diff --stat
git diff
```

Before commit:

```bash
git status --short --branch
```

Publish flow:

```bash
git add <relevant-files>
git commit -m "<clear message>"
git push -u origin <branch>
gh pr create --fill
```

Leave the PR open for human review. Do not merge unless the user explicitly asks.

## Known Failure Modes

- `node --check app.js` catches parse errors that otherwise blank the app.
- CSS-only work can still make behavior look broken if layout hides or overlaps controls.
- Live deployment not showing changes can be a service-worker/cache-name issue.
- `gh auth status` may be misleading; retry the actual PR command once before declaring GitHub unavailable.
- `.git/index.lock` errors in sandboxed contexts may require escalated permissions rather than manual lock deletion.
