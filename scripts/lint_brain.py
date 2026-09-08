#!/usr/bin/env python3
"""Validate a repository-local Project Brain without modifying it."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path


REQUIRED_PATHS = (
    ".project-brain.json",
    "README.md",
    "index.md",
    "log.md",
    "architecture/architecture-idx.md",
    "decisions/decisions-idx.md",
    "techniques/techniques-idx.md",
    "conventions/conventions-idx.md",
    "raw",
    "dev-logs",
)
KNOWLEDGE_CATEGORIES = ("architecture", "decisions", "techniques", "conventions")
REQUIRED_FRONTMATTER = ("title", "abstract", "status", "date", "tags", "sources")
VALID_STATUSES = {"draft", "active", "superseded", "archived"}
WIKI_LINK = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", default=".", help="Repository root containing brain/")
    return parser.parse_args()


def parse_frontmatter(path: Path) -> tuple[dict[str, str], list[str]]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, ["missing YAML frontmatter"]
    try:
        end = lines.index("---", 1)
    except ValueError:
        return {}, ["unterminated YAML frontmatter"]

    values: dict[str, str] = {}
    for line in lines[1:end]:
        if not line or line[0].isspace() or line.lstrip().startswith("-"):
            continue
        if ":" in line:
            key, value = line.split(":", 1)
            values[key.strip()] = value.strip()
    return values, []


def knowledge_pages(brain_root: Path) -> list[Path]:
    pages: list[Path] = []
    for category in KNOWLEDGE_CATEGORIES:
        for path in (brain_root / category).rglob("*.md"):
            if not path.name.endswith("-idx.md"):
                pages.append(path)
    return sorted(pages)


def check_manifest(brain_root: Path, errors: list[str]) -> None:
    path = brain_root / ".project-brain.json"
    if not path.is_file():
        return
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f".project-brain.json: invalid JSON: {exc}")
        return
    if data.get("schema_version") != 1:
        errors.append(".project-brain.json: schema_version must be 1")
    if not data.get("project_name"):
        errors.append(".project-brain.json: project_name is required")


def check_pages(brain_root: Path, pages: list[Path], errors: list[str], warnings: list[str]) -> None:
    for path in pages:
        rel = path.relative_to(brain_root)
        values, parse_errors = parse_frontmatter(path)
        errors.extend(f"{rel}: {message}" for message in parse_errors)
        if parse_errors:
            continue
        missing = [key for key in REQUIRED_FRONTMATTER if key not in values]
        if missing:
            errors.append(f"{rel}: missing frontmatter fields: {', '.join(missing)}")
        status = values.get("status")
        if status and status not in VALID_STATUSES:
            errors.append(f"{rel}: invalid status: {status}")
        page_date = values.get("date", "")
        if page_date:
            try:
                date.fromisoformat(page_date)
            except ValueError:
                errors.append(f"{rel}: date must use YYYY-MM-DD")
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*\.md", path.name):
            warnings.append(f"{rel}: prefer a unique kebab-case filename")


def check_indexes(brain_root: Path, pages: list[Path], errors: list[str]) -> None:
    by_category: dict[str, list[Path]] = defaultdict(list)
    for path in pages:
        by_category[path.relative_to(brain_root).parts[0]].append(path)

    for category in KNOWLEDGE_CATEGORIES:
        index_path = brain_root / category / f"{category}-idx.md"
        if not index_path.is_file():
            continue
        text = index_path.read_text(encoding="utf-8")
        for path in by_category[category]:
            marker = f"[[{path.stem}]]"
            if marker not in text:
                errors.append(f"{index_path.relative_to(brain_root)}: missing {marker}")


def check_wiki_links(brain_root: Path, errors: list[str], warnings: list[str]) -> None:
    markdown_files = sorted(brain_root.rglob("*.md"))
    names: dict[str, list[Path]] = defaultdict(list)
    for path in markdown_files:
        names[path.stem].append(path)
    for stem, paths in names.items():
        if len(paths) > 1:
            joined = ", ".join(str(path.relative_to(brain_root)) for path in paths)
            warnings.append(f"ambiguous wiki-link target '{stem}': {joined}")
    for path in markdown_files:
        text = path.read_text(encoding="utf-8")
        for target in WIKI_LINK.findall(text):
            normalized = Path(target.strip()).stem
            if normalized not in names:
                errors.append(f"{path.relative_to(brain_root)}: unresolved wiki link [[{target}]]")


def main() -> int:
    args = parse_args()
    brain_root = Path(args.project_root).expanduser().resolve() / "brain"
    if not brain_root.is_dir():
        print(f"ERROR: brain directory not found: {brain_root}", file=sys.stderr)
        return 2

    errors: list[str] = []
    warnings: list[str] = []
    for relative in REQUIRED_PATHS:
        if not (brain_root / relative).exists():
            errors.append(f"missing required path: brain/{relative}")

    check_manifest(brain_root, errors)
    pages = knowledge_pages(brain_root)
    check_pages(brain_root, pages, errors, warnings)
    check_indexes(brain_root, pages, errors)
    check_wiki_links(brain_root, errors, warnings)

    for message in errors:
        print(f"ERROR: {message}")
    for message in warnings:
        print(f"WARNING: {message}")
    print(f"SUMMARY: {len(errors)} error(s), {len(warnings)} warning(s), {len(pages)} knowledge page(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())

