#!/usr/bin/env bash
# doc-sync-report.sh — write one reviewable report for a doc-sync pass.
# Read-only for the repo; writes the report outside the repo unless an output path is supplied.
set -euo pipefail

if ! git rev-parse --show-toplevel >/dev/null 2>&1; then
  echo "doc-sync-report: not inside a git repository" >&2
  exit 1
fi

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

BASE=""
BASE_LABEL=""
for ref in origin/main main origin/master master; do
  if git rev-parse --verify "$ref" >/dev/null 2>&1; then
    BASE="$(git merge-base "$ref" HEAD 2>/dev/null || true)"
    if [ -n "$BASE" ]; then
      BASE_LABEL="$ref"
      break
    fi
  fi
done

STAMP="$(date -u +"%Y-%m-%dT%H-%M-%SZ")"
BRANCH="$(git branch --show-current 2>/dev/null || echo detached)"
SAFE_BRANCH="$(printf '%s' "$BRANCH" | tr '/: ' '---')"
REPO_NAME="$(basename "$ROOT")"
OUT="${1:-}"
if [ -z "$OUT" ]; then
  OUT_DIR="${DOC_SYNC_REPORT_DIR:-${TMPDIR:-/tmp}/doc-sync-reports}"
  mkdir -p "$OUT_DIR"
  OUT="$OUT_DIR/${REPO_NAME}-${SAFE_BRANCH}-${STAMP}.md"
else
  mkdir -p "$(dirname "$OUT")"
fi

CHANGED_FILE="${TMPDIR:-/tmp}/doc-sync-report-changed.$$"
{
  [ -n "$BASE" ] && git diff --name-only "$BASE"..HEAD
  git status --porcelain | sed -E 's/^.{3}//' | sed -E 's/^.* -> //'
} 2>/dev/null | sed '/^$/d' | sort -u > "$CHANGED_FILE"

write_cmd_block() {
  local title="$1"
  shift
  echo "### $title"
  echo
  echo '```text'
  "$@" || true
  echo '```'
  echo
}

{
  echo "# doc-sync report"
  echo
  echo "- Repo: \`$ROOT\`"
  echo "- Branch: \`$BRANCH\`"
  echo "- Head: \`$(git rev-parse --short HEAD)\`"
  echo "- Base: \`${BASE_LABEL:-none}\`${BASE:+ (\`$(git rev-parse --short "$BASE")\`)}"
  echo "- Generated: \`$STAMP\`"
  echo

  echo "## Affected files"
  echo
  if [ ! -s "$CHANGED_FILE" ]; then
    echo "(No changed files.)"
  else
    while IFS= read -r f; do
      case "$f" in
        *.md) echo "- \`$f\` — doc" ;;
        *) echo "- \`$f\` — code/config" ;;
      esac
    done < "$CHANGED_FILE"
  fi
  echo

  echo "## Change summary"
  echo
  echo "- Fill this section with the human-readable summary of what changed."
  echo

  echo "## Diff stat"
  echo
  if [ -n "$BASE" ]; then
    write_cmd_block "Committed branch diff vs $BASE_LABEL" git diff --stat "$BASE"..HEAD
  fi
  write_cmd_block "Staged diff" git diff --stat --cached
  write_cmd_block "Unstaged diff" git diff --stat

  echo "## Full diff"
  echo
  if [ -n "$BASE" ]; then
    write_cmd_block "Committed branch diff vs $BASE_LABEL" git diff "$BASE"..HEAD
  fi
  write_cmd_block "Staged diff" git diff --cached
  write_cmd_block "Unstaged diff" git diff

  echo "## doc-sync check"
  echo
  echo '```text'
  bash "$(dirname "$0")/doc-sync-check.sh" || true
  echo '```'
  echo

  echo "## Accounting table"
  echo
  echo "| Doc | Verdict | Detail |"
  echo "|-----|---------|--------|"
  echo "| TODO | TODO | Fill this with one row per canonical doc before finalizing. |"
} > "$OUT"

rm -f "$CHANGED_FILE"
printf '%s\n' "$OUT"
