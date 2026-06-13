#!/usr/bin/env python3
"""Log an outbound touch on one or more threads, then rebuild the board.

The counterpart to log_reply.py — use it after you send a connect/DM/follow-up.

    python dashboard/log_sent.py shravani-reddy prashanthi-narapasetty --step connect
    python dashboard/log_sent.py raveena-avanthi --step "IG DM" --channel instagram
    python dashboard/log_sent.py studio-artha --step "revive follow-up" --status interested \
        --next "Await reply; bump in ~5 days" --due 2026-06-18

Defaults: status -> connect-sent, channel -> linkedin. Appends an OUT row, sets last_touch
to today, updates status/next_action, and rebuilds board.md + board.html.
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


def update_thread(slug: str, step: str, channel: str, status: str,
                  nxt: str | None, due: str | None) -> bool:
    path = THREADS / f"{slug}.md"
    if not path.exists():
        print(f"  ! no thread: {slug}", file=sys.stderr)
        return False
    lines = path.read_text(encoding="utf-8").splitlines()
    today = dt.date.today().isoformat()
    note = step.replace("|", "\\|").strip()
    new_row = f"| {today} | OUT | {channel} | {note} |"

    in_fm, fm_done, out = False, False, []
    for line in lines:
        if line.strip() == "---" and not fm_done:
            in_fm = not in_fm
            if not in_fm:
                fm_done = True
            out.append(line)
            continue
        if in_fm and re.match(r"^status:\s*", line):
            out.append(f"status: {status}")
        elif in_fm and re.match(r"^last_touch:\s*", line):
            out.append(f"last_touch: {today}")
        elif in_fm and nxt is not None and re.match(r"^next_action:\s*", line):
            out.append(f"next_action: {nxt}")
        elif in_fm and due is not None and re.match(r"^next_action_due:\s*", line):
            out.append(f"next_action_due: {due}")
        else:
            out.append(line)

    final, i, n, inserted = [], 0, len(out), False
    while i < n:
        line = out[i]
        final.append(line)
        if line.startswith("## Thread log"):
            j = i + 1
            block = []
            while j < n and not out[j].startswith("## "):
                block.append(out[j])
                j += 1
            rebuilt = [b for b in block if not re.match(r"^\|[\s|]*\|$", b)]
            last_tbl = max((k for k, b in enumerate(rebuilt) if b.strip().startswith("|")), default=-1)
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
        print(f"  ! no '## Thread log' in {slug}", file=sys.stderr)
        return False
    path.write_text("\n".join(final) + "\n", encoding="utf-8")
    print(f"  ✓ {slug}: {status} (OUT: {note})")
    return True


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("slugs", nargs="+")
    ap.add_argument("--step", default="connection request sent")
    ap.add_argument("--channel", default="linkedin")
    ap.add_argument("--status", default="connect-sent")
    ap.add_argument("--next", dest="nxt", default=None)
    ap.add_argument("--due", default=None)
    args = ap.parse_args()

    ok = 0
    for slug in args.slugs:
        if update_thread(slug, args.step, args.channel, args.status, args.nxt, args.due):
            ok += 1
    if ok:
        subprocess.run([sys.executable, str(ROOT / "build_board.py")], check=False)
        subprocess.run([sys.executable, str(ROOT / "build_html.py")], check=False)
    print(f"Logged {ok}/{len(args.slugs)} sends.")


if __name__ == "__main__":
    main()
