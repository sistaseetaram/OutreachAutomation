# ⭐ OUTREACH THREAD — Resume Log

> **Thread trigger:** when the user says "continue with the outreach" / "cold outreach" / "the outreach
> system" → THIS project (`OutreachAutomation`, the Setu Outreach Engine). Separate from parallel
> threads: `buildbridge` (Artchitectural_design_automation), MyPersonalBrand, ContentGenerator. Do not
> mix them.

**Last session:** 2026-06-07. Phase 1 BUILT + tested. Plan: `.claude/plans/ticklish-sauteeing-wilkinson.md`.

---

## State: Phase 1 complete (code), activation in progress

### Built + verified (✓ ran live on real data)
- `tools/`: config_loader, setu_voice, **personalization_engine✓**, **lead_tracker✓** (+cadence),
  lead_sourcer, lead_enrichment, **reply_classifier✓**, clickup_sync, clickup_build_out, drive_sync,
  **whatsapp_notifier✓**, whatsapp_sender
- Skill `.claude/skills/loom-outreach/`; 7 workflows in `workflows/`; v3 diagram in `artifacts/visuals/`
- Demo lead seeded in `.tmp/leads.json`: **Nine Bricks Studio** (sister Manjusha, warm, case-study #1)
- venv at `.venv` (run tools with `.venv/bin/python`)

### Staged THIS session
- `credentials/credentials.json` ← copied from `Documents/credentials/Gemini_API_OAuth/client_secret_web_client_2.json`
  - ⚠️ **type = "web"** (not Desktop). If `drive_sync.py` consent fails → make a **Desktop-app** OAuth
    client OR add `http://localhost` to the web client's redirect URIs. Drive+Sheets APIs must be enabled.
- `WHATSAPP_NOTIFY_TO=+919381814214` set in `credentials/.env` (spare-SIM WhatsApp).

### MCP situation (reload on fresh session)
- User connected **ClickUp MCP** + **Apollo MCP**. They disconnected at session end → reload next session.
- **Decision pending:** drive ClickUp/Apollo via **MCP** (interactive, one-time build-out + sourcing) vs
  **REST API token** (my Python tools `clickup_sync.py` / `lead_sourcer.py --apollo` use tokens, better for
  the automated daily loop). Recommend: use MCP for the one-time ClickUp build-out + ad-hoc Apollo pulls;
  add API tokens later if/when automating. Tools already dry-run-safe without tokens.

---

## NEXT STEPS (on resume, in order)
1. ~~**Drive:** done 2026-06-07. Desktop OAuth (YouTube creds reused). `token.json` saved. `GOOGLE_DRIVE_CLIENTS_FOLDER_ID=19o6XUb7KKTUeg2Lv_ggTitq0_TxTPpui` set. Nine Bricks first-touch uploaded to `Outreach/Leads/interior/Nine Bricks Studio/messages`.~~
2. ~~**ClickUp:** done 2026-06-07. Space `Setu — Outreach & Clients` (ID `90167179838`) built. Lists: Leads (`901615297544`), Engaged Clients (`901615297545`). 6 custom fields + stage tags. Nine Bricks Studio seeded. IDs in `.claude/mcp-registry.md`.~~
3. ~~**Apollo:** skipped — free plan blocks People Search API. Defer to Phase 2 cold outreach.~~
4. ~~**WhatsApp:** done 2026-06-08. Tokens set (`WHATSAPP_TOKEN`, `WHATSAPP_PHONE_ID`, `WHATSAPP_BUSINESS_ACCOUNT_ID`). API verified (200 + valid wa_id). Test delivery to spare SIM unreliable (Meta test number limitation) — will resolve when real business number registered.~~
5. **NEXT SESSION: Start warm outreach.** Nine Bricks Studio already active (skip). Add other warm leads to tracker → draft first-touch messages → send.

## Pending (later)
- Phase 2: cold email (domain + 2–3wk warmup + email_sender/compliance/domain_checker) for NRI + global English.
- Add other 4 warm leads to tracker.

## Guardrails (don't forget)
- New LinkedIn acct → manual sends, warmup ramp 5–10/day. WhatsApp warm/engaged only, never cold.
- Storage: outreach → Drive; local `~/Desktop/MyClients/` only on active paid delivery.
- Setu voice enforced via `tools/setu_voice.py` (forbidden words). Conservative ROI, no inflated claims.
