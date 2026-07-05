#!/usr/bin/env python3
"""Summarize PR changes and likely documentation surfaces with small output."""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path


COMMON_TERMS = {
    "about", "after", "again", "all", "also", "and", "any", "are", "args",
    "async", "before", "bool", "can", "case", "class", "const", "data",
    "def", "else", "false", "file", "for", "from", "func", "function",
    "get", "has", "have", "his", "html", "import", "into", "let", "line",
    "main", "make", "new", "none", "not", "null", "obj", "one", "only",
    "opts", "our", "out", "path", "props", "return", "set", "should",
    "state", "str", "string", "that", "the", "then", "this", "true",
    "type", "use", "used", "user", "value", "var", "was", "when", "will",
    "with", "you",
}

DOC_BASENAMES = {
    "agents.md", "claude.md", "context.md", "readme.md", "contributing.md",
    "architecture.md", "roadmap.md", "testing.md", "deployment.md",
    "security.md", "changelog.md", "current_state.md", "handoff.md",
}

DOC_EXTS = {".md", ".mdx", ".rst", ".adoc", ".txt"}


def run_git(args: list[str], cwd: Path, check: bool = False) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if check and proc.returncode != 0:
        raise SystemExit(proc.stderr.strip() or f"git {' '.join(args)} failed")
    return proc.stdout


def git_ok(args: list[str], cwd: Path) -> bool:
    proc = subprocess.run(
        ["git", *args],
        cwd=cwd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return proc.returncode == 0


def repo_root() -> Path:
    proc = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if proc.returncode != 0:
        raise SystemExit("Not inside a Git repository. Run this from the PR checkout.")
    return Path(proc.stdout.strip())


def choose_base(root: Path, requested: str | None) -> str:
    if requested:
        if git_ok(["rev-parse", "--verify", "--quiet", requested], root):
            return requested
        raise SystemExit(f"Requested base ref not found: {requested}")

    candidates = [
        os.environ.get("DOCS_BASE_REF"),
        os.environ.get("GITHUB_BASE_REF"),
        os.environ.get("BASE_REF"),
        "origin/main",
        "main",
        "origin/master",
        "master",
    ]
    for ref in filter(None, candidates):
        if git_ok(["rev-parse", "--verify", "--quiet", ref], root):
            return ref
    raise SystemExit("Could not find a base ref. Pass --base <ref>.")


def parse_name_status(raw: str, source: str) -> list[tuple[str, str, str]]:
    rows: list[tuple[str, str, str]] = []
    for line in raw.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        status = parts[0]
        path = parts[-1]
        rows.append((source, status, path))
    return rows


def changed_files(root: Path, base: str) -> list[tuple[str, str, str]]:
    rows: list[tuple[str, str, str]] = []
    rows += parse_name_status(run_git(["diff", "--name-status", "--find-renames", f"{base}...HEAD"], root), "base...HEAD")
    rows += parse_name_status(run_git(["diff", "--cached", "--name-status", "--find-renames"], root), "staged")
    rows += parse_name_status(run_git(["diff", "--name-status", "--find-renames"], root), "unstaged")
    for path in run_git(["ls-files", "--others", "--exclude-standard"], root).splitlines():
        rows.append(("untracked", "??", path))

    seen: set[tuple[str, str]] = set()
    deduped: list[tuple[str, str, str]] = []
    for source, status, path in rows:
        key = (source, path)
        if key not in seen:
            seen.add(key)
            deduped.append((source, status, path))
    return deduped


def diff_text(root: Path, base: str) -> str:
    chunks = [
        run_git(["diff", "--unified=0", "--find-renames", f"{base}...HEAD"], root),
        run_git(["diff", "--cached", "--unified=0", "--find-renames"], root),
        run_git(["diff", "--unified=0", "--find-renames"], root),
    ]
    return "\n".join(chunks)


def tokenize(text: str) -> list[str]:
    found = re.findall(r"[A-Za-z][A-Za-z0-9_-]{2,}", text)
    terms: list[str] = []
    for term in found:
        clean = term.strip("_-").lower()
        if len(clean) < 3 or clean in COMMON_TERMS:
            continue
        if clean.isdigit():
            continue
        terms.append(clean)
    return terms


def collect_terms(rows: list[tuple[str, str, str]], diff: str, max_terms: int) -> list[str]:
    counter: Counter[str] = Counter()
    for _source, _status, path in rows:
        p = Path(path)
        pieces = [p.stem, *p.parts]
        counter.update(tokenize(" ".join(pieces)))

    for line in diff.splitlines():
        if line.startswith(("+++", "---", "diff --git", "index ", "@@")):
            continue
        if line.startswith(("+", "-")):
            counter.update(tokenize(line[1:]))

    return [term for term, _count in counter.most_common(max_terms)]


def is_doc_path(path: str) -> bool:
    lower = path.lower()
    p = Path(lower)
    if p.name in DOC_BASENAMES:
        return True
    if p.suffix in DOC_EXTS and (lower.startswith("docs/") or lower.startswith("agents/")):
        return True
    if p.suffix in DOC_EXTS and any(part in {"doc", "docs", "documentation"} for part in p.parts):
        return True
    if lower.startswith(".github/") and p.suffix in DOC_EXTS:
        return True
    return False


def list_repo_files(root: Path) -> list[str]:
    raw = run_git(["ls-files", "--cached", "--others", "--exclude-standard"], root)
    return [line for line in raw.splitlines() if line.strip()]


def doc_priority(path: str) -> int:
    lower = path.lower()
    name = Path(lower).name
    score = 0
    if name in {"agents.md", "claude.md", "current_state.md"}:
        score += 25
    if name in {"readme.md", "context.md", "architecture.md", "roadmap.md", "testing.md"}:
        score += 15
    if lower.startswith(("docs/", "agents/")):
        score += 8
    return score


def scan_docs(root: Path, docs: list[str], terms: list[str], changed_doc_paths: set[str]) -> list[tuple[int, str, list[str]]]:
    if not terms and not changed_doc_paths:
        return []
    pattern = re.compile("|".join(re.escape(t) for t in terms), re.IGNORECASE) if terms else None
    results: list[tuple[int, str, list[str]]] = []

    for rel in docs:
        path = root / rel
        score = doc_priority(rel)
        hits: list[str] = []
        if rel in changed_doc_paths:
            score += 100
            hits.append("changed in diff")
        if pattern and path.exists() and path.is_file():
            try:
                with path.open("r", encoding="utf-8", errors="replace") as handle:
                    for lineno, line in enumerate(handle, 1):
                        match = pattern.search(line)
                        if not match:
                            continue
                        score += 1
                        if len(hits) < 4:
                            snippet = line.strip()
                            if len(snippet) > 110:
                                snippet = snippet[:107] + "..."
                            hits.append(f"L{lineno}:{match.group(0)}: {snippet}")
            except OSError:
                continue
        if score > 0 and hits:
            results.append((score, rel, hits))

    results.sort(key=lambda item: (-item[0], item[1]))
    return results


def print_grouped_changes(rows: list[tuple[str, str, str]]) -> None:
    grouped: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for source, status, path in rows:
        grouped[source].append((status, path))
    for source, items in grouped.items():
        print(f"\nChanged files ({source}):")
        for status, path in items[:80]:
            print(f"  {status:>3} {path}")
        if len(items) > 80:
            print(f"  ... {len(items) - 80} more")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", help="Base ref for PR comparison, e.g. origin/main")
    parser.add_argument("--max-terms", type=int, default=24, help="Maximum search terms to print")
    parser.add_argument("--max-docs", type=int, default=18, help="Maximum candidate docs to print")
    args = parser.parse_args()

    root = repo_root()
    base = choose_base(root, args.base)
    branch = run_git(["branch", "--show-current"], root).strip() or "(detached)"
    rows = changed_files(root, base)
    diff = diff_text(root, base)
    terms = collect_terms(rows, diff, args.max_terms)
    all_docs = [path for path in list_repo_files(root) if is_doc_path(path)]
    changed_doc_paths = {path for _source, _status, path in rows if is_doc_path(path)}
    candidates = scan_docs(root, all_docs, terms, changed_doc_paths)

    print(f"Repo: {root}")
    print(f"Branch: {branch}")
    print(f"Base: {base}")

    if not rows:
        print("\nNo changed files found against the selected base or working tree.")
        return 0

    print_grouped_changes(rows)

    print("\nSearch terms:")
    print("  " + (" | ".join(terms) if terms else "(none)"))

    if changed_doc_paths:
        print("\nDocumentation already changed:")
        for path in sorted(changed_doc_paths):
            print(f"  {path}")

    print("\nLikely documentation surfaces:")
    if candidates:
        for score, path, hits in candidates[: args.max_docs]:
            print(f"  score={score:>3} {path}")
            for hit in hits:
                print(f"       {hit}")
    else:
        print("  No keyword-linked docs found. Check doc-surface routing manually.")

    changed_paths = [path for _source, _status, path in rows]
    first_paths = " ".join(changed_paths[:6])
    first_terms = "|".join(re.escape(term) for term in terms[:8])
    print("\nFocused commands:")
    print(f"  git diff --unified=0 --find-renames {base}...HEAD -- {first_paths}".rstrip())
    if first_terms:
        print(f"  rg -n \"{first_terms}\" {' '.join(all_docs[:20])}")
    print("  git diff --check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
