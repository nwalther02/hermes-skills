#!/usr/bin/env bash
set -euo pipefail

remote="${1:-origin}"
branch="${2:-main}"
remote_ref="$remote/$branch"

section() {
  printf '\n## %s\n' "$1"
}

if ! git rev-parse --show-toplevel >/dev/null 2>&1; then
  echo "Not inside a Git repository."
  exit 1
fi

repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"

if ! git remote get-url "$remote" >/dev/null 2>&1; then
  echo "Remote not found: $remote"
  exit 1
fi

section "Fetch"
git fetch "$remote" --prune

if ! git rev-parse --verify --quiet "$remote_ref" >/dev/null; then
  echo "Remote branch not found: $remote_ref"
  exit 1
fi

current_branch="$(git branch --show-current 2>/dev/null || true)"

section "Sync local $branch"
if git show-ref --verify --quiet "refs/heads/$branch"; then
  if [[ "$current_branch" == "$branch" ]]; then
    if [[ -n "$(git status --porcelain)" ]]; then
      echo "Current branch '$branch' has local changes. Create/switch to a feature branch first, then rerun."
      exit 2
    fi
    git merge --ff-only "$remote_ref"
  else
    git fetch "$remote" "$branch:$branch"
  fi
else
  git branch --track "$branch" "$remote_ref"
fi

local_sha="$(git rev-parse "$branch")"
remote_sha="$(git rev-parse "$remote_ref")"

if [[ "$local_sha" != "$remote_sha" ]]; then
  echo "Local $branch is not equal to $remote_ref after sync."
  echo "local:  $local_sha"
  echo "remote: $remote_sha"
  exit 3
fi

echo "Local $branch is up to date with $remote_ref at $local_sha"
