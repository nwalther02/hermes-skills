---
name: local-docker-image-cleanup
description: Audits and cleans local Docker images with retention rules, archive-before-delete behavior, and project containerization checks. Use when the user asks to prune Docker images, decide which tags to keep, archive/remove old images, or confirm whether a project produces Docker artifacts.
---

# Local Docker Image Cleanup

## Quick start

Use live Docker state. Old image IDs, tags, and reclaimed-space numbers from memory are historical only.

## Workflow

1. Inspect current images, containers, and builder cache before proposing cleanup.
2. Ask or restate the retention rule before deletion, especially if the rule changed mid-run.
3. Check whether target projects actually have Docker surfaces:
   - `Dockerfile`
   - compose files
   - `.dockerignore`
   - package scripts or build docs
4. Distinguish app images, infrastructure images, extension images, and single-use scratch images.
5. Archive before removing when the user wants a reversible path.
6. Request approval before destructive removal unless the user explicitly requested that exact removal.
7. Verify the final image/container/cache state after cleanup.

## Archive Pattern

For images that must be recoverable, use `docker save` into a dated archive folder and include a short restore note with the image tag, digest or ID, and restore command.

## Reporting

Report retained images, archived images, removed images, skipped ambiguous items, and any cleanup that remains intentionally undone.
