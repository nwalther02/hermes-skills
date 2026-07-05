#!/usr/bin/env bash
# stop-reminder.sh — Stop hook. Non-blocking backstop that nudges (once per session) when
# a branch has code changes but an always-update doc is untouched. Never blocks, never edits.
# Reads hook JSON on stdin; emits {"systemMessage": ...} only when warranted.
set -uo pipefail

INPUT="$(cat 2>/dev/null || true)"
read_json() { printf '%s' "$INPUT" | sed -n "s/.*\"$1\"[[:space:]]*:[[:space:]]*\"\([^\"]*\)\".*/\1/p" | head -1; }
SID="$(read_json session_id)"; [ -z "$SID" ] && SID="nosession"
CWD="$(read_json cwd)"; [ -n "$CWD" ] && cd "$CWD" 2>/dev/null || true

remind() { printf '{"suppressOutput": true, "systemMessage": %s}\n' "$1"; exit 0; }
quiet()  { exit 0; }

git rev-parse --show-toplevel >/dev/null 2>&1 || quiet
ROOT="$(git rev-parse --show-toplevel)"; cd "$ROOT" || quiet

REG=""
[ -f "$ROOT/docs/DOC_REGISTRY.md" ] && REG="$ROOT/docs/DOC_REGISTRY.md"
[ -z "$REG" ] && quiet   # not a doc-sync project — never nag

ALWAYS="$(grep -iE '^always_update:' "$REG" | head -1 | sed -E 's/^[^:]*:[[:space:]]*//' | tr ',' ' ')"
[ -z "$ALWAYS" ] && quiet

MARKER="${TMPDIR:-/tmp}/doc-sync-reminded-${SID}"

BASE=""
for ref in origin/main main origin/master master; do
  if git rev-parse --verify "$ref" >/dev/null 2>&1; then
    BASE="$(git merge-base "$ref" HEAD 2>/dev/null)" && [ -n "$BASE" ] && break
  fi
done
CHANGED="$({ [ -n "$BASE" ] && git diff --name-only "$BASE"..HEAD; \
  git status --porcelain | sed -E 's/^.{3}//' | sed -E 's/^.* -> //'; } 2>/dev/null | sed '/^$/d' | sort -u)"

# In sync (no changes) → clear marker so a later divergence can re-remind.
[ -z "$CHANGED" ] && { rm -f "$MARKER" 2>/dev/null; quiet; }

in_list() { case " $2 " in *" $1 "*) return 0;; esac; return 1; }
CODE=0; TOUCHED=""
while IFS= read -r f; do
  [ -z "$f" ] && continue
  case "$f" in *.md) TOUCHED="$TOUCHED $f" ;; *) CODE=1 ;; esac
done <<< "$CHANGED"

MISSING=0
for d in $ALWAYS; do in_list "$d" "$TOUCHED" || MISSING=1; done

# Satisfied (always-update docs touched, or no code change) → re-arm + stay quiet.
if [ "$CODE" -eq 0 ] || [ "$MISSING" -eq 0 ]; then rm -f "$MARKER" 2>/dev/null; quiet; fi

# Warranted, but only remind once per session.
[ -f "$MARKER" ] && quiet
: > "$MARKER" 2>/dev/null || true
remind '"doc-sync: this branch has code changes but the always-update docs (CURRENT_STATE.md / WORKLOG.md) are untouched. Run doc-sync before bringing this to close."'
