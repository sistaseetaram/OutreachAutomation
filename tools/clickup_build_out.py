#!/usr/bin/env python3
"""
clickup_build_out.py — one-time ClickUp structure builder (Free-plan safe).

Creates: Space 'Setu — Outreach & Clients' with pipeline STATUSES, Lists (Leads, Engaged Clients),
6 custom fields on Leads, and space TAGS. Prints IDs so you paste CLICKUP_LEADS_LIST_ID into
credentials/.env. Then optionally seeds leads from lead_tracker store.

Free-plan guards: native statuses + tags do the heavy lifting; exactly 6 custom fields (<60-use cap);
no ClickUp automations (cadence runs in lead_tracker.py).

Usage:
    python tools/clickup_build_out.py            # dry-run (prints structure) if no token
    python tools/clickup_build_out.py --create   # create live (needs CLICKUP_API_TOKEN)
    python tools/clickup_build_out.py --seed      # push lead_tracker leads into Leads list
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

_CRED_ENV = Path(__file__).resolve().parent.parent / "credentials" / ".env"
load_dotenv(_CRED_ENV if _CRED_ENV.exists() else None)

TOKEN = os.getenv("CLICKUP_API_TOKEN")
TEAM_ID = os.getenv("CLICKUP_TEAM_ID")
BASE = "https://api.clickup.com/api/v2"

SPACE_NAME = "Setu — Outreach & Clients"
LISTS = ["Leads", "Engaged Clients"]

# (name, type) — first open, last done/closed
STATUSES = [
    ("Sourced", "open"), ("Researched", "custom"), ("Queued", "custom"), ("Contacted", "custom"),
    ("Follow-up 1", "custom"), ("Follow-up 2", "custom"), ("Follow-up 3", "custom"),
    ("Follow-up 4", "custom"), ("Replied", "custom"), ("Diagnosis Booked", "custom"),
    ("Free Build", "custom"), ("Delivered", "custom"), ("Testimonial/Referral", "custom"),
    ("Nurture", "custom"), ("Won", "done"), ("Lost", "closed"),
]
TAGS = ["warm", "cold", "interior", "architecture", "construction", "NRI", "founding-client"]
# 6 custom fields (<60-use cap)
FIELDS = [
    ("LinkedIn URL", "url"), ("Instagram", "url"), ("Email", "email"),
    ("Drive Folder", "url"), ("Follow-up count", "number"),
    ("Source", "drop_down"),
]
SOURCE_OPTIONS = ["apollo", "instagram", "maps", "justdial", "salesnav", "referral", "manual"]


def H():
    return {"Authorization": TOKEN, "Content-Type": "application/json"}


def structure_text() -> str:
    lines = [f"Space: {SPACE_NAME}",
             f"  Lists: {', '.join(LISTS)}",
             f"  Statuses ({len(STATUSES)}): " + " → ".join(s for s, _ in STATUSES),
             f"  Tags: {', '.join(TAGS)}",
             "  Custom fields (6): " + ", ".join(f"{n}[{t}]" for n, t in FIELDS),
             f"    Source options: {', '.join(SOURCE_OPTIONS)}",
             "  Automations: NONE (cadence runs in lead_tracker.py — avoids Free 100/mo cap)"]
    return "\n".join(lines)


def get_team_id() -> str:
    if TEAM_ID:
        return TEAM_ID
    r = requests.get(f"{BASE}/team", headers=H(), timeout=20)
    r.raise_for_status()
    teams = r.json().get("teams", [])
    if not teams:
        raise RuntimeError("No ClickUp teams found for this token.")
    return teams[0]["id"]


def create():
    team = get_team_id()
    print(f"team_id: {team}")
    # space with statuses
    body = {"name": SPACE_NAME,
            "multiple_assignees": False,
            "features": {"due_dates": {"enabled": True}, "tags": {"enabled": True},
                         "custom_fields": {"enabled": True}},
            "statuses": [{"status": s, "type": t} for s, t in STATUSES]}
    r = requests.post(f"{BASE}/team/{team}/space", headers=H(), json=body, timeout=30)
    if not r.ok:
        print(f"  [space create: {r.status_code} {r.text[:200]}] — may already exist; continuing")
    space_id = r.json().get("id") if r.ok else None
    if not space_id:
        # try to find existing
        sp = requests.get(f"{BASE}/team/{team}/space", headers=H(), timeout=20).json().get("spaces", [])
        space_id = next((s["id"] for s in sp if s["name"] == SPACE_NAME), None)
    print(f"space_id: {space_id}")

    list_ids = {}
    for ln in LISTS:
        lr = requests.post(f"{BASE}/space/{space_id}/list", headers=H(), json={"name": ln}, timeout=20)
        if lr.ok:
            list_ids[ln] = lr.json()["id"]
        print(f"  list '{ln}': {lr.status_code} {list_ids.get(ln, lr.text[:120])}")

    # tags
    for t in TAGS:
        requests.post(f"{BASE}/space/{space_id}/tag", headers=H(),
                      json={"tag": {"name": t}}, timeout=15)

    # custom fields on Leads
    leads_id = list_ids.get("Leads")
    if leads_id:
        for name, ftype in FIELDS:
            payload = {"name": name, "type": ftype}
            if ftype == "drop_down":
                payload["type_config"] = {"options": [{"name": o} for o in SOURCE_OPTIONS]}
            fr = requests.post(f"{BASE}/list/{leads_id}/field", headers=H(), json=payload, timeout=20)
            print(f"    field '{name}': {fr.status_code}")
    print("\nDONE. Paste into credentials/.env:")
    print(f"  CLICKUP_TEAM_ID={team}")
    print(f"  CLICKUP_LEADS_LIST_ID={leads_id}")


def seed():
    import lead_tracker as lt
    import clickup_sync as cu
    leads = lt.load()
    list_id = os.getenv("CLICKUP_LEADS_LIST_ID")
    if not (TOKEN and list_id):
        print("[DRY-RUN] would seed these leads into ClickUp Leads list:")
        for s, r in leads.items():
            print(f"  • {r['studio']} @ {r.get('status')} [{r.get('track')}/{r.get('segment')}]")
        return
    for s, r in leads.items():
        tags = [r.get("track"), r.get("segment")] + ([r["city"].lower()] if r.get("city") else [])
        res = cu.upsert_lead(list_id, r["studio"], r.get("status"), [t for t in tags if t],
                             {"LinkedIn URL": r.get("linkedin"), "Instagram": r.get("instagram"),
                              "Email": r.get("email"), "Drive Folder": r.get("drive_folder"),
                              "Source": r.get("source"), "Follow-up count": r.get("followups")})
        print(f"  {r['studio']}: {res}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--create", action="store_true")
    ap.add_argument("--seed", action="store_true")
    args = ap.parse_args()

    if not TOKEN:
        print("[DRY-RUN] CLICKUP_API_TOKEN not set — would create this structure:\n")
        print(structure_text())
        print("\nAdd CLICKUP_API_TOKEN (+ CLICKUP_TEAM_ID optional) to credentials/.env, then --create.")
        if args.seed:
            seed()
        return

    if args.create:
        create()
    elif args.seed:
        seed()
    else:
        print("Token present. Use --create to build the Space, then --seed to push leads.")
        print("\nWould create:\n" + structure_text())


if __name__ == "__main__":
    main()
