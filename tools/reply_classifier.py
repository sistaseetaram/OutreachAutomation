#!/usr/bin/env python3
"""
reply_classifier.py — classify an inbound reply and suggest the pipeline route.

Categories: interested | not_now | wrong_person | unsubscribe | question
Routes status: interested->Replied, question->Replied, not_now->Nurture,
wrong_person->Lost, unsubscribe->Lost (and remove).

Usage:
    python tools/reply_classifier.py --text "Sure, send me the video"
    python tools/reply_classifier.py --text "not interested, remove me" --studio "X Studio" --apply
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent))
_CRED_ENV = Path(__file__).resolve().parent.parent / "credentials" / ".env"
load_dotenv(_CRED_ENV if _CRED_ENV.exists() else None)

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
CLASSIFY_MODEL = os.getenv("CLASSIFY_MODEL", "claude-haiku-4-5")

ROUTE = {
    "interested": "Replied", "question": "Replied", "not_now": "Nurture",
    "wrong_person": "Lost", "unsubscribe": "Lost",
}

PROMPT = """Classify this outreach reply into exactly one category and return JSON.
Categories: interested, not_now, wrong_person, unsubscribe, question.
Reply: ```{text}```
Return ONLY: {{"category": "...", "confidence": 0-1, "reason": "<=12 words"}}"""


def classify(text: str) -> dict:
    p = PROMPT.format(text=text)
    if ANTHROPIC_API_KEY and ANTHROPIC_API_KEY != "your_key_here":
        try:
            import anthropic
            c = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
            m = c.messages.create(model=CLASSIFY_MODEL, max_tokens=150,
                                  messages=[{"role": "user", "content": p}])
            return _parse(m.content[0].text)
        except Exception as e:
            print(f"  [Claude failed: {e}] — OpenRouter...")
    if OPENROUTER_API_KEY:
        from openai import OpenAI
        c = OpenAI(api_key=OPENROUTER_API_KEY, base_url="https://openrouter.ai/api/v1")
        r = c.chat.completions.create(
            model=os.getenv("OPENROUTER_RESEARCH_MODEL", "moonshotai/kimi-k2.6"),
            max_tokens=150, messages=[{"role": "user", "content": p}])
        return _parse(r.choices[0].message.content)
    raise RuntimeError("No model key set.")


def _parse(s: str) -> dict:
    m = s[s.find("{"):s.rfind("}") + 1]
    try:
        return json.loads(m)
    except Exception:
        return {"category": "question", "confidence": 0.0, "reason": "parse-failed"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--text", required=True)
    ap.add_argument("--studio")
    ap.add_argument("--apply", action="store_true", help="advance the lead in lead_tracker")
    args = ap.parse_args()

    res = classify(args.text)
    cat = res.get("category", "question")
    status = ROUTE.get(cat, "Replied")
    res["suggested_status"] = status
    print(json.dumps(res, indent=2))
    if cat == "unsubscribe":
        print("  ACTION: remove from all sequences immediately (compliance).")
    if args.apply and args.studio:
        import lead_tracker as lt
        leads = lt.load()
        s = lt.slug(args.studio)
        if s in leads:
            lt.advance(s, status, leads)
        else:
            print(f"  [no lead '{s}' to apply to]")


if __name__ == "__main__":
    main()
