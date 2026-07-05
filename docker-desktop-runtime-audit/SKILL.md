---
name: docker-desktop-runtime-audit
description: Validates Docker Desktop runtime and config on this Mac from live daemon, context, containers, and extension compose files. Use when the user asks to validate Docker config, explain Docker Desktop extension containers, inspect local ports, or compare screenshot claims to live Docker state.
---

# Docker Desktop Runtime Audit

## Quick start

Keep the audit read-only unless the user asks for changes. Prefer live daemon and container evidence over inference from screenshots or repo searches.

## Workflow

1. Check Docker client/server versions and the active context.
2. Inspect `~/.docker/config.json` for credential-store shape and inline auth surprises.
3. List running containers and published ports.
4. Inspect relevant containers for mounts, commands, privileges, and network settings.
5. Locate Docker Desktop extension compose files under `~/Library/Containers/com.docker.docker/Data/extensions/.../vm/` when extension containers are involved.
6. Run compose config validation on active compose files when available.
7. Probe local ports only from a context that can reach the host; sandboxed probes can be false negatives.

## What To Call Out

- Privileged containers or host networking.
- Docker socket mounts.
- Ports bound beyond loopback.
- Extension containers whose risk is expected for their function.
- Any gap between repo-local Docker files and Docker Desktop runtime state.

## Reporting

Separate confirmed live findings from stale memory, screenshot inference, or sandbox-limited checks.
