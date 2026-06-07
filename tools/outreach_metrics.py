#!/usr/bin/env python3
"""
outreach_metrics.py — ClickUp tag analytics for Sales Navigator outreach.

Reads tasks from the ClickUp Leads list and reports sent, accepted, replied, and
booked counts by variant, channel, and batch tags.

Usage:
    python tools/outreach_metrics.py
    python tools/outreach_metrics.py --batch 2026-06-07
    python tools/outreach_metrics.py --list-id 901615297544 --json
"""

from __future__ import annotations

import argparse
import json
import os
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

import requests
from dotenv import load_dotenv

_CRED_ENV = Path(__file__).resolve().parent.parent / "credentials" / ".env"
load_dotenv(_CRED_ENV if _CRED_ENV.exists() else None)

TOKEN = os.getenv("CLICKUP_API_TOKEN") or os.getenv("CLICKUP_API_KEY")
LEADS_LIST_ID = os.getenv("CLICKUP_LEADS_LIST_ID")
BASE = "https://api.clickup.com/api/v2"

REPLIED_STATUSES = {"replied", "diagnosis booked", "free build", "delivered", "won", "lost"}
BOOKED_STATUSES = {"diagnosis booked", "free build", "delivered", "won"}
SENT_STATUSES = {
    "contacted",
    "follow-up 1",
    "follow-up 2",
    "follow-up 3",
    "follow-up 4",
    "replied",
    "diagnosis booked",
    "free build",
    "delivered",
    "testimonial/referral",
    "nurture",
    "won",
    "lost",
}


def headers() -> dict[str, str]:
    return {"Authorization": TOKEN, "Content-Type": "application/json"}


def available() -> bool:
    return bool(TOKEN)


def tag_names(task: dict) -> set[str]:
    out = set()
    for raw in task.get("tags", []):
        if isinstance(raw, dict):
            name = raw.get("name")
        else:
            name = str(raw)
        if name:
            out.add(name.strip())
    return out


def status_name(task: dict) -> str:
    raw = task.get("status")
    if isinstance(raw, dict):
        return str(raw.get("status", "")).strip().lower()
    return str(raw or "").strip().lower()


def first_prefixed(tags: Iterable[str], prefix: str, fallback: str) -> str:
    matches = sorted((t for t in tags if t.startswith(prefix)), key=str.lower)
    return matches[0] if matches else fallback


def task_sent(tags: set[str], status: str) -> bool:
    return any(t.startswith("channel:") for t in tags) or status in SENT_STATUSES or "stage:contacted" in tags


def task_accepted(tags: set[str]) -> bool:
    return "accepted" in tags


def task_replied(tags: set[str], status: str) -> bool:
    return any(t.startswith("reply:") and t != "reply:no-response" for t in tags) or status in REPLIED_STATUSES


def task_booked(tags: set[str], status: str) -> bool:
    return status in BOOKED_STATUSES or "stage:diagnosis-booked" in tags


def iter_tasks(list_id: str):
    page = 0
    while True:
        r = requests.get(
            f"{BASE}/list/{list_id}/task",
            headers=headers(),
            params={"archived": "false", "include_closed": "true", "page": page},
            timeout=30,
        )
        r.raise_for_status()
        payload = r.json()
        tasks = payload.get("tasks", [])
        if not tasks:
            break
        yield from tasks
        if payload.get("last_page") is True:
            break
        page += 1


def summarize(tasks: Iterable[dict], batch: str | None = None) -> dict:
    totals = Counter()
    by_variant = defaultdict(Counter)
    by_channel = defaultdict(Counter)
    by_batch = defaultdict(Counter)
    tag_counts = Counter()

    for task in tasks:
        tags = tag_names(task)
        if batch and f"batch:{batch}" not in tags:
            continue
        status = status_name(task)
        variant = first_prefixed(tags, "variant:", "variant:unknown")
        channel = first_prefixed(tags, "channel:", "channel:unknown")
        batch_tag = first_prefixed(tags, "batch:", "batch:unknown")

        flags = {
            "sent": task_sent(tags, status),
            "accepted": task_accepted(tags),
            "replied": task_replied(tags, status),
            "booked": task_booked(tags, status),
        }

        totals["tasks"] += 1
        for tag in tags:
            if any(tag.startswith(prefix) for prefix in ("variant:", "channel:", "geo:", "batch:", "reply:")):
                tag_counts[tag] += 1
        for metric, active in flags.items():
            if not active:
                continue
            totals[metric] += 1
            by_variant[variant][metric] += 1
            by_channel[channel][metric] += 1
            by_batch[batch_tag][metric] += 1

    return {
        "totals": dict(totals),
        "by_variant": {k: dict(v) for k, v in sorted(by_variant.items())},
        "by_channel": {k: dict(v) for k, v in sorted(by_channel.items())},
        "by_batch": {k: dict(v) for k, v in sorted(by_batch.items())},
        "tag_counts": dict(sorted(tag_counts.items())),
    }


def print_counter_table(title: str, rows: dict[str, dict]) -> None:
    print(f"\n{title}")
    print("-" * len(title))
    print(f"{'group':<28} {'sent':>5} {'accepted':>8} {'replied':>7} {'booked':>6}")
    for group, counts in rows.items():
        print(
            f"{group:<28} "
            f"{counts.get('sent', 0):>5} "
            f"{counts.get('accepted', 0):>8} "
            f"{counts.get('replied', 0):>7} "
            f"{counts.get('booked', 0):>6}"
        )


def print_report(summary: dict, batch: str | None) -> None:
    totals = summary["totals"]
    scope = f"batch:{batch}" if batch else "all batches"
    print(f"Outreach metrics ({scope})")
    print("=" * (19 + len(scope)))
    print(f"tasks:    {totals.get('tasks', 0)}")
    print(f"sent:     {totals.get('sent', 0)}")
    print(f"accepted: {totals.get('accepted', 0)}")
    print(f"replied:  {totals.get('replied', 0)}")
    print(f"booked:   {totals.get('booked', 0)}")
    print_counter_table("By variant", summary["by_variant"])
    print_counter_table("By channel", summary["by_channel"])
    print_counter_table("By batch", summary["by_batch"])


def main() -> None:
    ap = argparse.ArgumentParser(description="Report ClickUp outreach metrics from Leads list tags")
    ap.add_argument("--batch", help="filter by batch date, e.g. 2026-06-07")
    ap.add_argument("--list-id", default=LEADS_LIST_ID)
    ap.add_argument("--json", action="store_true", help="print JSON summary")
    args = ap.parse_args()

    if not available():
        print("[DRY-RUN] CLICKUP_API_TOKEN / CLICKUP_API_KEY not set.")
        print("Would fetch ClickUp Leads tasks and report sent/accepted/replied/booked by variant/channel/batch.")
        return
    if not args.list_id:
        raise SystemExit("No list id. Set CLICKUP_LEADS_LIST_ID or pass --list-id.")

    summary = summarize(iter_tasks(args.list_id), args.batch)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print_report(summary, args.batch)


if __name__ == "__main__":
    main()
