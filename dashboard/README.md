# 📋 Setu Warm Outreach Dashboard

The fast working layer for warm outreach. One file per lead in [`threads/`](threads/),
each carrying that lead's research, ready-to-send messages, full thread log, and current status.
The board below is **auto-generated** from those files — never edit it by hand.

- **Playbook (the sales rules):** [SALES-PLAYBOOK.md](SALES-PLAYBOOK.md)
- **Strategy of record:** [../artifacts/outreach/current-strategy.md](../artifacts/outreach/current-strategy.md)
- **Analytics of record:** ClickUp space *Setu — Outreach & Clients*

---

## The Board

<!-- BOARD:START -->
**12 leads** — 🌶️ 1 interested  ·  💬 1 replied  ·  🤝 1 connected  ·  📨 3 connect-sent  ·  🆕 6 new

| | Status | Lead | Firm | ICP | Geo | Next action | Due |
|---|---|---|---|---|---|---|---|
| 🌶️ | interested | [The Studio Artha](threads/studio-artha.md) | The Studio Artha | 🟢 | andhra-pradesh | REVIVE — follow up to lock a call time (he agreed in principle, then went silent; our follow-up never went out) | 2026-06-13 |
| 💬 | replied | [Avinash Doddathippanna](threads/avinash-doddathippanna.md) | — | 🟡 | uk | Chase the promised referral (interiors/manufacturing) — follow-up overdue | 2026-06-13 |
| 🤝 | connected | [Nine Bricks Studio](threads/nine-bricks-studio.md) | Nine Bricks Studio | 🟢 | bengaluru | Follow-up #1 — this is the active pilot / proof firm | 2026-06-13 |
| 📨 | connect-sent | [Claudia Duffield](threads/claudia-duffield.md) | — | 🟡 | canada | Awaiting reply — bump after 5–7 days; she's an advisor, not a buyer | 2026-06-14 |
| 📨 | connect-sent | [Earl Lawson](threads/earl-lawson.md) | V6B Design Group | 🟡 | vancouver | Awaiting reply — bump after 5–7 days with a soft value-add | 2026-06-14 |
| 📨 | connect-sent | [Eric Marshall](threads/eric-marshall.md) | — | 🟡 | arizona | Awaiting reply — bump after 5–7 days with a soft value-add | 2026-06-14 |
| 🆕 | new | [Prashanthi Narapasetty](threads/prashanthi-narapasetty.md) | Design Dialogue | 🟢 | hyderabad | Step 1 — comment on her recent post, then send connect request | 2026-06-13 |
| 🆕 | new | [Shravani Reddy](threads/shravani-reddy.md) | Spacetime Creative | 🟢 | hyderabad | Step 1 — comment on her recent post, then send connect request | 2026-06-13 |
| 🆕 | new | [Monica Reddy](threads/monica-reddy.md) | Studio Purple Elephant | 🟡 | hyderabad | Instagram — comment on a recent post, then DM (she's IG-active) | 2026-06-13 |
| 🆕 | new | [Raveena Avanthi](threads/raveena-avanthi.md) | KalaaZodh Architecture | 🟡 | hyderabad | Instagram — comment on recent post, then DM (LinkedIn inactive) | 2026-06-13 |
| 🆕 | new | [Sravani Andhavarapu](threads/sravani-andhavarapu.md) | Hypercube Studio | 🟡 | hyderabad | Step 1 — comment on her recent post, then send connect request | 2026-06-13 |
| 🆕 | new | [Jyothi Kuchibhotla](threads/jyothi-kuchibhotla.md) | Skydes Studio | 🔴 | hyderabad | VERIFY ownership before investing — then Step 1/2 if she's a principal | 2026-06-13 |
<!-- BOARD:END -->

Legend — Status: ✅ converted · 🔥 call-booked · 🌶️ interested · 💬 replied · 🤝 connected · 📨 connect-sent · 👀 engaging · 🆕 new · ⏳ not-now · ⚰️ dead.  ICP: 🟢 strong · 🟡 medium · 🔴 weak.

---

## 🎯 Today's play (Step 1 + Step 2)

For every 🆕 new lead, in order:

1. **Step 1 — engage their post.** Open the lead's thread, copy the *Step 1* comment, post it on their most recent relevant LinkedIn post. (Verify it's actually their latest post first — research was done off-LinkedIn.) This warms the connection.
2. **Step 2 — send the connection request.** Copy the *Step 2* message (≤300 chars, no pitch) and send the connect.
3. Log it: in the thread file, set `status: connect-sent`, set `last_touch:` to today, add a row to the Thread log. Run `python dashboard/build_board.py`.

> ⚠️ LinkedIn safety: **max 20–25 connection requests/day.** Randomize timing. 6 today is well within limits.
> **Step 3** (follow-up DM) fires only *after* they accept. **No pitch until they reply** — see the playbook.

**Priority order today:** 🟢 Shravani Reddy & Prashanthi Narapasetty first (bullseye owners), then 🟡 Raveena Avanthi & Sravani Andhavarapu. Jyothi & Monica are 🔴 weak (not owners) — see their cards before spending a touch.

**Don't forget the warm pipeline:** 🔥 **Studio Artha** has a diagnosis call booked — that's the highest-value action in the whole board. **Nine Bricks** (the pilot) needs follow-up #1. **Avinash** owes a referral (overdue).

---

## 🔁 Outreach Watch Mode (session-scoped, you turn it on)

Not a 24/7 daemon — a watch you switch on when you sit down to do outreach, off when done.
Detection is a tokenless script; drafting is Claude, looping during your session.

**Start it:** tell Claude **"starting outreach"**. Claude then loops until you say **"stop outreach"**:
1. runs `python dashboard/scan_replies.py` to find threads with a reply logged but no draft,
2. drafts the next message (per [SALES-PLAYBOOK.md](SALES-PLAYBOOK.md)) into each thread's **Next reply** section,
3. rebuilds the board + `board.html`, and tells you what's ready.

**Log a reply (two ways — pick either):**
- **CLI:** `python dashboard/log_reply.py shravani-reddy --text "Sure, tell me more"`
- **Just paste it to Claude:** "Shravani replied: …" — Claude logs it and drafts.

**The detector** (`scan_replies.py`) flags a thread when its Thread log has an `| … | IN | … |` row
but the **Next reply** section is still empty. Run `python dashboard/scan_replies.py` anytime to see
the draft queue (`--json` for the loop).

> Why not an always-on agent? At your stage there's no event stream to justify a daemon, and a
> subagent can't persist/listen anyway (they're one-shot). Drafting needs an LLM — so the model is:
> **detection automated, drafting by Claude inside a watch loop you control.**

---

## How to use this dashboard

### When a lead replies
Paste their reply to Claude (or add it to the thread log as an `IN` row). Claude reads the
[playbook](SALES-PLAYBOOK.md) reply-handling rules and writes the recommended next message into
that thread's **"Next reply"** section.

### Add a new lead — two ways
- **You (CLI):**
  ```bash
  python dashboard/add_lead.py --name "Asha Rao" --firm "Studio X" \
      --linkedin "https://www.linkedin.com/in/asha-rao/" --geo hyderabad --icp medium
  ```
- **Claude:** just ask — Claude researches the profile, writes the `threads/<slug>.md`, and rebuilds the board.

### Update a lead's status
Edit the `status:` (and `last_touch:`, `next_action:`) in the thread's front matter, add a thread-log row,
then run `python dashboard/build_board.py`. Mirror the stage tag in ClickUp so the 100-send review stays accurate.

### Status flow
`new → engaging → connect-sent → connected → replied → interested → call-booked → converted`
(off-ramps: `not-now`, `dead`)
