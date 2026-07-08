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


---

## ⚠ VAULT MIGRATION — one-time, self-removing (added 2026-07-08)

This project's secrets now live in the **AIOS vault** (`~/.config/aios-vault/master.env`),
under the project key **`OutreachAutomation`**. Do this ONCE, before other work, then remove this block:

1. **WIRE** (make the entry point load from the vault instead of the local `.env`):
   **Already wired** — the entry point loads from the vault. Just VERIFY + CLEAN below.

2. **VERIFY** the keys resolve, and the project actually runs pulling from the vault:
   ```bash
   python3 ~/Desktop/Claude/SharedInfra/vault/vault_loader.py --audit OutreachAutomation
   ```

3. **IF it works** (all required keys `<set>`, project runs):
   a. Overwrite `credentials/.env` with ONLY this line — strip every secret value:
      `# Secrets moved to ~/.config/aios-vault/master.env — load via SharedInfra vault_loader`
   b. **Delete this entire "VAULT MIGRATION — one-time, self-removing" block from this file.** Migration done.

4. **IF it fails** (missing keys / load error): leave `credentials/.env` untouched, report which
   keys are missing (add them to the vault via `master.env`), and keep this block for next time.

**Never print secret values** during any of this. Confirm with masked `--audit` only.
