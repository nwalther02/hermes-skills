#!/usr/bin/env python3
"""Thin wrapper around the central ai-context-template installer."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
CONFIG_PATH = Path.home() / ".codex/project-context-bootstrap.json"
FALLBACK_TEMPLATE = Path.home() / "Code/Projects/ai-context-template"


@dataclass
class TemplateChoice:
    path: Path
    source: str


def atomic_write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, raw = tempfile.mkstemp(prefix=f".{path.name}.tmp-", dir=str(path.parent))
    temp = Path(raw)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, sort_keys=True)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp, path)
        if hasattr(os, "O_DIRECTORY"):
            dir_fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
            try:
                os.fsync(dir_fd)
            finally:
                os.close(dir_fd)
    except Exception:
        try:
            temp.unlink()
        except FileNotFoundError:
            pass
        raise


def read_config() -> Path | None:
    if not CONFIG_PATH.exists():
        return None
    try:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid config {CONFIG_PATH}: {exc}") from exc
    if data.get("schema_version") != 1:
        raise SystemExit(f"unsupported config schema in {CONFIG_PATH}")
    raw = data.get("template_path")
    if not isinstance(raw, str) or not raw.startswith("/"):
        raise SystemExit(f"invalid template_path in {CONFIG_PATH}")
    return Path(raw)


def resolve_template(args: argparse.Namespace) -> TemplateChoice:
    if args.template:
        return TemplateChoice(Path(args.template).expanduser(), "--template")
    env = os.environ.get("AI_CONTEXT_TEMPLATE")
    if env:
        return TemplateChoice(Path(env).expanduser(), "AI_CONTEXT_TEMPLATE")
    config_path = read_config()
    if config_path:
        return TemplateChoice(config_path, str(CONFIG_PATH))
    return TemplateChoice(FALLBACK_TEMPLATE, "fallback")


def installer_path(template: Path) -> Path:
    return template / "install.py"


def validate_template(choice: TemplateChoice, target: Path) -> dict[str, Any]:
    template = choice.path.resolve()
    errors: list[str] = []
    if not installer_path(template).is_file():
        errors.append("missing install.py")
    if not (template / "template/docs/ai/context.yml").is_file():
        errors.append("missing template/docs/ai/context.yml")
    if errors:
        raise SystemExit(
            f"invalid template path from {choice.source}: {template}\n"
            + "\n".join(f"- {error}" for error in errors)
        )
    return central_status(template, target)


def central_status(template: Path, target: Path) -> dict[str, Any]:
    proc = subprocess.run(
        [
            sys.executable,
            str(installer_path(template)),
            "--status",
            "--json",
            "--target",
            str(target),
            "--template",
            str(template),
        ],
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        print("central status failed", file=sys.stderr)
        if proc.stdout:
            print(proc.stdout, file=sys.stderr)
        if proc.stderr:
            print(proc.stderr, file=sys.stderr)
        raise SystemExit(proc.returncode)
    try:
        status = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        print("central status returned invalid JSON", file=sys.stderr)
        print(proc.stdout, file=sys.stderr)
        print(proc.stderr, file=sys.stderr)
        raise SystemExit(1) from exc
    if status.get("status_schema_version") != SCHEMA_VERSION:
        print("central status schema is unrecognized", file=sys.stderr)
        print(proc.stdout, file=sys.stderr)
        print(proc.stderr, file=sys.stderr)
        raise SystemExit(1)
    return status


def run_central(template: Path, target: Path, args: argparse.Namespace) -> int:
    cmd = [
        sys.executable,
        str(installer_path(template)),
        "--target",
        str(target),
        "--template",
        str(template),
    ]
    if args.install:
        cmd.append("--install")
    elif args.repair:
        cmd.append("--repair")
    elif args.fix_generated:
        cmd.append("--fix-generated")
    elif args.upgrade_report:
        cmd.append("--upgrade-report")
        if args.write_upgrade_artifacts:
            cmd.append("--write-upgrade-artifacts")
    for adapter in args.enable_adapter:
        cmd.extend(["--enable-adapter", adapter])

    proc = subprocess.run(cmd, text=True, capture_output=True)
    if proc.stdout:
        print(proc.stdout, end="")
    if proc.stderr:
        print(proc.stderr, end="", file=sys.stderr)
    return proc.returncode


def summarize(status: dict[str, Any]) -> None:
    print(
        "ai-context "
        f"state={status['target']['installed_state']} "
        f"version={status['target']['context_version']} "
        f"action_required={str(status['action_required']).lower()}"
    )
    present = set(status["required"]["present"])
    has_agents = "AGENTS.md" in present
    has_project = "PROJECT_CONTEXT.md" in present
    if has_agents and has_project:
        print("load: read AGENTS.md, then PROJECT_CONTEXT.md")
    elif has_agents:
        print("load: read AGENTS.md; missing PROJECT_CONTEXT.md")
    elif has_project:
        print("load: read PROJECT_CONTEXT.md; missing AGENTS.md")
    else:
        print("load: AI context not installed")

    for label, values in (
        ("missing", status["required"]["missing"]),
        ("conflicts", status["files"]["conflicts"]),
        ("stale generated", status["generated"]["stale"]),
        ("adapter issues", status["adapters"]["pointer_errors"]),
        ("check errors", status["check"]["errors"]),
    ):
        if values:
            print(f"{label}: {json.dumps(values, sort_keys=True)}")


def set_template(path: str) -> None:
    choice = TemplateChoice(Path(path).expanduser(), "--set-template")
    validate_template(choice, Path.cwd())
    resolved = choice.path.resolve()
    atomic_write_json(
        CONFIG_PATH,
        {"schema_version": 1, "template_path": str(resolved)},
    )
    print(f"set template_path {resolved}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", default=".", help="target repo root")
    parser.add_argument("--template", help="source ai-context-template root")
    parser.add_argument("--set-template", help="persist a validated template path")
    parser.add_argument("--status", action="store_true", help="inspect target status")
    parser.add_argument("--json", action="store_true", help="emit status JSON")
    parser.add_argument("--install", action="store_true")
    parser.add_argument("--repair", action="store_true")
    parser.add_argument("--fix-generated", action="store_true")
    parser.add_argument("--upgrade-report", action="store_true")
    parser.add_argument("--write-upgrade-artifacts", action="store_true")
    parser.add_argument(
        "--enable-adapter",
        action="append",
        choices=["claude", "cursor", "copilot", "platform-skill"],
        default=[],
    )
    args = parser.parse_args()

    if args.set_template:
        set_template(args.set_template)
        return 0

    actions = [
        args.install,
        args.repair,
        args.fix_generated,
        args.upgrade_report,
    ]
    if sum(bool(action) for action in actions) > 1:
        parser.error("choose only one write/report action")
    if args.write_upgrade_artifacts and not args.upgrade_report:
        parser.error("--write-upgrade-artifacts requires --upgrade-report")

    target = Path(args.target).expanduser().resolve()
    choice = resolve_template(args)
    status = validate_template(choice, target)

    if args.json and not any(actions):
        print(json.dumps(status, indent=2, sort_keys=True))
        return 0

    if any(actions):
        code = run_central(choice.path.resolve(), target, args)
        if code != 0:
            return code
        status = central_status(choice.path.resolve(), target)

    summarize(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
