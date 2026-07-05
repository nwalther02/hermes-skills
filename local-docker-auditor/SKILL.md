---
name: local-docker-auditor
description: Audits local Docker state across Docker Desktop config, runtime containers, image retention, and project containerization surfaces. Use when the user asks to validate Docker, clean Docker images, decide which tags to keep, archive/remove images, inspect Docker Desktop extension containers, or check whether a repo has Docker artifacts.
---

# Local Docker Auditor

## Quick start

Use live Docker state. Old image IDs, tags, ports, and reclaimed-space numbers from memory are historical only.

## Audit Workflow

1. Identify whether the task is validation, cleanup, or project containerization.
2. Inspect Docker client/server version, active context, running containers, images, volumes, and builder cache.
3. Inspect `~/.docker/config.json` for credential-store shape and inline auth surprises.
4. For Docker Desktop extension containers, inspect their compose files under `~/Library/Containers/com.docker.docker/Data/extensions/.../vm/`.
5. For project checks, search real repo surfaces: `Dockerfile`, compose files, `.dockerignore`, package scripts, deployment docs, and CI.
6. Treat sandboxed localhost probe failures as suspect until tested from a host-reachable context.

## Cleanup Workflow

1. Confirm or restate the retention rule before removing images.
2. Separate app images from infrastructure, extension, Playwright, devcontainer, and scratch images.
3. Archive before destructive removal when reversibility matters.
4. Request approval before destructive removal unless the user explicitly requested that exact action.
5. Verify final image/container/cache state after cleanup.

## Reporting

Separate confirmed live findings from stale memory, screenshot inference, or sandbox-limited checks. Report kept, archived, removed, skipped, and still-ambiguous items.
