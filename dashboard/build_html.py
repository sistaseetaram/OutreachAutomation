#!/usr/bin/env python3
"""Render a self-contained, browser-viewable dashboard from the thread + guide files.

    python dashboard/build_html.py [--open]

Produces dashboard/board.html — one local file (inline CSS/JS, no network, no deps),
with three tabs: Board, Call Guide, Playbook. Outreach messages and scripted call lines
get Copy buttons. board.html is gitignored (local only).
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
CALL_GUIDE = ROOT / "CALL-GUIDE.md"
PLAYBOOK = ROOT / "SALES-PLAYBOOK.md"

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
                fm[k.strip()] = v.strip().strip('"')
    msgs, cur, hook, in_hook = [], None, [], False
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
    fm["_msgs"], fm["_hook"] = msgs, " ".join(hook)
    return fm


def inline(s: str) -> str:
    s = html.escape(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
    s = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2" target="_blank">\1</a>', s)
    return s


def md_to_html(text: str) -> str:
    lines = text.split("\n")
    out, i, n = [], 0, len(lines)
    while i < n:
        line = lines[i]
        if line.strip().startswith("<!--"):
            while i < n and "-->" not in lines[i]:
                i += 1
            i += 1
            continue
        if line.startswith("```"):
            i += 1
            buf = []
            while i < n and not lines[i].startswith("```"):
                buf.append(html.escape(lines[i]))
                i += 1
            i += 1
            out.append('<pre class="code">' + "\n".join(buf) + "</pre>")
            continue
        h = re.match(r"^(#{1,6})\s+(.*)", line)
        if h:
            lvl = len(h.group(1))
            out.append(f"<h{lvl}>{inline(h.group(2).strip())}</h{lvl}>")
            i += 1
            continue
        if re.match(r"^---+\s*$", line):
            out.append("<hr>")
            i += 1
            continue
        if line.startswith(">"):
            buf = []
            while i < n and lines[i].startswith(">"):
                buf.append(lines[i].lstrip(">").strip())
                i += 1
            joined = "\n".join(buf)
            esc = html.escape(joined, quote=True)
            body = "<br>".join(inline(b) for b in buf)
            out.append(f'<div class="script"><button class="copy" data-copy="{esc}">Copy</button>'
                       f'<div class="script-b">{body}</div></div>')
            continue
        if "|" in line and i + 1 < n and re.match(r"^\s*\|?[\s:|-]+\|", lines[i + 1]) and "---" in lines[i + 1]:
            header = [c.strip() for c in line.strip().strip("|").split("|")]
            i += 2
            rows = []
            while i < n and "|" in lines[i] and lines[i].strip():
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            th = "".join(f"<th>{inline(c)}</th>" for c in header)
            trs = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in rows)
            out.append(f'<table class="md"><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table>')
            continue
        cb = re.match(r"^\s*-\s+\[([ xX])\]\s+(.*)", line)
        if cb:
            buf = []
            while i < n and re.match(r"^\s*-\s+\[([ xX])\]\s+(.*)", lines[i]):
                mm = re.match(r"^\s*-\s+\[([ xX])\]\s+(.*)", lines[i])
                box = "☑" if mm.group(1).lower() == "x" else "☐"
                buf.append(f'<li class="check">{box} {inline(mm.group(2))}</li>')
                i += 1
            out.append('<ul class="checklist">' + "".join(buf) + "</ul>")
            continue
        if re.match(r"^\s*[-*]\s+", line):
            buf = []
            while i < n and re.match(r"^\s*[-*]\s+", lines[i]) and not re.match(r"^\s*-\s+\[", lines[i]):
                buf.append("<li>" + inline(re.sub(r"^\s*[-*]\s+", "", lines[i])) + "</li>")
                i += 1
            out.append("<ul>" + "".join(buf) + "</ul>")
            continue
        if re.match(r"^\s*\d+\.\s+", line):
            buf = []
            while i < n and re.match(r"^\s*\d+\.\s+", lines[i]):
                buf.append("<li>" + inline(re.sub(r"^\s*\d+\.\s+", "", lines[i])) + "</li>")
                i += 1
            out.append("<ol>" + "".join(buf) + "</ol>")
            continue
        if line.strip() == "":
            i += 1
            continue
        out.append("<p>" + inline(line) + "</p>")
        i += 1
    return "\n".join(out)


def badge(st):
    e, _, c = STATUS.get(st, ("❓", 99, "#475569"))
    return f'<span class="badge" style="background:{c}">{e} {html.escape(st)}</span>'


def icp_badge(v):
    e, c = ICP.get(v, ("⚪", "#94a3b8"))
    return f'<span class="icp" style="color:{c}">{e} {html.escape(v or "?")}</span>'


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--open", action="store_true")
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

    rows = ""
    for d in leads:
        rows += (f'<tr onclick="document.getElementById(\'{d["slug"]}\').scrollIntoView({{behavior:\'smooth\'}})">'
                 f'<td>{badge(d.get("status","new"))}</td><td><b>{html.escape(d.get("name",""))}</b></td>'
                 f'<td>{html.escape(d.get("firm","") or "—")}</td><td>{icp_badge(d.get("icp_fit","unknown"))}</td>'
                 f'<td>{html.escape(d.get("geo","") or "—")}</td><td>{html.escape(d.get("next_action","") or "—")}</td>'
                 f'<td>{html.escape(d.get("next_action_due","") or "—")}</td></tr>')

    cards = ""
    for d in leads:
        msg_html = ""
        for heading, msg in d["_msgs"]:
            esc_attr = html.escape(msg, quote=True)
            msg_html += (f'<div class="msg"><div class="msg-h">{html.escape(heading)}'
                         f'<button class="copy" data-copy="{esc_attr}">Copy</button></div>'
                         f'<div class="msg-b">{html.escape(msg)}</div></div>')
        li = d.get("linkedin", "")
        ig = d.get("instagram", "")
        link = f'<a href="{html.escape(li)}" target="_blank">LinkedIn ↗</a>' if li else ""
        iglink = f' · <a href="https://instagram.com/{html.escape(ig.lstrip("@"))}" target="_blank">IG ↗</a>' if ig and "CONFIRM" not in ig else ""
        cu = d.get("clickup", "")
        culink = f' · <a href="{html.escape(cu)}" target="_blank">ClickUp ↗</a>' if cu else ""
        hook = f'<p class="hook">🎯 {html.escape(d["_hook"])}</p>' if d.get("_hook") else ""
        nxt = (f'<p class="next"><b>Next:</b> {html.escape(d.get("next_action","") or "—")} '
               f'<span class="due">({html.escape(d.get("next_action_due","") or "")})</span></p>')
        cards += (f'<div class="card" id="{d["slug"]}"><div class="card-h">{badge(d.get("status","new"))} '
                  f'{icp_badge(d.get("icp_fit","unknown"))}<h2>{html.escape(d.get("name",""))}</h2>'
                  f'<span class="firm">{html.escape(d.get("firm","") or "")}</span>'
                  f'<span class="links">{link}{iglink}{culink} · <a href="threads/{d["_file"]}" target="_blank">thread .md ↗</a></span></div>'
                  f'{hook}{nxt}{msg_html}</div>')

    n = len(leads)
    counts = {}
    for d in leads:
        counts[d.get("status", "new")] = counts.get(d.get("status", "new"), 0) + 1
    summary = " · ".join(f'{STATUS.get(s,("❓",))[0]} {c} {s}'
                         for s, c in sorted(counts.items(), key=lambda kv: STATUS.get(kv[0], ("", 99))[1]))

    call_html = md_to_html(CALL_GUIDE.read_text(encoding="utf-8")) if CALL_GUIDE.exists() else "<p>No CALL-GUIDE.md</p>"
    play_html = md_to_html(PLAYBOOK.read_text(encoding="utf-8")) if PLAYBOOK.exists() else "<p>No SALES-PLAYBOOK.md</p>"

    page = f"""<!doctype html><html lang=en><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1"><title>Setu Warm Outreach</title><style>
:root{{--bg:#0f172a;--card:#1e293b;--mut:#94a3b8;--fg:#e2e8f0;--line:#334155;--accent:#60a5fa}}
*{{box-sizing:border-box}}body{{margin:0;font:15px/1.6 -apple-system,Segoe UI,Roboto,sans-serif;background:var(--bg);color:var(--fg)}}
header{{padding:20px 28px 0;border-bottom:1px solid var(--line);position:sticky;top:0;background:var(--bg);z-index:5}}
h1{{margin:0 0 4px;font-size:21px}}.sub{{color:var(--mut);font-size:13px;margin-bottom:14px}}
.tabs{{display:flex;gap:4px}}.tab{{padding:9px 18px;cursor:pointer;border:0;background:none;color:var(--mut);font-size:14px;font-weight:600;border-bottom:2px solid transparent}}
.tab.active{{color:var(--fg);border-bottom-color:var(--accent)}}
.wrap{{max-width:1040px;margin:0 auto;padding:24px 28px}}.panel{{display:none}}.panel.active{{display:block}}
table{{width:100%;border-collapse:collapse;font-size:13px;margin-bottom:28px}}
th,td{{text-align:left;padding:9px 10px;border-bottom:1px solid var(--line);vertical-align:top}}
th{{color:var(--mut);font-weight:600;text-transform:uppercase;font-size:11px;letter-spacing:.04em}}
tbody tr{{cursor:pointer}}tbody tr:hover{{background:#172033}}
.badge{{color:#fff;padding:2px 8px;border-radius:20px;font-size:11px;white-space:nowrap}}
.icp{{font-weight:600;font-size:12px;white-space:nowrap}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px 20px;margin-bottom:16px}}
.card-h{{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:6px}}
.card-h h2{{margin:0;font-size:18px}}.firm{{color:var(--mut)}}
.links{{margin-left:auto;font-size:12px}}.links a{{color:var(--accent);text-decoration:none;margin-left:8px}}
.hook{{color:#fcd34d;font-size:13px;margin:6px 0}}.next{{font-size:13px;margin:6px 0 12px}}.due{{color:var(--mut)}}
.msg,.script{{background:#0f1729;border:1px solid var(--line);border-radius:8px;margin:8px 0;overflow:hidden}}
.msg-h{{display:flex;align-items:center;justify-content:space-between;padding:7px 12px;background:#172033;font-size:12px;color:var(--mut);font-weight:600}}
.msg-b{{padding:10px 12px;font-size:14px;white-space:pre-wrap}}
.script{{position:relative;padding:12px 14px}}.script .copy{{position:absolute;top:8px;right:8px}}
.script-b{{font-size:14px;padding-right:60px;color:#dbeafe}}
.copy{{background:#2563eb;color:#fff;border:0;border-radius:6px;padding:4px 12px;font-size:12px;cursor:pointer}}
.copy:hover{{background:#1d4ed8}}.copy.ok{{background:#16a34a}}
.panel h1{{font-size:24px;margin:18px 0 8px}}.panel h2{{font-size:19px;margin:28px 0 8px;border-bottom:1px solid var(--line);padding-bottom:6px}}
.panel h3{{font-size:15px;margin:20px 0 6px;color:#fcd34d}}
.panel p{{margin:8px 0}}.panel ul,.panel ol{{margin:8px 0;padding-left:22px}}.panel li{{margin:3px 0}}
.checklist{{list-style:none;padding-left:4px}}.check{{color:var(--fg)}}
.panel code{{background:#0f1729;padding:1px 6px;border-radius:4px;font-size:13px}}
.panel a{{color:var(--accent)}}.panel hr{{border:0;border-top:1px solid var(--line);margin:20px 0}}
table.md{{font-size:13px}}table.md th{{background:#172033}}
.legend{{color:var(--mut);font-size:12px;margin:-10px 0 22px}}
</style></head><body>
<header><h1>📋 Setu Warm Outreach</h1><div class=sub>{n} leads · {summary}</div>
<div class=tabs>
<button class="tab active" data-t="board">Board</button>
<button class="tab" data-t="call">📞 Call Guide</button>
<button class="tab" data-t="play">📘 Playbook</button>
</div></header>
<div class="panel active" id="p-board"><div class=wrap>
<p class=legend>Click a row to jump to its card. Each message has a Copy button — comment first, then connect/DM. LinkedIn cap: 20–25 connects/day. Regenerate: <code>python dashboard/build_html.py --open</code></p>
<table><thead><tr><th>Status</th><th>Lead</th><th>Firm</th><th>ICP</th><th>Geo</th><th>Next action</th><th>Due</th></tr></thead><tbody>{rows}</tbody></table>
{cards}</div></div>
<div class="panel" id="p-call"><div class=wrap>{call_html}</div></div>
<div class="panel" id="p-play"><div class=wrap>{play_html}</div></div>
<script>
document.querySelectorAll('.tab').forEach(t=>t.addEventListener('click',()=>{{
 document.querySelectorAll('.tab').forEach(x=>x.classList.remove('active'));
 document.querySelectorAll('.panel').forEach(x=>x.classList.remove('active'));
 t.classList.add('active');
 document.getElementById('p-'+t.dataset.t).classList.add('active');
 window.scrollTo(0,0);
}}));
document.addEventListener('click',e=>{{
 const b=e.target.closest('.copy');if(!b)return;e.stopPropagation();
 navigator.clipboard.writeText(b.dataset.copy).then(()=>{{
  const t=b.textContent;b.textContent='Copied ✓';b.classList.add('ok');
  setTimeout(()=>{{b.textContent=t;b.classList.remove('ok')}},1400);
 }});
}});
</script></body></html>"""
    OUT.write_text(page, encoding="utf-8")
    print(f"Wrote {OUT} ({n} leads, 3 tabs)")
    if args.open:
        subprocess.run(["open", str(OUT)], check=False)


if __name__ == "__main__":
    main()
