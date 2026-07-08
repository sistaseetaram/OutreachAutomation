#!/usr/bin/env python3
"""
config_loader.py — central config + credential loader for OutreachAutomation.

All secrets live in `credentials/.env` and `credentials/credentials.json` (gitignored).
Multi-account ready: a `personal` Google account (Drive/Sheets/notifications) now, and a
future `sender` account (email campaigns) later — each with its own creds/token path.

Usage:
    from tools.config_loader import env, require_env, is_set, google_creds_path, SCOPES
    key = require_env("ANTHROPIC_API_KEY")

CLI:
    python tools/config_loader.py        # prints masked credential status
"""

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CREDENTIALS_DIR = PROJECT_ROOT / "credentials"
ENV_PATH = CREDENTIALS_DIR / ".env"
ROOT_ENV = PROJECT_ROOT / ".env"  # legacy fallback

# Load from central vault first; fall back to local .env during transition.
_SHARED_INFRA = Path.home() / "Desktop/Claude/SharedInfra"
try:
    if str(_SHARED_INFRA) not in sys.path:
        sys.path.insert(0, str(_SHARED_INFRA))
    from vault.vault_loader import load_for_project
    load_for_project("OutreachAutomation", strict=False)
except Exception:
    from dotenv import load_dotenv
    if ENV_PATH.exists():
        load_dotenv(ENV_PATH)
    elif ROOT_ENV.exists():
        load_dotenv(ROOT_ENV)

# Google OAuth scopes — Drive + Sheets (personal account = storage + notifications).
SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets",
]

_PLACEHOLDERS = {"", "your_key_here", "your-key-here", "changeme", "TODO"}


def env(key: str, default=None):
    """Return env var or default."""
    return os.getenv(key, default)


def is_set(key: str) -> bool:
    """True if env var is present and not a placeholder."""
    v = os.getenv(key)
    return bool(v) and v not in _PLACEHOLDERS


def require_env(key: str) -> str:
    """Return env var or raise with a clear message pointing at credentials/.env."""
    v = os.getenv(key)
    if not v or v in _PLACEHOLDERS:
        raise RuntimeError(f"{key} not set. Add it to {ENV_PATH}")
    return v


def google_creds_path(account: str = "personal") -> Path:
    """
    OAuth client-secrets path for a named Google account.
    Default `personal` -> credentials/credentials.json.
    Override via GOOGLE_ACCOUNT_<NAME>_CREDENTIALS in .env.
    """
    override = os.getenv(f"GOOGLE_ACCOUNT_{account.upper()}_CREDENTIALS")
    if override:
        return Path(override)
    if account == "personal":
        return CREDENTIALS_DIR / "credentials.json"
    return CREDENTIALS_DIR / f"credentials.{account}.json"


def google_token_path(account: str = "personal") -> Path:
    """Cached OAuth token path for a named Google account."""
    override = os.getenv(f"GOOGLE_ACCOUNT_{account.upper()}_TOKEN")
    if override:
        return Path(override)
    if account == "personal":
        return CREDENTIALS_DIR / "token.json"
    return CREDENTIALS_DIR / f"token.{account}.json"


# Keys the system expects — used for the masked status report only.
EXPECTED_KEYS = [
    "ANTHROPIC_API_KEY", "OPENROUTER_API_KEY", "GOOGLE_API_KEY", "FIRECRAWL_API_KEY",
    "KIE_AI_API_KEY", "CLICKUP_API_TOKEN", "CLICKUP_API_KEY", "CLICKUP_TEAM_ID",
    "CLICKUP_LEADS_LIST_ID", "APIFY_API_TOKEN",
    "APOLLO_API_KEY", "WHATSAPP_TOKEN", "WHATSAPP_PHONE_ID",
    "WHATSAPP_BUSINESS_ACCOUNT_ID", "GOOGLE_DRIVE_ROOT_FOLDER_ID",
    "GOOGLE_DRIVE_CLIENTS_FOLDER_ID",
]


def masked_report() -> str:
    """Masked presence report — never prints values (per security rule)."""
    lines = ["Credential status (masked):"]
    for k in EXPECTED_KEYS:
        lines.append(f"  {k}=<{'set' if is_set(k) else 'not set'}>")
    creds = google_creds_path("personal")
    lines.append(f"  credentials/credentials.json=<{'present' if creds.exists() else 'missing'}>")
    token = google_token_path("personal")
    lines.append(f"  credentials/token.json=<{'present' if token.exists() else 'missing'}>")
    return "\n".join(lines)


if __name__ == "__main__":
    print(f"PROJECT_ROOT: {PROJECT_ROOT}")
    print(f"ENV_PATH:     {ENV_PATH} (exists={ENV_PATH.exists()})")
    print(masked_report())
