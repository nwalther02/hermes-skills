#!/usr/bin/env python3
"""Create packet-based handoffs between Codex and Claude Code."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


DEFAULT_CLAUDE = "/Users/nicksmac/.local/bin/claude"
DEFAULT_ROOT = Path("/tmp/claude-code-bridge")


def run(
    cmd: list[str],
    cwd: Path | None = None,
    timeout: int = 60,
    input_text: str | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        input=input_text,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
        check=False,
    )


def slugify(text: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", text.strip().lower()).strip("-")
    return (slug[:50] or "handoff").strip("-")


def now_stamp() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def json_print(data: dict[str, Any]) -> None:
    print(json.dumps(data, indent=2, sort_keys=True))


def resolve_claude() -> str:
    configured = os.environ.get("CLAUDE_BIN")
    if configured:
        return configured
    return DEFAULT_CLAUDE if Path(DEFAULT_CLAUDE).exists() else shutil.which("claude") or DEFAULT_CLAUDE


def git_snapshot(cwd: Path) -> dict[str, Any]:
    if run(["git", "rev-parse", "--is-inside-work-tree"], cwd=cwd).stdout.strip() != "true":
        return {"is_git_repo": False}
    commands = {
        "root": ["git", "rev-parse", "--show-toplevel"],
        "branch": ["git", "branch", "--show-current"],
        "status_short": ["git", "status", "--short", "--branch"],
        "remotes": ["git", "remote", "-v"],
    }
    out: dict[str, Any] = {"is_git_repo": True}
    for key, cmd in commands.items():
        proc = run(cmd, cwd=cwd)
        out[key] = proc.stdout.strip()
    return out


def path_info(path: Path) -> dict[str, Any]:
    resolved = path.expanduser().resolve()
    exists = resolved.exists()
    data: dict[str, Any] = {
        "input": str(path),
        "path": str(resolved),
        "exists": exists,
    }
    if exists:
        data["kind"] = "directory" if resolved.is_dir() else "file"
        if resolved.is_file():
            data["bytes"] = resolved.stat().st_size
    return data


def add_dir_for(path: Path) -> Path:
    resolved = path.expanduser().resolve()
    return resolved if resolved.is_dir() else resolved.parent


def make_prompt(task: str, cwd: Path, includes: list[dict[str, Any]], packet: Path) -> str:
    lines = [
        "# Claude Code Bridge Packet",
        "",
        "You are receiving a structured handoff from Codex. Use the included paths as the shared source of truth.",
        "",
        "## Task",
        "",
        task.strip(),
        "",
        "## Working Directory",
        "",
        str(cwd),
        "",
        "## Included Paths",
        "",
    ]
    for item in includes:
        status = "exists" if item["exists"] else "missing"
        lines.append(f"- `{item['path']}` ({status})")
    lines.extend(
        [
            "",
            "## Return Contract",
            "",
            "Write your final answer in these sections:",
            "",
            "- Summary",
            "- Findings",
            "- Recommended next step",
            "- Artifacts",
            "- Questions",
            "",
            f"If you create files, write them inside `{packet}` and list their absolute paths under Artifacts.",
            "Do not edit source files unless the task explicitly asks you to perform edits.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def command_status(args: argparse.Namespace) -> int:
    claude = resolve_claude()
    version = run([claude, "--version"], timeout=30)
    auth = run([claude, "auth", "status"], timeout=30)
    payload = {
        "claude_bin": claude,
        "version": version.stdout.strip(),
        "version_exit_code": version.returncode,
        "auth_exit_code": auth.returncode,
        "auth_stdout": safe_json_or_text(auth.stdout),
        "auth_stderr": auth.stderr.strip(),
    }
    if auth.returncode != 0 and os.environ.get("CODEX_SHELL"):
        payload["sandbox_hint"] = (
            "Claude auth may be hidden from sandboxed child processes. "
            "From Codex, rerun the bridge command with sandbox escalation before invoking Claude."
        )
    json_print(payload)
    return 0 if version.returncode == 0 and auth.returncode == 0 else 1


def command_smoke(args: argparse.Namespace) -> int:
    claude = resolve_claude()
    cmd = [
        claude,
        "-p",
        "--output-format",
        "json",
        "--permission-mode",
        "plan",
        "--name",
        "codex-bridge-smoke",
        "--no-session-persistence",
    ]
    if args.max_budget_usd:
        cmd.extend(["--max-budget-usd", str(args.max_budget_usd)])
    proc = run(cmd, timeout=args.timeout, input_text="Reply exactly BRIDGE_OK.")
    parsed = safe_json_or_text(proc.stdout)
    result_text = ""
    is_error = False
    api_error_status = None
    if isinstance(parsed, dict):
        result_text = str(parsed.get("result", ""))
        is_error = bool(parsed.get("is_error"))
        api_error_status = parsed.get("api_error_status")
    elif isinstance(parsed, str):
        result_text = parsed
    ok = proc.returncode == 0 and not is_error and "BRIDGE_OK" in result_text
    payload: dict[str, Any] = {
        "ok": ok,
        "exit_code": proc.returncode,
        "api_error_status": api_error_status,
        "stdout": parsed,
        "stderr": proc.stderr.strip(),
    }
    if not ok and api_error_status == 401:
        payload["auth_recovery"] = (
            "Claude auth status can be stale. Run `claude auth login` in a trusted terminal "
            "or use Claude Code's login flow, then rerun this smoke check."
        )
    json_print(payload)
    return 0 if ok else 1


def safe_json_or_text(text: str) -> Any:
    stripped = text.strip()
    if not stripped:
        return ""
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        return stripped


def command_send(args: argparse.Namespace) -> int:
    if not args.task and not args.prompt_file:
        raise SystemExit("send requires --task or --prompt-file")

    cwd = Path(args.cwd or os.getcwd()).expanduser().resolve()
    root = Path(args.out_dir).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)

    task_text = args.task or Path(args.prompt_file).expanduser().read_text(encoding="utf-8")
    packet = root / f"{now_stamp()}-{slugify(task_text)}"
    packet.mkdir(parents=True, exist_ok=False)

    include_paths = [Path(p) for p in args.include]
    includes = [path_info(p) for p in include_paths]
    prompt = make_prompt(task_text, cwd, includes, packet)
    prompt_path = packet / "PROMPT.md"
    manifest_path = packet / "MANIFEST.json"
    prompt_path.write_text(prompt, encoding="utf-8")

    readable_dirs = {str(cwd), str(packet)}
    for p in include_paths:
        readable = add_dir_for(p)
        if readable.exists():
            readable_dirs.add(str(readable))
    for p in args.add_dir:
        readable = Path(p).expanduser().resolve()
        if not readable.is_dir():
            raise SystemExit(f"--add-dir must be an existing directory: {readable}")
        readable_dirs.add(str(readable))

    claude = resolve_claude()
    cmd = [
        claude,
        "-p",
        "--output-format",
        args.output_format,
        "--permission-mode",
        args.permission_mode,
        "--name",
        args.name,
    ]
    if args.model:
        cmd.extend(["--model", args.model])
    if args.effort:
        cmd.extend(["--effort", args.effort])
    if args.max_budget_usd:
        cmd.extend(["--max-budget-usd", str(args.max_budget_usd)])
    if not args.persist_session:
        cmd.append("--no-session-persistence")
    for readable in sorted(readable_dirs):
        cmd.extend(["--add-dir", readable])
    claude_input = f"Read {prompt_path} and complete the bridge task."

    manifest = {
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "cwd": str(cwd),
        "packet": str(packet),
        "prompt": str(prompt_path),
        "includes": includes,
        "readable_dirs": sorted(readable_dirs),
        "git": git_snapshot(cwd),
        "claude_bin": claude,
        "command": cmd,
        "prompt_input": claude_input,
        "no_run": args.no_run,
    }
    if os.environ.get("CODEX_SHELL"):
        manifest["codex_sandbox_note"] = (
            "If Claude reports logged out from this packet, rerun the bridge helper with sandbox escalation."
        )
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")

    if args.no_run:
        print(packet)
        return 0

    proc = run(cmd, cwd=cwd, timeout=args.timeout, input_text=claude_input)
    stdout_path = packet / ("claude-stdout.json" if args.output_format == "json" else "claude-stdout.txt")
    stderr_path = packet / "claude-stderr.txt"
    stdout_path.write_text(proc.stdout, encoding="utf-8")
    stderr_path.write_text(proc.stderr, encoding="utf-8")

    reply = extract_reply(proc.stdout)
    (packet / "reply.md").write_text(reply, encoding="utf-8")

    manifest["completed_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
    manifest["exit_code"] = proc.returncode
    manifest["stdout_path"] = str(stdout_path)
    manifest["stderr_path"] = str(stderr_path)
    manifest["reply_path"] = str(packet / "reply.md")
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")

    print(packet)
    return proc.returncode


def extract_reply(stdout: str) -> str:
    parsed = safe_json_or_text(stdout)
    if isinstance(parsed, dict):
        for key in ("result", "response", "text", "content"):
            value = parsed.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip() + "\n"
        return json.dumps(parsed, indent=2, sort_keys=True) + "\n"
    return str(parsed).strip() + "\n"


def command_show(args: argparse.Namespace) -> int:
    packet = Path(args.packet).expanduser().resolve()
    if not packet.exists():
        raise SystemExit(f"packet not found: {packet}")
    for name in ("MANIFEST.json", "PROMPT.md", "reply.md", "claude-stderr.txt"):
        path = packet / name
        if path.exists():
            print(f"\n===== {path} =====")
            print(path.read_text(encoding="utf-8", errors="replace").rstrip())
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    status = sub.add_parser("status", help="Check Claude binary, version, and auth status.")
    status.set_defaults(func=command_status)

    smoke = sub.add_parser("smoke", help="Verify Claude print mode can answer a tiny prompt.")
    smoke.add_argument("--max-budget-usd", default="1.00", help="Optional Claude spend cap for print mode.")
    smoke.add_argument("--timeout", type=int, default=120, help="Claude timeout in seconds.")
    smoke.set_defaults(func=command_smoke)

    send = sub.add_parser("send", help="Create a packet and optionally run Claude.")
    send.add_argument("--task", help="Task to send to Claude.")
    send.add_argument("--prompt-file", help="Read task text from a file.")
    send.add_argument("--include", action="append", default=[], help="File or directory path Claude should inspect.")
    send.add_argument("--add-dir", action="append", default=[], help="Extra directory to grant Claude read access.")
    send.add_argument("--cwd", help="Working directory for Claude. Defaults to current directory.")
    send.add_argument("--out-dir", default=str(DEFAULT_ROOT), help="Packet root directory.")
    send.add_argument("--permission-mode", default="plan", help="Claude permission mode. Defaults to plan.")
    send.add_argument("--output-format", default="json", choices=["json", "text"], help="Claude print output format.")
    send.add_argument("--model", help="Optional Claude model alias/name.")
    send.add_argument("--effort", help="Optional effort level.")
    send.add_argument("--max-budget-usd", default="2.00", help="Optional Claude spend cap for print mode.")
    send.add_argument("--name", default="codex-bridge", help="Claude session display name.")
    send.add_argument("--timeout", type=int, default=900, help="Claude timeout in seconds.")
    send.add_argument("--no-run", action="store_true", help="Create packet only; do not invoke Claude.")
    send.add_argument("--persist-session", action="store_true", help="Keep the Claude print session in history.")
    send.set_defaults(func=command_send)

    show = sub.add_parser("show", help="Print the important files from a packet.")
    show.add_argument("packet", help="Packet directory under /tmp/claude-code-bridge.")
    show.set_defaults(func=command_show)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
