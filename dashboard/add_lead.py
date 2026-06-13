#!/usr/bin/env python3
"""Add a new lead thread to the dashboard, then rebuild the board.

Two ways to add a lead:
  1) Setu (CLI):   python dashboard/add_lead.py --name "Asha Rao" --firm "Studio X" \
                       --linkedin "https://www.linkedin.com/in/asha-rao/" --geo hyderabad
  2) Claude:       just writes a threads/<slug>.md file directly, then runs build_board.py

Either way, run build_board.py after (this script does it for you).
"""
from __future__ import annotations
import argparse
import datetime as dt
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent
THREADS = ROOT / "threads"


def slugify(name: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return s or "lead"


def main() -> None:
    ap = argparse.ArgumentParser(description="Add a lead thread to the dashboard.")
    ap.add_argument("--name", required=True)
    ap.add_argument("--firm", default="")
    ap.add_argument("--linkedin", default="")
    ap.add_argument("--geo", default="hyderabad")
    ap.add_argument("--icp", default="unknown", choices=["strong", "medium", "weak", "unknown"])
    ap.add_argument("--role", default="unknown")
    ap.add_argument("--variant", default="soft-touch", choices=["soft-touch", "offer-campaign"])
    ap.add_argument("--status", default="new")
    args = ap.parse_args()

    slug = slugify(args.name)
    path = THREADS / f"{slug}.md"
    if path.exists():
        print(f"Thread already exists: {path}", file=sys.stderr)
        sys.exit(1)

    today = dt.date.today().isoformat()
    path.write_text(f"""---
name: {args.name}
firm: {args.firm}
slug: {slug}
linkedin: {args.linkedin}
status: {args.status}
variant: {args.variant}
icp_fit: {args.icp}
role: {args.role}
geo: {args.geo}
last_touch:
next_action: Research + draft connect message
next_action_due: {today}
---

## Snapshot
- **Who:** {args.name}{f" — {args.firm}" if args.firm else ""}
- **ICP fit:** {args.icp}

## Research
<!-- fill in: firm, role, focus, public footprint -->

## Personalization hook
<!-- the ONE real signal -->

## Messages (drafts ready to send)
### Step 1 — engage on their post
>

### Step 2 — connection request (<=300 chars, no pitch)
>

### Step 3 — follow-up DM after they accept
>

## Thread log
| date | dir | channel | message / note |
|------|-----|---------|----------------|
|      |     |         |                |

## Next reply (filled by Claude when Setu pastes their reply)
""", encoding="utf-8")
    print(f"Created {path}")

    # Rebuild the board.
    subprocess.run([sys.executable, str(ROOT / "build_board.py")], check=False)


if __name__ == "__main__":
    main()
