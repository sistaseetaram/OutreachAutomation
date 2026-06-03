# Workflow: LinkedIn Outreach (NEW account — manual sends)

**Objective:** Connect with interior-design founders safely from a new LinkedIn account, generate
personalized requests, and never trip LinkedIn's spam throttles.

## Hard safety rules (new account <3 months)
- **Warmup ramp:** Week 1–2: 5–10 requests/day · Week 3: 10–15 · Week 4: 15–20 · then 20–25/day max.
- Spread across business hours; vary timing; do not batch-blast.
- **Acceptance rate matters:** keep >40% accepted. If acceptance drops, slow down.
- **All sends are MANUAL.** We generate the content; you paste-send. No automation tool on a new account.
- Engage first (like/comment on 1–2 of their posts) before sending the request when possible.

## Procedure (per lead)
1. `company_researcher.py --company "<studio>"` → profile to `.tmp/<slug>_profile.md`.
2. `personalization_engine.py --studio "<studio>" --channel linkedin_note --stage first_touch --profile <p>`
   → ≤300-char note (signal-grounded, 0 forbidden words).
3. `clickup_sync.py` (or `lead_tracker.py --advance`) → status `Contacted`, log the note.
4. `drive_sync.py --subfolder messages` → save the note to the lead's Drive folder.
5. You manually send the connection request with that note. Stop at today's safe slice.

## After acceptance
- `--channel linkedin_dm --stage first_touch` → soft opener (no pitch).
- If conversation warms → `--stage loom_invite` → offer the free Loom (use `loom-outreach` skill to script).

## Role-based sequence (Day 0 / 3 / 7 / 14)
- Decision-maker (founder): Day0 connect+note · Day3 follow-up · Day7 value/Loom · Day14 soft ask.
- Cadence + caps live in `lead_tracker.py` (`--next`). Warm = up to 4 touches.

## Daily run
`lead_tracker.py --next` → today's due actions · then send today's warmup slice of NEW requests.
`whatsapp_notifier.py` pings you the digest.
