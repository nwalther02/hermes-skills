---
name: project-context-bootstrap
description: Verify or install a repo's vendor-neutral AI context scaffold before project work. Use when starting, onboarding, or resuming a coding project; when a user asks to check, install, repair, or upgrade AI context docs; or when a repo lacks clear AGENTS.md/PROJECT_CONTEXT.md loading guidance.
---

# Project Context Bootstrap

Use this skill to make repo context cheap and systematic before non-trivial work.
The source of truth is the central template package; this skill is only a wrapper.

## Workflow

1. Run status first:

```bash
python scripts/bootstrap_ai_context.py --target /path/to/repo
```

2. Read the result:
   - If both `AGENTS.md` and `PROJECT_CONTEXT.md` exist, read `AGENTS.md` first, then `PROJECT_CONTEXT.md`.
   - If one exists, read the existing file and report the missing required counterpart.
   - If neither exists, report that AI context is not installed.

3. Use write flags only when explicitly requested:

```bash
python scripts/bootstrap_ai_context.py --target /path/to/repo --install
python scripts/bootstrap_ai_context.py --target /path/to/repo --repair
python scripts/bootstrap_ai_context.py --target /path/to/repo --fix-generated
python scripts/bootstrap_ai_context.py --target /path/to/repo --upgrade-report
```

## Template Path

Resolve the central template in this order:

1. `--template`
2. `AI_CONTEXT_TEMPLATE`
3. `~/.codex/project-context-bootstrap.json`
4. `$HOME/Code/Projects/ai-context-template`

Set a persistent path with:

```bash
python scripts/bootstrap_ai_context.py --set-template /absolute/path/to/ai-context-template
```

The config file schema is:

```json
{ "schema_version": 1, "template_path": "/absolute/path" }
```

## Safety Rules

- Do not write by default.
- Do not generate project prose.
- Do not duplicate central template policy in the skill.
- Treat central status JSON as the machine contract. It must have `status_schema_version == 1`.
- If central status output is unknown, invalid JSON, or missing the schema version, fail closed and show stdout/stderr.
- Never claim the skill enforces future agent behavior. It prepares context and prompts loading.

## Script

Use `scripts/bootstrap_ai_context.py`. It validates the central template path, calls
the central `install.py`, summarizes status, and passes write requests through to
the central installer.
