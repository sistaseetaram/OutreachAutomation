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
