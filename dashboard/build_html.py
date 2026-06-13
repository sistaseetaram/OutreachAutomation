#!/usr/bin/env python3
"""Render a self-contained, browser-viewable dashboard from the thread files.

    python dashboard/build_html.py [--open]

Produces dashboard/board.html — a single local file (inline CSS/JS, no network,
no dependencies). Cards carry copy buttons for every outreach message so Setu can
run outreach straight from the browser. NOT committed (board.html is gitignored).
"""
from __future__ import annotations
import argparse
import html
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent
THREADS = ROOT / "threads"
OUT = ROOT / "board.html"

STATUS = {
    "converted": ("✅", 0, "#16a34a"), "call-booked": ("🔥", 1, "#dc2626"),
    "interested": ("🌶️", 2, "#ea580c"), "replied": ("💬", 3, "#d97706"),
    "connected": ("🤝", 4, "#0891b2"), "connect-sent": ("📨", 5, "#2563eb"),
    "engaging": ("👀", 6, "#7c3aed"), "new": ("🆕", 7, "#475569"),
    "not-now": ("⏳", 8, "#94a3b8"), "dead": ("⚰️", 9, "#cbd5e1"),
}
ICP = {"strong": ("🟢", "#16a34a"), "medium": ("🟡", "#d97706"),
       "weak": ("🔴", "#dc2626"), "unknown": ("⚪", "#94a3b8")}


def parse(text: str) -> dict:
    fm = {}
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if m:
        for line in m.group(1).splitlines():
            if ":" in line and not line.strip().startswith("#"):
                k, _, v = line.partition(":")
                fm[k.strip()] = v.strip()
    # message blocks: heading "### ..." -> following "> " lines
    msgs, cur = [], None
    hook = []
    in_hook = False
    for line in text.splitlines():
        if line.startswith("### "):
            cur = line[4:].strip()
        elif line.startswith("> ") and cur:
            msgs.append((cur, line[2:].strip()))
            cur = None
        if line.startswith("## Personalization hook"):
            in_hook = True
            continue
        if in_hook:
            if line.startswith("## "):
                in_hook = False
            elif line.strip() and not line.strip().startswith("<!--"):
                hook.append(line.strip())
    fm["_msgs"] = msgs
    fm["_hook"] = " ".join(hook)
    return fm


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--open", action="store_true", help="open in default browser")
    args = ap.parse_args()

    leads = []
    for f in sorted(THREADS.glob("*.md")):
        fm = parse(f.read_text(encoding="utf-8"))
        if not fm.get("name"):
            continue
        fm["_file"] = f.name
        st = fm.get("status", "new")
        fm["_rank"] = STATUS.get(st, ("❓", 99, "#000"))[1]
        fm["_icp_rank"] = {"strong": 0, "medium": 1, "weak": 2}.get(fm.get("icp_fit", ""), 3)
        leads.append(fm)
    leads.sort(key=lambda d: (d["_rank"], d["_icp_rank"], d.get("name", "")))

    def badge(st):
        e, _, c = STATUS.get(st, ("❓", 99, "#475569"))
        return f'<span class="badge" style="background:{c}">{e} {html.escape(st)}</span>'

    def icp_badge(v):
        e, c = ICP.get(v, ("⚪", "#94a3b8"))
        return f'<span class="icp" style="color:{c}">{e} {html.escape(v or "?")}</span>'

    rows = ""
    for d in leads:
        rows += (f'<tr onclick="document.getElementById(\'{d["slug"]}\')'
                 f'.scrollIntoView({{behavior:\'smooth\'}})">'
                 f'<td>{badge(d.get("status","new"))}</td>'
                 f'<td><b>{html.escape(d.get("name",""))}</b></td>'
                 f'<td>{html.escape(d.get("firm","") or "—")}</td>'
                 f'<td>{icp_badge(d.get("icp_fit","unknown"))}</td>'
                 f'<td>{html.escape(d.get("geo","") or "—")}</td>'
                 f'<td>{html.escape(d.get("next_action","") or "—")}</td>'
                 f'<td>{html.escape(d.get("next_action_due","") or "—")}</td></tr>')

    cards = ""
    for d in leads:
        msg_html = ""
        for heading, msg in d["_msgs"]:
            esc_attr = html.escape(msg, quote=True)
            msg_html += (
                f'<div class="msg"><div class="msg-h">{html.escape(heading)}'
                f'<button class="copy" data-copy="{esc_attr}">Copy</button></div>'
                f'<div class="msg-b">{html.escape(msg)}</div></div>')
        li = d.get("linkedin", "")
        link = f'<a href="{html.escape(li)}" target="_blank">LinkedIn ↗</a>' if li else ""
        cu = d.get("clickup", "")
        culink = f' · <a href="{html.escape(cu)}" target="_blank">ClickUp ↗</a>' if cu else ""
        hook = f'<p class="hook">🎯 {html.escape(d["_hook"])}</p>' if d.get("_hook") else ""
        nxt = f'<p class="next"><b>Next:</b> {html.escape(d.get("next_action","") or "—")} <span class="due">({html.escape(d.get("next_action_due","") or "")})</span></p>'
        cards += (
            f'<div class="card" id="{d["slug"]}">'
            f'<div class="card-h">{badge(d.get("status","new"))} {icp_badge(d.get("icp_fit","unknown"))}'
            f'<h2>{html.escape(d.get("name",""))}</h2>'
            f'<span class="firm">{html.escape(d.get("firm","") or "")}</span>'
            f'<span class="links">{link}{culink} · <a href="threads/{d["_file"]}" target="_blank">thread .md ↗</a></span></div>'
            f'{hook}{nxt}{msg_html}</div>')

    n = len(leads)
    counts = {}
    for d in leads:
        counts[d.get("status", "new")] = counts.get(d.get("status", "new"), 0) + 1
    summary = " · ".join(f'{STATUS.get(s,("❓",))[0]} {c} {s}' for s, c in
                         sorted(counts.items(), key=lambda kv: STATUS.get(kv[0], ("", 99))[1]))

    page = f"""<!doctype html><html lang=en><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>Setu Warm Outreach</title><style>
:root{{--bg:#0f172a;--card:#1e293b;--mut:#94a3b8;--fg:#e2e8f0;--line:#334155}}
*{{box-sizing:border-box}}body{{margin:0;font:15px/1.5 -apple-system,Segoe UI,Roboto,sans-serif;background:var(--bg);color:var(--fg)}}
header{{padding:24px 28px;border-bottom:1px solid var(--line);position:sticky;top:0;background:var(--bg);z-index:5}}
h1{{margin:0 0 4px;font-size:22px}}.sub{{color:var(--mut);font-size:13px}}
.wrap{{max-width:1100px;margin:0 auto;padding:24px 28px}}
table{{width:100%;border-collapse:collapse;font-size:13px;margin-bottom:32px}}
th,td{{text-align:left;padding:9px 10px;border-bottom:1px solid var(--line)}}
th{{color:var(--mut);font-weight:600;text-transform:uppercase;font-size:11px;letter-spacing:.04em}}
tr{{cursor:pointer}}tbody tr:hover{{background:#172033}}
.badge{{color:#fff;padding:2px 8px;border-radius:20px;font-size:11px;white-space:nowrap}}
.icp{{font-weight:600;font-size:12px;white-space:nowrap}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px 20px;margin-bottom:16px}}
.card-h{{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:6px}}
.card-h h2{{margin:0;font-size:18px}}.firm{{color:var(--mut)}}
.links{{margin-left:auto;font-size:12px}}.links a{{color:#60a5fa;text-decoration:none;margin-left:8px}}
.hook{{color:#fcd34d;font-size:13px;margin:6px 0}}
.next{{font-size:13px;color:var(--fg);margin:6px 0 12px}}.due{{color:var(--mut)}}
.msg{{background:#0f1729;border:1px solid var(--line);border-radius:8px;margin:8px 0;overflow:hidden}}
.msg-h{{display:flex;align-items:center;justify-content:space-between;padding:7px 12px;background:#172033;font-size:12px;color:var(--mut);font-weight:600}}
.msg-b{{padding:10px 12px;font-size:14px;white-space:pre-wrap}}
.copy{{background:#2563eb;color:#fff;border:0;border-radius:6px;padding:4px 12px;font-size:12px;cursor:pointer}}
.copy:hover{{background:#1d4ed8}}.copy.ok{{background:#16a34a}}
.legend{{color:var(--mut);font-size:12px;margin:-12px 0 24px}}
a.doc{{color:#60a5fa}}
</style></head><body>
<header><h1>📋 Setu Warm Outreach</h1>
<div class=sub>{n} leads · {summary}</div></header>
<div class=wrap>
<p class=legend>Click any row to jump to its card. Each message has a Copy button — comment first, then send the connect. LinkedIn cap: 20–25 connects/day. Source of truth: the <a class=doc href="threads/" >thread .md files</a> + <a class=doc href="SALES-PLAYBOOK.md">playbook</a>. Regenerate: <code>python dashboard/build_html.py --open</code></p>
<table><thead><tr><th>Status</th><th>Lead</th><th>Firm</th><th>ICP</th><th>Geo</th><th>Next action</th><th>Due</th></tr></thead>
<tbody>{rows}</tbody></table>
{cards}
</div>
<script>
document.querySelectorAll('.copy').forEach(b=>b.addEventListener('click',e=>{{
 e.stopPropagation();
 navigator.clipboard.writeText(b.dataset.copy).then(()=>{{
  const t=b.textContent;b.textContent='Copied ✓';b.classList.add('ok');
  setTimeout(()=>{{b.textContent=t;b.classList.remove('ok')}},1400);
 }});
}}));
</script></body></html>"""
    OUT.write_text(page, encoding="utf-8")
    print(f"Wrote {OUT} ({n} leads)")
    if args.open:
        subprocess.run(["open", str(OUT)], check=False)


if __name__ == "__main__":
    main()
