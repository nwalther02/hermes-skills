---
name: "claude-code-bridge"
description: "Use when Claude Code needs to receive work from Codex, return artifacts to Codex, or create a packet-based handoff that Codex can read without copying long chat transcripts."
type: "skill"
parameters:
  - name: packet
    description: Optional /tmp/claude-code-bridge packet path to read or update.
    required: false
  - name: task
    description: Optional handoff, review, validation, or artifact-sharing task.
    required: false
---

# Claude Code Bridge

Use a shared packet directory as the communication contract with Codex. Prefer paths, manifests, and packet-local artifacts over pasting long file contents.

## Packet Shape

Bridge packets live under `/tmp/claude-code-bridge/<timestamp>-<slug>/` and usually contain:

- `PROMPT.md`: task and context from Codex.
- `MANIFEST.json`: cwd, git state, included paths, allowed directories, and command metadata.
- `reply.md`: your response for Codex.
- Additional artifact files that you create for Codex to inspect.

## Receiving From Codex

1. If given a packet path, read `PROMPT.md` and `MANIFEST.json` first.
2. Treat included file paths as source of truth; read only what the task needs.
3. Do not edit source files unless the prompt explicitly asks for edits.
4. Write any new handoff files inside the packet directory.
5. End with packet-local artifact paths Codex should read next.

## Returning To Codex

Write `reply.md` in the packet when possible, using:

- `Summary`: one paragraph.
- `Findings`: prioritized issues with file/line evidence when reviewing code.
- `Recommended next step`: one decisive action.
- `Artifacts`: absolute paths for packet-local files you created.
- `Questions`: only blockers that prevent progress.

## Starting A Handoff To Codex

If you need to initiate a handoff, create a new directory under `/tmp/claude-code-bridge/`, write `PROMPT.md`, `MANIFEST.json`, and `reply.md`, then give Codex the packet path. Keep payloads compact and reference readable files by path.

## Safety

- Never put secrets, tokens, private keys, or credential files in packets.
- Keep unrelated dirty work out of handoffs.
- For repo work, respect the branch/PR workflow and call out if the current branch is `main`.
- Do not claim Codex applied or verified anything; provide artifacts and evidence for Codex to inspect.
