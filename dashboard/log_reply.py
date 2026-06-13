#!/usr/bin/env python3
"""Log an inbound reply onto a thread, then rebuild the board.

This is how Setu drops a reply during outreach so watch mode (scan_replies.py + Claude)
picks it up and drafts the next message. (You can also just paste the reply to Claude.)

    python dashboard/log_reply.py shravani-reddy --text "Sure, tell me more" [--channel linkedin]

It appends an IN row to the thread's log, sets status: replied + last_touch: today,
sets next_action, and rebuilds board.md + board.html. Then say "starting outreach" (or
just ping Claude) and Claude drafts the reply into the thread's Next reply section.
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


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("slug", help="thread slug, e.g. shravani-reddy")
    ap.add_argument("--text", required=True, help="what they said")
    ap.add_argument("--channel", default="linkedin")
    ap.add_argument("--status", default="replied")
    args = ap.parse_args()

    path = THREADS / f"{args.slug}.md"
    if not path.exists():
        print(f"No thread: {path}", file=sys.stderr)
        sys.exit(1)

    lines = path.read_text(encoding="utf-8").splitlines()
    today = dt.date.today().isoformat()
    safe = args.text.replace("|", "\\|").strip()
    new_row = f"| {today} | IN | {args.channel} | {safe} |"

    # --- update front matter: status, last_touch, next_action ---
    in_fm, fm_done = False, False
    out = []
    for line in lines:
        if line.strip() == "---" and not fm_done:
            if not in_fm:
                in_fm = True
            else:
                in_fm, fm_done = False, True
            out.append(line)
            continue
        if in_fm and re.match(r"^status:\s*", line):
            out.append(f"status: {args.status}")
        elif in_fm and re.match(r"^last_touch:\s*", line):
            out.append(f"last_touch: {today}")
        elif in_fm and re.match(r"^next_action:\s*", line):
            out.append("next_action: Draft + send the next reply (they replied)")
        else:
            out.append(line)

    # --- append IN row to the Thread log table ---
    final, i, n = [], 0, len(out)
    inserted = False
    while i < n:
        line = out[i]
        final.append(line)
        if line.startswith("## Thread log"):
            # walk to the table, drop empty placeholder rows, append new row after last data row
            j = i + 1
            # copy until end of table block
            block = []
            while j < n and not out[j].startswith("## "):
                block.append(out[j])
                j += 1
            # within block: keep header+separator+non-empty rows, then add new row
            rebuilt = []
            for b in block:
                if re.match(r"^\|[\s|]*\|$", b):  # empty placeholder row -> skip
                    continue
                rebuilt.append(b)
            # find last table line index in rebuilt
            last_tbl = max((k for k, b in enumerate(rebuilt) if b.strip().startswith("|")),
                           default=-1)
            if last_tbl >= 0:
                rebuilt.insert(last_tbl + 1, new_row)
            else:
                rebuilt.append(new_row)
            final.extend(rebuilt)
            i = j
            inserted = True
            continue
        i += 1

    if not inserted:
        print("Could not find '## Thread log' — row not added.", file=sys.stderr)
        sys.exit(1)

    path.write_text("\n".join(final) + "\n", encoding="utf-8")
    print(f"Logged reply on {args.slug}: \"{safe[:60]}\"")
    subprocess.run([sys.executable, str(ROOT / "build_board.py")], check=False)
    subprocess.run([sys.executable, str(ROOT / "build_html.py")], check=False)


if __name__ == "__main__":
    main()
