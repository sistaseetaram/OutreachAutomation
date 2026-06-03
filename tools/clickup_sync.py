#!/usr/bin/env python3
"""
clickup_sync.py — ClickUp CRM sync for outreach leads (ClickUp API v2).

ClickUp = single source of truth for pipeline STATUS. One task per lead in the Leads list.
This tool upserts a lead task (status, tags, custom fields). If CLICKUP_API_TOKEN is not set,
it runs in DRY-RUN and prints the payload it would send.

Usage:
    python tools/clickup_sync.py --studio "Nine Bricks Studio" --status "Contacted" \\
        --tags warm,interior,bengaluru --linkedin "https://linkedin.com/in/..." \\
        --drive "https://drive.google.com/..." --source salesnav --followups 0
    python tools/clickup_sync.py --whoami        # list teams/workspaces (needs token)
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
LEADS_LIST_ID = os.getenv("CLICKUP_LEADS_LIST_ID")
BASE = "https://api.clickup.com/api/v2"

# custom-field names we manage (resolved to IDs at runtime against the list)
CUSTOM_FIELD_NAMES = ["LinkedIn URL", "Instagram", "Email", "Drive Folder", "Follow-up count", "Source"]


def _headers() -> dict:
    return {"Authorization": TOKEN, "Content-Type": "application/json"}


def available() -> bool:
    return bool(TOKEN)


def whoami() -> dict:
    r = requests.get(f"{BASE}/team", headers=_headers(), timeout=20)
    r.raise_for_status()
    return r.json()


def list_fields(list_id: str) -> dict:
    """name -> field dict (id, type)."""
    r = requests.get(f"{BASE}/list/{list_id}/field", headers=_headers(), timeout=20)
    r.raise_for_status()
    return {f["name"]: f for f in r.json().get("fields", [])}


def find_task(list_id: str, name: str) -> str | None:
    r = requests.get(f"{BASE}/list/{list_id}/task", headers=_headers(),
                     params={"archived": "false"}, timeout=20)
    r.raise_for_status()
    for t in r.json().get("tasks", []):
        if t.get("name", "").strip().lower() == name.strip().lower():
            return t["id"]
    return None


def _custom_fields_payload(list_id: str, values: dict) -> list:
    """Map {field_name: value} -> ClickUp custom_fields list using live field IDs."""
    fields = list_fields(list_id)
    out = []
    for name, val in values.items():
        if val in (None, "") or name not in fields:
            continue
        out.append({"id": fields[name]["id"], "value": val})
    return out


def upsert_lead(list_id: str, studio: str, status: str | None, tags: list[str],
                custom: dict) -> dict:
    task_id = find_task(list_id, studio)
    cf = _custom_fields_payload(list_id, custom) if task_id is None else None
    if task_id:
        body: dict = {}
        if status:
            body["status"] = status
        if body:
            r = requests.put(f"{BASE}/task/{task_id}", headers=_headers(), json=body, timeout=20)
            r.raise_for_status()
        # tags + custom fields set individually on existing task
        for tg in tags:
            requests.post(f"{BASE}/task/{task_id}/tag/{tg}", headers=_headers(), timeout=20)
        fields = list_fields(list_id)
        for name, val in custom.items():
            if val not in (None, "") and name in fields:
                requests.post(f"{BASE}/task/{task_id}/field/{fields[name]['id']}",
                              headers=_headers(), json={"value": val}, timeout=20)
        return {"action": "updated", "task_id": task_id}
    body = {"name": studio, "tags": tags}
    if status:
        body["status"] = status
    if cf:
        body["custom_fields"] = cf
    r = requests.post(f"{BASE}/list/{list_id}/task", headers=_headers(), json=body, timeout=20)
    r.raise_for_status()
    return {"action": "created", "task_id": r.json().get("id")}


def main():
    ap = argparse.ArgumentParser(description="Upsert a lead task in ClickUp")
    ap.add_argument("--studio")
    ap.add_argument("--status")
    ap.add_argument("--tags", default="", help="comma-separated")
    ap.add_argument("--linkedin"); ap.add_argument("--instagram"); ap.add_argument("--email")
    ap.add_argument("--drive"); ap.add_argument("--source")
    ap.add_argument("--followups", type=int)
    ap.add_argument("--list-id", default=LEADS_LIST_ID)
    ap.add_argument("--whoami", action="store_true")
    args = ap.parse_args()

    tags = [t.strip() for t in args.tags.split(",") if t.strip()]
    custom = {
        "LinkedIn URL": args.linkedin, "Instagram": args.instagram, "Email": args.email,
        "Drive Folder": args.drive, "Source": args.source,
        "Follow-up count": args.followups if args.followups is not None else None,
    }

    if not available():
        print("[DRY-RUN] CLICKUP_API_TOKEN not set — would perform:")
        if args.whoami:
            print("  GET /team (list workspaces)")
        else:
            print(f"  upsert task '{args.studio}' in list {args.list_id}")
            print(f"    status: {args.status}")
            print(f"    tags:   {tags}")
            print(f"    fields: { {k: v for k, v in custom.items() if v not in (None, '')} }")
        print("Add CLICKUP_API_TOKEN (+ CLICKUP_LEADS_LIST_ID) to credentials/.env to run live.")
        return

    if args.whoami:
        import json
        print(json.dumps(whoami(), indent=2)[:2000])
        return

    if not args.list_id:
        print("No list id. Set CLICKUP_LEADS_LIST_ID or pass --list-id (run Slice 4 build-out first).")
        return
    result = upsert_lead(args.list_id, args.studio, args.status, tags, custom)
    print(f"ClickUp: {result}")


if __name__ == "__main__":
    main()
