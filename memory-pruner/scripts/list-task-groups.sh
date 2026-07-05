#!/usr/bin/env bash
set -euo pipefail

memory_file="${1:-/Users/nicksmac/.codex/memories/MEMORY.md}"

if [[ ! -f "$memory_file" ]]; then
  echo "memory file not found: $memory_file" >&2
  exit 1
fi

awk '
/^# Task Group:/ {
  if (start) {
    printf "%4d-%4d | %4d lines | %s\n", start, NR - 1, NR - start, title
  }
  start = NR
  title = $0
}
END {
  if (start) {
    printf "%4d-%4d | %4d lines | %s\n", start, NR, NR - start + 1, title
  }
}
' "$memory_file"
