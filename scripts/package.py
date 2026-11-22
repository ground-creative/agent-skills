#!/usr/bin/env python3
"""Package skills into zips for hosts that take an upload instead of a directory.

    python3 scripts/package.py                 # every skill -> dist/<name>.zip
    python3 scripts/package.py web-access      # one skill
    python3 scripts/package.py --out /tmp/pkg  # somewhere else

Claude Code, and this editor, read a directory and need none of this. claude.ai
and the Skills API do, and they are stricter than the filesystem is:

  - SKILL.md must sit at the upload root or at the top of a single enclosing
    folder, so the archive holds exactly one directory and it is named after the
    skill;
  - the archive must stay under 30 MB uncompressed;
  - the frontmatter may carry only the six fields the spec defines. Claude Code
    tolerates extra ones such as disable-model-invocation; an upload rejects them
    with a hard error, which turns a working skill into a broken one at the last
    step.

So this refuses to build an archive that would be rejected. Failing here is the
point: a skill that packages is a skill that uploads.
"""

from __future__ import annotations

import argparse
import pathlib
import sys
import zipfile

try:
    import yaml
except ImportError:  # pragma: no cover - documented dependency
    sys.exit("package.py: pyyaml is required (pip install pyyaml)")

SPEC_FIELDS = {
    "name",
    "description",
    "license",
    "compatibility",
    "metadata",
    "allowed-tools",
}
SIZE_LIMIT = 30 * 1024 * 1024


def frontmatter(path: pathlib.Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise ValueError("SKILL.md must start with YAML frontmatter")
    try:
        end = text.index("\n---", 3)
    except ValueError:
        raise ValueError("unterminated frontmatter") from None
    meta = yaml.safe_load(text[3:end]) or {}
    if not isinstance(meta, dict):
        raise ValueError("frontmatter must be a mapping")
    return meta


def collect(skill: pathlib.Path) -> tuple[pathlib.Path, int]:
    """Return the skill directory and its uncompressed size."""
    size = 0
    for path in skill.rglob("*"):
        if path.is_file():
            size += path.stat().st_size
    return skill, size


def package(skill: pathlib.Path, out: pathlib.Path) -> pathlib.Path:
    meta = frontmatter(skill / "SKILL.md")

    extra = set(meta) - SPEC_FIELDS
    if extra:
        names = ", ".join(sorted(extra))
        raise ValueError(
            f"unexpected key(s) in SKILL.md frontmatter: {names}\n"
            f"  an upload accepts only: {', '.join(sorted(SPEC_FIELDS))}\n"
            f"  move the rest into the body, or ship this skill to a host that "
            f"reads a directory"
        )

    if meta.get("name") != skill.name:
        raise ValueError(
            f"frontmatter name is {meta.get('name')!r} but the folder is "
            f"{skill.name!r}; the archive top-level folder must match the name"
        )

    _, size = collect(skill)
    if size >= SIZE_LIMIT:
        raise ValueError(
            f"{size / 1048576:.1f} MB exceeds the 30 MB uncompressed limit; keep "
            f"the body in SKILL.md and move bulk into references/ only if you "
            f"are under the limit"
        )

    out.mkdir(parents=True, exist_ok=True)
    archive = out / f"{skill.name}.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(skill.rglob("*")):
            if path.is_file():
                zf.write(path, arcname=path.relative_to(skill.parent))
    return archive


def main() -> int:
    root = pathlib.Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("names", nargs="*", help="skill names (default: all)")
    parser.add_argument("--skills", default=str(root / "skills"), help="skill root")
    parser.add_argument("--out", default=str(root / "dist"), help="output directory")
    args = parser.parse_args()

    skills_root = pathlib.Path(args.skills)
    out = pathlib.Path(args.out)

    if args.names:
        selected = [skills_root / name for name in args.names]
    else:
        selected = sorted(p for p in skills_root.iterdir() if p.is_dir())

    if not selected:
        print(f"package.py: no skills under {skills_root}", file=sys.stderr)
        return 1

    failed = 0
    for skill in selected:
        if not (skill / "SKILL.md").exists():
            print(f"fail {skill.name}: no SKILL.md", file=sys.stderr)
            failed += 1
            continue
        try:
            archive = package(skill, out)
        except ValueError as exc:
            print(f"fail {skill.name}: {exc}", file=sys.stderr)
            failed += 1
            continue
        size = archive.stat().st_size
        print(f"ok   {skill.name} -> {archive} ({size / 1024:.1f} KB)")

    if failed:
        print(f"\n{failed} skill(s) not packaged", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
