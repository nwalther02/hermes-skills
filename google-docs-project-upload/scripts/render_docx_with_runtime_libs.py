#!/usr/bin/env python3
"""Render DOCX with the bundled Documents renderer and runtime dylibs."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def first_existing(paths: list[Path]) -> Path | None:
    for path in paths:
        if path.exists():
            return path
    return None


def find_render_docx() -> Path:
    env_path = os.environ.get("DOCUMENTS_RENDER_DOCX")
    if env_path:
        path = Path(env_path).expanduser()
        if path.exists():
            return path

    home = Path.home()
    candidates = sorted(
        home.glob(
            ".codex/plugins/cache/openai-primary-runtime/documents/*/skills/documents/render_docx.py"
        ),
        reverse=True,
    )
    path = first_existing(candidates)
    if path:
        return path

    raise SystemExit(
        "Could not find Documents render_docx.py. Set DOCUMENTS_RENDER_DOCX."
    )


def find_liblcms_dir() -> Path | None:
    env_path = os.environ.get("CODEX_LIBLCMS_DIR")
    if env_path:
        path = Path(env_path).expanduser()
        if (path / "liblcms2.2.dylib").exists():
            return path

    home = Path.home()
    candidates = [
        home
        / ".cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/poppler/lib",
    ]
    candidates.extend(
        sorted(
            {
                path.parent
                for path in home.glob(
                    ".cache/codex-runtimes/**/liblcms2.2.dylib"
                )
            },
            reverse=True,
        )
    )

    for path in candidates:
        if (path / "liblcms2.2.dylib").exists():
            return path
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_docx")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--emit-pdf", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    input_docx = Path(args.input_docx).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()
    if not input_docx.exists():
        raise SystemExit(f"Missing input DOCX: {input_docx}")

    render_docx = find_render_docx()
    env = os.environ.copy()
    lib_dir = find_liblcms_dir()
    if lib_dir:
        existing = env.get("DYLD_LIBRARY_PATH")
        env["DYLD_LIBRARY_PATH"] = (
            f"{lib_dir}:{existing}" if existing else str(lib_dir)
        )

    cmd = [
        sys.executable,
        str(render_docx),
        str(input_docx),
        "--output_dir",
        str(output_dir),
    ]
    if args.emit_pdf:
        cmd.append("--emit_pdf")
    if args.verbose:
        cmd.append("--verbose")

    return subprocess.run(cmd, env=env, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
