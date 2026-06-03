# Setu Outreach Engine — Activation Checklist

Everything is **built and tested in dry-run**. To go live, provide the keys below (in priority order).
All secrets go in `credentials/.env` (copy from `credentials/.env.template`) or `credentials/credentials.json`.
Check wiring anytime (masked, no values printed): `.venv/bin/python tools/config_loader.py`

Run tools with the venv: `.venv/bin/python tools/<tool>.py`

---

## 1. Google Drive + Sheets  (storage — highest priority)
- Google Cloud Console → enable **Drive API + Sheets API** → create **OAuth client (Desktop app)**.
- Save the client secrets as `credentials/credentials.json` (personal Gmail).
- Paste your existing Drive **"Clients" folder link** → I'll set `GOOGLE_DRIVE_CLIENTS_FOLDER_ID`.
- First run opens a browser consent → writes `credentials/token.json`.
- Test: `.venv/bin/python tools/drive_sync.py --studio "Nine Bricks Studio" --tier outreach --subfolder messages --file .tmp/nine_bricks_studio_linkedin_note_first_touch.md`

## 2. ClickUp  (CRM)
- ClickUp → Settings → Apps → **generate API token** → `CLICKUP_API_TOKEN` in `credentials/.env`.
- Build the workspace: `.venv/bin/python tools/clickup_build_out.py --create`
- Paste the printed `CLICKUP_TEAM_ID` + `CLICKUP_LEADS_LIST_ID` into `credentials/.env`.
- Seed leads: `.venv/bin/python tools/clickup_build_out.py --seed`

## 3. WhatsApp Business Cloud API  (warm sends + self-notify) — parallel track, ~days
- Meta Business Account → WhatsApp → add **spare SIM** number (no consumer WhatsApp active on it).
- Verify business using **setuagency.com** domain → display-name approval → submit **message templates**.
- Fill `WHATSAPP_TOKEN`, `WHATSAPP_PHONE_ID`, `WHATSAPP_BUSINESS_ACCOUNT_ID`, `WHATSAPP_NOTIFY_TO` (your number), `WHATSAPP_TEMPLATE_FOLLOWUP`.
- Until approved: send warm WhatsApp manually from your phone; notifier prints to console.
- Test: `.venv/bin/python tools/whatsapp_notifier.py`

## 4. Apollo  (one lead source) — free tier
- Apollo → Settings → API → key → `APOLLO_API_KEY`.
- Test: `.venv/bin/python tools/lead_sourcer.py --apollo --apollo-title "interior designer" --apollo-geo "India"`

## 5. Apify  (Instagram / Google Maps / Justdial scrapers)
- apify.com → Settings → Integrations → **API token** → `APIFY_API_TOKEN`.

---

## Daily run loop (once live)
1. `.venv/bin/python tools/lead_tracker.py --next`            # who's due today (warm 4 / cold 1 caps)
2. `.venv/bin/python tools/whatsapp_notifier.py`              # digest to your WhatsApp
3. Per due lead: `personalization_engine.py` → send manually (LinkedIn warmup slice ≤10/day on new acct)
4. `lead_tracker.py --advance <slug>` + `clickup_sync.py` + `drive_sync.py`
5. On reply: `reply_classifier.py --text "..." --studio "..." --apply`
6. Positive → free diagnosis (Gem) → free build (buildbridge) → Loom → fence (testimonial + referral)

## What's built (all in `tools/` unless noted)
config_loader · setu_voice · personalization_engine · lead_tracker (incl. cadence) · lead_sourcer ·
lead_enrichment · reply_classifier · clickup_sync · clickup_build_out · drive_sync · whatsapp_notifier ·
whatsapp_sender · skill `.claude/skills/loom-outreach/` · 7 workflows in `workflows/` · funnel diagram in `artifacts/visuals/`.

## Reminders
- LinkedIn new account: warmup ramp 5–10/day → 20–25/day; never blast. Manual sends only.
- WhatsApp: warm/engaged only, never cold.
- Storage: outreach artifacts → Drive (not local); local `~/Desktop/MyClients/` only on active paid delivery.
- Phase 2 (next): cold email (domain + warmup + compliance) for NRI + global English market.
