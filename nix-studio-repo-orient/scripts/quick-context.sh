#!/usr/bin/env bash
set -euo pipefail

repo="${1:-/Users/nicksmac/Code/Projects/nix-studio}"

if [[ ! -d "$repo/.git" ]]; then
  echo "Not a git repo: $repo" >&2
  exit 1
fi

cd "$repo"

echo "== repo =="
pwd

echo
echo "== git =="
git status --short --branch
printf 'branch: '
git branch --show-current
printf 'head: '
git log -1 --oneline

echo
echo "== package scripts =="
sed -n '/"scripts": {/,/  }/p' package.json

echo
echo "== dispatch docs =="
for file in AGENT_START_HERE.md CURRENT_STATE.md WORKLOG.md CLAUDE.md docs/DOC_REGISTRY.md; do
  if [[ -f "$file" ]]; then
    printf '%s: present (%s lines)\n' "$file" "$(wc -l < "$file" | tr -d ' ')"
  else
    printf '%s: missing\n' "$file"
  fi
done

echo
echo "== current state excerpt =="
if [[ -f CURRENT_STATE.md ]]; then
  sed -n '1,90p' CURRENT_STATE.md
fi

echo
echo "== recent worklog =="
if [[ -f WORKLOG.md ]]; then
  sed -n '1,80p' WORKLOG.md
fi

echo
echo "== top-level files =="
rg --files -g '!*node_modules*' -g '!*.png' -g '!pnpm-lock.yaml' | sed -n '1,120p'
