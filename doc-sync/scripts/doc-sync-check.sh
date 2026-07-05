#!/usr/bin/env bash
# doc-sync-check.sh — deterministic facts for the doc-sync skill.
# Reports: registry location, branch changes (code vs docs), registry docs touched /
# not-touched, always-update status, and registry drift. Read-only; never edits.
set -uo pipefail

# ---- locate repo + registry -------------------------------------------------
if ! git rev-parse --show-toplevel >/dev/null 2>&1; then
  echo "doc-sync: not inside a git repository — nothing to check."
  exit 0
fi
ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT" || exit 0

REG=""
[ -f "$ROOT/docs/DOC_REGISTRY.md" ] && REG="$ROOT/docs/DOC_REGISTRY.md"

echo "=================================================================="
echo " doc-sync check — $ROOT"
echo "=================================================================="

if [ -z "$REG" ]; then
  echo
  echo "NO REGISTRY FOUND (looked for docs/DOC_REGISTRY.md)."
  for legacy in ".codex/DOC_REGISTRY.md" ".claude/DOC_REGISTRY.md" "DOC_REGISTRY.md"; do
    [ -f "$ROOT/$legacy" ] && echo "Legacy/non-canonical registry present: $legacy — migrate it to docs/DOC_REGISTRY.md."
  done
  echo "→ Bootstrap one (see REFERENCE.md). Tracked .md files on disk:"
  git ls-files '*.md' ':!:**/node_modules/**' | sed 's/^/    /'
  exit 0
fi
echo "Registry: ${REG#$ROOT/}"
for legacy in ".codex/DOC_REGISTRY.md" ".claude/DOC_REGISTRY.md" "DOC_REGISTRY.md"; do
  [ -f "$ROOT/$legacy" ] && echo "Legacy/non-canonical registry also present: $legacy — keep one shared registry at docs/DOC_REGISTRY.md."
done

# ---- parse registry ---------------------------------------------------------
# always_update + exclude from the config comment
ALWAYS="$(grep -iE '^always_update:' "$REG" | head -1 | sed -E 's/^[^:]*:[[:space:]]*//' | tr ',' ' ')"
EXCLUDE="$(grep -iE '^exclude:' "$REG" | head -1 | sed -E 's/^[^:]*:[[:space:]]*//' | tr ',' ' ')"
# canonical doc paths = first backticked token of each table row
REG_DOCS="$(grep -E '^\|[[:space:]]*`[^`]+`' "$REG" | sed -E 's/^\|[[:space:]]*`([^`]+)`.*/\1/' | sort -u)"

echo "Branch:   $(git branch --show-current 2>/dev/null || echo '(detached)')"
echo

# ---- determine changed files (branch commits + working tree) ----------------
BASE=""
for ref in origin/main main origin/master master; do
  if git rev-parse --verify "$ref" >/dev/null 2>&1; then
    BASE="$(git merge-base "$ref" HEAD 2>/dev/null)" && [ -n "$BASE" ] && break
  fi
done
{
  [ -n "$BASE" ] && git diff --name-only "$BASE"..HEAD
  git status --porcelain | sed -E 's/^.{3}//' | sed -E 's/^.* -> //'
} 2>/dev/null | sed '/^$/d' | sort -u > /tmp/.docsync_changed.$$
CHANGED="$(cat /tmp/.docsync_changed.$$)"; rm -f /tmp/.docsync_changed.$$

if [ -z "$CHANGED" ]; then
  echo "No changes vs ${BASE:+merge-base }main and a clean working tree — nothing to sync."
  exit 0
fi

in_list() { case " $2 " in *" $1 "*) return 0;; esac; return 1; }
has_glob() { case "$1" in *"*"*|*"?"*|*"["*) return 0;; esac; return 1; }
matches_pathspec() {
  local path="$1" spec="$2"
  if has_glob "$spec"; then
    case "$path" in $spec) return 0;; esac
  else
    [ "$path" = "$spec" ] && return 0
  fi
  return 1
}
doc_touched() {
  local spec="$1" f
  for f in $DOC_TOUCHED; do
    matches_pathspec "$f" "$spec" && return 0
  done
  return 1
}
registered_doc() {
  local path="$1" spec
  while IFS= read -r spec; do
    [ -z "$spec" ] && continue
    matches_pathspec "$path" "$spec" && return 0
  done <<< "$REG_DOCS"
  return 1
}
registry_doc_exists() {
  local spec="$1" f
  if has_glob "$spec"; then
    while IFS= read -r f; do
      [ -z "$f" ] && continue
      matches_pathspec "$f" "$spec" && return 0
    done <<< "$DISK"
    return 1
  fi
  [ -f "$ROOT/$spec" ]
}

# ---- classify changes -------------------------------------------------------
echo "------------------------------------------------------------------"
echo " CHANGES ON THIS BRANCH"
echo "------------------------------------------------------------------"
CODE_CHANGED=0; DOC_TOUCHED=""
while IFS= read -r f; do
  [ -z "$f" ] && continue
  case "$f" in
    *.md) echo "  [doc ] $f"; DOC_TOUCHED="$DOC_TOUCHED $f" ;;
    *)    echo "  [code] $f"; CODE_CHANGED=1 ;;
  esac
done <<< "$CHANGED"

# ---- always-update status ---------------------------------------------------
echo
echo "------------------------------------------------------------------"
echo " ALWAYS-UPDATE DOCS (must reflect any substantive change)"
echo "------------------------------------------------------------------"
MISSING_ALWAYS=0
for d in $ALWAYS; do
  if in_list "$d" "$DOC_TOUCHED"; then echo "  ✅ $d — touched"
  else echo "  ❌ $d — NOT touched"; MISSING_ALWAYS=1; fi
done
[ -z "$ALWAYS" ] && echo "  (none declared in registry config)"

# ---- registry docs not touched ---------------------------------------------
echo
echo "------------------------------------------------------------------"
echo " REGISTRY DOCS NOT TOUCHED — decide each (update or justify skip)"
echo "------------------------------------------------------------------"
NT=0
while IFS= read -r d; do
  [ -z "$d" ] && continue
  in_list "$d" "$EXCLUDE" && continue
  if ! doc_touched "$d"; then echo "  • $d"; NT=$((NT+1)); fi
done <<< "$REG_DOCS"
[ "$NT" -eq 0 ] && echo "  (all registry docs were touched)"

# ---- drift ------------------------------------------------------------------
echo
echo "------------------------------------------------------------------"
echo " REGISTRY DRIFT"
echo "------------------------------------------------------------------"
DISK="$(git ls-files '*.md' ':!:**/node_modules/**' | sort -u)"
DRIFT=0
while IFS= read -r f; do
  [ -z "$f" ] && continue
  in_list "$f" "$EXCLUDE" && continue
  registered_doc "$f" || { echo "  + on disk, NOT in registry: $f"; DRIFT=1; }
done <<< "$DISK"
while IFS= read -r d; do
  [ -z "$d" ] && continue
  registry_doc_exists "$d" || { echo "  - in registry, MISSING on disk: $d"; DRIFT=1; }
done <<< "$REG_DOCS"
[ "$DRIFT" -eq 0 ] && echo "  (registry matches disk)"

# ---- summary ----------------------------------------------------------------
echo
echo "=================================================================="
if [ "$CODE_CHANGED" -eq 1 ] && [ "$MISSING_ALWAYS" -eq 1 ]; then
  echo " ⚠️  Code changed but an always-update doc is untouched — sync before close."
fi
echo " Next: address each doc above, then finalize the doc-sync run report (SKILL.md)."
echo "=================================================================="
exit 0
