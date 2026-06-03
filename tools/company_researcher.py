#!/usr/bin/env python3
"""
Company Researcher Tool
Track 2: Audit — generates structured company profile before client calls.

Usage:
    python tools/company_researcher.py --company "Acme Corp" --url "https://acme.com"
    python tools/company_researcher.py --company "Acme Corp" --contact "John Smith"
    python tools/company_researcher.py --company "Acme Corp" --url "https://acme.com" --contact "John Smith, CEO"
"""

import argparse
import os
import re
import json
from pathlib import Path
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import anthropic
from openai import OpenAI

_CRED_ENV = Path(__file__).resolve().parent.parent / "credentials" / ".env"
load_dotenv(_CRED_ENV if _CRED_ENV.exists() else None)

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_RESEARCH_MODEL = os.getenv("OPENROUTER_RESEARCH_MODEL", "moonshotai/kimi-k2.6")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

TMP_DIR = Path(".tmp")
TMP_DIR.mkdir(exist_ok=True)


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def scrape_url(url: str) -> str:
    """Scrape a URL. Uses Firecrawl if key available, else requests+BS4."""
    if FIRECRAWL_API_KEY:
        try:
            resp = requests.post(
                "https://api.firecrawl.dev/v1/scrape",
                headers={"Authorization": f"Bearer {FIRECRAWL_API_KEY}"},
                json={"url": url, "formats": ["markdown"]},
                timeout=30,
            )
            if resp.ok:
                data = resp.json()
                return data.get("data", {}).get("markdown", "")
        except Exception:
            pass

    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; research-bot/1.0)"}
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        return soup.get_text(separator="\n", strip=True)[:8000]
    except Exception as e:
        return f"[Could not scrape {url}: {e}]"


def search_web(query: str, max_results: int = 5) -> list[dict]:
    """Search using DuckDuckGo. Returns list of {title, href, body}."""
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        return results
    except Exception as e:
        print(f"  [search failed: {e}]")
        return []


def gather_raw_data(company: str, url: str | None, contact: str | None) -> dict:
    """Gather all raw data about the company from multiple sources."""
    print(f"\n[1/4] Searching for company info: {company}")

    raw = {
        "company": company,
        "url": url,
        "contact": contact,
        "website_content": "",
        "news": [],
        "linkedin_signals": [],
        "job_signals": [],
        "funding_signals": [],
    }

    # Scrape company website
    if url:
        print(f"  Scraping website: {url}")
        raw["website_content"] = scrape_url(url)

        # Also try /about and /team pages
        base = url.rstrip("/")
        for path in ["/about", "/about-us", "/team", "/company"]:
            extra = scrape_url(base + path)
            if len(extra) > 200:
                raw["website_content"] += f"\n\n--- {path} ---\n{extra[:3000]}"
                break

    print(f"  Searching news and signals...")

    # News search
    news_results = search_web(f"{company} news 2024 2025", max_results=5)
    raw["news"] = [{"title": r.get("title", ""), "body": r.get("body", "")[:300]} for r in news_results]

    # LinkedIn signals
    linkedin_results = search_web(f'"{company}" site:linkedin.com', max_results=3)
    raw["linkedin_signals"] = [{"title": r.get("title", ""), "body": r.get("body", "")[:300]} for r in linkedin_results]

    # Job postings
    job_results = search_web(f"{company} jobs hiring 2024 2025", max_results=4)
    raw["job_signals"] = [{"title": r.get("title", ""), "body": r.get("body", "")[:300]} for r in job_results]

    # Funding / Crunchbase
    funding_results = search_web(f"{company} funding crunchbase raised investment", max_results=3)
    raw["funding_signals"] = [{"title": r.get("title", ""), "body": r.get("body", "")[:300]} for r in funding_results]

    # Contact research
    if contact:
        contact_name = contact.split(",")[0].strip()
        print(f"  Researching contact: {contact_name}")
        contact_results = search_web(f'{contact_name} {company} linkedin', max_results=3)
        raw["contact_signals"] = [{"title": r.get("title", ""), "body": r.get("body", "")[:300]} for r in contact_results]

    return raw


def synthesize_profile(raw: dict) -> str:
    """Synthesize raw data into structured profile. Uses Kimi via OpenRouter if key set, else Claude."""
    raw_text = json.dumps(raw, indent=2)[:12000]

    prompt = f"""You are a research analyst preparing a pre-call brief for an AI agency consultant who is about to have a discovery call with a potential client.

Company: {raw["company"]}
Contact: {raw.get("contact", "Unknown")}
Website: {raw.get("url", "Unknown")}

Raw research data collected:
{raw_text}

Generate a structured company profile in this EXACT format. Use only information you can verify from the data. If you don't know something, write "Unknown" or "Not found". Never fabricate information.

---

## Company: {raw["company"]}
Founded: [Year or "Unknown"] | Size: [Employee range or "Unknown"] | Industry: [Vertical]
Website: {raw.get("url", "Unknown")} | LinkedIn: [URL if found or "Not found"]

## Key People
- CEO/Founder: [Name, brief background — 1 sentence]
- Your contact: [{raw.get("contact", "Unknown")}, their role, any background found]
- Other relevant: [Any other decision-makers found]

## Business Model
[2–3 sentences: what they do, who they serve, how they make money. Be specific.]

## Current State (from research)
- Revenue/stage: [funding stage / revenue if known / growth signals]
- Recent news: [bullet points — specific events from last 12 months]
- Hiring signals: [roles they're hiring for — implies what their bottlenecks are]
- Tech stack: [tools identified from job posts or website]
- Company culture signals: [anything from Glassdoor, LinkedIn posts, or reviews]

## Likely Pain Points (hypothesis — based on evidence)
1. [Most likely pain — cite the specific evidence: "They're hiring 3 SDRs which suggests..."]
2. [Second likely pain — cite evidence]
3. [Third likely pain — cite evidence]

## Conversation Starters (specific to this company)
- [A specific observation you can open with — based on real data]
- [A question triggered by a hiring signal or news item]
- [A pattern you've noticed in companies at this stage]

## Red Flags / Watch For
- [Anything unusual, sensitive, or worth being careful about]

## Research Confidence
- Overall: [High / Medium / Low]
- Gaps: [What you couldn't find — be honest]

---"""

    # 1. Kimi via OpenRouter (primary deep research)
    if OPENROUTER_API_KEY and OPENROUTER_API_KEY != "your_key_here":
        print(f"\n[2/4] Synthesizing with Kimi ({OPENROUTER_RESEARCH_MODEL}) via OpenRouter...")
        try:
            client = OpenAI(
                api_key=OPENROUTER_API_KEY,
                base_url="https://openrouter.ai/api/v1",
            )
            response = client.chat.completions.create(
                model=OPENROUTER_RESEARCH_MODEL,
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"  [Kimi failed: {e}] — trying Gemini fallback...")

    # 2. Gemini 2.5 Flash (secondary deep research fallback)
    if GOOGLE_API_KEY and GOOGLE_API_KEY != "your_key_here":
        print(f"\n[2/4] Synthesizing with Gemini 2.5 Flash...")
        try:
            client = OpenAI(
                api_key=GOOGLE_API_KEY,
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            )
            response = client.chat.completions.create(
                model="gemini-2.5-flash",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"  [Gemini failed: {e}] — falling back to Claude...")

    # 3. Claude Sonnet (last resort — reasoning model, used only if research models unavailable)
    print(f"\n[2/4] Synthesizing with Claude Sonnet (last resort)...")
    if not ANTHROPIC_API_KEY or ANTHROPIC_API_KEY == "your_key_here":
        raise ValueError("All research models failed and ANTHROPIC_API_KEY not set. Check .env")

    claude = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    message = claude.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def save_profile(company: str, profile_text: str) -> Path:
    """Save profile to .tmp/[company_slug]_profile.md"""
    print(f"\n[3/4] Saving profile...")
    output_path = TMP_DIR / f"{slug(company)}_profile.md"
    output_path.write_text(
        f"# Company Profile: {company}\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n{profile_text}",
        encoding="utf-8",
    )
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Research a company before an audit call")
    parser.add_argument("--company", required=True, help="Company name")
    parser.add_argument("--url", help="Company website URL")
    parser.add_argument("--contact", help="Contact name and role (e.g. 'John Smith, CEO')")
    args = parser.parse_args()

    print(f"\n{'='*50}")
    print(f"  COMPANY RESEARCHER")
    print(f"  Company: {args.company}")
    if args.url:
        print(f"  Website: {args.url}")
    if args.contact:
        print(f"  Contact: {args.contact}")
    print(f"{'='*50}")

    raw = gather_raw_data(args.company, args.url, args.contact)
    profile = synthesize_profile(raw)
    output_path = save_profile(args.company, profile)

    print(f"\n[4/4] Done!")
    print(f"\n{'='*50}")
    print(f"  Profile saved to: {output_path}")
    print(f"  Next: run interview_template_generator.py --profile {output_path}")
    print(f"{'='*50}\n")

    print(profile)


if __name__ == "__main__":
    main()
