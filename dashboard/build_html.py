#!/usr/bin/env python3
"""Render self-contained outreach dashboard from thread files.

    python dashboard/build_html.py [--open]

Produces dashboard/board.html — one local file (inline CSS/JS, no network deps).
"""
from __future__ import annotations
import argparse
import datetime
import html
import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent
THREADS = ROOT / "threads"
OUT = ROOT / "board.html"
CALL_GUIDE = ROOT / "CALL-GUIDE.md"
PLAYBOOK = ROOT / "SALES-PLAYBOOK.md"

TODAY = datetime.date.today().isoformat()

STATUS = {
    "converted":    ("✅ Converted",    0, "#10b981"),
    "call-booked":  ("🔥 Call booked",  1, "#ef4444"),
    "interested":   ("🌶️ Interested",   2, "#f97316"),
    "replied":      ("💬 Replied",       3, "#eab308"),
    "connected":    ("🤝 Connected",     4, "#06b6d4"),
    "connect-sent": ("📨 Sent",          5, "#3b82f6"),
    "engaging":     ("👀 Engaging",      6, "#8b5cf6"),
    "new":          ("🆕 New",           7, "#64748b"),
    "not-now":      ("⏳ Not now",       8, "#475569"),
    "dead":         ("⚰️ Dead",          9, "#334155"),
}
DEAD = {"dead", "not-now"}
ICP = {
    "strong":  ("🟢 Strong",  "#10b981"),
    "medium":  ("🟡 Medium",  "#eab308"),
    "weak":    ("🔴 Weak",    "#ef4444"),
    "unknown": ("⚪",         "#64748b"),
}
PAIN_LABEL = {
    "1": ("⚡ Pain #1 · Slow lead response",    "#f97316"),
    "2": ("💸 Pain #2 · Follow-up black hole",  "#eab308"),
    "3": ("🕐 Pain #3 · Senior time drain",     "#8b5cf6"),
}
CHANNEL_BTN = {
    "linkedin":  ('<a class="ch ch-li" href="{url}" target="_blank">🔗 LinkedIn</a>', "#0A66C2"),
    "instagram": ('<a class="ch ch-ig" href="https://instagram.com/{handle}" target="_blank">📷 Instagram</a>', "#E1306C"),
    "clickup":   ('<a class="ch ch-cu" href="{url}" target="_blank">CU</a>', "#7B68EE"),
    "thread":    ('<a class="ch ch-md" href="threads/{file}" target="_blank">thread ↗</a>', "#475569"),
}


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
            in_hook = True; continue
        if in_hook:
            if line.startswith("## "):
                in_hook = False
            elif line.strip() and not line.strip().startswith("<!--"):
                hook.append(line.strip())
    fm["_msgs"] = msgs
    fm["_hook"] = " ".join(hook)
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
            while i < n and "-->" not in lines[i]: i += 1
            i += 1; continue
        if line.startswith("```"):
            i += 1; buf = []
            while i < n and not lines[i].startswith("```"):
                buf.append(html.escape(lines[i])); i += 1
            i += 1
            out.append('<pre class="code">' + "\n".join(buf) + "</pre>"); continue
        h = re.match(r"^(#{1,6})\s+(.*)", line)
        if h:
            lvl = len(h.group(1))
            out.append(f"<h{lvl}>{inline(h.group(2).strip())}</h{lvl}>"); i += 1; continue
        if re.match(r"^---+\s*$", line):
            out.append("<hr>"); i += 1; continue
        if line.startswith(">"):
            buf = []
            while i < n and lines[i].startswith(">"):
                buf.append(lines[i].lstrip(">").strip()); i += 1
            esc = html.escape("\n".join(buf), quote=True)
            body = "<br>".join(inline(b) for b in buf)
            out.append(f'<div class="script"><button class="copy" data-copy="{esc}">Copy</button>'
                       f'<div class="script-b">{body}</div></div>'); continue
        if "|" in line and i + 1 < n and re.match(r"^\s*[|]?[\s:|-]+[|]", lines[i+1]) and "---" in lines[i+1]:
            header = [c.strip() for c in line.strip().strip("|").split("|")]
            i += 2; rows = []
            while i < n and "|" in lines[i] and lines[i].strip():
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")]); i += 1
            th = "".join(f"<th>{inline(c)}</th>" for c in header)
            trs = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in rows)
            out.append(f'<table class="md"><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table>'); continue
        if re.match(r"^\s*[-*]\s+", line):
            buf = []
            while i < n and re.match(r"^\s*[-*]\s+", lines[i]):
                buf.append("<li>" + inline(re.sub(r"^\s*[-*]\s+", "", lines[i])) + "</li>"); i += 1
            out.append("<ul>" + "".join(buf) + "</ul>"); continue
        if re.match(r"^\s*\d+\.\s+", line):
            buf = []
            while i < n and re.match(r"^\s*\d+\.\s+", lines[i]):
                buf.append("<li>" + inline(re.sub(r"^\s*\d+\.\s+", "", lines[i])) + "</li>"); i += 1
            out.append("<ol>" + "".join(buf) + "</ol>"); continue
        if line.strip() == "":
            i += 1; continue
        out.append("<p>" + inline(line) + "</p>"); i += 1
    return "\n".join(out)


def due_class(due: str) -> str:
    if not due: return ""
    try:
        d = datetime.date.fromisoformat(due)
        today = datetime.date.today()
        if d < today: return "due-overdue"
        if d == today: return "due-today"
    except ValueError: pass
    return "due-future"


def channel_html(d: dict, file: str) -> str:
    parts = []
    li = d.get("linkedin", "")
    ig = d.get("instagram", "")
    cu = d.get("clickup", "")
    if li and "UNVERIFIED" not in li:
        parts.append(f'<a class="ch ch-li" href="{html.escape(li)}" target="_blank">🔗 LinkedIn</a>')
    elif li and "UNVERIFIED" in li:
        parts.append('<span class="ch ch-warn" title="Find profile before sending">🔗 LI ⚠️</span>')
    if ig and "UNVERIFIED" not in ig:
        handle = ig.lstrip("@")
        parts.append(f'<a class="ch ch-ig" href="https://instagram.com/{html.escape(handle)}" target="_blank">📷 @{html.escape(handle)}</a>')
    elif ig and "UNVERIFIED" in ig:
        parts.append('<span class="ch ch-warn" title="Confirm IG handle before commenting">📷 IG ⚠️</span>')
    if cu:
        parts.append(f'<a class="ch ch-cu" href="{html.escape(cu)}" target="_blank">CU</a>')
    parts.append(f'<a class="ch ch-md" href="threads/{html.escape(file)}" target="_blank">md ↗</a>')
    return "".join(parts)


def build_card(d: dict) -> str:
    st = d.get("status", "new")
    label, _, color = STATUS.get(st, ("❓", 99, "#475569"))
    icp_v = d.get("icp_fit", "unknown")
    icp_lbl, icp_c = ICP.get(icp_v, ("⚪", "#64748b"))
    geo = d.get("geo", "")
    pain_v = d.get("pain_target", "")
    pain_html = ""
    if pain_v in PAIN_LABEL:
        plbl, pc = PAIN_LABEL[pain_v]
        pain_html = f'<span class="pain-tag" style="color:{pc};border-color:{pc}">{plbl}</span>'

    due = d.get("next_action_due", "")
    dc = due_class(due)
    due_badge = ""
    if dc == "due-overdue":
        due_badge = f'<span class="due-chip due-overdue">⚠️ OVERDUE · {html.escape(due)}</span>'
    elif dc == "due-today":
        due_badge = f'<span class="due-chip due-today">🎯 TODAY · {html.escape(due)}</span>'
    elif due:
        due_badge = f'<span class="due-chip due-future">{html.escape(due)}</span>'

    channels = channel_html(d, d.get("_file", ""))
    hook = d.get("_hook", "")
    next_a = d.get("next_action", "")

    msg_html = ""
    for heading, msg in d.get("_msgs", []):
        esc = html.escape(msg, quote=True)
        step_num = ""
        sm = re.match(r"^Step\s*(\d+)", heading, re.IGNORECASE)
        if sm:
            step_num = f'<span class="step-num">Step {sm.group(1)}</span>'
        msg_html += (
            f'<div class="msg-block">'
            f'<div class="msg-hdr">{step_num}<span class="msg-label">{html.escape(heading)}</span>'
            f'<button class="copy" data-copy="{esc}">Copy</button></div>'
            f'<div class="msg-body">{html.escape(msg)}</div>'
            f'</div>'
        )

    is_new = st in {"new", "engaging"}
    msgs_open = "open" if is_new else ""

    return (
        f'<div class="card" id="{d["slug"]}" data-status="{html.escape(st)}" '
        f'data-geo="{html.escape(geo)}" data-icp="{html.escape(icp_v)}">'
        f'<div class="card-stripe" style="background:{color}"></div>'
        f'<div class="card-inner">'
        # row 1: tags + channels
        f'<div class="card-row1">'
        f'<div class="card-tags">'
        f'<span class="status-badge" style="background:{color}">{html.escape(label)}</span>'
        f'<span class="icp-badge" style="color:{icp_c}">{html.escape(icp_lbl)}</span>'
        f'{"<span class='geo-tag'>" + html.escape(geo) + "</span>" if geo else ""}'
        f'</div>'
        f'<div class="card-channels">{channels}</div>'
        f'</div>'
        # row 2: name + firm
        f'<div class="card-row2">'
        f'<div>'
        f'<h2 class="card-name">{html.escape(d.get("name",""))}</h2>'
        f'<div class="card-firm">{html.escape(d.get("firm","") or "")} · {html.escape(d.get("role","") or "")}</div>'
        f'</div>'
        f'</div>'
        # pain tag
        + (f'<div class="pain-row">{pain_html}</div>' if pain_html else "")
        # hook
        + (f'<div class="card-hook">🎯 {html.escape(hook)}</div>' if hook else "")
        # next action
        + (f'<div class="card-next"><span class="next-label">Next →</span> {html.escape(next_a)} {due_badge}</div>' if next_a else "")
        # messages
        + (f'<details class="msgs-toggle" {msgs_open}>'
           f'<summary class="msgs-summary">{len(d.get("_msgs",[]))} message{"s" if len(d.get("_msgs",[])) != 1 else ""}</summary>'
           f'<div class="msgs-inner">{msg_html}</div>'
           f'</details>' if msg_html else "")
        + '</div></div>'
    )


def build_table_row(d: dict) -> str:
    st = d.get("status", "new")
    label, _, color = STATUS.get(st, ("❓", 99, "#475569"))
    due = d.get("next_action_due", "")
    dc = due_class(due)
    due_cell = html.escape(due)
    if dc == "due-overdue":
        due_cell = f'<span style="color:#ef4444;font-weight:700">⚠️ {html.escape(due)}</span>'
    elif dc == "due-today":
        due_cell = f'<span style="color:#f97316;font-weight:700">🎯 {html.escape(due)}</span>'

    li = d.get("linkedin", "")
    ig = d.get("instagram", "")
    ch_icons = []
    if li and "UNVERIFIED" not in li:
        ch_icons.append(f'<a class="tbl-ch li" href="{html.escape(li)}" target="_blank">LI</a>')
    elif li and "UNVERIFIED" in li:
        ch_icons.append('<span class="tbl-ch warn" title="Unverified">LI⚠</span>')
    if ig and "UNVERIFIED" not in ig:
        ch_icons.append(f'<a class="tbl-ch ig" href="https://instagram.com/{html.escape(ig.lstrip("@"))}" target="_blank">IG</a>')
    elif ig and "UNVERIFIED" in ig:
        ch_icons.append('<span class="tbl-ch warn" title="Unverified">IG⚠</span>')

    slug = d.get("slug", "")
    next_a = (d.get("next_action", "") or "")[:80] + ("…" if len(d.get("next_action","") or "") > 80 else "")

    return (
        f'<tr class="tbl-row" onclick="jumpTo(\'{slug}\')">'
        f'<td><span class="tbl-badge" style="background:{color}">{html.escape(label)}</span></td>'
        f'<td><b>{html.escape(d.get("name",""))}</b><br><span class="tbl-firm">{html.escape(d.get("firm","") or "")}</span></td>'
        f'<td>{"".join(ch_icons) or "—"}</td>'
        f'<td class="tbl-next">{html.escape(next_a)}</td>'
        f'<td class="tbl-due">{due_cell}</td>'
        f'</tr>'
    )


def build_pipeline(leads: list[dict]) -> str:
    stages = ["converted","call-booked","interested","replied","connected","connect-sent","engaging","new"]
    counts = {}
    for d in leads:
        s = d.get("status","new")
        if s not in DEAD:
            counts[s] = counts.get(s, 0) + 1
    parts = []
    for s in stages:
        c = counts.get(s, 0)
        if c == 0: continue
        lbl, _, col = STATUS[s]
        parts.append(
            f'<button class="pipe-stage" data-filter-status="{s}" style="--sc:{col}">'
            f'<span class="pipe-count" style="color:{col}">{c}</span>'
            f'<span class="pipe-label">{html.escape(lbl)}</span>'
            f'</button>'
        )
    if not parts: return ""
    return '<div class="pipeline">' + '<span class="pipe-arrow">›</span>'.join(parts) + '</div>'


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--open", action="store_true")
    args = ap.parse_args()

    all_leads = []
    for f in sorted(THREADS.glob("*.md")):
        fm = parse(f.read_text(encoding="utf-8"))
        if not fm.get("name"): continue
        fm["_file"] = f.name
        st = fm.get("status", "new")
        fm["_rank"] = STATUS.get(st, ("", 99, ""))[1]
        fm["_icp_rank"] = {"strong": 0, "medium": 1, "weak": 2}.get(fm.get("icp_fit", ""), 3)
        all_leads.append(fm)
    all_leads.sort(key=lambda d: (d["_rank"], d["_icp_rank"], d.get("name", "")))

    active = [d for d in all_leads if d.get("status", "new") not in DEAD]
    dead   = [d for d in all_leads if d.get("status", "new") in DEAD]

    counts = {}
    for d in all_leads:
        s = d.get("status","new"); counts[s] = counts.get(s, 0) + 1
    summary_parts = []
    for s, c in sorted(counts.items(), key=lambda kv: STATUS.get(kv[0],("",99,""))[1]):
        lbl = STATUS.get(s, ("❓",))[0]; summary_parts.append(f"{lbl} {c}")
    summary = "  ·  ".join(summary_parts)

    pipeline_html = build_pipeline(all_leads)
    active_rows   = "".join(build_table_row(d) for d in active)
    dead_rows     = "".join(build_table_row(d) for d in dead)
    active_cards  = "".join(build_card(d) for d in active)
    dead_cards    = "".join(build_card(d) for d in dead)

    call_html = md_to_html(CALL_GUIDE.read_text(encoding="utf-8")) if CALL_GUIDE.exists() else "<p>No CALL-GUIDE.md</p>"
    play_html = md_to_html(PLAYBOOK.read_text(encoding="utf-8")) if PLAYBOOK.exists() else "<p>No SALES-PLAYBOOK.md</p>"

    geos = sorted({d.get("geo","") for d in all_leads if d.get("geo","")})
    geo_filters = "".join(f'<button class="flt" data-geo="{g}">{html.escape(g)}</button>' for g in geos)

    page = f"""<!doctype html><html lang=en><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1"><title>Setu Outreach</title><style>
:root{{
  --bg:#080d18;--surface:#0d1526;--card:#111d30;--card-h:#16253e;
  --border:#1e2d45;--mut:#4a6080;--fg:#dce7f5;--accent:#3b82f6;
  --green:#10b981;--yellow:#eab308;--orange:#f97316;--red:#ef4444;
  --purple:#8b5cf6;--cyan:#06b6d4;--li:#0A66C2;--ig:#E1306C;--cu:#7B68EE;
}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font:14px/1.6 -apple-system,Segoe UI,Roboto,sans-serif;background:var(--bg);color:var(--fg)}}
a{{color:var(--accent);text-decoration:none}}a:hover{{text-decoration:underline}}
code{{background:#0a1020;padding:1px 5px;border-radius:4px;font-size:12px}}

/* ── HEADER ── */
#hdr{{position:sticky;top:0;z-index:10;background:var(--bg);border-bottom:1px solid var(--border);padding:14px 24px 0}}
.hdr-top{{display:flex;align-items:baseline;gap:12px;margin-bottom:10px}}
.hdr-top h1{{font-size:18px;font-weight:700;color:var(--fg)}}
.hdr-sub{{color:var(--mut);font-size:12px}}
.hdr-regen{{margin-left:auto;color:var(--mut);font-size:11px;font-family:monospace}}

/* ── PIPELINE BAR ── */
.pipeline{{display:flex;align-items:center;gap:4px;margin-bottom:10px;flex-wrap:wrap}}
.pipe-stage{{
  display:flex;flex-direction:column;align-items:center;
  background:var(--surface);border:1px solid var(--border);border-radius:8px;
  padding:5px 12px;cursor:pointer;transition:all .15s;min-width:64px;
  border-bottom:2px solid var(--sc,var(--border));
}}
.pipe-stage:hover,.pipe-stage.active{{background:var(--card-h);border-color:var(--sc,var(--accent))}}
.pipe-count{{font-size:20px;font-weight:800;line-height:1}}
.pipe-label{{font-size:10px;color:var(--mut);white-space:nowrap;margin-top:2px}}
.pipe-arrow{{color:var(--mut);font-size:18px;padding:0 2px}}

/* ── TABS ── */
.tab-row{{display:flex;gap:2px}}
.tab{{padding:8px 16px;cursor:pointer;border:0;background:none;color:var(--mut);font-size:13px;font-weight:600;border-bottom:2px solid transparent}}
.tab.active{{color:var(--fg);border-bottom-color:var(--accent)}}

/* ── PANELS ── */
.panel{{display:none}}.panel.on{{display:block}}
.wrap{{max-width:1060px;margin:0 auto;padding:20px 24px}}

/* ── FILTER BAR ── */
.filter-bar{{display:flex;align-items:center;gap:6px;margin-bottom:16px;flex-wrap:wrap}}
.flt{{
  padding:4px 12px;border-radius:20px;border:1px solid var(--border);
  background:var(--surface);color:var(--mut);font-size:12px;cursor:pointer;
}}
.flt:hover,.flt.active{{background:var(--accent);color:#fff;border-color:var(--accent)}}
.flt-label{{color:var(--mut);font-size:12px;margin-right:4px}}

/* ── TABLE ── */
.lead-table{{width:100%;border-collapse:collapse;font-size:12px;margin-bottom:24px}}
.lead-table th{{
  text-align:left;padding:7px 8px;border-bottom:2px solid var(--border);
  color:var(--mut);font-weight:600;text-transform:uppercase;font-size:10px;letter-spacing:.06em;
}}
.tbl-row{{cursor:pointer;border-bottom:1px solid var(--border)}}
.tbl-row:hover{{background:var(--surface)}}
.tbl-row td{{padding:8px 8px;vertical-align:top}}
.tbl-badge{{
  display:inline-block;padding:2px 8px;border-radius:12px;color:#fff;
  font-size:10px;font-weight:600;white-space:nowrap;
}}
.tbl-firm{{color:var(--mut);font-size:11px}}
.tbl-next{{color:var(--fg);max-width:320px}}
.tbl-due{{white-space:nowrap;font-size:11px}}
.tbl-ch{{
  display:inline-block;padding:2px 6px;border-radius:4px;font-size:10px;
  font-weight:700;margin-right:3px;text-decoration:none;color:#fff;
}}
.tbl-ch.li{{background:var(--li)}}
.tbl-ch.ig{{background:var(--ig)}}
.tbl-ch.warn{{background:#374151;color:var(--yellow)}}

/* ── CARDS ── */
.cards-section,.dead-section{{margin-top:8px}}
.card{{
  display:flex;margin-bottom:12px;border-radius:10px;overflow:hidden;
  border:1px solid var(--border);background:var(--card);
}}
.card[data-status="dead"],.card[data-status="not-now"]{{opacity:.65}}
.card-stripe{{width:5px;flex-shrink:0}}
.card-inner{{flex:1;padding:14px 16px}}
.card-row1{{display:flex;align-items:flex-start;gap:8px;flex-wrap:wrap;margin-bottom:8px}}
.card-tags{{display:flex;align-items:center;gap:6px;flex-wrap:wrap;flex:1}}
.status-badge{{
  display:inline-block;padding:3px 10px;border-radius:12px;color:#fff;
  font-size:11px;font-weight:600;white-space:nowrap;
}}
.icp-badge{{font-size:12px;font-weight:700}}
.geo-tag{{
  font-size:11px;color:var(--mut);background:var(--surface);
  padding:2px 7px;border-radius:10px;border:1px solid var(--border);
}}
.card-channels{{display:flex;gap:5px;flex-wrap:wrap;align-items:center;margin-left:auto}}
.ch{{
  display:inline-block;padding:4px 10px;border-radius:6px;font-size:11px;
  font-weight:600;color:#fff;text-decoration:none;white-space:nowrap;
}}
.ch:hover{{filter:brightness(1.15);text-decoration:none}}
.ch-li{{background:var(--li)}}
.ch-ig{{background:linear-gradient(135deg,#f09433,#e6683c,#dc2743,#cc2366,#bc1888)}}
.ch-cu{{background:var(--cu)}}
.ch-md{{background:var(--surface);color:var(--mut);border:1px solid var(--border)}}
.ch-warn{{background:#1e2d45;color:var(--yellow);border:1px dashed var(--yellow);cursor:default}}
.card-row2{{margin-bottom:6px}}
.card-name{{font-size:17px;font-weight:700;color:var(--fg);margin-bottom:1px}}
.card-firm{{font-size:12px;color:var(--mut)}}
.pain-row{{margin:6px 0}}
.pain-tag{{
  display:inline-block;font-size:11px;font-weight:600;
  padding:2px 10px;border-radius:12px;border:1px solid;
}}
.card-hook{{
  font-size:12px;color:#fcd34d;
  background:rgba(252,211,77,.07);border-left:2px solid rgba(252,211,77,.4);
  padding:6px 10px;border-radius:0 6px 6px 0;margin:8px 0;
}}
.card-next{{
  font-size:13px;padding:8px 12px;border-radius:6px;margin:8px 0;
  background:var(--surface);border-left:3px solid var(--border);
}}
.card-next .next-label{{font-weight:700;color:var(--mut)}}
.due-chip{{
  display:inline-block;font-size:10px;font-weight:700;
  padding:1px 7px;border-radius:8px;margin-left:6px;vertical-align:middle;
}}
.due-chip.due-overdue{{background:rgba(239,68,68,.2);color:var(--red)}}
.due-chip.due-today{{background:rgba(249,115,22,.2);color:var(--orange)}}
.due-chip.due-future{{background:var(--surface);color:var(--mut);border:1px solid var(--border)}}

/* ── MESSAGES ── */
.msgs-toggle{{margin-top:10px}}
.msgs-summary{{
  cursor:pointer;font-size:12px;font-weight:600;color:var(--mut);
  padding:5px 0;list-style:none;user-select:none;
}}
.msgs-summary:hover{{color:var(--fg)}}
.msgs-summary::marker,.msgs-summary::-webkit-details-marker{{display:none}}
.msgs-summary::before{{content:"▶ ";font-size:9px}}
details[open] .msgs-summary::before{{content:"▼ "}}
.msgs-inner{{margin-top:8px;display:flex;flex-direction:column;gap:8px}}
.msg-block{{background:var(--surface);border:1px solid var(--border);border-radius:7px;overflow:hidden}}
.msg-hdr{{
  display:flex;align-items:center;gap:6px;padding:6px 10px;
  background:var(--card-h);border-bottom:1px solid var(--border);
}}
.step-num{{
  font-size:10px;font-weight:800;color:#fff;background:var(--accent);
  padding:1px 6px;border-radius:8px;flex-shrink:0;
}}
.msg-label{{font-size:11px;color:var(--mut);flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
.msg-body{{padding:10px 12px;font-size:13px;white-space:pre-wrap;color:var(--fg);line-height:1.55}}
.copy{{
  margin-left:auto;flex-shrink:0;background:var(--accent);color:#fff;
  border:0;border-radius:5px;padding:3px 10px;font-size:11px;cursor:pointer;
}}
.copy:hover{{background:#2563eb}}.copy.ok{{background:var(--green)}}

/* ── DEAD SECTION ── */
.dead-section{{margin-top:24px}}
.dead-section > summary{{
  cursor:pointer;color:var(--mut);font-size:12px;font-weight:600;
  padding:8px 0;border-top:1px solid var(--border);list-style:none;
}}
.dead-section > summary::before{{content:"▶  "}}
details.dead-section[open] > summary::before{{content:"▼  "}}

/* ── GUIDE / PLAYBOOK PANELS ── */
.wrap h1{{font-size:22px;margin:16px 0 8px}}
.wrap h2{{font-size:17px;margin:24px 0 6px;border-bottom:1px solid var(--border);padding-bottom:4px}}
.wrap h3{{font-size:14px;margin:18px 0 4px;color:#fcd34d}}
.wrap p{{margin:6px 0}}.wrap ul,.wrap ol{{margin:6px 0;padding-left:20px}}.wrap li{{margin:2px 0}}
.wrap hr{{border:0;border-top:1px solid var(--border);margin:18px 0}}
.script{{position:relative;background:var(--surface);border:1px solid var(--border);border-radius:7px;padding:12px 50px 12px 14px;margin:8px 0}}
.script .copy{{position:absolute;top:8px;right:8px}}
.script-b{{font-size:13px;color:#dbeafe;white-space:pre-wrap}}
table.md{{font-size:12px;width:100%;border-collapse:collapse;margin:10px 0}}
table.md th,table.md td{{text-align:left;padding:6px 8px;border-bottom:1px solid var(--border)}}
table.md th{{background:var(--card-h);color:var(--mut)}}
pre.code{{background:var(--surface);padding:10px 14px;border-radius:6px;font-size:12px;overflow-x:auto}}
</style></head><body>
<div id="hdr">
  <div class="hdr-top">
    <h1>Setu Outreach</h1>
    <div class="hdr-sub">{len(all_leads)} leads total · {len(active)} active · {len(dead)} parked</div>
    <div class="hdr-regen">python dashboard/build_html.py --open</div>
  </div>
  <div class="hdr-top" style="margin-bottom:6px"><span style="color:var(--mut);font-size:11px">{summary}</span></div>
  {pipeline_html}
  <div class="tab-row">
    <button class="tab active" data-t="board">📋 Board</button>
    <button class="tab" data-t="call">📞 Call Guide</button>
    <button class="tab" data-t="play">📘 Playbook</button>
  </div>
</div>

<div class="panel on" id="p-board"><div class="wrap">
  <div class="filter-bar">
    <span class="flt-label">Filter:</span>
    <button class="flt active" data-all>All</button>
    <button class="flt" data-icp="strong">🟢 Strong ICP</button>
    {geo_filters}
    <button class="flt" data-channel="instagram">📷 IG leads</button>
  </div>
  <table class="lead-table">
    <thead><tr><th>Status</th><th>Name · Firm</th><th>Channels</th><th>Next action</th><th>Due</th></tr></thead>
    <tbody id="tbl-body">{active_rows}</tbody>
  </table>
  <div class="cards-section" id="active-cards">{active_cards}</div>
  <details class="dead-section">
    <summary>⚰️ Parked / Dead · {len(dead)} leads</summary>
    <div style="margin-top:10px">
      <table class="lead-table"><thead><tr><th>Status</th><th>Name · Firm</th><th>Channels</th><th>Next action</th><th>Due</th></tr></thead><tbody>{dead_rows}</tbody></table>
      {dead_cards}
    </div>
  </details>
</div></div>

<div class="panel" id="p-call"><div class="wrap">{call_html}</div></div>
<div class="panel" id="p-play"><div class="wrap">{play_html}</div></div>

<script>
const TODAY = "{TODAY}";

// tabs
document.querySelectorAll('.tab').forEach(t => t.addEventListener('click', () => {{
  document.querySelectorAll('.tab').forEach(x => x.classList.remove('active'));
  document.querySelectorAll('.panel').forEach(x => x.classList.remove('on'));
  t.classList.add('active');
  document.getElementById('p-' + t.dataset.t).classList.add('on');
  window.scrollTo(0,0);
}}));

// copy buttons
document.addEventListener('click', e => {{
  const b = e.target.closest('.copy'); if (!b) return; e.stopPropagation();
  navigator.clipboard.writeText(b.dataset.copy).then(() => {{
    const t = b.textContent; b.textContent = 'Copied ✓'; b.classList.add('ok');
    setTimeout(() => {{ b.textContent = t; b.classList.remove('ok'); }}, 1400);
  }});
}});

// jump to card on row click
function jumpTo(slug) {{
  const el = document.getElementById(slug);
  if (el) {{ el.scrollIntoView({{behavior:'smooth',block:'start'}}); }}
}}

// pipeline filter
let activeStatus = null;
document.querySelectorAll('.pipe-stage').forEach(btn => {{
  btn.addEventListener('click', () => {{
    const s = btn.dataset.filterStatus;
    if (activeStatus === s) {{ activeStatus = null; clearFilter(); }}
    else {{ activeStatus = s; filterByStatus(s); }}
    document.querySelectorAll('.pipe-stage').forEach(b => b.classList.toggle('active', b.dataset.filterStatus === activeStatus));
  }});
}});
function filterByStatus(s) {{
  document.querySelectorAll('.card').forEach(c => {{
    c.style.display = (c.dataset.status === s) ? '' : 'none';
  }});
  document.querySelectorAll('.tbl-row').forEach(r => {{
    r.style.display = (r.dataset && r.dataset.status === s) ? '' : 'none';
  }});
}}
function clearFilter() {{
  document.querySelectorAll('.card,.tbl-row').forEach(el => el.style.display = '');
  applyFilters();
}}

// tag filters
let activeGeo = null, activeIcp = null, activeChannel = null;
document.querySelectorAll('.flt').forEach(btn => {{
  btn.addEventListener('click', () => {{
    if ('all' in btn.dataset) {{
      activeGeo = null; activeIcp = null; activeChannel = null;
      document.querySelectorAll('.flt').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
    }} else if (btn.dataset.geo) {{
      activeGeo = (activeGeo === btn.dataset.geo) ? null : btn.dataset.geo;
    }} else if (btn.dataset.icp) {{
      activeIcp = (activeIcp === btn.dataset.icp) ? null : btn.dataset.icp;
    }} else if (btn.dataset.channel) {{
      activeChannel = (activeChannel === btn.dataset.channel) ? null : btn.dataset.channel;
    }}
    document.querySelectorAll('.flt:not([data-all])').forEach(b => {{
      b.classList.toggle('active',
        (b.dataset.geo && b.dataset.geo === activeGeo) ||
        (b.dataset.icp && b.dataset.icp === activeIcp) ||
        (b.dataset.channel && b.dataset.channel === activeChannel)
      );
    }});
    if (!activeGeo && !activeIcp && !activeChannel) {{
      document.querySelector('.flt[data-all]').classList.add('active');
    }} else {{
      document.querySelector('.flt[data-all]').classList.remove('active');
    }}
    applyFilters();
  }});
}});

function applyFilters() {{
  activeStatus = null;
  document.querySelectorAll('.pipe-stage').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.card').forEach(c => {{
    const geoOk  = !activeGeo  || c.dataset.geo  === activeGeo;
    const icpOk  = !activeIcp  || c.dataset.icp  === activeIcp;
    const chOk   = !activeChannel || c.querySelector('.ch-ig') !== null;
    c.style.display = (geoOk && icpOk && chOk) ? '' : 'none';
  }});
  document.querySelectorAll('.tbl-row').forEach(r => {{
    const geoOk  = !activeGeo  || r.dataset.geo  === activeGeo;
    const icpOk  = !activeIcp  || r.dataset.icp  === activeIcp;
    r.style.display = (geoOk && icpOk) ? '' : 'none';
  }});
}}

// stamp geo+icp onto table rows from card data-attrs (cards already have them)
document.querySelectorAll('.tbl-row').forEach((r, i) => {{
  const slug = r.getAttribute('onclick')?.match(/jumpTo[(]'([^']+)'[)]/)?.[1];
  if (slug) {{
    const card = document.getElementById(slug);
    if (card) {{ r.dataset.geo = card.dataset.geo; r.dataset.icp = card.dataset.icp; }}
  }}
}});
</script></body></html>"""

    OUT.write_text(page, encoding="utf-8")
    print(f"✓ Wrote {OUT}  ({len(all_leads)} leads — {len(active)} active, {len(dead)} parked)")
    if args.open:
        subprocess.run(["open", str(OUT)], check=False)


if __name__ == "__main__":
    main()
