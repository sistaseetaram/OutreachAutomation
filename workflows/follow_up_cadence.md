# Workflow: Follow-up Cadence

**Objective:** Consistent, non-spammy follow-ups. Warm gets persistence; cold gets one polite nudge.

## Caps (enforced in `lead_tracker.py`)
- **Warm: up to 4 follow-ups** (gap ~3 days). Channels: LinkedIn / WhatsApp / Instagram.
- **Cold: 1 follow-up** (gap ~5 days). Then → Nurture.
- 3:1 value-to-ask: most touches give something, don't just ask.

## Schedule (warm, Day 0 anchor)
- Day 0: first touch (connect/DM/WhatsApp)
- Day 3: Follow-up 1 — value angle, no ask (`--stage followup`)
- Day 7: Follow-up 2 — Loom invite (`--stage loom_invite`)
- Day 11: Follow-up 3 — different angle / mini case
- Day 14: Follow-up 4 — soft ask, then breakup (`--stage breakup`)

## Cold
- Day 0: first touch · Day 5: Follow-up 1 (one value nudge) · then Nurture.

## Run
- `lead_tracker.py --next` lists who's due today (respects caps).
- Generate the message with `personalization_engine.py --stage <followup|loom_invite|breakup>`.
- `whatsapp_notifier.py` sends you the daily digest.
- On reply → `reply_classifier.py` routes (interested→Replied, not_now→Nurture, unsubscribe→Lost+remove).

## Rule
Never exceed the cap. Silence after the cap = move to Nurture, not more messages.
