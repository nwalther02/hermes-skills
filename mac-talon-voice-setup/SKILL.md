---
name: mac-talon-voice-setup
description: Builds Talon-based Mac voice-control setup guidance and starter files grounded in local community command names. Use when the user asks to add voice control to Mac, install/configure Talon, create Talon commands, or inspect Codex/LM Studio machine-control state.
---

# Mac Talon Voice Setup

## Quick start

Use this for Talon-centered Mac voice control. Treat older Chronicle, Codex, LM Studio, or device snapshots as routing clues only; re-check live state before making dependent claims.

## Workflow

1. Check whether Talon is installed and whether `~/.talon/user` exists.
2. Inspect local Talon/community files before naming commands or actions.
3. Prefer `talonhub/community` conventions when building starter commands.
4. Create setup notes and starter files only after the current local layout is known.
5. For custom commands that launch local apps or scripts, use a whitelist and `subprocess.Popen([...])`.
6. Avoid arbitrary shell strings in example voice commands.
7. Clearly mark any installer/network step that was not verified.

## Machine-State Checks

When the task touches Codex, LM Studio, Chronicle, remote-control settings, or connected devices, verify current app or filesystem state before reporting it as current.

## Handoff

Return the installed paths, commands added, unverified setup steps, and a small smoke-test checklist for the user.
