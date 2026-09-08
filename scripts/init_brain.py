#!/usr/bin/env python3
"""Create a safe, empty Project Brain scaffold in a repository."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import date
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", default=".", help="Target repository root")
    parser.add_argument("--project-name", help="Display name; defaults to the root directory name")
    return parser.parse_args()


def copy_template(template_root: Path, brain_root: Path, project_name: str) -> None:
    shutil.copytree(template_root, brain_root)
    replacements = {
        "{{PROJECT_NAME}}": project_name,
        "{{DATE}}": date.today().isoformat(),
    }
    for path in brain_root.rglob("*"):
        if not path.is_file() or path.suffix not in {".md", ".json"}:
            continue
        content = path.read_text(encoding="utf-8")
        for source, target in replacements.items():
            content = content.replace(source, target)
        path.write_text(content, encoding="utf-8")


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).expanduser().resolve()
    if not project_root.is_dir():
        print(f"ERROR: project root is not a directory: {project_root}", file=sys.stderr)
        return 2

    brain_root = project_root / "brain"
    if brain_root.exists():
        print(f"ERROR: refusing to overwrite existing path: {brain_root}", file=sys.stderr)
        return 3

    template_root = Path(__file__).resolve().parent.parent / "assets" / "brain-template"
    if not template_root.is_dir():
        print(f"ERROR: template directory is missing: {template_root}", file=sys.stderr)
        return 4

    project_name = args.project_name or project_root.name
    try:
        copy_template(template_root, brain_root, project_name)
    except Exception:
        if brain_root.exists():
            shutil.rmtree(brain_root)
        raise

    manifest = brain_root / ".project-brain.json"
    data = json.loads(manifest.read_text(encoding="utf-8"))
    print(json.dumps({"created": str(brain_root), "manifest": data}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

