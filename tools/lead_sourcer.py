#!/usr/bin/env python3
"""
lead_sourcer.py — multi-source lead intake -> normalized -> deduped into lead_tracker store.

Sources (Phase 1, India interior):
  --csv <path>          Sales Navigator / manual export (works now)
  --firecrawl-url <url> scrape a directory/studio listing page (Firecrawl; key set) -> raw to .tmp for review
  --apollo              Apollo people-search (graceful dry-run if APOLLO_API_KEY unset)
  --apify-instagram     Apify IG scraper (graceful dry-run if APIFY_API_TOKEN unset)

Dedup key: studio slug. New leads enter at status 'Sourced'.

Usage:
    python tools/lead_sourcer.py --csv leads.csv --segment interior --track cold --source salesnav
    python tools/lead_sourcer.py --firecrawl-url "https://www.justdial.com/Bangalore/Interior-Designers"
    python tools/lead_sourcer.py --apollo --apollo-title "interior designer" --apollo-geo "India"
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lead_tracker as lt  # noqa: E402

_CRED_ENV = Path(__file__).resolve().parent.parent / "credentials" / ".env"
load_dotenv(_CRED_ENV if _CRED_ENV.exists() else None)

APOLLO_API_KEY = os.getenv("APOLLO_API_KEY")
APIFY_API_TOKEN = os.getenv("APIFY_API_TOKEN")
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")

# flexible CSV header aliases -> our fields
ALIASES = {
    "studio": ["studio", "company", "company name", "organization", "name", "full name"],
    "founder": ["founder", "first name", "contact", "owner", "principal"],
    "city": ["city", "location", "geo"],
    "linkedin": ["linkedin", "linkedin url", "profile url", "person linkedin url"],
    "instagram": ["instagram", "ig"],
    "email": ["email", "email address", "work email"],
}


def _match(header: str, field: str) -> bool:
    return header.strip().lower() in ALIASES[field]


def normalize_row(row: dict) -> dict:
    out = {}
    for field in ALIASES:
        for h, v in row.items():
            if h and _match(h, field) and v:
                out[field] = v.strip()
                break
    return out


def upsert(records: list[dict], segment, track, source):
    leads = lt.load()
    added = 0
    for r in records:
        studio = r.get("studio") or r.get("founder")
        if not studio:
            continue
        s = lt.slug(studio)
        if s in leads:
            continue  # dedup
        rec = {f: "" for f in lt.FIELDS}
        rec.update({
            "studio": studio, "founder": r.get("founder", ""), "segment": segment,
            "track": track, "city": r.get("city", ""), "status": "Sourced",
            "source": source, "followups": 0, "last_touch": lt._today(),
            "next_action_date": lt._today(), "linkedin": r.get("linkedin", ""),
            "instagram": r.get("instagram", ""), "email": r.get("email", ""),
        })
        leads[s] = rec
        added += 1
    lt.save(leads)
    print(f"sourced {added} new leads (deduped). total now {len(leads)}.")


def from_csv(path, segment, track, source):
    rows = list(csv.DictReader(open(path, encoding="utf-8-sig")))
    recs = [normalize_row(r) for r in rows]
    upsert(recs, segment, track, source)


def from_firecrawl(url):
    if not FIRECRAWL_API_KEY:
        print("[DRY-RUN] FIRECRAWL_API_KEY unset."); return
    import requests
    r = requests.post("https://api.firecrawl.dev/v1/scrape",
                      headers={"Authorization": f"Bearer {FIRECRAWL_API_KEY}"},
                      json={"url": url, "formats": ["markdown"]}, timeout=60)
    md = r.json().get("data", {}).get("markdown", "") if r.ok else ""
    out = Path(".tmp") / f"sourced_{lt.slug(url)[:40]}.md"
    out.write_text(md, encoding="utf-8")
    print(f"scraped -> {out} ({len(md)} chars). Review + extract studios, then import via --csv.")
    print("(Auto-extraction to structured leads = LLM pass; kept manual to control cost.)")


def from_apollo(title, geo):
    if not APOLLO_API_KEY:
        print("[DRY-RUN] APOLLO_API_KEY unset — would POST Apollo people-search:")
        print(f"  title~='{title}', location='{geo}', then enrich emails (free tier 10k/mo).")
        print("  Add APOLLO_API_KEY to credentials/.env to run live.")
        return
    import requests
    r = requests.post("https://api.apollo.io/v1/mixed_people/search",
                      headers={"Content-Type": "application/json", "X-Api-Key": APOLLO_API_KEY},
                      json={"person_titles": [title], "person_locations": [geo], "page": 1}, timeout=30)
    people = r.json().get("people", []) if r.ok else []
    recs = [{"studio": p.get("organization", {}).get("name", ""),
             "founder": p.get("name", ""), "city": (p.get("city") or ""),
             "linkedin": p.get("linkedin_url", ""), "email": p.get("email", "")} for p in people]
    upsert([x for x in recs if x.get("studio")], "interior", "cold", "apollo")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv"); ap.add_argument("--firecrawl-url")
    ap.add_argument("--apollo", action="store_true")
    ap.add_argument("--apollo-title", default="interior designer")
    ap.add_argument("--apollo-geo", default="India")
    ap.add_argument("--apify-instagram", action="store_true")
    ap.add_argument("--segment", default="interior", choices=["interior", "architecture", "construction"])
    ap.add_argument("--track", default="cold", choices=["warm", "cold"])
    ap.add_argument("--source", default="manual")
    args = ap.parse_args()

    if args.csv:
        from_csv(args.csv, args.segment, args.track, args.source)
    elif args.firecrawl_url:
        from_firecrawl(args.firecrawl_url)
    elif args.apollo:
        from_apollo(args.apollo_title, args.apollo_geo)
    elif args.apify_instagram:
        if not APIFY_API_TOKEN:
            print("[DRY-RUN] APIFY_API_TOKEN unset — would run Apify Instagram scraper "
                  "(by hashtag/location) -> normalize -> upsert. Add APIFY_API_TOKEN to run.")
        else:
            print("Apify IG live-run: wire actor id + run-sync-get-dataset-items (TODO at activation).")
    else:
        print("Pick a source: --csv | --firecrawl-url | --apollo | --apify-instagram")


if __name__ == "__main__":
    main()
