#!/usr/bin/env python3
"""
Interview Template Generator
Track 2: Audit — generates customized audit interview questions from company profile.

Usage:
    python tools/interview_template_generator.py --profile ".tmp/acme_corp_profile.md"
    python tools/interview_template_generator.py --profile ".tmp/acme_corp_profile.md" --call-date "2026-06-02 15:00"
"""

import argparse
import os
import re
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
import anthropic

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
TMP_DIR = Path(".tmp")
TMP_DIR.mkdir(exist_ok=True)


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def load_profile(profile_path: str) -> str:
    path = Path(profile_path)
    if not path.exists():
        raise FileNotFoundError(f"Profile not found: {profile_path}")
    return path.read_text(encoding="utf-8")


def extract_company_name(profile_text: str) -> str:
    match = re.search(r"## Company: (.+)", profile_text)
    if match:
        return match.group(1).strip()
    match = re.search(r"Company Profile: (.+)", profile_text)
    if match:
        return match.group(1).strip()
    return "Unknown Company"


def generate_audit_package(profile_text: str, company: str, call_date: str | None) -> str:
    """Use Claude to generate the full audit package from the company profile."""
    print(f"\n[1/3] Generating customized audit package with Claude...")

    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY not set in .env")

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    prompt = f"""You are an expert AI transformation consultant preparing for a $10,000 audit discovery call.

You have completed research on this company:

{profile_text}

Generate a complete Pre-Call Audit Package. Every question must be SPECIFIC to this company — referencing their actual business model, known pain signals, company size, industry, and the specific person you're meeting. Generic questions that could apply to any company are unacceptable.

Format:

---

# Pre-Call Audit Package: {company}
Call date: {call_date or "TBD"}
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}

---

## Section 1: Pre-Call Brief

**Company summary (read this first):**
[2–3 sentences: what they do, who they serve, their stage]

**Your contact:**
[Name, role, any relevant background — how to address them, what their perspective likely is]

**Why they're likely interested in AI:**
[Based on the specific pain signals found in research — cite the evidence]

**What to watch for:**
[Any red flags, sensitive topics, or things to navigate carefully]

---

## Section 2: Your Opening (first 2 minutes)

[Write the exact opening you'll use — personalized to this company and contact. Reference something specific from research to show you've done your homework. Example: "I noticed you're scaling the sales team — that usually comes with operational challenges around [X]. I want to understand what that's been like for you."]

---

## Section 3: Stakeholder Discovery Questions

Instructions: These are for the leadership/decision-maker on the call. Ask them in conversational order — not as a checklist. Listen and follow threads.

### 3a. Role & Team (get the lay of the land)
[Write 3 specific questions that fit THIS company's structure and role]
→ For each: write what to LISTEN FOR in their answer

### 3b. Core Processes (find the engines)
[Write 3–4 specific questions about how this company actually runs — reference their business model]
→ For each: write what to LISTEN FOR

### 3c. Biggest Time Drains (find the friction)
[Write 3 specific questions that probe for manual, repetitive, error-prone work]
→ For each: write what to LISTEN FOR

### 3d. Tools & Systems (find integration gaps)
[Write 2–3 questions about their tech stack and where things break down — reference any tools identified in research]
→ For each: write what to LISTEN FOR

### 3e. Vision & Success (find the stakes)
[Write 2 questions about what success looks like and what's preventing it]
→ For each: write what to LISTEN FOR

---

## Section 4: Deep Dive Questions (per hypothesis)

For each of the top 3 AI opportunity hypotheses from research, write 3–4 questions to verify and quantify the pain:

### Hypothesis 1: [Name from research]
[Questions that probe specifically for this pain — ask for numbers, frequency, who's involved]

### Hypothesis 2: [Name from research]
[Questions for this hypothesis]

### Hypothesis 3: [Name from research]
[Questions for this hypothesis]

---

## Section 5: End-User Questions (if you interview employees)

If you get access to employees (not just the executive), these questions work for the most likely role types at this company:

### For [Role Type 1 — most likely based on company type]:
[3–4 specific questions about their daily workflow and frustrations]

### For [Role Type 2]:
[3–4 specific questions]

---

## Section 6: Initial Opportunity Hypotheses

Based on research, these are the most likely AI opportunities. Test these during the call.

| # | Opportunity | Evidence from Research | Expected Impact | Expected Effort |
|---|---|---|---|---|
| 1 | [Name] | [Specific evidence] | High/Med/Low | High/Med/Low |
| 2 | [Name] | [Specific evidence] | High/Med/Low | High/Med/Low |
| 3 | [Name] | [Specific evidence] | High/Med/Low | High/Med/Low |

---

## Section 7: Call Agenda

[Duration: fill in based on how long the call is scheduled]

| Time | Agenda Item |
|---|---|
| 00:00–05:00 | Intro + set expectations |
| 05:00–25:00 | Stakeholder discovery (Sections 3a–3e) |
| 25:00–40:00 | Deep dive on strongest hypothesis |
| 40:00–48:00 | Pivot to audit offer |
| 48:00–55:00 | Handle questions + close / next steps |

---

## Section 8: What to Offer

Based on this company's profile:
- **Recommended audit scope:** [based on size and complexity]
- **Price point:** $[X] (based on company size and complexity)
- **Timeline:** [X weeks, Y interviews]
- **Positioning:** [One sentence on how to frame the audit for THIS specific company's context]

---

## Section 9: Note-Taking Template (use during the call)

Key pain points captured (their exact words):
-

Time sinks identified:
-

Quantified (hours/week, people affected):
-

Their reaction to the audit offer:
[ ] Hot — ready to proceed
[ ] Warm — interested, needs more info
[ ] Cold — not the right time
[ ] Wrong person — need to involve [role]

Next action:
[ ] Send proposal by [date]
[ ] Schedule follow-up call on [date]
[ ] Follow up in [X] weeks
[ ] Not a fit — archive

---"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8000,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def save_package(company: str, package_text: str) -> Path:
    print(f"\n[2/3] Saving audit package...")
    output_path = TMP_DIR / f"{slug(company)}_audit_package.md"
    output_path.write_text(package_text, encoding="utf-8")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Generate customized audit interview package")
    parser.add_argument("--profile", required=True, help="Path to company profile (.tmp/[name]_profile.md)")
    parser.add_argument("--call-date", help="Scheduled call date/time (optional)")
    args = parser.parse_args()

    print(f"\n{'='*50}")
    print(f"  INTERVIEW TEMPLATE GENERATOR")
    print(f"  Profile: {args.profile}")
    print(f"{'='*50}")

    profile_text = load_profile(args.profile)
    company = extract_company_name(profile_text)

    print(f"  Company: {company}")

    package = generate_audit_package(profile_text, company, args.call_date)
    output_path = save_package(company, package)

    print(f"\n[3/3] Done!")
    print(f"\n{'='*50}")
    print(f"  Audit package saved to: {output_path}")
    print(f"  Open and review before your call.")
    print(f"{'='*50}\n")

    print(package)


if __name__ == "__main__":
    main()
