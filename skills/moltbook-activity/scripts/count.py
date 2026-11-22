#!/usr/bin/env python3
"""Count Moltbook activity without doing arithmetic by hand.

    python3 scripts/count.py activity.json
    <fetch activity> | python3 scripts/count.py

Reads the activity payload and prints the header the report needs, then one line
per post. It prefers a total supplied by the source and otherwise sums the
per-record counts; it never invents a number, and it fails when the parts do not
add up to the stated whole.

Why a script: a model counting notifications gets it wrong silently, and the
wrong number is the first line of the report. The arithmetic is the part that
must not be improvised.
"""

from __future__ import annotations

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


def main() -> int:
    try:
        if len(sys.argv) > 1 and sys.argv[1] != "-":
            payload = json.load(open(sys.argv[1], encoding="utf-8"))
        else:
            payload = json.load(sys.stdin)
    except OSError as exc:
        print(f"count.py: cannot read input: {exc}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(f"count.py: input is not JSON: {exc}", file=sys.stderr)
        return 2

    records = records_of(payload)
    if not records:
        print("count.py: no activity records found in the payload", file=sys.stderr)
        return 1

    per_post: dict[str, int] = {}
    counted = 0
    for record in records:
        if not isinstance(record, dict):
            continue
        post = first(record, POST_KEYS, "<unknown post>")
        count = count_of(record)
        if count is None:
            count = 1
            print(
                f"count.py: no count on record for {post}; counting it as 1",
                file=sys.stderr,
            )
        per_post[post] = per_post.get(post, 0) + count
        counted += 1

    summed = sum(per_post.values())
    total = stated_total(payload)

    print(
        f"Total notifications: {total if total is not None else summed} | "
        f"Posts with activity: {len(per_post)}"
    )
    print()
    for post, count in sorted(per_post.items(), key=lambda kv: -kv[1]):
        print(f"  {post}  {count}")

    if total is None:
        print(
            f"\ncount.py: no total in the payload; {summed} summed from "
            f"{counted} record(s) — say so in the report",
            file=sys.stderr,
        )
        return 0

    if total != summed:
        print(
            f"\ncount.py: stated total {total} != summed {summed} across "
            f"{len(per_post)} post(s). The feed disagrees with itself: a page you "
            f"did not read, or a record for a post you skipped. Resolve it before "
            f"reporting.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
