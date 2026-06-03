#!/usr/bin/env python3
"""
lead_tracker.py — the working lead store + pipeline orchestration.

ClickUp is the eventual system of record; until a token is set, leads live in a local cache
(`.tmp/leads.json`) that syncs to ClickUp via clickup_sync.py when ready. Defines the shared
lead schema + pipeline statuses used across cadence_engine, lead_sourcer, whatsapp_notifier.

Usage:
    python tools/lead_tracker.py --add --studio "Nine Bricks Studio" --founder Manjusha \\
        --segment architecture --track warm --city Bengaluru --status "Contacted"
    python tools/lead_tracker.py --status                  # board
    python tools/lead_tracker.py --next                    # actions due today
    python tools/lead_tracker.py --advance nine_bricks_studio --to "Follow-up 1"
    python tools/lead_tracker.py --set nine_bricks_studio email=x@y.com drive=<link>
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from datetime import date, datetime, timedelta

STORE = Path(".tmp/leads.json")
STORE.parent.mkdir(exist_ok=True)

# Pipeline statuses (mirror ClickUp). Order matters for --advance.
STATUSES = [
    "Sourced", "Researched", "Queued", "Contacted",
    "Follow-up 1", "Follow-up 2", "Follow-up 3", "Follow-up 4",
    "Replied", "Diagnosis Booked", "Free Build", "Delivered",
    "Testimonial/Referral", "Won", "Nurture", "Lost",
]
# follow-up cadence gap (days) by track
GAP_DAYS = {"warm": 3, "cold": 5}
MAX_FOLLOWUPS = {"warm": 4, "cold": 1}

FIELDS = ["studio", "founder", "segment", "track", "city", "linkedin", "instagram",
          "email", "phone", "status", "source", "followups", "last_touch",
          "next_action_date", "drive_folder", "clickup_task_id", "notes"]


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def load() -> dict:
    if STORE.exists():
        return json.loads(STORE.read_text())
    return {}


def save(d: dict):
    STORE.write_text(json.dumps(d, indent=2), encoding="utf-8")


def _today() -> str:
    return date.today().isoformat()


def add(args, leads):
    s = slug(args.studio)
    rec = {f: "" for f in FIELDS}
    rec.update({
        "studio": args.studio, "founder": args.founder or "", "segment": args.segment,
        "track": args.track, "city": args.city or "", "status": args.status or "Sourced",
        "source": args.source or "", "followups": 0, "last_touch": _today(),
        "next_action_date": _today(),
        "linkedin": args.linkedin or "", "instagram": args.instagram or "", "email": args.email or "",
    })
    leads[s] = {**rec, **leads.get(s, {})} if s in leads else rec
    save(leads)
    print(f"added/updated: {s} ({args.studio}) @ {rec['status']}")


def advance(slug_id, to, leads):
    if slug_id not in leads:
        print(f"no lead '{slug_id}'"); return
    rec = leads[slug_id]
    if to:
        rec["status"] = to
    else:
        i = STATUSES.index(rec["status"]) if rec["status"] in STATUSES else 0
        rec["status"] = STATUSES[min(i + 1, len(STATUSES) - 1)]
    if rec["status"].startswith("Follow-up"):
        rec["followups"] = int(rec.get("followups") or 0) + 1
    rec["last_touch"] = _today()
    gap = GAP_DAYS.get(rec.get("track", "warm"), 3)
    rec["next_action_date"] = (date.today() + timedelta(days=gap)).isoformat()
    save(leads)
    print(f"{slug_id} -> {rec['status']} (next action {rec['next_action_date']})")


def set_fields(slug_id, pairs, leads):
    if slug_id not in leads:
        print(f"no lead '{slug_id}'"); return
    alias = {"drive": "drive_folder", "li": "linkedin", "ig": "instagram"}
    for p in pairs:
        if "=" not in p:
            continue
        k, v = p.split("=", 1)
        k = alias.get(k, k)
        if k in FIELDS:
            leads[slug_id][k] = v
    save(leads)
    print(f"updated {slug_id}: {pairs}")


def board(leads):
    if not leads:
        print("no leads yet. Add with --add."); return
    by_status: dict = {}
    for s, r in leads.items():
        by_status.setdefault(r.get("status", "?"), []).append(r)
    print(f"\n{'='*56}\n  LEAD BOARD  ({len(leads)} leads)\n{'='*56}")
    for st in STATUSES:
        rows = by_status.get(st, [])
        if not rows:
            continue
        print(f"\n[{st}]  ({len(rows)})")
        for r in rows:
            tags = f"{r.get('track','')}/{r.get('segment','')}"
            print(f"  • {r['studio']:<28} {tags:<22} fu={r.get('followups',0)} next={r.get('next_action_date','')}")


def due_today(leads):
    today = _today()
    out = []
    for s, r in leads.items():
        if r.get("status") in ("Won", "Lost", "Nurture", "Delivered", "Testimonial/Referral"):
            continue
        if (r.get("next_action_date") or "9999") <= today:
            cap = MAX_FOLLOWUPS.get(r.get("track", "warm"), 4)
            if r.get("status", "").startswith("Follow-up") and int(r.get("followups") or 0) >= cap:
                continue
            out.append(r)
    print(f"\n{'='*56}\n  ACTIONS DUE ({len(out)})  [{today}]\n{'='*56}")
    for r in out:
        print(f"  • {r['studio']:<28} status={r.get('status')} track={r.get('track')} fu={r.get('followups',0)}")
    if not out:
        print("  nothing due. (new LinkedIn acct: also send today's warmup slice of new requests)")
    return out


def main():
    ap = argparse.ArgumentParser(description="Lead tracker / pipeline")
    ap.add_argument("--add", action="store_true")
    ap.add_argument("--studio"); ap.add_argument("--founder"); ap.add_argument("--city")
    ap.add_argument("--segment", default="interior", choices=["interior", "architecture", "construction"])
    ap.add_argument("--track", default="warm", choices=["warm", "cold"])
    ap.add_argument("--status"); ap.add_argument("--source")
    ap.add_argument("--linkedin"); ap.add_argument("--instagram"); ap.add_argument("--email")
    ap.add_argument("--advance"); ap.add_argument("--to")
    ap.add_argument("--set", nargs="+")
    ap.add_argument("--status-board", "--board", dest="board", action="store_true")
    ap.add_argument("--next", action="store_true")
    args = ap.parse_args()

    leads = load()
    if args.add:
        add(args, leads)
    elif args.advance:
        advance(args.advance, args.to, leads)
    elif args.set:
        # first token is slug
        set_fields(args.set[0], args.set[1:], leads)
    elif args.next:
        due_today(leads)
    else:
        board(leads)


if __name__ == "__main__":
    main()
