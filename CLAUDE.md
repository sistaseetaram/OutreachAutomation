@/Users/sistaseetaram/Desktop/Claude/Youtubers/Nate/CLAUDE.md

## Branch ownership

Codex is implementing ClickUp outreach tracking on branch `codex`. Claude must not switch to, edit, or merge that branch unless the user explicitly instructs Claude to do so.

## Wiki context

This project loads the MentorsWikki wiki at `/Users/sistaseetaram/Documents/Obsidian Vault/MentorsWikki`.

At session start: read `/Users/sistaseetaram/Documents/Obsidian Vault/MentorsWikki/AGENTS.md`, then `wiki/index.md` + all `wiki/syntheses/`. Claude automates this through `.claude/settings.json`; other agents must do it by hand.

At session end: run the write-back check: "Did anything this session contradict or extend the wiki?" Append to `wiki/log.md` if yes.

Current outreach doctrine from MentorsWikki (cached snapshot — verify against wiki syntheses if doctrine seems stale):
- 100 daily primary outreach actions is the volume floor.
- At Setu's pre-revenue stage, proof-led warm outreach beats paid acquisition.
- Use one deeply scoped offer before building a services menu.
- For first clients, prioritize warm contacts in architecture/interior/construction and sell one concrete workflow outcome.

## Industry Targeting — LOCKED (2026-06-15)

Active target: **Architecture firms + Interior Design Studios**. Full pain brief,
hooks, ROI, and product ranking live in `artifacts/outreach/target-brief.md`
(visual: `arch-interior-pain-infographic.html`). Read the brief before drafting outreach.

**Top 3 pains → product:** (1) Slow lead response → Live Lead Engagement · (2) Follow-up
black hole → Lead Reactivation SMS · (3) Senior time drain → Website Widget.

**Outreach rule:** Every message on every platform opens with ONE of these 3 pains and
names ONE specific product fix. Never a generic "AI automation" opener. Anchor ROI in ₹, not just %.

## Applied Learning

- **Dashboard writing style — never caveman.** Everything written into `dashboard/` (threads,
  lead cards, status) uses clean, full, normal English with structured + flexible UI. No
  caveman/terse fragments in dashboard content, regardless of session caveman mode.

<!-- Add one-line bullets here as we discover platform quirks, rate limits, workarounds -->

### Advice & drafting discipline — STRICT (locked 2026-06-13)

Every recommendation and every draft must pass these before it leaves your mouth:

1. **Stage-aware, never generic.** Setu is pre-revenue, ~6 warm sends in, one pilot (Nine Bricks), zero paid clients. Calibrate advice to THIS stage — not generic agency playbooks written for funded/scaled shops. If a tactic assumes a team, ad budget, or existing clients he doesn't have, it's wrong here.
2. **Grounded, not hallucinated.** No invented facts, names, dates, firms, prices, or stats. Ground claims in his locked doctrine (`artifacts/outreach/current-strategy.md`), MentorsWikki, and the `artifacts/references/` frameworks. If you can't verify it, say "I can't confirm this" — never guess.
3. **Check before you drop.** Never put a date, day, time, name, number, or URL into a draft without verifying it first. Dates/days: run `date` and compute the actual gap (a Saturday message proposing "Thu/Fri" is a real miss). Names: confirm spelling. This is non-negotiable.
4. **Mentor, not yes-man.** Push back on off-doctrine impulses (e.g., free websites, widening the offer) even when Setu proposes them. Recommend a clear path; don't just validate. He has explicitly asked to be guided, not agreed with.
