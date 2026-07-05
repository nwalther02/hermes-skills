#!/usr/bin/env bash
set -u

section() {
  printf '\n## %s\n' "$1"
}

if ! git rev-parse --show-toplevel >/dev/null 2>&1; then
  echo "Not inside a Git repository."
  exit 1
fi

repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root" || exit 1

section "Repo"
printf 'root: %s\n' "$repo_root"
printf 'branch: %s\n' "$(git branch --show-current 2>/dev/null || printf '(detached)')"
git remote -v 2>/dev/null | sed 's/^/remote: /' || true

section "Status"
git status --short --branch

section "Changed Files"
git diff --name-status --find-renames || true
git diff --cached --name-status --find-renames || true
git ls-files --others --exclude-standard | sed 's/^/??\t/' || true

section "Diff Stat"
git diff --stat || true
git diff --cached --stat || true

section "Branch Tracking"
git branch -vv --no-color 2>/dev/null | sed -n '1,40p' || true

if command -v gh >/dev/null 2>&1; then
  section "GitHub PR"
  gh pr status 2>/dev/null || true
  if gh pr view --json number,title,url,state,isDraft,headRefName,baseRefName,mergeStateStatus,reviewDecision,statusCheckRollup >/tmp/github-pr-shipper-pr.json 2>/tmp/github-pr-shipper-pr.err; then
    cat /tmp/github-pr-shipper-pr.json
    printf '\n'
  elif gh pr view --json number,title,url,state,isDraft,headRefName,baseRefName >/tmp/github-pr-shipper-pr.json 2>/tmp/github-pr-shipper-pr.err; then
    cat /tmp/github-pr-shipper-pr.json
    printf '\n'
  else
    sed 's/^/gh pr view: /' /tmp/github-pr-shipper-pr.err || true
  fi
  rm -f /tmp/github-pr-shipper-pr.json /tmp/github-pr-shipper-pr.err
else
  section "GitHub PR"
  echo "gh not found on PATH."
fi
