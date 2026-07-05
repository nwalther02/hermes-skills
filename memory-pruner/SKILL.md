---
name: memory-pruner
description: Ranks and conservatively compacts Codex memory files while preserving provenance and rollout archives. Use when the user asks to prune memories, reduce memory token load, rank memory importance, compact MEMORY.md, or create ad-hoc memory update notes.
---

# Memory Pruner

## Quick start

Use this for memory cleanup, not ordinary repo cleanup. The safe default is to shrink hot registry surfaces while preserving cold evidence.

## Workflow

1. Read the current memory instructions and the relevant `MEMORY.md` sections.
2. List task groups and sizes before judging importance.
3. Rank memories by:
   - active project gravity;
   - durable user preference value;
   - safety or data-loss relevance;
   - uniqueness versus existing skills or summaries;
   - drift risk.
4. Compact only low-risk or duplicated sections.
5. Preserve rollout summaries, Chronicle resources, and raw evidence unless the user explicitly asks for storage cleanup.
6. Stop and ask before deleting or collapsing ambiguous project memories.
7. Write requested changes through `extensions/ad_hoc/notes/*.md`; do not directly edit canonical memory files unless the memory system explicitly allows it.

## Helper

To list task groups and line counts:

```bash
bash ~/.claude/skills/memory-pruner/scripts/list-task-groups.sh /Users/nicksmac/.codex/memories/MEMORY.md
```

## Prune Note Shape

Include:

- ranking criteria;
- keep-verbose sections;
- compact-later sections;
- exact replacement text for safe compactions;
- explicit do-not-prune boundaries;
- expected effect.

## Guardrails

- Do not confuse registry compaction with evidence deletion.
- Do not present memory-derived facts as current when live verification is cheap.
- Preserve behavior-changing qualifiers like "when explicitly asked".
