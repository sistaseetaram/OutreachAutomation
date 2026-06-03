# credentials/

Single home for all secrets. **Nothing here is committed** except this README and `.env.template`
(see `.gitignore`). Loaded by `tools/config_loader.py`.

## Files (you create these — gitignored)

| File | What | Account |
|---|---|---|
| `.env` | All API keys / tokens | — |
| `credentials.json` | Google OAuth client secrets (Drive + Sheets scope) | `personal` (Gmail: storage + notifications) |
| `token.json` | Cached Google OAuth token (auto-created on first auth) | `personal` |
| `credentials.sender.json` / `token.sender.json` | *(future)* separate email-campaign account | `sender` |

## Setup

1. `cp credentials/.env.template credentials/.env` and fill values.
2. Drop your Google OAuth client secrets as `credentials/credentials.json`
   (Google Cloud Console → enable **Drive API + Sheets API** → OAuth client → Desktop app).
3. First Google call opens a browser consent → writes `credentials/token.json`.
4. Check wiring (masked, no values printed): `python tools/config_loader.py`

## Multi-account

`personal` = your Gmail (Drive/Sheets/WhatsApp notify) now. A future `sender` account (email
campaigns) is supported via `GOOGLE_ACCOUNT_SENDER_CREDENTIALS` / `_TOKEN` in `.env` — no code change.

## Rule

Secrets are read for use only — never echoed to the chat or logs. Status is reported masked
(`KEY=<set>` / `<not set>`).
