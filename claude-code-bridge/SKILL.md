---
name: claude-code-bridge
description: Coordinate low-friction handoffs between Codex and Claude Code through shared packet files and the local Claude CLI. Use when the user wants Codex to connect to Claude Code, ask Claude for review or validation, share files/data with Claude, or pass work between Codex and Claude.
---

# Claude Code Bridge

Use a file packet as the contract between agents. Prefer paths and compact manifests over pasting large file bodies.

## Quick Start

Check Claude readiness:

```bash
python3 ~/.agents/skills/claude-code-bridge/scripts/claude_bridge.py status
python3 ~/.agents/skills/claude-code-bridge/scripts/claude_bridge.py smoke
```

In Codex sandboxed runs, Claude auth/keychain access may be hidden from child processes. If `status` reports `loggedIn: false` but a direct `claude auth status` is logged in, rerun the helper with sandbox escalation before invoking Claude. Treat `smoke` as the authoritative check for whether Claude can actually answer.

Ask Claude from the current repo in read-only planning mode:

```bash
python3 ~/.agents/skills/claude-code-bridge/scripts/claude_bridge.py send \
  --task "Review this plan and return risks, missing gates, and a recommended next step." \
  --include docs/plan.md
```

Create a packet without running Claude:

```bash
python3 ~/.agents/skills/claude-code-bridge/scripts/claude_bridge.py send \
  --task "Pick up this implementation handoff." \
  --include HANDOFF.md \
  --no-run
```

Read a returned packet:

```bash
python3 ~/.agents/skills/claude-code-bridge/scripts/claude_bridge.py show /tmp/claude-code-bridge/<packet>
```

## Protocol

Each bridge exchange lives under `/tmp/claude-code-bridge/<timestamp>-<slug>/`:

- `PROMPT.md`: the actual task, context, file list, and return contract.
- `MANIFEST.json`: machine-readable cwd, git state, included paths, command, and timestamps.
- `reply.md`: Claude's human-readable response when available.
- `claude-stdout.*` and `claude-stderr.txt`: raw execution evidence.

Default to `--permission-mode plan`. Use write-capable Claude modes only when the user explicitly asks Claude to edit files.

## Workflow

1. Resolve the shared workspace.
   - Run from the repo or project directory when possible.
   - Include only the paths Claude needs with repeated `--include`.
   - Add extra readable roots with `--add-dir` only when files live outside the cwd.
2. Run `status` if this session has not recently checked Claude auth; escalate the helper if sandboxing hides Claude auth.
3. Run `smoke` before the first real Claude request when reliability matters.
4. Run `send` with a narrow task and included paths.
5. Inspect `reply.md`, raw stdout/stderr, and any files Claude wrote into the packet.
6. Import Claude's suggestions intentionally. Do not treat Claude output as applied work unless the files were actually changed and verified.

## Return Contract For Claude

Ask Claude to return:

- `Summary`: one paragraph.
- `Findings`: prioritized issues with file/line evidence when reviewing code.
- `Recommended next step`: one decisive action.
- `Artifacts`: any packet-local files it created.
- `Questions`: only blockers that prevent progress.

## Claude To Codex

When Claude needs to hand work back, it should create the same packet shape under `/tmp/claude-code-bridge/`, write a `reply.md` or artifact files there, and give Codex the packet path. Codex should run `show <packet>` before acting.

## Safety Rules

- Do not pass secrets, tokens, private keys, or credential files through a bridge packet.
- Do not use `--dangerously-skip-permissions` for bridge work.
- Keep repo edits on feature branches and preserve unrelated dirty changes.
- If Claude auth or smoke generation fails, report the output and ask the user to restore Claude login before retrying.
