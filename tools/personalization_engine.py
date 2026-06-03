#!/usr/bin/env python3
"""
personalization_engine.py — Setu-voice, per-channel outreach copy generator.

Core of Track 1. Consumes a company_researcher.py profile, picks the strongest available
personalization signal (waterfall), and writes channel/stage-appropriate copy in Setu voice.
Hard gates: forbidden-words (reject + regenerate once), channel length limits, copy test.

Usage:
    python tools/personalization_engine.py --studio "Studio Lotus" \\
        --channel linkedin_note --stage first_touch \\
        --profile .tmp/studio_lotus_profile.md
    python tools/personalization_engine.py --studio "Studio Lotus" --channel whatsapp \\
        --stage loom_invite --signal "just posted a Jaipur villa reveal on Instagram"

Channels: linkedin_note | linkedin_dm | whatsapp | instagram | email
Stages:   first_touch | followup | loom_invite | breakup
"""

from __future__ import annotations

import argparse
import os
import re
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv

# local
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from setu_voice import voice_system_prompt, find_forbidden, COPY_TEST  # noqa: E402

_CRED_ENV = Path(__file__).resolve().parent.parent / "credentials" / ".env"
load_dotenv(_CRED_ENV if _CRED_ENV.exists() else None)

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
COPY_MODEL = os.getenv("COPY_MODEL", "claude-sonnet-4-6")

TMP_DIR = Path(".tmp")
TMP_DIR.mkdir(exist_ok=True)

# channel -> (limit_kind, limit, format_guidance)
CHANNELS = {
    "linkedin_note": ("chars", 300,
        "LinkedIn connection-request note. ONE specific real observation about them. "
        "Zero sales language. No link. Warm, peer-to-peer."),
    "linkedin_dm": ("chars", 500,
        "LinkedIn DM after they accepted. Conversation starter or soft value. No pitch."),
    "whatsapp": ("chars", 400,
        "WhatsApp message to a warm contact. Personal, short, plain. One line of value."),
    "instagram": ("chars", 400,
        "Instagram DM. Casual, reference their actual work/post. Short. No pitch."),
    "email": ("words", 120,
        "Cold/warm email. First line = a subject line prefixed 'Subject:'. Body outcome-first, "
        "under 120 words, no links, plain text."),
}

STAGES = {
    "first_touch": "Opening message. Earn a reply, not a meeting. One observation + a light reason to talk.",
    "followup": "Follow-up with NO ask — share one useful angle or thought. 3:1 value-to-ask.",
    "loom_invite": ("Permission-style invite: offer a short free Loom showing one concrete way Setu could "
                    "automate a boring part of their workflow. Ask if they'd like it. Soft, optional."),
    "breakup": "Brief, graceful last touch. No guilt. Leave the door open.",
}

WATERFALL = """Personalization signal waterfall — use the HIGHEST available from the profile,
and ground the copy in it (state nothing you can't see in the profile):
1. Recent Instagram project post / reel (specific project)
2. Award, press feature, or publication
3. Hiring a junior designer / draftsman (workload growth)
4. New office / second location / expansion
5. A notable completed project or signature style
6. Honest-generic: the segment pain (quotes copied between sheets, specs by hand,
   client updates done manually) — use ONLY if no specific signal exists."""


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def load_profile(path: str | None) -> str:
    if not path:
        return "(no research profile provided — use honest-generic segment pain only)"
    p = Path(path)
    if not p.exists():
        print(f"  [profile not found at {path} — using honest-generic]")
        return "(no research profile provided — use honest-generic segment pain only)"
    return p.read_text(encoding="utf-8")[:8000]


def build_prompt(studio, channel, stage, profile_text, signal, segment) -> str:
    _, limit, fmt = CHANNELS[channel]
    limit_kind = CHANNELS[channel][0]
    stage_desc = STAGES[stage]
    if isinstance(stage_desc, tuple):
        stage_desc = stage_desc[0]
    signal_line = f"\nOperator-supplied signal to use: {signal}" if signal else ""
    return f"""Write ONE outreach message.

Prospect studio: {studio}
Channel: {channel} — {fmt}
Hard limit: {limit} {limit_kind}.
Stage: {stage} — {stage_desc}{signal_line}

{WATERFALL}

Research profile on the prospect:
---
{profile_text}
---

Output ONLY the message text (for email, include the 'Subject:' line first). No preamble,
no explanation, no quotes around it. After the message, on a new line, add:
SIGNAL_USED: <which waterfall tier you used, 1 short phrase>"""


def call_model(system: str, prompt: str) -> str:
    # Primary: Anthropic Claude Sonnet (copywriting per tech stack)
    if ANTHROPIC_API_KEY and ANTHROPIC_API_KEY != "your_key_here":
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
            msg = client.messages.create(
                model=COPY_MODEL, max_tokens=600, system=system,
                messages=[{"role": "user", "content": prompt}],
            )
            return msg.content[0].text.strip()
        except Exception as e:
            print(f"  [Claude failed: {e}] — trying OpenRouter...")
    # Fallback: OpenRouter
    if OPENROUTER_API_KEY and OPENROUTER_API_KEY != "your_key_here":
        from openai import OpenAI
        client = OpenAI(api_key=OPENROUTER_API_KEY, base_url="https://openrouter.ai/api/v1")
        resp = client.chat.completions.create(
            model=os.getenv("OPENROUTER_RESEARCH_MODEL", "moonshotai/kimi-k2.6"),
            max_tokens=600,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": prompt}],
        )
        return resp.choices[0].message.content.strip()
    raise RuntimeError("No model key set (ANTHROPIC_API_KEY / OPENROUTER_API_KEY). Add to credentials/.env")


def enforce_voice(system, prompt, text):
    """Regenerate once if forbidden words appear."""
    hits = find_forbidden(text)
    if not hits:
        return text, []
    print(f"  [forbidden words {hits} — regenerating once]")
    fix = prompt + f"\n\nYou used banned words: {hits}. Rewrite WITHOUT them. Same length limit."
    text2 = call_model(system, fix)
    return text2, find_forbidden(text2)


def length_ok(channel, text):
    kind, limit, _ = CHANNELS[channel]
    # strip the SIGNAL_USED line for measurement
    body = re.split(r"\nSIGNAL_USED:", text)[0].strip()
    n = len(body) if kind == "chars" else len(body.split())
    return n <= limit, n, limit, kind


def main():
    ap = argparse.ArgumentParser(description="Generate Setu-voice outreach copy")
    ap.add_argument("--studio", required=True)
    ap.add_argument("--channel", required=True, choices=list(CHANNELS))
    ap.add_argument("--stage", default="first_touch", choices=list(STAGES))
    ap.add_argument("--profile", help="path to company_researcher .tmp profile")
    ap.add_argument("--signal", help="optional operator-supplied personalization hook")
    ap.add_argument("--segment", default="interior design studio")
    args = ap.parse_args()

    print(f"\n{'='*54}\n  PERSONALIZATION ENGINE — {args.studio}")
    print(f"  {args.channel} / {args.stage}\n{'='*54}")

    profile_text = load_profile(args.profile)
    system = voice_system_prompt(args.segment)
    prompt = build_prompt(args.studio, args.channel, args.stage, profile_text, args.signal, args.segment)

    print("\n[1/3] Generating...")
    text = call_model(system, prompt)
    print("[2/3] Voice gate (forbidden words + copy test)...")
    text, remaining = enforce_voice(system, prompt, text)
    ok, n, limit, kind = length_ok(args.channel, text)

    out = TMP_DIR / f"{slug(args.studio)}_{args.channel}_{args.stage}.md"
    out.write_text(
        f"# {args.studio} — {args.channel} / {args.stage}\n"
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        f"Length: {n}/{limit} {kind} ({'OK' if ok else 'OVER'})\n"
        f"Forbidden-word hits: {remaining or 'none'}\n"
        f"Copy test: {COPY_TEST}\n\n---\n\n{text}\n",
        encoding="utf-8",
    )

    print(f"[3/3] Saved -> {out}")
    print(f"  length: {n}/{limit} {kind} ({'OK' if ok else 'OVER — tighten'})")
    if remaining:
        print(f"  WARNING: forbidden words still present: {remaining}")
    print(f"\n{'-'*54}\n{text}\n{'-'*54}")
    print("Next: drive_sync.py to push to Drive + clickup_sync.py to log the touch.")


if __name__ == "__main__":
    main()
