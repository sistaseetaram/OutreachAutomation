#!/usr/bin/env python3
"""
whatsapp_sender.py — send a message to a WARM/ENGAGED lead via WhatsApp Cloud API.

GUARDRAIL: never cold. Outside the 24h customer-initiated window, WhatsApp requires a
pre-approved TEMPLATE. Use --template for first/outbound; --text only works if the lead
messaged you in the last 24h (session window). If WHATSAPP_TOKEN unset -> DRY-RUN.

Usage:
    python tools/whatsapp_sender.py --to +9198XXXXXXXX --template followup --lang en \\
        --params "Manjusha" "your status-report workflow"
    python tools/whatsapp_sender.py --to +9198XXXXXXXX --text "great — sending the Loom now" --session
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

_CRED_ENV = Path(__file__).resolve().parent.parent / "credentials" / ".env"
load_dotenv(_CRED_ENV if _CRED_ENV.exists() else None)

TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_ID = os.getenv("WHATSAPP_PHONE_ID")
GRAPH = "https://graph.facebook.com/v21.0"


def template_payload(to, name, lang, params):
    components = []
    if params:
        components = [{"type": "body", "parameters": [{"type": "text", "text": p} for p in params]}]
    return {"messaging_product": "whatsapp", "to": to, "type": "template",
            "template": {"name": name, "language": {"code": lang}, "components": components}}


def text_payload(to, body):
    return {"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": body}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--to", required=True, help="lead number E.164")
    ap.add_argument("--template"); ap.add_argument("--lang", default="en")
    ap.add_argument("--params", nargs="*", default=[])
    ap.add_argument("--text"); ap.add_argument("--session", action="store_true",
                    help="confirm lead messaged within last 24h (text allowed)")
    args = ap.parse_args()

    if args.text and not args.session and not args.template:
        print("REFUSED: free-text outside a session needs --session (lead replied <24h ago), "
              "or use --template. WhatsApp policy / ban risk.")
        return
    payload = (template_payload(args.to, args.template, args.lang, args.params)
               if args.template else text_payload(args.to, args.text))

    if not (TOKEN and PHONE_ID):
        print("[DRY-RUN] WhatsApp not configured — would POST:")
        print(f"  {GRAPH}/{PHONE_ID}/messages")
        print(f"  {payload}")
        print("Set WHATSAPP_TOKEN + WHATSAPP_PHONE_ID (after Meta verification + template approval).")
        return

    r = requests.post(f"{GRAPH}/{PHONE_ID}/messages",
                      headers={"Authorization": f"Bearer {TOKEN}"}, json=payload, timeout=20)
    print(f"WhatsApp send: {r.status_code} {r.text[:300]}")


if __name__ == "__main__":
    main()
