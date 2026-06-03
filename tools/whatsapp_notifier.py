#!/usr/bin/env python3
"""
whatsapp_notifier.py — push a daily action digest to YOUR WhatsApp (self-notification).

Pulls "actions due today" from lead_tracker and messages your own number via WhatsApp Cloud API.
If WHATSAPP_TOKEN is not set, prints the digest to console (graceful fallback).

Self-messaging is allowed; this is NOT cold outreach.

Usage:
    python tools/whatsapp_notifier.py            # send/print today's digest
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent))
_CRED_ENV = Path(__file__).resolve().parent.parent / "credentials" / ".env"
load_dotenv(_CRED_ENV if _CRED_ENV.exists() else None)

TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_ID = os.getenv("WHATSAPP_PHONE_ID")
NOTIFY_TO = os.getenv("WHATSAPP_NOTIFY_TO")  # your own number, E.164
GRAPH = "https://graph.facebook.com/v21.0"


def build_digest() -> str:
    import lead_tracker as lt
    leads = lt.load()
    due = [r for r in leads.values()
           if (r.get("next_action_date") or "9999") <= lt._today()
           and r.get("status") not in ("Won", "Lost", "Nurture", "Delivered", "Testimonial/Referral")]
    lines = [f"Setu — actions due ({len(due)}) {lt._today()}:"]
    for r in due[:20]:
        lines.append(f"• {r['studio']} — {r.get('status')} ({r.get('track')})")
    if not due:
        lines.append("• nothing due — send today's LinkedIn warmup slice")
    return "\n".join(lines)


def send_text(to: str, body: str) -> dict:
    url = f"{GRAPH}/{PHONE_ID}/messages"
    payload = {"messaging_product": "whatsapp", "to": to, "type": "text",
               "text": {"body": body}}
    r = requests.post(url, headers={"Authorization": f"Bearer {TOKEN}"}, json=payload, timeout=20)
    r.raise_for_status()
    return r.json()


def main():
    digest = build_digest()
    if not (TOKEN and PHONE_ID and NOTIFY_TO):
        print("[DRY-RUN] WhatsApp not configured — digest below (set WHATSAPP_TOKEN/PHONE_ID/NOTIFY_TO):\n")
        print(digest)
        return
    res = send_text(NOTIFY_TO, digest)
    print(f"WhatsApp notification sent: {res.get('messages', res)}")


if __name__ == "__main__":
    main()
