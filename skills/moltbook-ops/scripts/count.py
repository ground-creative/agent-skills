#!/usr/bin/env python3
"""Count Moltbook notifications without doing arithmetic by hand.

The header line of the report is the one number with an exact right answer, and it is
the one a model gets wrong silently. This does the arithmetic instead, and refuses to
invent anything.

Input is the activity payload, given one of three ways:

    python3 scripts/count.py activity.json                      # a file
    cat activity.json | python3 scripts/count.py                # stdin
    python3 scripts/count.py '{"activity_on_your_posts": []}'    # inline JSON

Output is JSON on stdout, because a host that runs skill scripts reads stdout as data
and treats prose as a failure:

    {
      "ok": true,
      "total": 1,
      "posts": 1,
      "total_source": "summed",
      "stated_total": null,
      "summed_total": 1,
      "per_post": [{"post_id": "5f7deedc-...", "notifications": 1}],
      "warnings": ["no total in the payload; summed from 1 record(s)"]
    }

`total` and `posts` are the two numbers the report's first line needs. Diagnostics
also go to stderr, so a person running it in a terminal sees what happened. Pass
--text for the human rendering instead of JSON.

When the stated total disagrees with its parts, `ok` is false, `total` is null, and
both numbers are given separately: the disagreement is the finding, not a number to
pick between.

Exit codes:
    0  counted (a sum is labelled as a sum when the source gives no total)
    1  the stated total disagrees with its parts, or there is nothing to count
    2  bad arguments, or the input is not readable JSON
"""

from __future__ import annotations

import argparse
import json
import sys

RECORD_KEYS = ("activity_on_your_posts", "activity", "records", "items")
POST_KEYS = ("post_id", "postId", "id")
COUNT_KEYS = ("new_notification_count", "notification_count", "count", "notifications")
TOTAL_KEYS = ("total_notifications", "total", "notification_total")


def records_of(payload):
    if isinstance(payload, list):
        return payload
    if not isinstance(payload, dict):
        return []
    for key in RECORD_KEYS:
        value = payload.get(key)
        if isinstance(value, list):
            return value
    for value in payload.values():
        if isinstance(value, dict):
            found = records_of(value)
            if found:
                return found
    return []


def stated_total(payload):
    if not isinstance(payload, dict):
        return None
    for key in TOTAL_KEYS:
        value = payload.get(key)
        if isinstance(value, int):
            return value
    for value in payload.values():
        if isinstance(value, dict):
            found = stated_total(value)
            if found is not None:
                return found
    return None


def first(record, keys, default=None):
    for key in keys:
        if key in record and record[key] is not None:
            return record[key]
    return default


def count_of(record):
    for key in COUNT_KEYS:
        value = record.get(key)
        if isinstance(value, int):
            return value
    return None


def emit(result, text=False):
    """Print the result as JSON, or as the human header when --text is given."""
    if not text:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return
    if result.get("error"):
        print(
            f"count.py: {result['error']}\n"
            f"  stated {result.get('stated_total')} / summed {result.get('summed_total')}",
            file=sys.stderr,
        )
        return
    print(
        f"Total notifications: {result['total']} | "
        f"Posts with activity: {result['posts']}"
    )
    print()
    for row in result["per_post"]:
        print(f"  {row['post_id']}  {row['notifications']}")


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="count.py",
        description="Count Moltbook notifications and check that the parts add up.",
        epilog=(
            "A non-zero exit means the payload disagrees with itself: report the "
            "disagreement rather than one of the two numbers."
        ),
    )
    parser.add_argument(
        "payload",
        nargs="?",
        default="-",
        help="activity JSON file, inline JSON, or - to read stdin (default)",
    )
    parser.add_argument(
        "--text",
        action="store_true",
        help="print the human header and one line per post instead of JSON",
    )
    args = parser.parse_args()

    try:
        source = args.payload
        if source == "-":
            if sys.stdin.isatty():
                print(
                    "count.py: no input. Pass a file, inline JSON, or pipe a payload:\n"
                    "  python3 scripts/count.py activity.json\n"
                    "  cat activity.json | python3 scripts/count.py",
                    file=sys.stderr,
                )
                return 2
            payload = json.load(sys.stdin)
        elif source.lstrip().startswith(("{", "[")):
            payload = json.loads(source)
        else:
            with open(source, encoding="utf-8") as handle:
                payload = json.load(handle)
    except OSError as exc:
        print(f"count.py: cannot read {args.payload}: {exc}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(
            f"count.py: input is not JSON: {exc}. Expected the activity payload as "
            f"returned by the platform.",
            file=sys.stderr,
        )
        return 2

    records = records_of(payload)
    if not records:
        message = "no activity records found in the payload"
        print(f"count.py: {message}", file=sys.stderr)
        emit({"ok": False, "error": message}, args.text)
        return 1

    per_post: dict[str, int] = {}
    warnings_list: list[str] = []
    counted = 0
    for record in records:
        if not isinstance(record, dict):
            continue
        post = first(record, POST_KEYS, "<unknown post>")
        count = count_of(record)
        if count is None:
            count = 1
            warning = f"no count on the record for {post}; counted as 1"
            warnings_list.append(warning)
            print(f"count.py: {warning}", file=sys.stderr)
        per_post[post] = per_post.get(post, 0) + count
        counted += 1

    summed = sum(per_post.values())
    stated = stated_total(payload)

    rows = [
        {"post_id": post, "notifications": count}
        for post, count in sorted(per_post.items(), key=lambda kv: -kv[1])
    ]

    if stated is None:
        warning = f"no total in the payload; summed from {counted} record(s)"
        warnings_list.append(warning)
        print(f"count.py: {warning} — say so in the report", file=sys.stderr)
        emit(
            {
                "ok": True,
                "total": summed,
                "posts": len(per_post),
                "total_source": "summed",
                "stated_total": None,
                "summed_total": summed,
                "per_post": rows,
                "warnings": warnings_list,
            },
            args.text,
        )
        return 0

    if stated != summed:
        error = (
            f"stated total {stated} does not equal the {summed} summed across "
            f"{len(per_post)} post(s)"
        )
        print(
            f"count.py: {error}. The payload disagrees with itself: a page you did not "
            f"read, or a record for a post you skipped. Resolve it before reporting.",
            file=sys.stderr,
        )
        emit(
            {
                "ok": False,
                "error": error,
                "total": None,
                "posts": len(per_post),
                "total_source": "disagree",
                "stated_total": stated,
                "summed_total": summed,
                "per_post": rows,
                "warnings": warnings_list,
            },
            args.text,
        )
        return 1

    emit(
        {
            "ok": True,
            "total": stated,
            "posts": len(per_post),
            "total_source": "stated",
            "stated_total": stated,
            "summed_total": summed,
            "per_post": rows,
            "warnings": warnings_list,
        },
        args.text,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
