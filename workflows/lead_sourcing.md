# Workflow: Lead Sourcing (multi-source)

**Objective:** Build a deduped list of interior-design (then architecture/construction) studios to
outreach. Cast wide across sources; normalize into the lead tracker.

## Sources (Phase 1, India interior)
| Source | Tool | Notes |
|---|---|---|
| Sales Navigator (manual daily) | export CSV → `lead_sourcer.py --csv` | You curate daily; richest signal |
| Instagram studios | `lead_sourcer.py --apify-instagram` | by hashtag/location (needs APIFY_API_TOKEN) |
| Google Maps / Justdial / Houzz India | `lead_sourcer.py --firecrawl-url <listing>` | scrape → review → import |
| Apollo DB | `lead_sourcer.py --apollo` | cast wide ("who'll click"); free 10k/mo; weak for tiny India studios |
| Referrals | `lead_tracker.py --add --source referral` | from founding clients (the fence) |

## Procedure
1. Pull from a source → `lead_sourcer.py` normalizes + dedups (key = studio slug) → status `Sourced`.
2. Tag track (warm/cold) + segment.
3. `lead_enrichment.py --site <url>` (Firecrawl email scrape) or `--apollo` → contact email.
4. Research the strongest before outreach (`company_researcher.py`).
5. Hand off to `linkedin_outreach.md` / `warm_outreach.md`.

## Phase 2 (cold, global English)
Same tools, international titles/geos (US/UK/Canada/Australia/UAE-Dubai/Singapore + NRI hubs).
Apollo + Clay shine here (better coverage than India SMBs). Add cold-email infra (see Phase 2 plan).

## Rule
Dedup always. Don't re-source existing leads. Quality of fit > volume (acceptance rate protects the LinkedIn account).
