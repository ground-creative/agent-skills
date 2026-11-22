#!/usr/bin/env python3
"""Link the skills in this repository into an agent's skills directory.

    python3 scripts/install.py                       # ~/.agents/skills
    python3 scripts/install.py --target ~/.claude/skills
    python3 scripts/install.py --check               # verify only

Installation is a symlink, not a copy: the repository stays the single source, so
editing a skill here changes what the agent loads and the two cannot drift. Use
--check to verify a host without changing it; it exits non-zero when a skill is
missing or points somewhere else.

This script never deletes a real directory. If a skill name is already occupied by
one, it reports the name and leaves it alone — moving your files is your call.
"""

from __future__ import annotations

import argparse
import os
import pathlib
import sys


def default_target() -> pathlib.Path:
    return pathlib.Path(
        os.environ.get("AGENT_SKILLS_DIR", "~/.agents/skills")
    ).expanduser()


def skills_in(root: pathlib.Path) -> list[pathlib.Path]:
    return sorted(
        p.resolve() for p in root.iterdir() if p.is_dir() and not p.name.startswith(".")
    )


def state_of(target: pathlib.Path, source: pathlib.Path) -> str:
    """installed | missing | wrong-target | occupied."""
    link = target / source.name
    if link.is_symlink():
        return "installed" if link.resolve() == source else "wrong-target"
    if link.exists():
        return "occupied"
    return "missing"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Link skills into an agent's skills directory."
    )
    parser.add_argument(
        "--target", default=str(default_target()), help="skills directory to populate"
    )
    parser.add_argument(
        "--check", action="store_true", help="verify only; change nothing"
    )
    parser.add_argument(
        "root", nargs="?", default="skills", help="skills directory in this repository"
    )
    args = parser.parse_args()

    source_root = pathlib.Path(args.root)
    if not source_root.is_dir():
        print(f"install.py: {source_root} is not a directory", file=sys.stderr)
        return 2

    target = pathlib.Path(args.target).expanduser()
    if not args.check:
        target.mkdir(parents=True, exist_ok=True)

    skills = skills_in(source_root)
    if not skills:
        print(f"install.py: no skills under {source_root}", file=sys.stderr)
        return 2

    problems = 0
    for source in skills:
        state = state_of(target, source)
        link = target / source.name

        if state == "installed":
            print(f"{source.name:28s} installed")
            continue

        if state == "occupied":
            print(
                f"{source.name:28s} a real directory is already there; move it away, "
                "then run this again",
                file=sys.stderr,
            )
            problems += 1
            continue

        if args.check:
            print(f"{source.name:28s} {state}")
            problems += 1
            continue

        if link.is_symlink():
            link.unlink()
        link.symlink_to(source)
        print(f"{source.name:28s} linked -> {source}")

    print(f"\ntarget: {target}")
    if problems:
        print(
            f"{problems} skill(s) not installed from this repository", file=sys.stderr
        )
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
