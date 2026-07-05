---
name: qa-dev-docker
description: Add or plan a production-shaped Docker Dev/QA workflow for an existing app. Use when the user wants Docker configuration for local testing, QA gates, smoke testing, static app serving, compose profiles, non-root runtime containers, first-step container deployment prep, or repeatable Docker setup without immediately migrating live production.
---

# QA Dev Docker

## Purpose

Create Docker setups that make local development and QA feel like production without forcing a live deployment migration. Keep the existing app workflow intact, add a repeatable container runtime, and document the path from local smoke testing to future production promotion.

## Default Stance

- Treat Docker v1 as Dev/QA unless the user explicitly asks for a live cutover.
- Preserve the current production deployment path by default.
- Use a PR branch for code changes. Do not commit Docker work directly to `main`.
- Keep the first pass small: Dockerfile, `.dockerignore`, Compose, server/runtime config, docs, and validation.
- Prefer production-shaped runtime behavior over convenience-only dev containers.
- Do not add registries, CI publishing, DNS, TLS, reverse proxies, or VPS automation unless the user asks for that phase.

## Workflow

1. Inspect the repo.
   - Identify app type, package manager, build output, test commands, dev server, static/runtime files, and current deployment target.
   - Read existing README/deploy docs before changing assumptions.
   - Check git status and branch. Create a feature branch when implementing.

2. Classify the target.
   - Static/PWA: read `references/static-pwa.md`.
   - Node/API service: read `references/node-service.md`.
   - Other app types: adapt the core workflow and keep the Docker surface minimal.

3. Add `.dockerignore`.
   - Exclude `.git`, dependencies, local env files, logs, test artifacts, caches, editor files, and agent/tool clutter.
   - Prefer deny-by-default for static apps when the runtime should ship only a few files.
   - Ensure files needed for Docker QA are not accidentally excluded.

4. Add a multi-stage `Dockerfile`.
   - Use digest-pinned base images resolved during implementation.
   - Include a QA/build stage that runs syntax checks, tests, and build/cache-prep commands.
   - Include a runtime stage that contains only production runtime assets and dependencies.
   - Run as non-root, expose the intended container port, and include a simple healthcheck.

5. Add `compose.yml`.
   - Provide the normal app service with a configurable host port, usually `${APP_PORT:-8080}:8080`.
   - Add a `qa` profile that runs the Dockerized QA/build gate.
   - Add conservative runtime hardening when compatible: `read_only`, `tmpfs`, `cap_drop: ["ALL"]`, and `no-new-privileges`.

6. Add runtime/server config when needed.
   - Static apps usually need cache headers, security headers, SPA fallback, and explicit asset serving.
   - Leave HSTS/TLS to a reverse-proxy or TLS phase unless HTTPS is actually configured in this Docker setup.
   - Keep CSP aligned with the existing deployment. If unsure, use report-only for local/IP smoke.

7. Document the workflow.
   - Add docs with exact commands for local up/down, QA profile, runtime smoke, and expected URLs.
   - State clearly whether Docker is Dev/QA only or part of live production.
   - Include a v2 promotion path: registry publishing, reverse proxy, TLS, rollback, and deployment automation.

8. Validate.
   - Read `references/validation.md`.
   - Run host checks first, then Docker build, Compose QA, runtime curl smoke, and browser smoke when available.
   - Confirm generated build/cache files did not mutate tracked source files unexpectedly.
   - End with `git diff --check` and a clean explanation of what changed.

## Image Pinning

- Pin base images by digest in the Dockerfile. Resolve digests at implementation time with Docker tooling or registry metadata.
- Keep human-readable tags beside digests, such as `node:24-alpine@sha256:...`, so upgrades remain understandable.
- Use supported official or well-known images that match the app's runtime needs.
- Document any substitution if the requested tag or image family is unavailable.

## Guardrails

- Do not copy secrets into images.
- Do not include `.env`, Wrangler state, local credentials, private keys, screenshots, Playwright reports, or dependency directories in build context unless explicitly required.
- Do not install build tools in the final runtime image unless the app truly needs them at runtime.
- Do not expose production ports publicly or change DNS/TLS from a Docker v1 request.
- Do not rewrite the app architecture to fit Docker. The container should wrap the app, not become the app.

## User-Facing Closeout

Report:

- Branch/PR status if code was committed or opened.
- Files added or changed.
- Commands run and whether they passed.
- Local URL and Docker Desktop expectations.
- Any intentional deferrals, especially registry, TLS, DNS, CI, and live cutover.
