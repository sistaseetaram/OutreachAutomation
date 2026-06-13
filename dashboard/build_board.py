#!/usr/bin/env python3
"""Regenerate the dashboard board in README.md from thread front matter.

No dependencies (stdlib only). Run after adding/editing any thread:

    python dashboard/build_board.py

It parses the YAML-ish front matter of every dashboard/threads/*.md and rewrites
the table between the <!-- BOARD:START --> and <!-- BOARD:END --> markers in README.md.
"""
from __future__ import annotations
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent
THREADS = ROOT / "threads"
README = ROOT / "README.md"

# status -> (emoji, sort rank). Lower rank = hotter = higher on the board.
STATUS = {
    "converted":    ("✅", 0),
    "call-booked":  ("🔥", 1),
    "interested":   ("🌶️", 2),
    "replied":      ("💬", 3),
    "connected":    ("🤝", 4),
    "connect-sent": ("📨", 5),
    "engaging":     ("👀", 6),
    "new":          ("🆕", 7),
    "not-now":      ("⏳", 8),
    "dead":         ("⚰️", 9),
}
ICP = {"strong": "🟢", "medium": "🟡", "weak": "🔴", "unknown": "⚪"}


def parse_front_matter(text: str) -> dict:
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.strip().startswith("#"):
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip()
    return fm


def main() -> None:
    rows = []
    for f in sorted(THREADS.glob("*.md")):
        fm = parse_front_matter(f.read_text(encoding="utf-8"))
        if not fm:
            continue
        status = fm.get("status", "new")
        emoji, rank = STATUS.get(status, ("❓", 99))
        rows.append({
            "rank": rank,
            "icp_rank": {"strong": 0, "medium": 1, "weak": 2}.get(fm.get("icp_fit", ""), 3),
            "emoji": emoji,
            "status": status,
            "name": fm.get("name", f.stem),
            "firm": fm.get("firm", "") or "—",
            "icp": ICP.get(fm.get("icp_fit", "unknown"), "⚪"),
            "geo": fm.get("geo", "") or "—",
            "next": fm.get("next_action", "") or "—",
            "due": fm.get("next_action_due", "") or "—",
            "file": f"threads/{f.name}",
        })

    rows.sort(key=lambda r: (r["rank"], r["icp_rank"], r["name"]))

    header = (
        "| | Status | Lead | Firm | ICP | Geo | Next action | Due |\n"
        "|---|---|---|---|---|---|---|---|\n"
    )
    body = "\n".join(
        f"| {r['emoji']} | {r['status']} | [{r['name']}]({r['file']}) | {r['firm']} | "
        f"{r['icp']} | {r['geo']} | {r['next']} | {r['due']} |"
        for r in rows
    )
    counts = {}
    for r in rows:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    summary = "  ·  ".join(f"{STATUS.get(s, ('❓',))[0]} {n} {s}" for s, n in
                           sorted(counts.items(), key=lambda kv: STATUS.get(kv[0], ('', 99))[1]))
    table = f"**{len(rows)} leads** — {summary}\n\n{header}{body}\n"

    text = README.read_text(encoding="utf-8")
    new = re.sub(
        r"<!-- BOARD:START -->.*?<!-- BOARD:END -->",
        f"<!-- BOARD:START -->\n{table}<!-- BOARD:END -->",
        text,
        flags=re.DOTALL,
    )
    README.write_text(new, encoding="utf-8")
    print(f"Board updated: {len(rows)} leads written to {README}")


if __name__ == "__main__":
    main()
