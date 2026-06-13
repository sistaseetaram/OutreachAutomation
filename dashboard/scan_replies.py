#!/usr/bin/env python3
"""Detector for outreach watch mode — deterministic, no API, no tokens.

Scans dashboard/threads/*.md and reports which threads have an inbound reply logged
(`| ... | IN | ... |` row in the Thread log) but NO drafted response yet (empty
"## Next reply" section). Those are the threads that need Claude to draft.

    python dashboard/scan_replies.py            # human-readable
    python dashboard/scan_replies.py --json      # machine-readable (for the watch loop)

Exit code 0 always. Prints nothing actionable when the queue is empty.
"""
from __future__ import annotations
import argparse
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent
THREADS = ROOT / "threads"


def section(text: str, heading: str) -> str:
    """Return the body under a '## heading' up to the next '## '."""
    m = re.search(rf"^##\s+{re.escape(heading)}.*?$(.*?)(?=^##\s|\Z)", text,
                  re.DOTALL | re.MULTILINE)
    return m.group(1) if m else ""


def front(text: str, key: str) -> str:
    m = re.search(rf"^{key}:\s*(.*)$", text, re.MULTILINE)
    return m.group(1).strip().strip('"') if m else ""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    pending = []
    for f in sorted(THREADS.glob("*.md")):
        t = f.read_text(encoding="utf-8")
        log = section(t, "Thread log")
        # inbound rows: a table row whose 2nd cell is IN
        inbound = [r for r in re.findall(r"^\|(.+)\|$", log, re.MULTILINE)
                   if len(r.split("|")) >= 2 and r.split("|")[1].strip().upper() == "IN"]
        if not inbound:
            continue
        # next-reply body, minus the heading's parenthetical and html comments
        nxt = section(t, "Next reply")
        nxt_clean = re.sub(r"<!--.*?-->", "", nxt, flags=re.DOTALL).strip()
        # the heading line itself may carry "(filled by Claude...)" — section() already drops the heading line
        if nxt_clean:
            continue  # already drafted
        last_in = inbound[-1].split("|")
        pending.append({
            "slug": f.stem,
            "name": front(t, "name"),
            "status": front(t, "status"),
            "last_reply": last_in[3].strip() if len(last_in) > 3 else "",
            "file": f"threads/{f.name}",
        })

    if args.json:
        print(json.dumps(pending, ensure_ascii=False))
        return
    if not pending:
        print("✓ No replies awaiting a draft.")
        return
    print(f"⚑ {len(pending)} thread(s) need a draft:\n")
    for p in pending:
        print(f"  • {p['name']} ({p['slug']}) — status: {p['status']}")
        if p["last_reply"]:
            print(f"      reply: {p['last_reply'][:90]}")


if __name__ == "__main__":
    main()
