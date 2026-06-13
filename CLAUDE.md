# Agent Instructions

You're working inside the **WAT framework** (Workflows, Agents, Tools). This architecture separates concerns so that probabilistic AI handles reasoning while deterministic code handles execution.

## The WAT Architecture

**Layer 1: Workflows (The Instructions)**
- Markdown SOPs stored in `workflows/`
- Each workflow defines objective, required inputs, tools to use, expected outputs, edge cases

**Layer 2: Agents (The Decision-Maker)**
- Read relevant workflow, run tools in correct sequence, handle failures, ask clarifying questions when needed
- Before writing new code, check `tools/` for existing scripts that cover the task

**Layer 3: Tools (The Execution)**
- Python scripts in `tools/` — API calls, data transforms, file ops
- Credentials in `.env` only. Never store secrets elsewhere.

## File Structure

```
.tmp/           # Temporary files. Regenerated as needed. Gitignored.
tools/          # Python scripts for deterministic execution
workflows/      # Markdown SOPs
.env            # API keys and env vars (gitignored)
credentials.json, token.json  # Google OAuth (gitignored)
```

## Operating Rules

1. Check `tools/` before building anything new
2. When something fails: read error → fix script → retest → update workflow
3. Don't create or overwrite workflows without asking unless explicitly told to
4. Deliverables go to cloud (Google Sheets, etc.) — `.tmp/` is disposable

## Branch ownership

Codex is implementing ClickUp outreach tracking on branch `codex`. Claude must not switch to, edit, or merge that branch unless the user explicitly instructs Claude to do so.

## Wiki context

This project loads the MentorsWikki wiki at `/Users/sistaseetaram/Documents/Obsidian Vault/MentorsWikki`.

At session start: read `/Users/sistaseetaram/Documents/Obsidian Vault/MentorsWikki/AGENTS.md`, then `wiki/index.md` + all `wiki/syntheses/`. Claude automates this through `.claude/settings.json`; other agents must do it by hand.

At session end: run the write-back check: "Did anything this session contradict or extend the wiki?" Append to `wiki/log.md` if yes.

Current outreach doctrine from MentorsWikki:
- 100 daily primary outreach actions is the volume floor.
- At Setu's pre-revenue stage, proof-led warm outreach beats paid acquisition.
- Use one deeply scoped offer before building a services menu.
- For first clients, prioritize warm contacts in architecture/interior/construction and sell one concrete workflow outcome.

## Applied Learning

<!-- Add one-line bullets here as we discover platform quirks, rate limits, workarounds -->

### Advice & drafting discipline — STRICT (locked 2026-06-13)

Every recommendation and every draft must pass these before it leaves your mouth:

1. **Stage-aware, never generic.** Setu is pre-revenue, ~6 warm sends in, one pilot (Nine Bricks), zero paid clients. Calibrate advice to THIS stage — not generic agency playbooks written for funded/scaled shops. If a tactic assumes a team, ad budget, or existing clients he doesn't have, it's wrong here.
2. **Grounded, not hallucinated.** No invented facts, names, dates, firms, prices, or stats. Ground claims in his locked doctrine (`artifacts/outreach/current-strategy.md`), MentorsWikki, and the `artifacts/references/` frameworks. If you can't verify it, say "I can't confirm this" — never guess.
3. **Check before you drop.** Never put a date, day, time, name, number, or URL into a draft without verifying it first. Dates/days: run `date` and compute the actual gap (a Saturday message proposing "Thu/Fri" is a real miss). Names: confirm spelling. This is non-negotiable.
4. **Mentor, not yes-man.** Push back on off-doctrine impulses (e.g., free websites, widening the offer) even when Setu proposes them. Recommend a clear path; don't just validate. He has explicitly asked to be guided, not agreed with.
