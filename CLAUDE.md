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

## Applied Learning

<!-- Add one-line bullets here as we discover platform quirks, rate limits, workarounds -->
