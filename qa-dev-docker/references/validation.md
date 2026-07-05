# Validation Checklist

Use the repo's native checks first, then prove the Docker path.

## Host Baseline

Run the commands the repo already trusts, for example:

```bash
npm run test
npm run test:run
npm run build
npm run lint
npm run typecheck
```

Also run syntax checks for important runtime files when useful:

```bash
node --check app.js
node --check server.js
node --check sw.js
```

## Docker Gates

Run target builds explicitly:

```bash
docker build --target qa -t app:qa .
docker build --target runtime -t app:local .
docker compose --profile qa run --rm qa
docker compose up --build -d app
docker compose ps
```

Use the actual service name and image names from the repo.

## Runtime Smoke

Probe the published host port:

```bash
curl -I http://127.0.0.1:8080/
curl -I http://127.0.0.1:8080/app.js
curl -I http://127.0.0.1:8080/sw.js
curl -I http://127.0.0.1:8080/manifest.json
```

For APIs, use `/health`, `/api/health`, or the repo's documented readiness endpoint.

Check:

- HTTP status is expected.
- Cache headers match app shell versus immutable assets.
- Security headers are present where intended.
- Healthcheck reaches healthy state.
- Container logs are clean.

## Browser Smoke

Open the local URL and test the app's main workflow. For frontends, include a mobile viewport when the app is mobile-first or responsive.

For PWAs, verify:

- App shell loads.
- Main interaction works.
- Service worker file is served with no-cache.
- Manifest loads.
- No obvious console/runtime errors.

## Final Checks

Run:

```bash
git diff --check
git status --short
```

Confirm build-time scripts did not mutate tracked runtime files unless that mutation is intentional and committed.

Stop the local stack if it was only needed for validation:

```bash
docker compose down
```
