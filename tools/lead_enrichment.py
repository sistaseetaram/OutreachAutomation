#!/usr/bin/env python3
"""
lead_enrichment.py — find a verified email/contact for a lead.

Bootstrap path (works now): scrape the studio site with Firecrawl and extract emails.
Scale path (keys): Apollo match / Clay waterfall (graceful dry-run until keys set).
Only accept results we can show; write back to lead_tracker.

Usage:
    python tools/lead_enrichment.py --studio "Nine Bricks Studio" --site https://ninebricks.in
    python tools/lead_enrichment.py --studio "X" --apollo   # dry-run unless APOLLO_API_KEY
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lead_tracker as lt  # noqa: E402

_CRED_ENV = Path(__file__).resolve().parent.parent / "credentials" / ".env"
load_dotenv(_CRED_ENV if _CRED_ENV.exists() else None)

APOLLO_API_KEY = os.getenv("APOLLO_API_KEY")
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")
EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")


def scrape_emails(site: str) -> list[str]:
    if not FIRECRAWL_API_KEY:
        print("[DRY-RUN] FIRECRAWL_API_KEY unset."); return []
    import requests
    found = set()
    for path in ["", "/contact", "/contact-us", "/about"]:
        try:
            r = requests.post("https://api.firecrawl.dev/v1/scrape",
                              headers={"Authorization": f"Bearer {FIRECRAWL_API_KEY}"},
                              json={"url": site.rstrip("/") + path, "formats": ["markdown"]},
                              timeout=40)
            if r.ok:
                md = r.json().get("data", {}).get("markdown", "")
                found.update(EMAIL_RE.findall(md))
        except Exception:
            pass
    # filter junk
    return [e for e in found if not e.endswith((".png", ".jpg", "example.com"))]


def apollo_match(studio):
    if not APOLLO_API_KEY:
        print(f"[DRY-RUN] APOLLO_API_KEY unset — would Apollo-match '{studio}' for a verified email.")
        return None
    import requests
    r = requests.post("https://api.apollo.io/v1/people/match",
                      headers={"Content-Type": "application/json", "X-Api-Key": APOLLO_API_KEY},
                      json={"organization_name": studio}, timeout=30)
    return (r.json().get("person", {}) or {}).get("email") if r.ok else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--studio", required=True)
    ap.add_argument("--site")
    ap.add_argument("--apollo", action="store_true")
    args = ap.parse_args()

    email = None
    if args.site:
        emails = scrape_emails(args.site)
        print(f"site emails found: {emails or 'none'}")
        email = emails[0] if emails else None
    if not email and args.apollo:
        email = apollo_match(args.studio)
        if email:
            print(f"apollo email: {email}")

    if email:
        leads = lt.load()
        s = lt.slug(args.studio)
        if s in leads:
            leads[s]["email"] = email
            lt.save(leads)
            print(f"wrote email to lead_tracker[{s}]")
    else:
        print("no email found (try --site or add APOLLO_API_KEY).")


if __name__ == "__main__":
    main()
