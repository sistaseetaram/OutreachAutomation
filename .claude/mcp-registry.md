# MCP Registry — OutreachAutomation

> Cache of connected MCP servers, key tool names, and resolved IDs.
> Load this instead of calling ToolSearch/get_workspace_hierarchy at session start.
> Updated: 2026-06-07

---

## ClickUp MCP (`mcp__claude_ai_ClickUp__*`)

**Workspace:** `90161624544` (Team Space ID: `90167029985`)
**Space:** `Setu — Outreach & Clients` → ID `90167179838`
**Lists:**
- Leads → `901615297544`
- Engaged Clients → `901615297545`

**Key tools (load schema via ToolSearch `select:` before calling):**
| Tool | Purpose |
|------|---------|
| `clickup_get_workspace_hierarchy` | Map spaces/folders/lists |
| `clickup_create_task` | Add task to list (needs `list_id`) |
| `clickup_update_task` | Edit task (needs `task_id`) |
| `clickup_filter_tasks` | Search tasks in list |
| `clickup_create_folder` | New folder in space |
| `clickup_create_list` | New list in space/folder |
| `clickup_get_custom_fields` | Get field IDs for a list |

**Custom fields on Leads list (IDs resolved at runtime via `clickup_sync.list_fields`):**
- LinkedIn URL (url), Instagram (url), Email (email), Drive Folder (url)
- Follow-up count (number), Source (drop_down: apollo/instagram/maps/justdial/salesnav/referral/manual)

**Pipeline stages (encoded as tags `stage:xxx` — Free plan has no custom statuses):**
sourced → researched → queued → contacted → follow-up-1..4 → replied → diagnosis-booked → free-build → delivered → testimonial-referral → nurture → won → lost

**Segment tags:** warm, cold, interior, architecture, construction, NRI, founding-client

---

## Apollo MCP (`mcp__claude_ai_Apollo_io__*`)

**Status:** Connected (reconnect each session via Claude MCP panel)
**Key tools:**
| Tool | Purpose |
|------|---------|
| `apollo_mixed_people_api_search` | Search contacts by title/location/company |
| `apollo_mixed_companies_search` | Search companies |
| `apollo_contacts_create` | Add contact to Apollo |
| `apollo_emailer_campaigns_search` | List sequences |

---

## Google Drive / Sheets

**Auth:** OAuth Desktop client (`credentials/credentials.json` + `credentials/token.json`)
**Scopes:** `drive`, `spreadsheets`
**Folder IDs:**
- Clients root: `19o6XUb7KKTUeg2Lv_ggTitq0_TxTPpui`

**Tier paths:**
- Outreach leads: `Outreach/Leads/<segment>/<studio>/<subfolder>`
- Clients: `Clients/<studio>/<subfolder>`

---

## Env vars summary (credentials/.env)

| Var | Status |
|-----|--------|
| `CLICKUP_API_KEY` | set |
| `CLICKUP_TEAM_ID` | `90161624544` |
| `CLICKUP_LEADS_LIST_ID` | `901615297544` |
| `GOOGLE_DRIVE_CLIENTS_FOLDER_ID` | `19o6XUb7KKTUeg2Lv_ggTitq0_TxTPpui` |
| `ANTHROPIC_API_KEY` | set |
| `OPENROUTER_API_KEY` | set |
| `APPOLO_API_KEY` | set |
| `WHATSAPP_NOTIFY_TO` | set |
