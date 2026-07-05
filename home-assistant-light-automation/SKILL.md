---
name: home-assistant-light-automation
description: Drafts paste-ready Home Assistant lighting YAML that separates scheduled default colors from motion behavior so manual color changes persist. Use when the user asks for Home Assistant light automations, motion sensors, red/warm schedules, room lighting YAML, or manual color override preservation.
---

# Home Assistant Light Automation

## Quick start

Return copy/paste-ready YAML when the user asks for Home Assistant automations. Confirm or clearly placeholder entity IDs, motion sensors, brightness, and off behavior.

## Pattern

Use separate concerns:

1. Scheduled defaults set color, brightness, color temperature, and transition.
2. Motion-on turns lights on without color data so manual color changes persist.
3. Motion-off remains separate so lights do not stay on indefinitely.

## Drafting Workflow

1. Identify rooms, light entities, motion entities, times, colors, brightness, and transitions.
2. Use `choose` for time-triggered schedule branches when one automation owns multiple defaults.
3. Keep motion-on `data` empty unless the user explicitly wants motion to override color.
4. Include comments or placeholders only where entity IDs or room-specific values are unknown.
5. Mention any assumptions after the YAML, not in place of it.

## Review Checklist

- YAML is paste-ready.
- Motion does not fight manual color changes.
- Off behavior is explicit.
- Brightness and transition choices are stated.
- Entity IDs needing user replacement are obvious.
