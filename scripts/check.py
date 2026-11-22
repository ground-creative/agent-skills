#!/usr/bin/env python3
"""Validate skills against the Agent Skills specification (agentskills.io).

    python3 scripts/check.py skills
    python3 scripts/check.py            # same, default path

Checks the rules that are easy to get wrong and expensive to discover late: the
frontmatter, the name/directory agreement, the description, the body size, and
that every relative link resolves to a file in the skill.
"""

from __future__ import annotations

import re
import sys
import pathlib

try:
    import yaml
except ImportError:  # pragma: no cover - documented dependency
    sys.exit("check.py: pyyaml is required (pip install pyyaml)")

NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
XML = re.compile(r"<[A-Za-z/][^>]*>")
MD_LINK = re.compile(r"\]\((?!https?:|mailto:|#)([^)\s]+\.md)\)")
RESERVED = ("anthropic", "claude")
BODY_LINE_LIMIT = 500


def check(skill: pathlib.Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    path = skill / "SKILL.md"

    if not path.exists():
        return [f"{skill.name}: no SKILL.md"], warnings

    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return [f"{skill.name}: SKILL.md must start with YAML frontmatter"], warnings
    try:
        end = text.index("\n---", 3)
    except ValueError:
        return [f"{skill.name}: unterminated frontmatter"], warnings

    raw = text[3:end]
    try:
        meta = yaml.safe_load(raw) or {}
    except yaml.YAMLError as exc:
        return [f"{skill.name}: frontmatter is not valid YAML: {exc}"], warnings
    if not isinstance(meta, dict):
        return [f"{skill.name}: frontmatter must be a mapping"], warnings

    if XML.search(raw):
        errors.append(f"{skill.name}: frontmatter must not contain XML tags")

    name = meta.get("name")
    if not name:
        errors.append(f"{skill.name}: name is required")
    else:
        name = str(name)
        if len(name) > 64:
            errors.append(f"{skill.name}: name is {len(name)} characters, limit is 64")
        if not NAME.match(name):
            errors.append(
                f"{skill.name}: name {name!r} must be lowercase words joined by single hyphens"
            )
        if name != skill.name:
            errors.append(f"{skill.name}: name {name!r} must equal the directory name")
        for word in RESERVED:
            if word in name:
                warnings.append(f"{skill.name}: name contains reserved word {word!r}")

    description = meta.get("description") or ""
    if not description:
        errors.append(f"{skill.name}: description is required")
    else:
        description = str(description)
        if len(description) > 1024:
            errors.append(
                f"{skill.name}: description is {len(description)} characters, limit is 1024"
            )
        lowered = description.lower()
        if "use when" not in lowered and "when " not in lowered:
            warnings.append(
                f"{skill.name}: description should say when to use the skill, "
                "not only what it does"
            )

    compatibility = meta.get("compatibility")
    if compatibility is not None and len(str(compatibility)) > 500:
        errors.append(f"{skill.name}: compatibility exceeds 500 characters")

    metadata = meta.get("metadata")
    if metadata is not None and not isinstance(metadata, dict):
        errors.append(f"{skill.name}: metadata must be a mapping of string to string")
    elif isinstance(metadata, dict):
        for key, value in metadata.items():
            if not isinstance(key, str) or not isinstance(value, str):
                warnings.append(f"{skill.name}: metadata[{key!r}] should be a string")

    body = text[end + 4 :]
    lines = len(body.splitlines())
    if lines > BODY_LINE_LIMIT:
        errors.append(
            f"{skill.name}: body is {lines} lines, limit is {BODY_LINE_LIMIT}; "
            "move detail into references/ and link it"
        )
    if lines == 0 or not body.strip():
        errors.append(f"{skill.name}: body is empty")

    for target in MD_LINK.findall(body):
        if not (skill / target).exists():
            errors.append(f"{skill.name}: link {target!r} does not exist")

    return errors, warnings


def main() -> int:
    root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "skills")
    if not root.is_dir():
        print(f"check.py: {root} is not a directory", file=sys.stderr)
        return 2

    skills = sorted(
        p for p in root.iterdir() if p.is_dir() and not p.name.startswith(".")
    )
    if not skills:
        print(f"check.py: no skills under {root}", file=sys.stderr)
        return 2

    all_errors: list[str] = []
    all_warnings: list[str] = []
    for skill in skills:
        errors, warnings = check(skill)
        all_errors.extend(errors)
        all_warnings.extend(warnings)
        state = "ok" if not errors else f"{len(errors)} error(s)"
        print(f"{skill.name:28s} {state}")

    for message in all_warnings:
        print(f"WARN {message}")
    for message in all_errors:
        print(f"FAIL {message}", file=sys.stderr)

    print(
        f"\n{len(skills)} skill(s), {len(all_errors)} error(s), "
        f"{len(all_warnings)} warning(s)"
    )
    return 1 if all_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
