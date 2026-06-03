#!/usr/bin/env python3
"""
setu_voice.py — Setu brand voice spec, embedded for runtime use.

Source of truth: Obsidian content-wiki
(`content-wiki/wiki/concepts/setu-voice.md`, `setu-values.md`, `setu-positioning.md`).
Embedded here so outreach tools stay self-contained (no Obsidian dependency at runtime).
If the wiki changes, update this file.
"""

# Hard NO — reject + regenerate if any appears in output (case-insensitive, word-ish match).
FORBIDDEN_WORDS = [
    "revolutionary", "revolutionize", "game-changing", "game changer", "game-changer",
    "disrupt", "disruptive", "disruption", "synergy", "synergies", "cutting-edge",
    "cutting edge", "empower", "empowering", "unlock your potential", "unlock potential",
    "supercharge", "leverage", "paradigm", "next-level", "best-in-class",
    "we're not just an agency", "we are not just an agency", "movement",
]

POSITIONING = (
    "Setu is an AI agency that finds where AI saves a business time and money, then builds it — "
    "one workflow at a time. Tagline: \"AI that pays you back. One workflow at a time.\" / "
    "\"Built, not advised.\" Setu means bridge."
)

VALUES = [
    "Work, not tech — lead with hours saved / money / outcomes, never model names or APIs.",
    "Quiet over loud — calm, confident, plainspoken. No hype.",
    "Respect owners — never lecture; show you understand their workflow first.",
    "Ship, don't slide — point to something running, built, real.",
    "Map before build — show the diagnosis; prep earns the right to recommend.",
]

VOICE_DO = [
    "Specifics — real hours, real money, real workflows.",
    "Short sentences, plain words.",
    "Outcome first; mention tech quietly only if needed.",
    "Warm, peer-to-peer; quietly confident expert.",
]

VOICE_DONT = [
    "Abstractions: 'synergies', 'ecosystems', 'solutions'.",
    "Jargon, hype, leading with the tech stack.",
    "Sales-y pressure or flattery.",
    "Fabricated or unverifiable claims.",
]

COPY_TEST = (
    "Would a smart, busy interior-design studio owner read this and feel respected — not sold to? "
    "If sold to, rewrite."
)


def voice_system_prompt(segment: str = "interior design studio") -> str:
    """System prompt fragment encoding Setu voice for any copy task."""
    return f"""You write outreach copy for Setu, an AI agency. {POSITIONING}

Audience: a founder-owner of a {segment} (India, 3–50 people, runs on WhatsApp/Excel/email).

Setu's five values (every line must pass):
- {chr(10).join('  ' + v for v in VALUES)}

Voice — DO:
- {chr(10).join('  ' + d for d in VOICE_DO)}
Voice — DON'T:
- {chr(10).join('  ' + d for d in VOICE_DONT)}

Copy test (apply before finalizing): {COPY_TEST}

NEVER use these words/phrases: {", ".join(FORBIDDEN_WORDS)}.
Never fabricate facts about the prospect — use only what you are given. If you lack a specific
hook, be honestly generic rather than inventing a connection."""


def find_forbidden(text: str):
    """Return list of forbidden words/phrases present in text (case-insensitive)."""
    low = text.lower()
    return [w for w in FORBIDDEN_WORDS if w in low]
